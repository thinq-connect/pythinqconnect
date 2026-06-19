from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from collections import defaultdict
from dataclasses import InitVar, dataclass, field
from datetime import date
from typing import Any, ClassVar

from ..const import PROPERTY_READABLE, PROPERTY_WRITABLE
from ..device import BaseDevice
from .const import Location, Property, Resource

TYPE = "type"
UNIT = "unit"
READABILITY = "readable"
WRITABILITY = "writable"
READABLE_VALUES = "read_values"
WRITABLE_VALUES = "write_values"

USAGE_MONTHLY = "MONTHLY"
USAGE_DAILY = "DAILY"


class ConnectDeviceProfile:
    def __init__(
        self,
        profile: dict[str, Any],
        resource_map: dict[str, Resource] | None = None,
        profile_map: dict[str, dict[str, Property]] | None = None,
        location_map: dict[str, Location] | None = None,
        custom_resources: list[str] | None = None,
        use_extension_property: bool = False,
        use_sub_profile_only: bool = False,
        use_notification: bool = True,
    ):
        self._RESOURCE_MAP: dict[str, Resource] = resource_map or {}
        self._LOCATION_MAP: dict[str, Location] = location_map or {}
        self._PROFILE: dict[str, dict[str, Property]] = profile_map or {}
        self._CUSTOM_RESOURCES: list[str] = custom_resources or []

        self._properties: dict[str, list] = {}
        self._location_properties: dict[str, dict[str, list]] = {}

        self.generate_notification(notification=profile.get("notification") if use_notification else None)

        if not use_sub_profile_only:
            self.generate_error(errors=profile.get("error"))
            self.generate_properties(
                property=profile.get("property" if not use_extension_property else "extensionProperty")
            )
            self.generate_property_map()
        else:
            self._error = None

    @staticmethod
    def _safe_get(data, *keys):
        for key in keys:
            try:
                data = data[key]
            except (TypeError, KeyError):
                return None
        return data

    @staticmethod
    def _is_readable_property(property: Any) -> bool:
        return (not isinstance(property, dict)) or "r" in property.get("mode", [])

    @staticmethod
    def _is_writable_property(property: Any) -> bool:
        return isinstance(property, dict) and "w" in property.get("mode", [])

    @staticmethod
    def __disable_prop_mode_value(type: str) -> dict | list:
        return {} if type == "range" else []

    @staticmethod
    def __get_readonly_string_property(value: str) -> dict:
        return {
            TYPE: "string",
            READABILITY: True,
            WRITABILITY: False,
            READABLE_VALUES: [value],
            WRITABLE_VALUES: [],
        }

    @staticmethod
    def _get_readonly_enum_property(values: list[str]) -> dict:
        return {
            TYPE: "enum",
            READABILITY: True,
            WRITABILITY: False,
            READABLE_VALUES: values,
            WRITABLE_VALUES: [],
        }

    @staticmethod
    def _get_properties(resource_property: dict, key: str) -> dict:
        _property: str | dict[str:Any] = resource_property.get(key, {})
        if isinstance(_property, str):
            return ConnectDeviceProfile.__get_readonly_string_property(_property)

        _property_type = _property.get(TYPE)
        _property_unit = _property.get(UNIT) or resource_property.get(UNIT)
        prop = {
            TYPE: _property_type,
            READABILITY: ConnectDeviceProfile._is_readable_property(_property),
            WRITABILITY: ConnectDeviceProfile._is_writable_property(_property),
            **({UNIT: _property_unit} if _property_unit else {}),
        }
        if isinstance(_property, dict) and _property_type in ["enum", "range", "list"]:
            prop[READABLE_VALUES] = (
                ConnectDeviceProfile._safe_get(resource_property, key, "value", PROPERTY_READABLE)
                if prop[READABILITY]
                else ConnectDeviceProfile.__disable_prop_mode_value(_property_type)
            )
            prop[WRITABLE_VALUES] = (
                ConnectDeviceProfile._safe_get(resource_property, key, "value", PROPERTY_WRITABLE)
                if prop[WRITABILITY]
                else ConnectDeviceProfile.__disable_prop_mode_value(_property_type)
            )
        return prop

    @property
    def properties(self) -> dict:
        return self._properties

    @property
    def location_properties(self) -> dict:
        return self._location_properties

    @property
    def property_map(self) -> dict:
        return self._property_map

    @property
    def writable_properties(self) -> list:
        _writable_props = []
        for resource in self.properties.keys():
            _writable_props.extend(getattr(self, resource)["w"])
        return _writable_props

    @property
    def notification(self) -> dict | None:
        return self._convert_property_to_profile(self._notification) if self._notification else None

    @property
    def error(self) -> list | None:
        return self._convert_property_to_profile(self._error) if self._error else None

    @property
    def locations(self):
        return self._location_properties.keys()

    def get_sub_profile(self, location_name: Location) -> ConnectDeviceProfile | None:
        if location_name in self.locations:
            return getattr(self, location_name)
        else:
            return None

    def get_location_key(self, location_name: Location) -> str | None:
        for key, name in self._LOCATION_MAP.items():
            if name == location_name:
                return key

    @staticmethod
    def _convert_property_to_profile(prop: dict) -> dict:
        if prop.get(READABLE_VALUES) or prop.get(WRITABLE_VALUES):
            return {
                TYPE: prop[TYPE],
                PROPERTY_READABLE: prop[READABLE_VALUES],
                PROPERTY_WRITABLE: prop[WRITABLE_VALUES],
                **({UNIT: prop[UNIT]} if prop.get(UNIT) else {}),
            }
        return {TYPE: prop[TYPE], PROPERTY_READABLE: prop[READABILITY], PROPERTY_WRITABLE: prop[WRITABILITY]}

    def get_property(self, property_name: str) -> dict:
        _prop = self._get_prop_attr(property_name)
        return self._convert_property_to_profile(_prop)

    def get_profile(self) -> dict:
        return self._PROFILE

    def generate_error(self, errors: list[str] | None) -> None:
        self._error = self._get_readonly_enum_property(errors) if errors else None

    def generate_notification(self, notification: dict[str, Any] | None) -> None:
        notification_push = notification and notification.get("push")
        self._notification = self._get_readonly_enum_property(notification_push) if notification_push else None

    def _get_prop_attr(self, key: Property | str) -> dict:
        return getattr(self, f"__{key}")

    def _set_prop_attr(self, key: Property | str, prop: dict) -> None:
        setattr(self, f"__{key}", prop)

    def _set_resource_props(self, resource: Resource | str, props: dict | None) -> None:
        if hasattr(self, resource):
            old_props = getattr(self, resource)
            if all([old_props, props]):
                for mode in ["r", "w"]:
                    props[mode] = old_props[mode] + props[mode]
            elif old_props:
                props = old_props
        setattr(self, resource, props)

    def _set_sub_profile(self, location_name: Location, sub_profile: ConnectDeviceProfile):
        setattr(self, location_name, sub_profile)

    def _set_properties(self, resource: Resource, value: list):
        self._properties[resource.value] = (self._properties.get(resource.value, [])) + value

    def _set_location_properties(self, location: Location, value: dict):
        self._location_properties[location.value] = value

    def _generate_custom_resource_properties(
        self, resource_key: str, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        # pylint: disable=unused-argument
        readable_props = []
        writable_props = []
        # Need to be implemented by child classes
        return readable_props, writable_props

    def _generate_resource_properties(
        self, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        readable_props = []
        writable_props = []

        for prop_key, prop_attr in props.items():
            prop = self._get_properties(resource_property, prop_key)
            if prop[READABILITY]:
                readable_props.append(str(prop_attr))
            if prop[WRITABILITY]:
                writable_props.append(str(prop_attr))
            self._set_prop_attr(prop_attr, prop)
        return readable_props, writable_props

    def generate_properties(self, property: dict[str, Any]) -> None:
        """Get properties."""
        if property is None:
            raise ValueError("Property value is None")
        for resource, props in self._PROFILE.items():
            resource_property = property.get(resource)
            _readable = None
            _writable = None
            if resource_property:
                if resource in self._CUSTOM_RESOURCES:
                    _readable, _writable = self._generate_custom_resource_properties(
                        resource, resource_property, props
                    )
                elif isinstance(resource_property, dict):
                    _readable, _writable = self._generate_resource_properties(resource_property, props)
                readable_list = _readable or []
                writable_list = _writable or []
                if readable_list or writable_list:
                    self._set_properties(self._RESOURCE_MAP[resource], list(set(readable_list + writable_list)))

                self._set_resource_props(self._RESOURCE_MAP[resource], {"r": _readable, "w": _writable})
            else:
                self._set_resource_props(self._RESOURCE_MAP[resource], None)
                for _, prop_attr in props.items():
                    self._set_prop_attr(prop_attr, {READABILITY: False, WRITABILITY: False})

    def generate_property_map(self) -> None:
        self._property_map = {}
        for properties in self.properties.values():
            for prop in properties:
                self._property_map[prop] = self.get_property(prop)

        if self.notification:
            self._property_map["notification"] = self.notification
        if self.error:
            self._property_map["error"] = self.error

    def check_attribute_readable(self, prop_attr: Property) -> bool:
        return self._get_prop_attr(prop_attr)[READABILITY]

    def check_attribute_writable(self, prop_attr: Property) -> bool:
        return self._get_prop_attr(prop_attr)[WRITABILITY]

    def check_range_attribute_writable(self, prop_attr: Property, value: int) -> bool:
        values = self._get_prop_attr(prop_attr)[WRITABLE_VALUES]
        if not values:
            return False
        v_min = values["min"]
        v_max = values["max"]
        v_step = values.get("step", 1)
        v_except = values.get("except", [])
        return v_min <= value and value <= v_max and (value - v_min) % v_step == 0 and value not in v_except

    def check_enum_attribute_writable(self, prop_attr: Property, value: str | bool) -> bool:
        return self._get_prop_attr(prop_attr)[WRITABILITY] and value in self._get_prop_attr(prop_attr)[WRITABLE_VALUES]

    def _get_attribute_payload(self, attribute: Property, value: str | int) -> dict:
        for resource, props in self._PROFILE.items():
            for prop_key, prop_attr in props.items():
                if prop_attr == attribute:
                    return {resource: {prop_key: value}}

    def get_attribute_payload(self, attribute: Property, value: int | bool) -> dict:
        if not self.check_attribute_writable(attribute):
            raise ValueError(f"Not support {attribute}")
        return self._get_attribute_payload(attribute, value)

    def get_range_attribute_payload(self, attribute: Property, value: int) -> dict:
        if not self.check_range_attribute_writable(attribute, value):
            raise ValueError(f"Not support {attribute} : {value}")
        return self._get_attribute_payload(attribute, value)

    def get_enum_attribute_payload(self, attribute: Property, value: str) -> dict:
        if not self.check_enum_attribute_writable(attribute, value):
            raise ValueError(f"Not support {attribute} : {value}")
        return self._get_attribute_payload(attribute, value)

    def _get_preferred_property_key(self, profile: dict[str, Any], resource: str, preferred_keys: list[str]) -> str:
        """Get the first available property key from preferred_keys list."""
        resource_property = profile.get("property", {}).get(resource, {})
        for key in preferred_keys:
            if key in resource_property:
                return key
        return preferred_keys[-1]  # Return last key as fallback


class ConnectSubDeviceProfile(ConnectDeviceProfile):
    def __init__(
        self,
        profile: dict[str, Any],
        location_name: Location,
        resource_map: dict[str, Resource] | None = None,
        profile_map: dict[str, dict[str, Property]] | None = None,
        custom_resources: list[str] | None = None,
        use_sub_notification: bool = False,
    ):
        self._location_name = location_name
        super().__init__(
            profile=profile,
            resource_map=resource_map,
            profile_map=profile_map,
            custom_resources=custom_resources,
            use_notification=use_sub_notification,
        )


@dataclass
class ConnectBaseDevice(BaseDevice):
    profile: InitVar[dict[str, Any] | None] = None
    profiles: ConnectDeviceProfile
    _profiles: ConnectDeviceProfile = field(init=False, repr=False)
    _sub_devices: dict[str, ConnectBaseDevice] = field(init=False, default_factory=dict)

    energy_properties: list = field(init=False, default_factory=list)
    energy_profile: dict[str, Any] | None = field(default=None)

    PROFILE_TYPE: ClassVar[type | None]
    _CUSTOM_SET_PROPERTY_NAME: ClassVar[dict[str, str]] = {}
    _EXTEND_SET_FN_NAME: ClassVar[list] = []

    def __post_init__(self, profile):
        if profile and self.PROFILE_TYPE:
            self._profiles = self.PROFILE_TYPE(profile=profile)
        if self.energy_profile:
            self.energy_properties = self.energy_profile.get("result", {}).get("property", [])

    @property
    def profiles(self) -> ConnectDeviceProfile:
        return self._profiles

    @profiles.setter
    def profiles(self, profiles: ConnectDeviceProfile):
        self._profiles = profiles

    def get_property_key(self, resource: str, origin_key: str) -> str | None:
        _resource_profile: dict[str, str] = self._profiles.get_profile().get(resource, {})
        return str(_prop_key) if (_prop_key := _resource_profile.get(origin_key, None)) else None

    def __return_exist_fun_name(self, fn_name: str) -> str | None:
        return fn_name if hasattr(self, fn_name) else None

    def get_property_set_fn(self, property_name: str) -> str | None:
        return (
            self.__return_exist_fun_name(f"set_{property_name}")
            if property_name not in self._CUSTOM_SET_PROPERTY_NAME
            else self.__return_exist_fun_name(f"set_{self._CUSTOM_SET_PROPERTY_NAME[property_name]}")
        )

    def get_sub_device(self, location_name: Location) -> ConnectBaseDevice | None:
        if location_name in self._profiles.locations:
            return self._sub_devices.get(location_name)
        else:
            return None

    def _set_custom_resources(
        self,
        prop_key: str,
        attribute: str,
        resource_status: dict[str, str] | list[dict[str, str]],
        is_updated: bool = False,
    ) -> bool:
        # pylint: disable=unused-argument
        # Need to be implemented by child classes
        return False

    def __set_property_status(
        self, resource_status: dict | None, resource: str, prop_key: str, prop_attr: str, is_updated: bool = False
    ) -> None:
        if prop_attr == "location_name":
            return

        value = None
        if resource_status is not None:
            if resource in self._profiles._CUSTOM_RESOURCES:
                if self._set_custom_resources(prop_key, prop_attr, resource_status, is_updated):
                    return
            if isinstance(resource_status, dict):
                value = resource_status.get(prop_key)
            if is_updated:
                if prop_key in resource_status:
                    self._set_status_attr(prop_attr, value)
                return

        self._set_status_attr(prop_attr, value)

    def _set_status_attr(self, property_name: Property | str, value: Any) -> None:
        setattr(self, property_name, value)

    def __set_error_status(self, status: dict) -> None:
        if self._profiles.error:
            self._set_status_attr("error", status.get("error"))

    def __set_status(self, status: dict) -> None:
        for resource, props in self._profiles.get_profile().items():
            resource_status = status.get(resource)
            for prop_key, prop_attr in props.items():
                self.__set_property_status(resource_status, resource, prop_key, prop_attr)

    def __update_status(self, status: dict) -> None:
        device_profile = self._profiles.get_profile()
        for resource, resource_status in status.items():
            if resource not in device_profile:
                continue
            for prop_key, prop_attr in device_profile[resource].items():
                self.__set_property_status(resource_status, resource, prop_key, prop_attr, True)

    def _set_status(self, status: dict | list, is_updated: bool = False) -> None:
        if not isinstance(status, dict):
            return
        self.__set_error_status(status)
        if is_updated:
            self.__update_status(status)
        else:
            self.__set_status(status)

    def get_status(self, property_name: Property) -> Any:
        return (
            getattr(self, property_name)
            if hasattr(self, property_name)
            and (property_name == "error" or self._profiles.check_attribute_readable(property_name))
            else None
        )

    def set_status(self, status: dict | list) -> None:
        self._set_status(status)

    def update_status(self, status: dict | list) -> None:
        self._set_status(status, True)

    async def _do_attribute_command(self, payload: dict) -> dict | None:
        return await self.thinq_api.async_post_device_control(device_id=self.device_id, payload=payload)

    async def do_attribute_command(self, attribute: Property, value: int | bool) -> dict | None:
        return await self._do_attribute_command(self._profiles.get_attribute_payload(attribute, value))

    async def do_multi_attribute_command(self, attributes: dict[Property, int]) -> dict | None:
        payload = defaultdict(dict)
        for attr, value in attributes.items():
            for key, sub_dict in self._profiles.get_attribute_payload(attr, value).items():
                payload[key].update(sub_dict)
        return await self._do_attribute_command(payload)

    async def do_range_attribute_command(self, attribute: Property, value: int) -> dict | None:
        return await self._do_attribute_command(self._profiles.get_range_attribute_payload(attribute, value))

    async def do_multi_range_attribute_command(self, attributes: dict[Property, int]) -> dict | None:
        payload = defaultdict(dict)
        for attr, value in attributes.items():
            for key, sub_dict in self._profiles.get_range_attribute_payload(attr, value).items():
                payload[key].update(sub_dict)
        return await self._do_attribute_command(payload)

    async def do_enum_attribute_command(self, attribute: Property, value: str) -> dict | None:
        return await self._do_attribute_command(self._profiles.get_enum_attribute_payload(attribute, value))

    @staticmethod
    def _get_date_type_instance(date_str: str) -> tuple[str | None, date | None]:
        if len(date_str) == 8:
            date_type = USAGE_DAILY
        elif len(date_str) == 6:
            date_type = USAGE_MONTHLY
        else:
            return None, None

        if not date_str.isdigit():
            return None, None

        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:]) if date_type == USAGE_DAILY else 1

        try:
            return date_type, date(year, month, day)
        except ValueError:
            return None, None

    def _check_date_format(self, period: str, start_date: str, end_date: str):
        s_period, s_date = self._get_date_type_instance(start_date)
        e_period, e_date = self._get_date_type_instance(end_date)
        if period != s_period:
            raise ValueError(f"Invalid start date {start_date} in period {period}")
        if period != e_period:
            raise ValueError(f"Invalid end date {start_date} in period {period}")

        today = date.today()
        if today < e_date:
            raise ValueError(f"Invalid end date {end_date}")
        if e_date < s_date:
            raise ValueError(f"Invalid date period {start_date} - {end_date}")

    def _check_valid_energy_property(self, energy_property: str):
        if not (self.energy_properties and energy_property in self.energy_properties):
            raise ValueError(f"Energy Property is not supported: {energy_property} {self.energy_properties}")

    async def _get_energy_property_usage(
        self, energy_property: str, period: str, start_date: str, end_date: str
    ) -> dict | None:
        self._check_valid_energy_property(energy_property)
        self._check_date_format(period, start_date, end_date)
        return await self.thinq_api.async_get_device_energy_usage(
            device_id=self.device_id,
            energy_property=energy_property,
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_monthly_energy_usage(self, energy_property: str, start_date: str, end_date: str) -> dict | None:
        return await self._get_energy_property_usage(energy_property, USAGE_MONTHLY, start_date, end_date)

    async def get_daily_energy_usage(self, energy_property: str, start_date: str, end_date: str) -> dict | None:
        return await self._get_energy_property_usage(energy_property, USAGE_DAILY, start_date, end_date)


@dataclass
class ConnectMainDevice(ConnectBaseDevice):
    SUB_DEVICE_TYPE: ClassVar[type]

    def __post_init__(self, profile):
        super().__post_init__(profile)
        if self.SUB_DEVICE_TYPE:
            self._init_sub_devices()

    def _init_sub_devices(self):
        for location_name in self._profiles.locations:
            _sub_device = self.SUB_DEVICE_TYPE(
                profiles=self._profiles.get_sub_profile(location_name),
                location_name=self._profiles.get_location_key(location_name),
                thinq_api=self.thinq_api,
                device_id=self.device_id,
                device_type=self.device_type,
                model_name=self.model_name,
                alias=self.alias,
                reportable=self.reportable,
            )
            self._set_sub_device(location_name, _sub_device)
            self._sub_devices[location_name] = _sub_device

    def _set_sub_device(self, location_name: Location | str, sub_device: ConnectBaseDevice):
        setattr(self, location_name, sub_device)

    def set_status(self, status: list) -> None:
        super().set_status(status)
        for sub_device in self._sub_devices.values():
            sub_device.set_status(status)

    def update_status(self, status: list) -> None:
        super().update_status(status)
        for sub_device in self._sub_devices.values():
            sub_device.update_status(status)


@dataclass
class ConnectSubDevice(ConnectBaseDevice):
    location_name: Location = ""
    is_single_resource: bool = field(init=False, default=False)

    def _get_location_name_from_status(self, location_status: dict) -> str | None:
        if self.is_single_resource:
            return location_status.get("locationName")
        else:
            return location_status.get("location", {}).get("locationName")

    def _is_current_location_status(self, location_status: dict) -> bool:
        return self._get_location_name_from_status(location_status) == self.location_name

    def _set_status(self, status: list | dict, is_updated: bool = False) -> None:
        if isinstance(status, list):
            for location_status in status:
                if not self._is_current_location_status(location_status):
                    continue
                super()._set_status(status=location_status, is_updated=is_updated)
                return
            return
        for resource in self._profiles._CUSTOM_RESOURCES:
            for location_status in status.get(resource, []):
                if not self._is_current_location_status(location_status):
                    continue
                super()._set_status(status={resource: location_status}, is_updated=is_updated)
                return

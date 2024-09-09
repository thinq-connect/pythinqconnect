from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..const import PROPERTY_READABLE
from ..thinq_api import ThinQApi
from .connect_device import (
    READABILITY,
    WRITABILITY,
    ConnectDeviceProfile,
    ConnectMainDevice,
    ConnectSubDevice,
    ConnectSubDeviceProfile,
)
from .const import Location, Property, Resource


class OvenProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            location_map={
                "OVEN": Location.OVEN,
                "UPPER": Location.UPPER,
                "LOWER": Location.LOWER,
            },
            resource_map={"info": Resource.INFO},
            profile_map={"info": {"type": Property.OVEN_TYPE}},
            use_extension_property=True,
        )
        for profile_property in profile.get("property", []):
            location_name = profile_property.get("location", {}).get("locationName")
            if location_name in self._LOCATION_MAP.keys():
                attr_key = self._LOCATION_MAP[location_name]
                _sub_profile = OvenSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)


class OvenSubProfile(ConnectSubDeviceProfile):
    _CUSTOM_RESOURCES = ["temperature"]

    def __init__(self, profile: dict[str, Any], location_name: Location = None):
        super().__init__(
            profile=profile,
            location_name=location_name,
            resource_map={
                "runState": Resource.RUN_STATE,
                "operation": Resource.OPERATION,
                "cook": Resource.COOK,
                "remoteControlEnable": Resource.REMOTE_CONTROL_ENABLE,
                "temperature": Resource.TEMPERATURE,
                "timer": Resource.TIMER,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "operation": {"ovenOperationMode": Property.OVEN_OPERATION_MODE},
                "cook": {"cookMode": Property.COOK_MODE},
                "remoteControlEnable": {"remoteControlEnabled": Property.REMOTE_CONTROL_ENABLED},
                "temperature": {
                    "C": Property.TARGET_TEMPERATURE_C,
                    "F": Property.TARGET_TEMPERATURE_F,
                },
                "timer": {
                    "remainHour": Property.REMAIN_HOUR,
                    "remainMinute": Property.REMAIN_MINUTE,
                    "remainSecond": Property.REMAIN_SECOND,
                    "targetHour": Property.TARGET_HOUR,
                    "targetMinute": Property.TARGET_MINUTE,
                    "targetSecond": Property.TARGET_SECOND,
                    "timerHour": Property.TIMER_HOUR,
                    "timerMinute": Property.TIMER_MINUTE,
                    "timerSecond": Property.TIMER_SECOND,
                },
            },
            custom_resources=["temperature"],
        )

    def get_range_attribute_payload(self, attribute: str, value: int) -> dict:
        temperature_info = self._get_prop_attr(attribute)
        if not self.check_range_attribute_writable(attribute, value):
            raise ValueError(f"Not support {attribute}")
        return {
            "location": {"locationName": self._location_name},
            "temperature": {
                "targetTemperature": value,
                "unit": temperature_info["unit"],
            },
        }

    def _generate_custom_resource_properties(
        self, resource_key: str, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        # pylint: disable=unused-argument
        readable_props = []
        writable_props = []
        if resource_key != "temperature":
            return readable_props, writable_props

        temperature_map = self._PROFILE[resource_key]
        for _temperature in resource_property:
            if _temperature["unit"] in temperature_map:
                attr_name = temperature_map[_temperature["unit"]]
                prop = self._get_properties(_temperature, "targetTemperature")
                self._set_prop_attr(attr_name, prop)
                if prop[READABILITY]:
                    readable_props.append(attr_name)
                if prop[WRITABILITY]:
                    writable_props.append(attr_name)

        return readable_props, writable_props

    def generate_properties(self, property: dict[str, Any]) -> None:
        """Generate properties."""
        for location_property in property:
            if location_property.get("location", {}).get("locationName") != self._location_name:
                continue
            super().generate_properties(location_property)


class OvenSubDevice(ConnectSubDevice):
    """Oven Device Sub."""

    def __init__(
        self,
        profiles: OvenSubProfile,
        location_name: Location,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        reportable: bool,
    ):
        super().__init__(profiles, location_name, thinq_api, device_id, device_type, model_name, alias, reportable)
        self._temp_unit = None

    @property
    def profiles(self) -> OvenSubProfile:
        return self._profiles

    @property
    def remain_time(self) -> dict:
        return {
            "hour": self.get_status("remain_hour"),
            "minute": self.get_status("remain_minute"),
            "second": self.get_status("remain_second"),
        }

    @property
    def target_time(self) -> dict:
        return {
            "hour": self.get_status("target_hour"),
            "minute": self.get_status("target_minute"),
            "second": self.get_status("target_second"),
        }

    @property
    def timer_time(self) -> dict:
        return {
            "hour": self.get_status("timer_hour"),
            "minute": self.get_status("timer_minute"),
            "second": self.get_status("timer_second"),
        }

    def _set_custom_resources(self, attribute: str, resource_status: dict[str, str]) -> bool:
        temperature_map = self.profiles._PROFILE["temperature"]
        _temp_status_value = resource_status.get("targetTemperature")
        _temp_status_unit = resource_status.get("unit")

        if not _temp_status_unit:
            _temp_status_unit = self._temp_unit
            self._set_status_attr(
                temperature_map.get(_temp_status_unit),
                {
                    "target_temperature": _temp_status_value,
                    "unit": _temp_status_unit,
                },
            )
            return True

        _temp_attr_name = temperature_map.get(_temp_status_unit)
        if attribute == _temp_attr_name:
            self._temp_unit = _temp_status_unit
            _attribute_value = {
                "target_temperature": _temp_status_value,
                "unit": _temp_status_unit,
            }
        elif attribute in temperature_map.values():
            _attribute_value = {
                "target_temperature": None,
                "unit": list(temperature_map.keys())[list(temperature_map.values()).index(attribute)],
            }
        else:
            _attribute_value = None
        self._set_status_attr(attribute, _attribute_value)
        return True

    async def set_oven_operation_mode(self, mode: str) -> dict | None:
        payload = self.profiles.get_enum_attribute_payload("oven_operation_mode", mode)
        return await self._do_attribute_command({"location": {"locationName": self._location_name}, **payload})

    async def set_cook_mode(self, mode: str) -> dict | None:
        payload = self.profiles.get_enum_attribute_payload("cook_mode", mode)
        return await self._do_attribute_command({"location": {"locationName": self._location_name}, **payload})

    async def _set_target_temperature(self, target_temperature: int, unit: str) -> dict | None:
        temperature_map = self.profiles._PROFILE["temperature"]
        payload = self.profiles.get_range_attribute_payload(temperature_map.get(unit), target_temperature)
        return await self._do_attribute_command({"location": {"locationName": self._location_name}, **payload})

    async def set_target_temperature_f(self, target_temperature: int) -> dict | None:
        return await self._set_target_temperature(target_temperature, "F")

    async def set_target_temperature_c(self, target_temperature: str) -> dict | None:
        return await self._set_target_temperature(target_temperature, "C")


class OvenDevice(ConnectMainDevice):
    """Oven Property."""

    def __init__(
        self,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        reportable: bool,
        profile: dict[str, Any],
    ):
        self._sub_devices: dict[str, OvenSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=OvenProfile(profile=profile),
            sub_device_type=OvenSubDevice,
        )
        self.oven_type = self.profiles.get_property("oven_type").get(PROPERTY_READABLE, [None])[0]

    @property
    def profiles(self) -> OvenProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> OvenSubDevice:
        return super().get_sub_device(location_name)

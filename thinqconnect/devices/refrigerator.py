from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import (
    READABLE_VALUES,
    WRITABLE_VALUES,
    ConnectDeviceProfile,
    ConnectMainDevice,
    ConnectSubDevice,
    ConnectSubDeviceProfile,
)
from .const import Location, Property, Resource


class RefrigeratorSubProfile(ConnectSubDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location):
        super().__init__(
            profile=profile,
            location_name=location_name,
            resource_map={
                "doorStatus": Resource.DOOR_STATUS,
                "temperature": Resource.TEMPERATURE,
            },
            profile_map={
                "doorStatus": {
                    "doorState": Property.DOOR_STATE,
                },
                "temperature": {
                    "targetTemperature": Property.TARGET_TEMPERATURE,
                    "unit": Property.TEMPERATURE_UNIT,
                },
            },
            custom_resources=["doorStatus", "temperature"],
        )

    def _generate_custom_resource_properties(
        self, resource_key: str, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        # pylint: disable=unused-argument
        readable_props = []
        writable_props = []
        if resource_key not in self._PROFILE.keys():
            return readable_props, writable_props

        for _location_property in resource_property:
            if _location_property["locationName"] != self._location_name:
                continue
            for _property_key in self._PROFILE[resource_key].keys():
                attr_name = self._PROFILE[resource_key][_property_key]
                prop = self._get_properties(_location_property, _property_key)
                self._set_prop_attr(attr_name, prop)
                if prop[READABLE_VALUES]:
                    readable_props.append(attr_name)
                if prop[WRITABLE_VALUES]:
                    writable_props.append(attr_name)

        return readable_props, writable_props


class RefrigeratorProfile(ConnectDeviceProfile):
    _DOOR_LOCATION_MAP = {"MAIN": Location.MAIN}
    _TEMPERATURE_LOCATION_MAP = {
        "FRIDGE": Location.FRIDGE,
        "FREEZER": Location.FREEZER,
        "CONVERTIBLE": Location.CONVERTIBLE,
    }

    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile,
            resource_map={
                "powerSave": Resource.POWER_SAVE,
                "ecoFriendly": Resource.ECO_FRIENDLY,
                "sabbath": Resource.SABBATH,
                "refrigeration": Resource.REFRIGERATION,
                "waterFilterInfo": Resource.WATER_FILTER_INFO,
            },
            profile_map={
                "powerSave": {
                    "powerSaveEnabled": Property.POWER_SAVE_ENABLED,
                },
                "ecoFriendly": {
                    "ecoFriendlyMode": Property.ECO_FRIENDLY_MODE,
                },
                "sabbath": {
                    "sabbathMode": Property.SABBATH_MODE,
                },
                "refrigeration": {
                    "rapidFreeze": Property.RAPID_FREEZE,
                    "expressMode": Property.EXPRESS_MODE,
                    "freshAirFilter": Property.FRESH_AIR_FILTER,
                },
                "waterFilterInfo": {
                    "usedTime": Property.USED_TIME,
                    "unit": Property.WATER_FILTER_INFO_UNIT,
                },
            },
        )

        for location_property in profile.get("property", {}).get("doorStatus", []):
            location_name = location_property.get("locationName")
            if location_name in self._DOOR_LOCATION_MAP.keys():
                attr_key = self._DOOR_LOCATION_MAP[location_name]
                _sub_profile = RefrigeratorSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)

        for location_property in profile.get("property", {}).get("temperature", []):
            location_name = location_property.get("locationName")
            if location_name in self._TEMPERATURE_LOCATION_MAP.keys():
                attr_key = self._TEMPERATURE_LOCATION_MAP[location_name]
                _sub_profile = RefrigeratorSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)

    def get_location_key(self, location_name: Location) -> str | None:
        for key, name in self._DOOR_LOCATION_MAP.items():
            if name == location_name:
                return key
        for key, name in self._TEMPERATURE_LOCATION_MAP.items():
            if name == location_name:
                return key


class RefrigeratorSubDevice(ConnectSubDevice):
    """Refrigerator Device Sub."""

    def __init__(
        self,
        profiles: RefrigeratorSubProfile,
        location_name: Location,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        reportable: bool,
    ):
        super().__init__(
            profiles,
            location_name,
            thinq_api,
            device_id,
            device_type,
            model_name,
            alias,
            reportable,
            is_single_resource=True,
        )

    @property
    def profiles(self) -> RefrigeratorSubProfile:
        return self._profiles

    async def set_target_temperature(self, temperature: float) -> dict | None:
        _resource_key = "temperature"
        _target_temperature_key, _unit_key = self.get_property_keys(_resource_key, ["targetTemperature", "unit"])

        _payload = self.profiles.get_range_attribute_payload(_target_temperature_key, temperature)
        _payload[_resource_key] = dict(
            {
                "locationName": self._location_name,
                "unit": self.get_status(_unit_key),
            },
            **(_payload[_resource_key]),
        )
        return await self._do_attribute_command(_payload)


class RefrigeratorDevice(ConnectMainDevice):
    """Refrigerator Property."""

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
        self._sub_devices: dict[str, RefrigeratorSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=RefrigeratorProfile(profile=profile),
            sub_device_type=RefrigeratorSubDevice,
        )

    @property
    def profiles(self) -> RefrigeratorProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> RefrigeratorSubDevice:
        return super().get_sub_device(location_name)

    async def set_rapid_freeze(self, mode: bool) -> dict | None:
        return await self.do_attribute_command(Property.RAPID_FREEZE, mode)

    async def set_express_mode(self, mode: bool) -> dict | None:
        return await self.do_attribute_command(Property.EXPRESS_MODE, mode)

    async def set_fresh_air_filter(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.FRESH_AIR_FILTER, mode)

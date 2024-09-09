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


class WineCellarSubProfile(ConnectSubDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location):
        super().__init__(
            profile=profile,
            location_name=location_name,
            resource_map={"temperature": Resource.TEMPERATURE},
            profile_map={
                "temperature": {
                    "targetTemperature": Property.TARGET_TEMPERATURE,
                    "unit": Property.TEMPERATURE_UNIT,
                },
            },
            custom_resources=["temperature"],
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


class WineCellarProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            location_map={
                "WINE_UPPER": Location.UPPER,
                "WINE_MIDDLE": Location.MIDDLE,
                "WINE_LOWER": Location.LOWER,
            },
            resource_map={"operation": Resource.OPERATION},
            profile_map={
                "operation": {
                    "lightBrightness": Property.LIGHT_BRIGHTNESS,
                    "optimalHumidity": Property.OPTIMAL_HUMIDITY,
                    "sabbathMode": Property.SABBATH_MODE,
                    "lightStatus": Property.LIGHT_STATUS,
                },
            },
            custom_resources=["temperature"],
        )

        for location_property in profile.get("property", {}).get("temperature", []):
            location_name = location_property.get("locationName")
            if location_name in self._LOCATION_MAP.keys():
                attr_key = self._LOCATION_MAP[location_name]
                _sub_profile = WineCellarSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)


class WineCellarSubDevice(ConnectSubDevice):
    """WineCellar Device Sub."""

    def __init__(
        self,
        profiles: WineCellarSubProfile,
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
    def profiles(self) -> WineCellarSubProfile:
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


class WineCellarDevice(ConnectMainDevice):
    """WineCellar Property."""

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
        self._sub_devices: dict[str, WineCellarSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=WineCellarProfile(profile=profile),
            sub_device_type=WineCellarSubDevice,
        )

    @property
    def profiles(self) -> WineCellarProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> WineCellarSubDevice:
        return super().get_sub_device(location_name)

    async def set_light_brightness(self, brightness_input: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.LIGHT_BRIGHTNESS, brightness_input)

    async def set_optimal_humidity(self, humidity_input: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.OPTIMAL_HUMIDITY, humidity_input)

    async def set_light_status(self, status_input: int) -> dict | None:
        return await self.do_range_attribute_command(Property.LIGHT_STATUS, status_input)

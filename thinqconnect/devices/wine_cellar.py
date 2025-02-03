from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

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


class WineCellarSubProfile(ConnectSubDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location):
        super().__init__(
            profile=profile,
            location_name=location_name,
            resource_map={"temperatureInUnits": Resource.TEMPERATURE},
            profile_map={
                "temperatureInUnits": {
                    "targetTemperatureC": Property.TARGET_TEMPERATURE_C,
                    "targetTemperatureF": Property.TARGET_TEMPERATURE_F,
                    "unit": Property.TEMPERATURE_UNIT,
                },
            },
            custom_resources=["temperatureInUnits"],
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
            for prop_key, prop_attr in props.items():
                prop = self._get_properties(_location_property, prop_key)
                prop.pop("unit", None)
                if prop[READABILITY]:
                    readable_props.append(str(prop_attr))
                if prop[WRITABILITY]:
                    writable_props.append(str(prop_attr))
                self._set_prop_attr(prop_attr, prop)

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
            custom_resources=["temperatureInUnits"],
        )

        for location_property in profile.get("property", {}).get("temperatureInUnits", []):
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

    def _set_custom_resources(
        self,
        prop_key: str,
        attribute: str,
        resource_status: dict[str, str] | list[dict[str, str]],
        is_updated: bool = False,
    ) -> bool:
        if is_updated and attribute in [Property.TARGET_TEMPERATURE_C, Property.TARGET_TEMPERATURE_F]:
            current_unit = resource_status.get("unit") or self.get_status(Property.TEMPERATURE_UNIT)
            if attribute[-1:].upper() == current_unit:
                self._set_status_attr(attribute, value=resource_status.get(prop_key))
            return True
        return False

    async def _set_target_temperature(self, temperature: float, unit: str) -> dict | None:
        _resource_key = "temperatureInUnits"
        _target_temperature_key = self.get_property_key(_resource_key, "targetTemperature" + unit)

        _payload = self.profiles.get_range_attribute_payload(_target_temperature_key, temperature)
        _payload[_resource_key] = dict(
            {
                "locationName": self._location_name,
            },
            **(_payload[_resource_key]),
        )
        return await self._do_attribute_command(_payload)

    async def set_target_temperature_c(self, temperature: float) -> dict | None:
        return await self._set_target_temperature(temperature, "C")

    async def set_target_temperature_f(self, temperature: float) -> dict | None:
        return await self._set_target_temperature(temperature, "F")


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

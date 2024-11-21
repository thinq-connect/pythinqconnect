from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectDeviceProfile, ConnectMainDevice, ConnectSubDevice
from .const import Location, Property, Resource


class PlantCultivatorProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            location_map={
                "UPPER": Location.UPPER,
                "LOWER": Location.LOWER,
            },
            use_sub_profile_only=True,
        )
        for profile_property in profile.get("property", []):
            location_name = profile_property.get("location", {}).get("locationName")
            if location_name in self._LOCATION_MAP.keys():
                attr_key = self._LOCATION_MAP[location_name]
                _sub_profile = PlantCultivatorSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)
        self.generate_property_map()


class PlantCultivatorSubProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location):
        self._location_name = location_name
        super().__init__(
            profile=profile,
            resource_map={
                "runState": Resource.RUN_STATE,
                "light": Resource.LIGHT,
                "temperature": Resource.TEMPERATURE,
            },
            profile_map={
                "runState": {
                    "currentState": Property.CURRENT_STATE,
                    "growthMode": Property.GROWTH_MODE,
                    "windVolume": Property.WIND_VOLUME,
                },
                "light": {
                    "brightness": Property.BRIGHTNESS,
                    "duration": Property.DURATION,
                    "startHour": Property.START_HOUR,
                    "startMinute": Property.START_MINUTE,
                },
                "temperature": {
                    "dayTargetTemperature": Property.DAY_TARGET_TEMPERATURE,
                    "nightTargetTemperature": Property.NIGHT_TARGET_TEMPERATURE,
                    "temperatureState": Property.TEMPERATURE_STATE,
                },
            },
        )

    def generate_properties(self, property: dict[str, Any]) -> None:
        """Get properties."""
        for location_property in property:
            if location_property.get("location", {}).get("locationName") != self._location_name:
                continue
            super().generate_properties(location_property)


class PlantCultivatorSubDevice(ConnectSubDevice):
    def __init__(
        self,
        profiles: PlantCultivatorSubProfile,
        location_name: Location,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        reportable: bool,
    ):
        super().__init__(profiles, location_name, thinq_api, device_id, device_type, model_name, alias, reportable)

    @property
    def profiles(self) -> PlantCultivatorSubProfile:
        return self._profiles


class PlantCultivatorDevice(ConnectMainDevice):
    """PlantCultivator Property."""

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
        self._sub_devices: dict[str, PlantCultivatorSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=PlantCultivatorProfile(profile=profile),
            sub_device_type=PlantCultivatorSubDevice,
        )

    @property
    def profiles(self) -> PlantCultivatorProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> PlantCultivatorSubDevice:
        return super().get_sub_device(location_name)

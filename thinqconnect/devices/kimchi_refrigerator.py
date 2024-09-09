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


class KimchiRefrigeratorSubProfile(ConnectSubDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location):
        super().__init__(
            profile=profile,
            location_name=location_name,
            resource_map={
                "temperature": Resource.TEMPERATURE,
            },
            profile_map={
                "temperature": {
                    "targetTemperature": Property.TARGET_TEMPERATURE,
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
        for _temperature in resource_property:
            if _temperature["locationName"] == self._location_name:
                attr_name = self._PROFILE["temperature"]["targetTemperature"]
                prop = self._get_properties(_temperature, "targetTemperature")
                self._set_prop_attr(attr_name, prop)
                if prop[READABLE_VALUES]:
                    readable_props.append(attr_name)
                if prop[WRITABLE_VALUES]:
                    writable_props.append(attr_name)

        return readable_props, writable_props


class KimchiRefrigeratorProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            location_map={
                "TOP": Location.TOP,
                "MIDDLE": Location.MIDDLE,
                "BOTTOM": Location.BOTTOM,
                "LEFT": Location.LEFT,
                "RIGHT": Location.RIGHT,
                "SINGLE": Location.SINGLE,
            },
            resource_map={"refrigeration": Resource.REFRIGERATION},
            profile_map={
                "refrigeration": {
                    "oneTouchFilter": Property.ONE_TOUCH_FILTER,
                    "freshAirFilter": Property.FRESH_AIR_FILTER,
                },
            },
        )
        for temperature_property in profile.get("property", {}).get("temperature", []):
            location_name = temperature_property.get("locationName")
            if location_name in self._LOCATION_MAP.keys():
                attr_key = self._LOCATION_MAP[location_name]
                _sub_profile = KimchiRefrigeratorSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)


class KimchiRefrigeratorSubDevice(ConnectSubDevice):
    """KimchiRefrigerator Device Sub."""

    def __init__(
        self,
        profiles: KimchiRefrigeratorSubProfile,
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
    def profiles(self) -> KimchiRefrigeratorSubProfile:
        return self._profiles


class KimchiRefrigeratorDevice(ConnectMainDevice):
    """KimchiRefrigerator Property."""

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
        self._sub_devices: dict[str, KimchiRefrigeratorSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=KimchiRefrigeratorProfile(profile=profile),
            sub_device_type=KimchiRefrigeratorSubDevice,
        )

    @property
    def profiles(self) -> KimchiRefrigeratorProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> KimchiRefrigeratorSubDevice:
        return super().get_sub_device(location_name)

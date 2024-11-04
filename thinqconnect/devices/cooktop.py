from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectDeviceProfile, ConnectMainDevice, ConnectSubDevice
from .const import Location, Property, Resource


class CooktopSubProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location):
        self._location_name = location_name
        super().__init__(
            profile=profile,
            resource_map={
                "cookingZone": Resource.COOKING_ZONE,
                "power": Resource.POWER,
                "remoteControlEnable": Resource.REMOTE_CONTROL_ENABLE,
                "timer": Resource.TIMER,
            },
            profile_map={
                "cookingZone": {
                    "currentState": Property.CURRENT_STATE,
                },
                "power": {
                    "powerLevel": Property.POWER_LEVEL,
                },
                "remoteControlEnable": {
                    "remoteControlEnabled": Property.REMOTE_CONTROL_ENABLED,
                },
                "timer": {
                    "remainHour": Property.REMAIN_HOUR,
                    "remainMinute": Property.REMAIN_MINUTE,
                },
            },
        )

    def generate_properties(self, property: dict[str, Any]) -> None:
        """Get properties."""
        for location_property in property:
            if location_property.get("location", {}).get("locationName") != self._location_name:
                continue
            super().generate_properties(location_property)


class CooktopProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        use_extension_property = True if "extensionProperty" in profile else False
        resource_map = {"operation": Resource.OPERATION} if use_extension_property else {}
        profile_map = {"operation": {"operationMode": Property.OPERATION_MODE}} if use_extension_property else {}
        super().__init__(
            profile=profile,
            resource_map=resource_map,
            profile_map=profile_map,
            location_map={
                "CENTER": Location.CENTER,
                "CENTER_FRONT": Location.CENTER_FRONT,
                "CENTER_REAR": Location.CENTER_REAR,
                "LEFT_FRONT": Location.LEFT_FRONT,
                "LEFT_REAR": Location.LEFT_REAR,
                "RIGHT_FRONT": Location.RIGHT_FRONT,
                "RIGHT_REAR": Location.RIGHT_REAR,
                "BURNER_1": Location.BURNER_1,
                "BURNER_2": Location.BURNER_2,
                "BURNER_3": Location.BURNER_3,
                "BURNER_4": Location.BURNER_4,
                "BURNER_5": Location.BURNER_5,
                "BURNER_6": Location.BURNER_6,
                "BURNER_7": Location.BURNER_7,
                "BURNER_8": Location.BURNER_8,
                "INDUCTION_1": Location.INDUCTION_1,
                "INDUCTION_2": Location.INDUCTION_2,
                "SOUSVIDE_1": Location.SOUSVIDE_1,
            },
            use_extension_property=use_extension_property,
        )

        for profile_property in profile.get("property", []):
            location_name = profile_property.get("location", {}).get("locationName")
            if location_name in self._LOCATION_MAP.keys():
                attr_key = self._LOCATION_MAP[location_name]
                _sub_profile = CooktopSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)


class CooktopSubDevice(ConnectSubDevice):
    """Cooktop Device Sub."""

    def __init__(
        self,
        profiles: CooktopSubProfile,
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
    def profiles(self) -> CooktopSubProfile:
        return self._profiles

    def _get_command_payload(self):
        return {
            "power": {"powerLevel": self.get_status(Property.POWER_LEVEL)},
            "timer": {
                "remainHour": self.get_status(Property.REMAIN_HOUR),
                "remainMinute": self.get_status(Property.REMAIN_MINUTE),
            },
            "location": {"locationName": self.location_name},
        }

    async def _do_custom_range_attribute_command(self, attr_name: str, value: int) -> dict | None:
        full_payload: dict[str, dict[str, int | str]] = self._get_command_payload()
        payload = self.profiles.get_range_attribute_payload(attr_name, value)
        for resource in payload.keys():
            full_payload[resource].update(payload[resource])
        return await self.thinq_api.async_post_device_control(device_id=self.device_id, payload=full_payload)

    async def set_power_level(self, value: int) -> dict | None:
        return await self._do_custom_range_attribute_command(Property.POWER_LEVEL, value)

    async def set_remain_hour(self, value: int) -> dict | None:
        return await self._do_custom_range_attribute_command(Property.REMAIN_HOUR, value)

    async def set_remain_minute(self, value: int) -> dict | None:
        return await self._do_custom_range_attribute_command(Property.REMAIN_MINUTE, value)


class CooktopDevice(ConnectMainDevice):
    """Cooktop Property."""

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
        self._sub_devices: dict[str, CooktopSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=CooktopProfile(profile=profile),
            sub_device_type=CooktopSubDevice,
        )

    @property
    def profiles(self) -> CooktopProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> CooktopSubDevice:
        return super().get_sub_device(location_name)

    async def set_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.OPERATION_MODE, mode)

    async def set_power_level(self, location_name: Location, value: int) -> dict | None:
        if sub_device := self._sub_devices.get(location_name):
            return await sub_device.set_power_level(value)
        else:
            raise ValueError(f"Invalid location : {location_name}")

    async def set_remain_hour(self, location_name: Location, value: int) -> dict | None:
        if sub_device := self._sub_devices.get(location_name):
            return await sub_device.set_remain_hour(value)
        else:
            raise ValueError(f"Invalid location : {location_name}")

    async def set_remain_minute(self, location_name: Location, value: int) -> dict | None:
        if sub_device := self._sub_devices.get(location_name):
            return await sub_device.set_remain_minute(value)
        else:
            raise ValueError(f"Invalid location : {location_name}")

from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectDeviceProfile, ConnectMainDevice, ConnectSubDevice, ConnectSubDeviceProfile
from .const import Location, Property, Resource


class WasherProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile, location_map={"MAIN": Location.MAIN, "MINI": Location.MINI}, use_sub_profile_only=True
        )
        for profile_property in profile.get("property", []):
            location_name = profile_property.get("location", {}).get("locationName")
            if location_name in self._LOCATION_MAP.keys():
                attr_key = self._LOCATION_MAP[location_name]
                _sub_profile = WasherSubProfile(profile, location_name)
                self._set_sub_profile(attr_key, _sub_profile)
                self._set_location_properties(attr_key, _sub_profile.properties)
        self.generate_property_map()


class WasherSubProfile(ConnectSubDeviceProfile):
    def __init__(self, profile: dict[str, Any], location_name: Location = None, use_sub_notification: bool = False):
        super().__init__(
            profile,
            location_name=location_name,
            resource_map={
                "runState": Resource.RUN_STATE,
                "operation": Resource.OPERATION,
                "remoteControlEnable": Resource.REMOTE_CONTROL_ENABLE,
                "timer": Resource.TIMER,
                "detergent": Resource.DETERGENT,
                "cycle": Resource.CYCLE,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "operation": {
                    "washerOperationMode": Property.WASHER_OPERATION_MODE,
                },
                "remoteControlEnable": {"remoteControlEnabled": Property.REMOTE_CONTROL_ENABLED},
                "timer": {
                    "remainHour": Property.REMAIN_HOUR,
                    "remainMinute": Property.REMAIN_MINUTE,
                    "totalHour": Property.TOTAL_HOUR,
                    "totalMinute": Property.TOTAL_MINUTE,
                    "relativeHourToStop": Property.RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.RELATIVE_MINUTE_TO_STOP,
                    "relativeHourToStart": Property.RELATIVE_HOUR_TO_START,
                    "relativeMinuteToStart": Property.RELATIVE_MINUTE_TO_START,
                },
                "detergent": {"detergentSetting": Property.DETERGENT_SETTING},
                "cycle": {"cycleCount": Property.CYCLE_COUNT},
            },
            use_sub_notification=use_sub_notification,
        )

    def generate_properties(self, property: list[dict[str, Any]] | dict[str, Any]) -> None:
        """Get properties."""
        if isinstance(property, list):
            for location_property in property:
                if location_property.get("location", {}).get("locationName") != self._location_name:
                    continue
                super().generate_properties(location_property)
        else:
            super().generate_properties(property)


class WasherSubDevice(ConnectSubDevice):
    """Washer Device Sub."""

    def __init__(
        self,
        profiles: WasherSubProfile,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        reportable: bool,
        location_name: Location = None,
        single_unit: bool = False,
    ):
        super().__init__(profiles, location_name, thinq_api, device_id, device_type, model_name, alias, reportable)

    @property
    def profiles(self) -> WasherSubProfile:
        return self._profiles

    @property
    def remain_time(self) -> dict:
        return {"hour": self.get_status(Property.REMAIN_HOUR), "minute": self.get_status(Property.REMAIN_MINUTE)}

    @property
    def total_time(self) -> dict:
        return {"hour": self.get_status(Property.TOTAL_HOUR), "minute": self.get_status(Property.TOTAL_MINUTE)}

    @property
    def relative_time_to_stop(self) -> dict:
        return {
            "hour": self.get_status(Property.RELATIVE_HOUR_TO_STOP),
            "minute": self.get_status(Property.RELATIVE_MINUTE_TO_STOP),
        }

    @property
    def relative_time_to_start(self) -> dict:
        return {
            "hour": self.get_status(Property.RELATIVE_HOUR_TO_START),
            "minute": self.get_status(Property.RELATIVE_MINUTE_TO_START),
        }

    def _set_status(self, status: dict | list, is_updated: bool = False) -> None:
        if isinstance(status, list):
            super()._set_status(status, is_updated)
        else:
            super(ConnectSubDevice, self)._set_status(status, is_updated)

    async def set_washer_operation_mode(self, mode: str) -> dict | None:
        payload = self.profiles.get_enum_attribute_payload(Property.WASHER_OPERATION_MODE, mode)
        return await self._do_attribute_command({"location": {"locationName": self._location_name}, **payload})

    async def set_relative_hour_to_start(self, hour: str) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_START, hour)
        return await self._do_attribute_command({"location": {"locationName": self._location_name}, **payload})

    async def set_relative_hour_to_stop(self, hour: str) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_STOP, hour)
        return await self._do_attribute_command({"location": {"locationName": self._location_name}, **payload})


class WasherDevice(ConnectMainDevice):
    """Washer Property."""

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
        self._sub_devices: dict[str, WasherSubDevice] = {}
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=WasherProfile(profile=profile),
            sub_device_type=WasherSubDevice,
        )

    @property
    def profiles(self) -> WasherProfile:
        return self._profiles

    def get_sub_device(self, location_name: Location) -> WasherSubDevice:
        return super().get_sub_device(location_name)

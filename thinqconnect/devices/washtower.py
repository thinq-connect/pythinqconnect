"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Location, Property
from .dryer import DryerDevice, DryerProfile
from .washer import WasherSubDevice, WasherSubProfile


class WashTowerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile, location_map={"DRYER": Location.DRYER, "WASHER": Location.WASHER}, use_sub_profile_only=True
        )
        for location_name, attr_key in self._LOCATION_MAP.items():
            _sub_profile = (
                WasherSubProfile(
                    profile=profile.get(attr_key), location_name=Location.WASHER, use_sub_notification=True
                )
                if location_name == "WASHER"
                else DryerProfile(profile=profile.get(attr_key))
            )
            self._set_sub_profile(attr_key, _sub_profile)
            self._set_location_properties(attr_key, _sub_profile.properties)
        self.generate_property_map()


class WasherDeviceSingle(WasherSubDevice):
    """Washtower Washer Single Device."""

    async def set_washer_operation_mode(self, operation: str) -> dict | None:
        payload = self.profiles.get_enum_attribute_payload(Property.WASHER_OPERATION_MODE, operation)
        return await self._do_attribute_command({"washer": {**payload}})

    async def set_relative_hour_to_start(self, hour: int) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_START, hour)
        return await self._do_attribute_command({"washer": {**payload}})

    async def set_relative_hour_to_stop(self, hour: int) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_STOP, hour)
        return await self._do_attribute_command({"washer": {**payload}})


class DryerDeviceSingle(DryerDevice):
    """Washtower Dryer Single Device."""

    async def set_dryer_operation_mode(self, operation: str) -> dict | None:
        payload = self.profiles.get_enum_attribute_payload(Property.DRYER_OPERATION_MODE, operation)
        return await self._do_attribute_command({"dryer": {**payload}})

    async def set_relative_time_to_start(self, hour: int) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_START, hour)
        return await self._do_attribute_command({"dryer": {**payload}})

    async def set_relative_time_to_stop(self, hour: int) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_STOP, hour)
        return await self._do_attribute_command({"dryer": {**payload}})


class WashtowerDevice(ConnectBaseDevice):
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
        super().__init__(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=WashTowerProfile(profile=profile),
        )
        self._sub_devices: dict[str, WasherDeviceSingle | DryerDeviceSingle] = {}
        self.dryer = DryerDeviceSingle(
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profile=profile.get("dryer"),
        )
        self.washer = WasherDeviceSingle(
            single_unit=True,
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
            profiles=self.profiles.get_sub_profile("washer"),
        )
        self._sub_devices["dryer"] = self.dryer
        self._sub_devices["washer"] = self.washer

    def set_status(self, status: dict) -> None:
        super().set_status(status)
        for device_type, sub_device in self._sub_devices.items():
            sub_device.set_status(status.get(device_type))

    def update_status(self, status: dict) -> None:
        super().update_status(status)
        for device_type, sub_device in self._sub_devices.items():
            sub_device.update_status(status.get(device_type))

    def get_sub_device(self, location_name: Location) -> DryerDeviceSingle | WasherDeviceSingle:
        return super().get_sub_device(location_name)

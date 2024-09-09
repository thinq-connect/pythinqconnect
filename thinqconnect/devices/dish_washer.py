from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class DishWasherProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "runState": Resource.RUN_STATE,
                "dishWashingStatus": Resource.DISH_WASHING_STATUS,
                "preference": Resource.PREFERENCE,
                "doorStatus": Resource.DOOR_STATUS,
                "operation": Resource.OPERATION,
                "remoteControlEnable": Resource.REMOTE_CONTROL_ENABLE,
                "timer": Resource.TIMER,
                "dishWashingCourse": Resource.DISH_WASHING_COURSE,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "dishWashingStatus": {"rinseRefill": Property.RINSE_REFILL},
                "preference": {
                    "rinseLevel": Property.RINSE_LEVEL,
                    "softeningLevel": Property.SOFTENING_LEVEL,
                    "mCReminder": Property.MACHINE_CLEAN_REMINDER,
                    "signalLevel": Property.SIGNAL_LEVEL,
                    "cleanLReminder": Property.CLEAN_LIGHT_REMINDER,
                },
                "doorStatus": {"doorState": Property.DOOR_STATE},
                "operation": {"dishWasherOperationMode": Property.DISH_WASHER_OPERATION_MODE},
                "remoteControlEnable": {"remoteControlEnabled": Property.REMOTE_CONTROL_ENABLED},
                "timer": {
                    "relativeHourToStart": Property.RELATIVE_HOUR_TO_START,
                    "relativeMinuteToStart": Property.RELATIVE_MINUTE_TO_START,
                    "remainHour": Property.REMAIN_HOUR,
                    "remainMinute": Property.REMAIN_MINUTE,
                    "totalHour": Property.TOTAL_HOUR,
                    "totalMinute": Property.TOTAL_MINUTE,
                },
                "dishWashingCourse": {"currentDishWashingCourse": Property.CURRENT_DISH_WASHING_COURSE},
            },
        )


class DishWasherDevice(ConnectBaseDevice):
    """DishWasher Property."""

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
            profiles=DishWasherProfile(profile=profile),
        )

    @property
    def profiles(self) -> DishWasherProfile:
        return self._profiles

    async def set_dish_washer_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.DISH_WASHER_OPERATION_MODE, mode)

    async def set_relative_hour_to_start(self, hour: int) -> dict | None:
        return await self.do_attribute_command(Property.RELATIVE_HOUR_TO_START, hour)

from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class RobotCleanerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "runState": Resource.RUN_STATE,
                "robotCleanerJobMode": Resource.ROBOT_CLEANER_JOB_MODE,
                "operation": Resource.OPERATION,
                "battery": Resource.BATTERY,
                "timer": Resource.TIMER,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "robotCleanerJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "operation": {"cleanOperationMode": Property.CLEAN_OPERATION_MODE},
                "battery": {"level": Property.BATTERY_LEVEL, "percent": Property.BATTERY_PERCENT},
                "timer": {
                    "absoluteHourToStart": Property.ABSOLUTE_HOUR_TO_START,
                    "absoluteMinuteToStart": Property.ABSOLUTE_MINUTE_TO_START,
                    "runningHour": Property.RUNNING_HOUR,
                    "runningMinute": Property.RUNNING_MINUTE,
                },
            },
        )


class RobotCleanerDevice(ConnectBaseDevice):
    """RobotCleaner Property."""

    _CUSTOM_SET_PROPERTY_NAME = {
        Property.ABSOLUTE_HOUR_TO_START: "absolute_time_to_start",
        Property.ABSOLUTE_MINUTE_TO_START: "absolute_time_to_start",
    }

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
            profiles=RobotCleanerProfile(profile=profile),
        )

    @property
    def profiles(self) -> RobotCleanerProfile:
        return self._profiles

    async def set_clean_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CLEAN_OPERATION_MODE, mode)

    async def set_absolute_time_to_start(self, hour: int, minute: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.ABSOLUTE_HOUR_TO_START: hour,
                **({Property.ABSOLUTE_MINUTE_TO_START: minute} if minute != 0 else {}),
            }
        )

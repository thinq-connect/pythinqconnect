from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class DryerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "runState": Resource.RUN_STATE,
                "operation": Resource.OPERATION,
                "remoteControlEnable": Resource.REMOTE_CONTROL_ENABLE,
                "timer": Resource.TIMER,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "operation": {
                    "dryerOperationMode": Property.DRYER_OPERATION_MODE,
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
            },
        )


class DryerDevice(ConnectBaseDevice):
    """Dryer Property."""

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
            profiles=DryerProfile(profile=profile),
        )

    @property
    def profiles(self) -> DryerProfile:
        return self._profiles

    async def set_dryer_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.DRYER_OPERATION_MODE, mode)

    async def set_relative_hour_to_start(self, hour: int) -> dict | None:
        return await self.do_attribute_command(Property.RELATIVE_HOUR_TO_START, hour)

    async def set_relative_hour_to_stop(self, hour: int) -> dict | None:
        return await self.do_range_attribute_command(Property.RELATIVE_HOUR_TO_STOP, hour)

from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class HoodProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "ventilation": Resource.VENTILATION,
                "lamp": Resource.LAMP,
                "operation": Resource.OPERATION,
                "timer": Resource.TIMER,
            },
            profile_map={
                "ventilation": {
                    "fanSpeed": Property.FAN_SPEED,
                },
                "lamp": {
                    "lampBrightness": Property.LAMP_BRIGHTNESS,
                },
                "operation": {
                    "hoodOperationMode": Property.HOOD_OPERATION_MODE,
                },
                "timer": {
                    "remainMinute": Property.REMAIN_MINUTE,
                    "remainSecond": Property.REMAIN_SECOND,
                },
            },
        )


class HoodDevice(ConnectBaseDevice):
    """Oven Property."""

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
            profiles=HoodProfile(profile=profile),
        )

    @property
    def profiles(self) -> HoodProfile:
        return self._profiles

    @property
    def remain_time(self) -> dict:
        return {"minute": self.remain_minute, "second": self.remain_second}

    async def set_fan_speed_lamp_brightness(self, fan_speed: int, lamp_brightness: int) -> dict | None:
        return await self.do_multi_range_attribute_command(
            {
                Property.FAN_SPEED: fan_speed,
                Property.LAMP_BRIGHTNESS: lamp_brightness,
            }
        )

    async def set_fan_speed(self, fan_speed: int) -> dict | None:
        return await self.do_multi_range_attribute_command(
            {Property.FAN_SPEED: fan_speed, Property.LAMP_BRIGHTNESS: self.lamp_brightness}
        )

    async def set_lamp_brightness(self, lamp_brightness: int) -> dict | None:
        return await self.do_multi_range_attribute_command(
            {
                Property.FAN_SPEED: self.fan_speed,
                Property.LAMP_BRIGHTNESS: lamp_brightness,
            }
        )

from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class MicrowaveOvenProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "runState": Resource.RUN_STATE,
                "timer": Resource.TIMER,
                "ventilation": Resource.VENTILATION,
                "lamp": Resource.LAMP,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "timer": {
                    "remainMinute": Property.REMAIN_MINUTE,
                    "remainSecond": Property.REMAIN_SECOND,
                },
                "ventilation": {"fanSpeed": Property.FAN_SPEED},
                "lamp": {"lampBrightness": Property.LAMP_BRIGHTNESS},
            },
        )


class MicrowaveOvenDevice(ConnectBaseDevice):
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
            profiles=MicrowaveOvenProfile(profile=profile),
        )

    @property
    def profiles(self) -> MicrowaveOvenProfile:
        return self._profiles

    async def set_fan_speed_lamp_brightness(self, fan_speed: int, lamp_brightness: int) -> dict | None:
        return await self.do_multi_range_attribute_command(
            {
                Property.FAN_SPEED: fan_speed,
                Property.LAMP_BRIGHTNESS: lamp_brightness,
            }
        )

    async def set_fan_speed(self, speed: int) -> dict | None:
        return await self.do_multi_range_attribute_command(
            {
                Property.LAMP_BRIGHTNESS: self.get_status(Property.LAMP_BRIGHTNESS),
                Property.FAN_SPEED: speed,
            }
        )

    async def set_lamp_brightness(self, brightness: int) -> dict | None:
        return await self.do_multi_range_attribute_command(
            {
                Property.LAMP_BRIGHTNESS: brightness,
                Property.FAN_SPEED: self.get_status(Property.FAN_SPEED),
            }
        )

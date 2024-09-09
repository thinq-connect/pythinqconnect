from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class HumidifierProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "humidifierJobMode": Resource.HUMIDIFIER_JOB_MODE,
                "operation": Resource.OPERATION,
                "timer": Resource.TIMER,
                "sleepTimer": Resource.SLEEP_TIMER,
                "humidity": Resource.HUMIDITY,
                "airFlow": Resource.AIR_FLOW,
                "airQualitySensor": Resource.AIR_QUALITY_SENSOR,
                "display": Resource.DISPLAY,
                "moodLamp": Resource.MOOD_LAMP,
            },
            profile_map={
                "humidifierJobMode": {
                    "currentJobMode": Property.CURRENT_JOB_MODE,
                },
                "operation": {
                    "humidifierOperationMode": Property.HUMIDIFIER_OPERATION_MODE,
                    "autoMode": Property.AUTO_MODE,
                    "sleepMode": Property.SLEEP_MODE,
                    "hygieneDryMode": Property.HYGIENE_DRY_MODE,
                },
                "timer": {
                    "absoluteHourToStart": Property.ABSOLUTE_HOUR_TO_START,
                    "absoluteHourToStop": Property.ABSOLUTE_HOUR_TO_STOP,
                    "absoluteMinuteToStart": Property.ABSOLUTE_MINUTE_TO_START,
                    "absoluteMinuteToStop": Property.ABSOLUTE_MINUTE_TO_STOP,
                },
                "sleepTimer": {
                    "relativeHourToStop": Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP,
                },
                "humidity": {
                    "targetHumidity": Property.TARGET_HUMIDITY,
                    "warmMode": Property.WARM_MODE,
                },
                "airFlow": {
                    "windStrength": Property.WIND_STRENGTH,
                },
                "airQualitySensor": {
                    "monitoringEnabled": Property.MONITORING_ENABLED,
                    "totalPollution": Property.TOTAL_POLLUTION,
                    "totalPollutionLevel": Property.TOTAL_POLLUTION_LEVEL,
                    "PM1": Property.PM1,
                    "PM2": Property.PM2,
                    "PM10": Property.PM10,
                    "humidity": Property.HUMIDITY,
                    "temperature": Property.TEMPERATURE,
                },
                "display": {
                    "light": Property.DISPLAY_LIGHT,
                },
                "moodLamp": {
                    "moodLampState": Property.MOOD_LAMP_STATE,
                },
            },
        )


class HumidifierDevice(ConnectBaseDevice):
    _CUSTOM_SET_PROPERTY_NAME = {
        Property.ABSOLUTE_HOUR_TO_START: "absolute_time_to_start",
        Property.ABSOLUTE_MINUTE_TO_START: "absolute_time_to_start",
        Property.ABSOLUTE_HOUR_TO_STOP: "absolute_time_to_stop",
        Property.ABSOLUTE_MINUTE_TO_STOP: "absolute_time_to_stop",
        Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP: "sleep_timer_relative_time_to_stop",
        Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP: "sleep_timer_relative_time_to_stop",
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
            profiles=HumidifierProfile(profile=profile),
        )

    @property
    def profiles(self) -> HumidifierProfile:
        return self._profiles

    async def set_current_job_mode(self, job_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, job_mode)

    async def set_humidifier_operation_mode(self, operation_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.HUMIDIFIER_OPERATION_MODE, operation_mode)

    async def set_auto_mode(self, auto_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AUTO_MODE, auto_mode)

    async def set_sleep_mode(self, sleep_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.SLEEP_MODE, sleep_mode)

    async def set_hygiene_dry_mode(self, hygiene_dry_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.HYGIENE_DRY_MODE, hygiene_dry_mode)

    async def set_absolute_time_to_start(self, hour: int, minute: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.ABSOLUTE_HOUR_TO_START: hour,
                Property.ABSOLUTE_MINUTE_TO_START: minute,
            }
        )

    async def set_absolute_time_to_stop(self, hour: int, minute: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.ABSOLUTE_HOUR_TO_STOP: hour,
                Property.ABSOLUTE_MINUTE_TO_STOP: minute,
            }
        )

    async def set_sleep_timer_relative_time_to_stop(self, hour: int, minute: int = 0) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP: hour,
                **({Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP: minute} if minute != 0 else {}),
            }
        )

    async def set_target_humidity(self, target_humidity: int) -> dict | None:
        return await self.do_attribute_command(Property.TARGET_HUMIDITY, target_humidity)

    async def set_warm_mode(self, warm_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WARM_MODE, warm_mode)

    async def set_wind_strength(self, wind_strength: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_STRENGTH, wind_strength)

    async def set_display_light(self, display_light: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.DISPLAY_LIGHT, display_light)

    async def set_mood_lamp_state(self, state: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.MOOD_LAMP_STATE, state)

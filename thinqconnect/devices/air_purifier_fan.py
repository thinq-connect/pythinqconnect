from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class AirPurifierFanProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "airFanJobMode": Resource.AIR_FAN_JOB_MODE,
                "operation": Resource.OPERATION,
                "timer": Resource.TIMER,
                "sleepTimer": Resource.SLEEP_TIMER,
                "airFlow": Resource.AIR_FLOW,
                "airQualitySensor": Resource.AIR_QUALITY_SENSOR,
                "display": Resource.DISPLAY,
                "misc": Resource.MISC,
            },
            profile_map={
                "airFanJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "operation": {"airFanOperationMode": Property.AIR_FAN_OPERATION_MODE},
                "timer": {
                    "absoluteHourToStart": Property.ABSOLUTE_HOUR_TO_START,
                    "absoluteMinuteToStart": Property.ABSOLUTE_MINUTE_TO_START,
                    "absoluteHourToStop": Property.ABSOLUTE_HOUR_TO_STOP,
                    "absoluteMinuteToStop": Property.ABSOLUTE_MINUTE_TO_STOP,
                },
                "sleepTimer": {
                    "relativeHourToStop": Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP,
                },
                "airFlow": {
                    "warmMode": Property.WARM_MODE,
                    "windTemperature": Property.WIND_TEMPERATURE,
                    "windStrength": Property.WIND_STRENGTH,
                    "windAngle": Property.WIND_ANGLE,
                },
                "airQualitySensor": {
                    "monitoringEnabled": Property.MONITORING_ENABLED,
                    "PM1": Property.PM1,
                    "PM2": Property.PM2,
                    "PM10": Property.PM10,
                    "humidity": Property.HUMIDITY,
                    "temperature": Property.TEMPERATURE,
                    "odor": Property.ODOR,
                    "odorLevel": Property.ODOR_LEVEL,
                    "totalPollution": Property.TOTAL_POLLUTION,
                    "totalPollutionLevel": Property.TOTAL_POLLUTION_LEVEL,
                },
                "display": {"light": Property.DISPLAY_LIGHT},
                "misc": {"uvNano": Property.UV_NANO},
            },
        )


class AirPurifierFanDevice(ConnectBaseDevice):
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
            profiles=AirPurifierFanProfile(profile=profile),
        )

    @property
    def profiles(self) -> AirPurifierFanProfile:
        return self._profiles

    async def set_current_job_mode(self, job_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, job_mode)

    async def set_air_fan_operation_mode(self, operation_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AIR_FAN_OPERATION_MODE, operation_mode)

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

    async def set_warm_mode(self, warm_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WARM_MODE, warm_mode)

    async def set_wind_temperature(self, wind_temperature: int) -> dict | None:
        return await self.do_attribute_command(Property.WIND_TEMPERATURE, wind_temperature)

    async def set_wind_strength(self, wind_strength: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_STRENGTH, wind_strength)

    async def set_wind_angle(self, wind_angle: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_ANGLE, wind_angle)

    async def set_display_light(self, display_light: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.DISPLAY_LIGHT, display_light)

    async def set_uv_nano(self, uv_nano: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.UV_NANO, uv_nano)

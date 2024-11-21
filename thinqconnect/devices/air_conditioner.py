from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class AirConditionerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "airConJobMode": Resource.AIR_CON_JOB_MODE,
                "operation": Resource.OPERATION,
                "temperature": Resource.TEMPERATURE,
                "twoSetTemperature": Resource.TWO_SET_TEMPERATURE,
                "timer": Resource.TIMER,
                "sleepTimer": Resource.SLEEP_TIMER,
                "powerSave": Resource.POWER_SAVE,
                "airFlow": Resource.AIR_FLOW,
                "airQualitySensor": Resource.AIR_QUALITY_SENSOR,
                "filterInfo": Resource.FILTER_INFO,
            },
            profile_map={
                "airConJobMode": {
                    "currentJobMode": Property.CURRENT_JOB_MODE,
                },
                "operation": {
                    "airConOperationMode": Property.AIR_CON_OPERATION_MODE,
                    "airCleanOperationMode": Property.AIR_CLEAN_OPERATION_MODE,
                },
                "temperature": {
                    "currentTemperature": Property.CURRENT_TEMPERATURE,
                    "targetTemperature": Property.TARGET_TEMPERATURE,
                    "heatTargetTemperature": Property.HEAT_TARGET_TEMPERATURE,
                    "coolTargetTemperature": Property.COOL_TARGET_TEMPERATURE,
                    "unit": "temperature_unit",
                },
                "twoSetTemperature": {
                    "currentTemperature": Property.TWO_SET_CURRENT_TEMPERATURE,
                    "heatTargetTemperature": Property.TWO_SET_HEAT_TARGET_TEMPERATURE,
                    "coolTargetTemperature": Property.TWO_SET_COOL_TARGET_TEMPERATURE,
                    "unit": Property.TWO_SET_TEMPERATURE_UNIT,
                },
                "timer": {
                    "relativeHourToStart": Property.RELATIVE_HOUR_TO_START,
                    "relativeMinuteToStart": Property.RELATIVE_MINUTE_TO_START,
                    "relativeHourToStop": Property.RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.RELATIVE_MINUTE_TO_STOP,
                    "absoluteHourToStart": Property.ABSOLUTE_HOUR_TO_START,
                    "absoluteMinuteToStart": Property.ABSOLUTE_MINUTE_TO_START,
                    "absoluteHourToStop": Property.ABSOLUTE_HOUR_TO_STOP,
                    "absoluteMinuteToStop": Property.ABSOLUTE_MINUTE_TO_STOP,
                },
                "sleepTimer": {
                    "relativeHourToStop": Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP,
                },
                "powerSave": {
                    "powerSaveEnabled": Property.POWER_SAVE_ENABLED,
                },
                "airFlow": {
                    "windStrength": Property.WIND_STRENGTH,
                    "windStep": Property.WIND_STEP,
                },
                "airQualitySensor": {
                    "PM1": Property.PM1,
                    "PM2": Property.PM2,
                    "PM10": Property.PM10,
                    "odor": Property.ODOR,
                    "odorLevel": Property.ODOR_LEVEL,
                    "humidity": Property.HUMIDITY,
                    "totalPollution": Property.TOTAL_POLLUTION,
                    "totalPollutionLevel": Property.TOTAL_POLLUTION_LEVEL,
                    "monitoringEnabled": Property.MONITORING_ENABLED,
                },
                "filterInfo": {
                    "usedTime": Property.USED_TIME,
                    "filterLifetime": Property.FILTER_LIFETIME,
                    "filterRemainPercent": Property.FILTER_REMAIN_PERCENT,
                },
            },
        )


class AirConditionerDevice(ConnectBaseDevice):
    """Air Conditioner Property."""

    _CUSTOM_SET_PROPERTY_NAME = {
        Property.RELATIVE_HOUR_TO_START: "relative_time_to_start",
        Property.RELATIVE_MINUTE_TO_START: "relative_time_to_start",
        Property.RELATIVE_HOUR_TO_STOP: "relative_time_to_stop",
        Property.RELATIVE_MINUTE_TO_STOP: "relative_time_to_stop",
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
            profiles=AirConditionerProfile(profile=profile),
        )

    @property
    def profiles(self) -> AirConditionerProfile:
        return self._profiles

    async def set_current_job_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, mode)

    async def set_air_con_operation_mode(self, operation: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AIR_CON_OPERATION_MODE, operation)

    async def set_air_clean_operation_mode(self, operation: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AIR_CLEAN_OPERATION_MODE, operation)

    async def set_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_range_attribute_command(Property.TARGET_TEMPERATURE, temperature)

    async def set_heat_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_range_attribute_command(Property.HEAT_TARGET_TEMPERATURE, temperature)

    async def set_cool_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_range_attribute_command(Property.COOL_TARGET_TEMPERATURE, temperature)

    async def set_two_set_heat_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.TWO_SET_HEAT_TARGET_TEMPERATURE: temperature,
                Property.TWO_SET_COOL_TARGET_TEMPERATURE: self.get_status(Property.TWO_SET_COOL_TARGET_TEMPERATURE),
            }
        )

    async def set_two_set_cool_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.TWO_SET_HEAT_TARGET_TEMPERATURE: self.get_status(Property.TWO_SET_HEAT_TARGET_TEMPERATURE),
                Property.TWO_SET_COOL_TARGET_TEMPERATURE: temperature,
            }
        )

    async def set_relative_time_to_start(self, hour: int, minute: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.RELATIVE_HOUR_TO_START: hour,
                Property.RELATIVE_MINUTE_TO_START: minute,
            }
        )

    async def set_relative_time_to_stop(self, hour: int, minute: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.RELATIVE_HOUR_TO_STOP: hour,
                **({Property.RELATIVE_MINUTE_TO_STOP: minute} if minute != 0 else {}),
            }
        )

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

    async def set_sleep_timer_relative_time_to_stop(self, hour: int, minute: int) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP: hour,
                Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP: minute,
            }
        )

    async def set_power_save_enabled(self, power_save_enabled: bool) -> dict | None:
        return await self.do_attribute_command(Property.POWER_SAVE_ENABLED, power_save_enabled)

    async def set_wind_strength(self, wind_strength: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_STRENGTH, wind_strength)

    async def set_wind_step(self, wind_step: int) -> dict | None:
        return await self.do_range_attribute_command(Property.WIND_STEP, wind_step)

    async def set_monitoring_enabled(self, monitoring_enabled: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.MONITORING_ENABLED, monitoring_enabled)

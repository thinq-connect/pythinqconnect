from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class AirPurifierProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "airPurifierJobMode": Resource.AIR_PURIFIER_JOB_MODE,
                "operation": Resource.OPERATION,
                "timer": Resource.TIMER,
                "airFlow": Resource.AIR_FLOW,
                "airQualitySensor": Resource.AIR_QUALITY_SENSOR,
                "filterInfo": Resource.FILTER_INFO,
            },
            profile_map={
                "airPurifierJobMode": {
                    "currentJobMode": Property.CURRENT_JOB_MODE,
                    "personalizationMode": Property.PERSONALIZATION_MODE,
                },
                "operation": {"airPurifierOperationMode": Property.AIR_PURIFIER_OPERATION_MODE},
                "timer": {
                    "absoluteHourToStart": Property.ABSOLUTE_HOUR_TO_START,
                    "absoluteMinuteToStart": Property.ABSOLUTE_MINUTE_TO_START,
                    "absoluteHourToStop": Property.ABSOLUTE_HOUR_TO_STOP,
                    "absoluteMinuteToStop": Property.ABSOLUTE_MINUTE_TO_STOP,
                },
                "airFlow": {
                    "windStrength": Property.WIND_STRENGTH,
                },
                "airQualitySensor": {
                    "monitoringEnabled": Property.MONITORING_ENABLED,
                    "PM1": Property.PM1,
                    "PM2": Property.PM2,
                    "PM10": Property.PM10,
                    "odor": Property.ODOR,
                    "odorLevel": Property.ODOR_LEVEL,
                    "humidity": Property.HUMIDITY,
                    "totalPollution": Property.TOTAL_POLLUTION,
                    "totalPollutionLevel": Property.TOTAL_POLLUTION_LEVEL,
                },
                "filterInfo": {
                    "filterRemainPercent": Property.FILTER_REMAIN_PERCENT,
                },
            },
        )


class AirPurifierDevice(ConnectBaseDevice):
    _CUSTOM_SET_PROPERTY_NAME = {
        Property.ABSOLUTE_HOUR_TO_START: "absolute_time_to_start",
        Property.ABSOLUTE_MINUTE_TO_START: "absolute_time_to_start",
        Property.ABSOLUTE_HOUR_TO_STOP: "absolute_time_to_stop",
        Property.ABSOLUTE_MINUTE_TO_STOP: "absolute_time_to_stop",
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
            profiles=AirPurifierProfile(profile=profile),
        )

    @property
    def profiles(self) -> AirPurifierProfile:
        return self._profiles

    async def set_current_job_mode(self, job_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, job_mode)

    async def set_air_purifier_operation_mode(self, operation_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AIR_PURIFIER_OPERATION_MODE, operation_mode)

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

    async def set_wind_strength(self, wind_strength: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_STRENGTH, wind_strength)

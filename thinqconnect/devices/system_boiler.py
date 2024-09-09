from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class SystemBoilerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "boilerJobMode": Resource.BOILER_JOB_MODE,
                "operation": Resource.OPERATION,
                "temperature": Resource.TEMPERATURE,
            },
            profile_map={
                "boilerJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "operation": {
                    "boilerOperationMode": Property.BOILER_OPERATION_MODE,
                    "hotWaterMode": Property.HOT_WATER_MODE,
                },
                "temperature": {
                    "currentTemperature": Property.CURRENT_TEMPERATURE,
                    "targetTemperature": Property.TARGET_TEMPERATURE,
                    "heatTargetTemperature": Property.HEAT_TARGET_TEMPERATURE,
                    "coolTargetTemperature": Property.COOL_TARGET_TEMPERATURE,
                    "heatMaxTemperature": Property.HEAT_MAX_TEMPERATURE,
                    "heatMinTemperature": Property.HEAT_MIN_TEMPERATURE,
                    "coolMaxTemperature": Property.COOL_MAX_TEMPERATURE,
                    "coolMinTemperature": Property.COOL_MIN_TEMPERATURE,
                    "unit": Property.TEMPERATURE_UNIT,
                },
            },
        )


class SystemBoilerDevice(ConnectBaseDevice):
    """SystemBoiler Property."""

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
            profiles=SystemBoilerProfile(profile=profile),
        )

    @property
    def profiles(self) -> SystemBoilerProfile:
        return self._profiles

    async def set_boiler_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.BOILER_OPERATION_MODE, mode)

    async def set_current_job_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, mode)

    async def set_hot_water_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.HOT_WATER_MODE, mode)

    async def set_heat_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_attribute_command(Property.HEAT_TARGET_TEMPERATURE, temperature)

    async def set_cool_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_attribute_command(Property.COOL_TARGET_TEMPERATURE, temperature)

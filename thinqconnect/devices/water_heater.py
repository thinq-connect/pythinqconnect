from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class WaterHeaterProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "waterHeaterJobMode": Resource.WATER_HEATER_JOB_MODE,
                "operation": Resource.OPERATION,
                "temperature": Resource.TEMPERATURE,
            },
            profile_map={
                "waterHeaterJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "operation": {"waterHeaterOperationMode": Property.WATER_HEATER_OPERATION_MODE},
                "temperature": {
                    "currentTemperature": Property.CURRENT_TEMPERATURE,
                    "targetTemperature": Property.TARGET_TEMPERATURE,
                },
            },
        )


class WaterHeaterDevice(ConnectBaseDevice):
    """WaterHeater Property."""

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
            profiles=WaterHeaterProfile(profile=profile),
        )

    @property
    def profiles(self) -> WaterHeaterProfile:
        return self._profiles

    async def set_current_job_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, mode)

    async def set_target_temperature(self, temperature: int) -> dict | None:
        return await self.do_attribute_command(Property.TARGET_TEMPERATURE, temperature)

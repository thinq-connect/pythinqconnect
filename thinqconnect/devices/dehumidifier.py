from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class DehumidifierProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "operation": Resource.OPERATION,
                "dehumidifierJobMode": Resource.DEHUMIDIFIER_JOB_MODE,
                "humidity": Resource.HUMIDITY,
                "airFlow": Resource.AIR_FLOW,
            },
            profile_map={
                "operation": {"dehumidifierOperationMode": Property.DEHUMIDIFIER_OPERATION_MODE},
                "dehumidifierJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "humidity": {"currentHumidity": Property.CURRENT_HUMIDITY},
                "airFlow": {"windStrength": Property.WIND_STRENGTH},
            },
        )


class DehumidifierDevice(ConnectBaseDevice):
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
            profiles=DehumidifierProfile(profile=profile),
        )

    @property
    def profiles(self) -> DehumidifierProfile:
        return self._profiles

    async def set_dehumidifier_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.DEHUMIDIFIER_OPERATION_MODE, mode)

    async def set_wind_strength(self, wind_strength: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_STRENGTH, wind_strength)

from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class WaterPurifierProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={"runState": Resource.RUN_STATE, "waterInfo": Resource.WATER_INFO},
            profile_map={
                "runState": {"cockState": Property.COCK_STATE, "sterilizingState": Property.STERILIZING_STATE},
                "waterInfo": {"waterType": Property.WATER_TYPE},
            },
        )


class WaterPurifierDevice(ConnectBaseDevice):
    """WaterPurifier Property."""

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
            profiles=WaterPurifierProfile(profile=profile),
        )

    @property
    def profiles(self) -> WaterPurifierProfile:
        return self._profiles

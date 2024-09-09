from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class StickCleanerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "runState": Resource.RUN_STATE,
                "stickCleanerJobMode": Resource.STICK_CLEANER_JOB_MODE,
                "battery": Resource.BATTERY,
            },
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "stickCleanerJobMode": {
                    "currentJobMode": Property.CURRENT_JOB_MODE,
                },
                "battery": {"level": Property.BATTERY_LEVEL, "percent": Property.BATTERY_PERCENT},
            },
        )


class StickCleanerDevice(ConnectBaseDevice):
    """StickCleaner Property."""

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
            profiles=StickCleanerProfile(profile=profile),
        )

    @property
    def profiles(self) -> StickCleanerProfile:
        return self._profiles

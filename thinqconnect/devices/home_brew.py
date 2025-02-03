from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class HomeBrewProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={"runState": Resource.RUN_STATE, "recipe": Resource.RECIPE, "timer": Resource.TIMER},
            profile_map={
                "runState": {"currentState": Property.CURRENT_STATE},
                "recipe": {
                    "beerRemain": Property.BEER_REMAIN,
                    "flavorInfo": Property.FLAVOR_INFO,
                    "flavorCapsule1": Property.FLAVOR_CAPSULE_1,
                    "flavorCapsule2": Property.FLAVOR_CAPSULE_2,
                    "hopOilInfo": Property.HOP_OIL_INFO,
                    "hopOilCapsule1": Property.HOP_OIL_CAPSULE_1,
                    "hopOilCapsule2": Property.HOP_OIL_CAPSULE_2,
                    "wortInfo": Property.WORT_INFO,
                    "yeastInfo": Property.YEAST_INFO,
                    "recipeName": Property.RECIPE_NAME,
                },
                "timer": {
                    "elapsedDayState": Property.ELAPSED_DAY_STATE,
                    "elapsedDayTotal": Property.ELAPSED_DAY_TOTAL,
                },
            },
        )


class HomeBrewDevice(ConnectBaseDevice):
    """HomeBrew Property."""

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
            profiles=HomeBrewProfile(profile=profile),
        )

    @property
    def profiles(self) -> HomeBrewProfile:
        return self._profiles

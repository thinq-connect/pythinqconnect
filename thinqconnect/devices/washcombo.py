"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .const import Property
from .washer import WasherSubDevice, WasherSubProfile


class WashcomboDevice(WasherSubDevice):
    @property
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, value: str):
        self._location = value

    @property
    def group_id(self) -> str:
        return self._group_id

    @group_id.setter
    def group_id(self, value: str):
        self._group_id = value

    async def set_washer_operation_mode(self, operation: str) -> dict | None:
        payload = self.profiles.get_enum_attribute_payload(Property.WASHER_OPERATION_MODE, operation)
        return await self._do_attribute_command({"location": {"locationName": self.location}, **payload})

    async def set_relative_hour_to_start(self, hour: int) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_START, hour)
        return await self._do_attribute_command({"location": {"locationName": self.location}, **payload})

    async def set_relative_hour_to_stop(self, hour: int) -> dict | None:
        payload = self.profiles.get_range_attribute_payload(Property.RELATIVE_HOUR_TO_STOP, hour)
        return await self._do_attribute_command({"location": {"locationName": self.location}, **payload})

    def __init__(
        self,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        group_id: str,
        reportable: bool,
        profile: dict[str, Any],
        location: str,
    ):
        super().__init__(
            profiles=WasherSubProfile(profile=profile, location_name=location, use_sub_notification=True),
            location_name=location,
            single_unit=True,
            thinq_api=thinq_api,
            device_id=device_id,
            device_type=device_type,
            model_name=model_name,
            alias=alias,
            reportable=reportable,
        )
        self.group_id = group_id
        self.location = location

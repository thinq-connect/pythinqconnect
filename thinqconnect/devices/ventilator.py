from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import READABILITY, WRITABILITY, ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class VentilatorProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "ventJobMode": Resource.VENTILATOR_JOB_MODE,
                "operation": Resource.OPERATION,
                "temperature": Resource.TEMPERATURE,
                "airQualitySensor": Resource.AIR_QUALITY_SENSOR,
                "airFlow": Resource.AIR_FLOW,
                "timer": Resource.TIMER,
                "sleepTimer": Resource.SLEEP_TIMER,
            },
            profile_map={
                "ventJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "operation": {"ventOperationMode": Property.VENTILATOR_OPERATION_MODE},
                "temperature": {
                    "currentTemperature": Property.CURRENT_TEMPERATURE,
                    "unit": Property.TEMPERATURE_UNIT,
                },
                "airQualitySensor": {
                    "PM1": Property.PM1,
                    "PM2": Property.PM2,
                    "PM10": Property.PM10,
                    "CO2": Property.CO2,
                },
                "airFlow": {"windStrength": Property.WIND_STRENGTH},
                "timer": {
                    "absoluteHourToStop": Property.ABSOLUTE_HOUR_TO_STOP,
                    "absoluteMinuteToStop": Property.ABSOLUTE_MINUTE_TO_STOP,
                    "absoluteHourToStart": Property.ABSOLUTE_HOUR_TO_START,
                    "absoluteMinuteToStart": Property.ABSOLUTE_MINUTE_TO_START,
                    "relativeHourToStop": Property.RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.RELATIVE_MINUTE_TO_STOP,
                    "relativeHourToStart": Property.RELATIVE_HOUR_TO_START,
                    "relativeMinuteToStart": Property.RELATIVE_MINUTE_TO_START,
                },
                "sleepTimer": {
                    "relativeHourToStop": Property.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP,
                    "relativeMinuteToStop": Property.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP,
                },
            },
            custom_resources=["temperature"],
        )

    def _generate_custom_resource_properties(
        self, resource_key: str, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        readable_props = []
        writable_props = []

        if resource_key not in self._CUSTOM_RESOURCES:
            return readable_props, writable_props

        for prop_key, prop_attr in props.items():
            prop = self._get_properties(resource_property, prop_key)
            prop.pop("unit", None)
            if prop[READABILITY]:
                readable_props.append(str(prop_attr))
            if prop[WRITABILITY]:
                writable_props.append(str(prop_attr))
            self._set_prop_attr(prop_attr, prop)

        return readable_props, writable_props


class VentilatorDevice(ConnectBaseDevice):
    """Ventilator Property."""

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
            profiles=VentilatorProfile(profile=profile),
        )

    @property
    def profiles(self) -> VentilatorProfile:
        return self._profiles

    async def set_current_job_mode(self, job_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, job_mode)

    async def set_ventilator_operation_mode(self, operation_mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.VENTILATOR_OPERATION_MODE, operation_mode)

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

    async def set_wind_strength(self, wind_strength: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.WIND_STRENGTH, wind_strength)

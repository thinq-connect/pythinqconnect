from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import READABILITY, WRITABILITY, ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class AirConditionerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "airConJobMode": Resource.AIR_CON_JOB_MODE,
                "operation": Resource.OPERATION,
                "temperatureInUnits": Resource.TEMPERATURE,
                "twoSetTemperature": Resource.TWO_SET_TEMPERATURE,
                "twoSetTemperatureInUnits": Resource.TWO_SET_TEMPERATURE,
                "timer": Resource.TIMER,
                "sleepTimer": Resource.SLEEP_TIMER,
                "powerSave": Resource.POWER_SAVE,
                "airFlow": Resource.AIR_FLOW,
                "airQualitySensor": Resource.AIR_QUALITY_SENSOR,
                "filterInfo": Resource.FILTER_INFO,
                "display": Resource.DISPLAY,
                "windDirection": Resource.WIND_DIRECTION,
            },
            profile_map={
                "airConJobMode": {
                    "currentJobMode": Property.CURRENT_JOB_MODE,
                },
                "operation": {
                    "airConOperationMode": Property.AIR_CON_OPERATION_MODE,
                    "airCleanOperationMode": Property.AIR_CLEAN_OPERATION_MODE,
                },
                "temperatureInUnits": {
                    "currentTemperatureC": Property.CURRENT_TEMPERATURE_C,
                    "currentTemperatureF": Property.CURRENT_TEMPERATURE_F,
                    "targetTemperatureC": Property.TARGET_TEMPERATURE_C,
                    "targetTemperatureF": Property.TARGET_TEMPERATURE_F,
                    "heatTargetTemperatureC": Property.HEAT_TARGET_TEMPERATURE_C,
                    "heatTargetTemperatureF": Property.HEAT_TARGET_TEMPERATURE_F,
                    "coolTargetTemperatureC": Property.COOL_TARGET_TEMPERATURE_C,
                    "coolTargetTemperatureF": Property.COOL_TARGET_TEMPERATURE_F,
                    "unit": Property.TEMPERATURE_UNIT,
                },
                "twoSetTemperature": {
                    "twoSetEnabled": Property.TWO_SET_ENABLED,
                },
                "twoSetTemperatureInUnits": {
                    "heatTargetTemperatureC": Property.TWO_SET_HEAT_TARGET_TEMPERATURE_C,
                    "heatTargetTemperatureF": Property.TWO_SET_HEAT_TARGET_TEMPERATURE_F,
                    "coolTargetTemperatureC": Property.TWO_SET_COOL_TARGET_TEMPERATURE_C,
                    "coolTargetTemperatureF": Property.TWO_SET_COOL_TARGET_TEMPERATURE_F,
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
                "display": {"light": Property.DISPLAY_LIGHT},
                "windDirection": {
                    "rotateUpDown": Property.WIND_ROTATE_UP_DOWN,
                    "rotateLeftRight": Property.WIND_ROTATE_LEFT_RIGHT,
                },
            },
            custom_resources=["twoSetTemperature", "temperatureInUnits", "twoSetTemperatureInUnits"],
        )

    _CUSTOM_PROPERTY_MAPPING_TABLE = {
        Property.CURRENT_TEMPERATURE_C: "currentTemperature",
        Property.CURRENT_TEMPERATURE_F: "currentTemperature",
        Property.TARGET_TEMPERATURE_C: "targetTemperature",
        Property.TARGET_TEMPERATURE_F: "targetTemperature",
        Property.HEAT_TARGET_TEMPERATURE_C: "heatTargetTemperature",
        Property.HEAT_TARGET_TEMPERATURE_F: "heatTargetTemperature",
        Property.COOL_TARGET_TEMPERATURE_C: "coolTargetTemperature",
        Property.COOL_TARGET_TEMPERATURE_F: "coolTargetTemperature",
        Property.TWO_SET_HEAT_TARGET_TEMPERATURE_C: "heatTargetTemperature",
        Property.TWO_SET_HEAT_TARGET_TEMPERATURE_F: "heatTargetTemperature",
        Property.TWO_SET_COOL_TARGET_TEMPERATURE_C: "coolTargetTemperature",
        Property.TWO_SET_COOL_TARGET_TEMPERATURE_F: "coolTargetTemperature",
    }

    def check_attribute_writable(self, prop_attr: Property) -> bool:
        return (
            prop_attr in [Property.TEMPERATURE_UNIT, Property.TWO_SET_TEMPERATURE_UNIT]
            or self._get_prop_attr(prop_attr)[WRITABILITY]
        )

    def _get_attribute_payload(self, attribute: Property, value: str | int) -> dict:
        for resource, props in self._PROFILE.items():
            for prop_key, prop_attr in props.items():
                if prop_attr == attribute:
                    return (
                        {resource: {prop_key: value}}
                        if attribute not in self._CUSTOM_PROPERTY_MAPPING_TABLE
                        else {resource: {self._CUSTOM_PROPERTY_MAPPING_TABLE[attribute]: value}}
                    )

    def _generate_custom_resource_properties(
        self, resource_key: str, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        # pylint: disable=unused-argument
        readable_props = []
        writable_props = []

        if resource_key not in self._CUSTOM_RESOURCES:
            return readable_props, writable_props

        if resource_key == "twoSetTemperature":
            for prop_key, prop_attr in props.items():
                prop = self._get_properties(resource_property, prop_key)
                if prop[READABILITY]:
                    readable_props.append(str(prop_attr))
                if prop[WRITABILITY]:
                    writable_props.append(str(prop_attr))
                self._set_prop_attr(prop_attr, prop)
            return readable_props, writable_props

        units = []

        for temperatures in resource_property:
            unit = temperatures["unit"]
            for prop_key, prop_attr in props.items():
                if prop_key[-1:] != unit:
                    continue
                prop = self._get_properties(temperatures, prop_key[:-1])
                if prop[READABILITY]:
                    readable_props.append(str(prop_attr))
                if prop[WRITABILITY]:
                    writable_props.append(str(prop_attr))
                self._set_prop_attr(prop_attr, prop)
            units.append(unit)

        prop_attr = props.get("unit")
        prop = self._get_readonly_enum_property(units)
        if prop[READABILITY]:
            readable_props.append(str(prop_attr))
        if prop[WRITABILITY]:
            writable_props.append(str(prop_attr))
        self._set_prop_attr(prop_attr, prop)

        return readable_props, writable_props


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

    def _set_custom_resources(
        self,
        prop_key: str,
        attribute: str,
        resource_status: dict[str, str] | list[dict[str, str]],
        is_updated: bool = False,
    ) -> bool:
        if attribute == Property.TWO_SET_ENABLED:
            return False

        for temperature_status in resource_status:
            unit = temperature_status.get("unit")
            if attribute in [Property.TEMPERATURE_UNIT, Property.TWO_SET_TEMPERATURE_UNIT]:
                if unit == "C":
                    self._set_status_attr(attribute, unit)
            elif attribute[-1:].upper() == unit:
                temperature_map = self.profiles._PROFILE["temperatureInUnits"]
                two_set_temperature_map = self.profiles._PROFILE["twoSetTemperatureInUnits"]
                _prop_key = None

                if attribute in temperature_map.values():
                    _prop_key = list(temperature_map.keys())[list(temperature_map.values()).index(attribute)]
                elif attribute in two_set_temperature_map.values():
                    _prop_key = list(two_set_temperature_map.keys())[
                        list(two_set_temperature_map.values()).index(attribute)
                    ]

                if not _prop_key:
                    _attribute_value = None
                elif _prop_key[:-1] not in temperature_status and is_updated:
                    continue
                else:
                    _attribute_value = temperature_status.get(_prop_key[:-1])
                self._set_status_attr(attribute, _attribute_value)
        return True

    async def set_current_job_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, mode)

    async def set_air_con_operation_mode(self, operation: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AIR_CON_OPERATION_MODE, operation)

    async def set_air_clean_operation_mode(self, operation: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.AIR_CLEAN_OPERATION_MODE, operation)

    async def _set_target_temperature(self, temperature: int, unit: str) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.TARGET_TEMPERATURE_C if unit == "C" else Property.TARGET_TEMPERATURE_F: temperature,
                Property.TEMPERATURE_UNIT: unit,
            }
        )

    async def _set_heat_target_temperature(self, temperature: int, unit: str) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.HEAT_TARGET_TEMPERATURE_C if unit == "C" else Property.HEAT_TARGET_TEMPERATURE_F: temperature,
                Property.TEMPERATURE_UNIT: unit,
            }
        )

    async def _set_cool_target_temperature(self, temperature: int, unit: str) -> dict | None:
        return await self.do_multi_attribute_command(
            {
                Property.COOL_TARGET_TEMPERATURE_C if unit == "C" else Property.COOL_TARGET_TEMPERATURE_F: temperature,
                Property.TEMPERATURE_UNIT: unit,
            }
        )

    async def set_heat_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_heat_target_temperature(temperature, "C")

    async def set_heat_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_heat_target_temperature(temperature, "F")

    async def set_cool_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_cool_target_temperature(temperature, "C")

    async def set_cool_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_cool_target_temperature(temperature, "F")

    async def _set_two_set_heat_target_temperature(self, temperature: int, unit: str) -> dict | None:
        heat_target_prop = (
            Property.TWO_SET_HEAT_TARGET_TEMPERATURE_C if unit == "C" else Property.TWO_SET_HEAT_TARGET_TEMPERATURE_F
        )
        cool_target_prop = (
            Property.TWO_SET_COOL_TARGET_TEMPERATURE_C if unit == "C" else Property.TWO_SET_COOL_TARGET_TEMPERATURE_F
        )
        return await self.do_multi_attribute_command(
            {
                heat_target_prop: temperature,
                cool_target_prop: self.get_status(cool_target_prop),
                Property.TWO_SET_TEMPERATURE_UNIT: unit,
            }
        )

    async def _set_two_set_cool_target_temperature(self, temperature: int, unit: str) -> dict | None:
        heat_target_prop = (
            Property.TWO_SET_HEAT_TARGET_TEMPERATURE_C if unit == "C" else Property.TWO_SET_HEAT_TARGET_TEMPERATURE_F
        )
        cool_target_prop = (
            Property.TWO_SET_COOL_TARGET_TEMPERATURE_C if unit == "C" else Property.TWO_SET_COOL_TARGET_TEMPERATURE_F
        )
        return await self.do_multi_attribute_command(
            {
                heat_target_prop: self.get_status(heat_target_prop),
                cool_target_prop: temperature,
                Property.TWO_SET_TEMPERATURE_UNIT: unit,
            }
        )

    async def set_two_set_heat_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_two_set_heat_target_temperature(temperature, "C")

    async def set_two_set_heat_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_two_set_heat_target_temperature(temperature, "F")

    async def set_two_set_cool_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_two_set_cool_target_temperature(temperature, "C")

    async def set_two_set_cool_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_two_set_cool_target_temperature(temperature, "F")

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

    async def set_display_light(self, display_light: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.DISPLAY_LIGHT, display_light)

    async def set_wind_rotate_up_down(self, wind_rotate_up_down: bool) -> dict | None:
        return await self.do_attribute_command(Property.WIND_ROTATE_UP_DOWN, wind_rotate_up_down)

    async def set_wind_rotate_left_right(self, wind_rotate_left_right: bool) -> dict | None:
        return await self.do_attribute_command(Property.WIND_ROTATE_LEFT_RIGHT, wind_rotate_left_right)

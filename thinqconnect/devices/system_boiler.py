from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from typing import Any

from ..thinq_api import ThinQApi
from .connect_device import READABILITY, WRITABILITY, ConnectBaseDevice, ConnectDeviceProfile
from .const import Property, Resource


class SystemBoilerProfile(ConnectDeviceProfile):
    def __init__(self, profile: dict[str, Any]):
        super().__init__(
            profile=profile,
            resource_map={
                "boilerJobMode": Resource.BOILER_JOB_MODE,
                "operation": Resource.OPERATION,
                "hotWaterTemperatureInUnits": Resource.HOT_WATER_TEMPERATURE,
                "roomTemperatureInUnits": Resource.ROOM_TEMPERATURE,
            },
            profile_map={
                "boilerJobMode": {"currentJobMode": Property.CURRENT_JOB_MODE},
                "operation": {
                    "boilerOperationMode": Property.BOILER_OPERATION_MODE,
                    "hotWaterMode": Property.HOT_WATER_MODE,
                    "roomTempMode": Property.ROOM_TEMP_MODE,
                    "roomWaterMode": Property.ROOM_WATER_MODE,
                },
                "hotWaterTemperatureInUnits": {
                    "currentTemperatureC": Property.HOT_WATER_CURRENT_TEMPERATURE_C,
                    "currentTemperatureF": Property.HOT_WATER_CURRENT_TEMPERATURE_F,
                    "targetTemperatureC": Property.HOT_WATER_TARGET_TEMPERATURE_C,
                    "targetTemperatureF": Property.HOT_WATER_TARGET_TEMPERATURE_F,
                    "maxTemperatureC": Property.HOT_WATER_MAX_TEMPERATURE_C,
                    "maxTemperatureF": Property.HOT_WATER_MAX_TEMPERATURE_F,
                    "minTemperatureC": Property.HOT_WATER_MIN_TEMPERATURE_C,
                    "minTemperatureF": Property.HOT_WATER_MIN_TEMPERATURE_F,
                    "unit": Property.HOT_WATER_TEMPERATURE_UNIT,
                },
                "roomTemperatureInUnits": {
                    "currentTemperatureC": Property.ROOM_CURRENT_TEMPERATURE_C,
                    "currentTemperatureF": Property.ROOM_CURRENT_TEMPERATURE_F,
                    "airCurrentTemperatureC": Property.ROOM_AIR_CURRENT_TEMPERATURE_C,
                    "airCurrentTemperatureF": Property.ROOM_AIR_CURRENT_TEMPERATURE_F,
                    "outWaterCurrentTemperatureC": Property.ROOM_OUT_WATER_CURRENT_TEMPERATURE_C,
                    "outWaterCurrentTemperatureF": Property.ROOM_OUT_WATER_CURRENT_TEMPERATURE_F,
                    "inWaterCurrentTemperatureC": Property.ROOM_IN_WATER_CURRENT_TEMPERATURE_C,
                    "inWaterCurrentTemperatureF": Property.ROOM_IN_WATER_CURRENT_TEMPERATURE_F,
                    "targetTemperatureC": Property.ROOM_TARGET_TEMPERATURE_C,
                    "targetTemperatureF": Property.ROOM_TARGET_TEMPERATURE_F,
                    "airCoolTargetTemperatureC": Property.ROOM_AIR_COOL_TARGET_TEMPERATURE_C,
                    "airCoolTargetTemperatureF": Property.ROOM_AIR_COOL_TARGET_TEMPERATURE_F,
                    "airHeatTargetTemperatureC": Property.ROOM_AIR_HEAT_TARGET_TEMPERATURE_C,
                    "airHeatTargetTemperatureF": Property.ROOM_AIR_HEAT_TARGET_TEMPERATURE_F,
                    "waterCoolTargetTemperatureC": Property.ROOM_WATER_COOL_TARGET_TEMPERATURE_C,
                    "waterCoolTargetTemperatureF": Property.ROOM_WATER_COOL_TARGET_TEMPERATURE_F,
                    "waterHeatTargetTemperatureC": Property.ROOM_WATER_HEAT_TARGET_TEMPERATURE_C,
                    "waterHeatTargetTemperatureF": Property.ROOM_WATER_HEAT_TARGET_TEMPERATURE_F,
                    "airHeatMaxTemperatureC": Property.ROOM_AIR_HEAT_MAX_TEMPERATURE_C,
                    "airHeatMaxTemperatureF": Property.ROOM_AIR_HEAT_MAX_TEMPERATURE_F,
                    "airHeatMinTemperatureC": Property.ROOM_AIR_HEAT_MIN_TEMPERATURE_C,
                    "airHeatMinTemperatureF": Property.ROOM_AIR_HEAT_MIN_TEMPERATURE_F,
                    "airCoolMaxTemperatureC": Property.ROOM_AIR_COOL_MAX_TEMPERATURE_C,
                    "airCoolMaxTemperatureF": Property.ROOM_AIR_COOL_MAX_TEMPERATURE_F,
                    "airCoolMinTemperatureC": Property.ROOM_AIR_COOL_MIN_TEMPERATURE_C,
                    "airCoolMinTemperatureF": Property.ROOM_AIR_COOL_MIN_TEMPERATURE_F,
                    "waterHeatMaxTemperatureC": Property.ROOM_WATER_HEAT_MAX_TEMPERATURE_C,
                    "waterHeatMaxTemperatureF": Property.ROOM_WATER_HEAT_MAX_TEMPERATURE_F,
                    "waterHeatMinTemperatureC": Property.ROOM_WATER_HEAT_MIN_TEMPERATURE_C,
                    "waterHeatMinTemperatureF": Property.ROOM_WATER_HEAT_MIN_TEMPERATURE_F,
                    "waterCoolMaxTemperatureC": Property.ROOM_WATER_COOL_MAX_TEMPERATURE_C,
                    "waterCoolMaxTemperatureF": Property.ROOM_WATER_COOL_MAX_TEMPERATURE_F,
                    "waterCoolMinTemperatureC": Property.ROOM_WATER_COOL_MIN_TEMPERATURE_C,
                    "waterCoolMinTemperatureF": Property.ROOM_WATER_COOL_MIN_TEMPERATURE_F,
                    "unit": Property.ROOM_TEMPERATURE_UNIT,
                },
            },
            custom_resources=["hotWaterTemperatureInUnits", "roomTemperatureInUnits"],
        )

    def check_attribute_writable(self, prop_attr: Property) -> bool:
        return (
            prop_attr in [Property.HOT_WATER_TEMPERATURE_UNIT, Property.ROOM_TEMPERATURE_UNIT]
            or self._get_prop_attr(prop_attr)[WRITABILITY]
        )

    def _get_attribute_payload(self, attribute: Property, value: str | int) -> dict:
        for resource, props in self._PROFILE.items():
            for prop_key, prop_attr in props.items():
                if prop_attr == attribute:
                    return (
                        {resource: {prop_key: value}}
                        if prop_key[-1:] not in ["C", "F"]
                        else {resource: {prop_key[:-1]: value}}
                    )

    def _generate_custom_resource_properties(
        self, resource_key: str, resource_property: dict | list, props: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        # pylint: disable=unused-argument
        readable_props = []
        writable_props = []

        if resource_key not in self._CUSTOM_RESOURCES:
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

    def _set_custom_resources(
        self,
        prop_key: str,
        attribute: str,
        resource_status: dict[str, str] | list[dict[str, str]],
        is_updated: bool = False,
    ) -> bool:
        for temperature_status in resource_status:
            unit = temperature_status.get("unit")
            if attribute in [Property.HOT_WATER_TEMPERATURE_UNIT, Property.ROOM_TEMPERATURE_UNIT]:
                if unit == "C":
                    self._set_status_attr(attribute, unit)
            elif attribute[-1:].upper() == unit:
                for temperature_map in [
                    self.profiles._PROFILE["hotWaterTemperatureInUnits"],
                    self.profiles._PROFILE["roomTemperatureInUnits"],
                ]:
                    if attribute in temperature_map.values():
                        _prop_key = list(temperature_map.keys())[list(temperature_map.values()).index(attribute)]
                        break

                if not _prop_key:
                    _attribute_value = None
                elif _prop_key[:-1] not in temperature_status and is_updated:
                    continue
                else:
                    _attribute_value = temperature_status.get(_prop_key[:-1])
                self._set_status_attr(attribute, _attribute_value)
        return True

    async def set_boiler_operation_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.BOILER_OPERATION_MODE, mode)

    async def set_current_job_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.CURRENT_JOB_MODE, mode)

    async def set_hot_water_mode(self, mode: str) -> dict | None:
        return await self.do_enum_attribute_command(Property.HOT_WATER_MODE, mode)

    async def _set_hot_water_target_temperature(self, temperature: int, unit: str) -> dict | None:
        property_map = {
            "C": Property.HOT_WATER_TARGET_TEMPERATURE_C,
            "F": Property.HOT_WATER_TARGET_TEMPERATURE_F,
        }
        return await self.do_multi_attribute_command(
            {
                property_map[unit]: temperature,
                Property.HOT_WATER_TEMPERATURE_UNIT: unit,
            }
        )

    async def set_hot_water_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_hot_water_target_temperature(temperature, "C")

    async def set_hot_water_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_hot_water_target_temperature(temperature, "F")

    async def _set_room_air_cool_target_temperature(self, temperature: int, unit: str) -> dict | None:
        property_map = {
            "C": Property.ROOM_AIR_COOL_TARGET_TEMPERATURE_C,
            "F": Property.ROOM_AIR_COOL_TARGET_TEMPERATURE_F,
        }
        return await self.do_multi_attribute_command(
            {
                property_map[unit]: temperature,
                Property.ROOM_TEMPERATURE_UNIT: unit,
            }
        )

    async def set_room_air_cool_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_room_air_cool_target_temperature(temperature, "C")

    async def set_room_air_cool_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_room_air_cool_target_temperature(temperature, "F")

    async def _set_room_air_heat_target_temperature(self, temperature: int, unit: str) -> dict | None:
        property_map = {
            "C": Property.ROOM_AIR_HEAT_TARGET_TEMPERATURE_C,
            "F": Property.ROOM_AIR_HEAT_TARGET_TEMPERATURE_F,
        }
        return await self.do_multi_attribute_command(
            {
                property_map[unit]: temperature,
                Property.ROOM_TEMPERATURE_UNIT: unit,
            }
        )

    async def set_room_air_heat_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_room_air_heat_target_temperature(temperature, "C")

    async def set_room_air_heat_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_room_air_heat_target_temperature(temperature, "F")

    async def _set_room_water_cool_target_temperature(self, temperature: int, unit: str) -> dict | None:
        property_map = {
            "C": Property.ROOM_WATER_COOL_TARGET_TEMPERATURE_C,
            "F": Property.ROOM_WATER_COOL_TARGET_TEMPERATURE_F,
        }
        return await self.do_multi_attribute_command(
            {
                property_map[unit]: temperature,
                Property.ROOM_TEMPERATURE_UNIT: unit,
            }
        )

    async def set_room_water_cool_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_room_water_cool_target_temperature(temperature, "C")

    async def set_room_water_cool_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_room_water_cool_target_temperature(temperature, "F")

    async def _set_room_water_heat_target_temperature(self, temperature: int, unit: str) -> dict | None:
        property_map = {
            "C": Property.ROOM_WATER_HEAT_TARGET_TEMPERATURE_C,
            "F": Property.ROOM_WATER_HEAT_TARGET_TEMPERATURE_F,
        }
        return await self.do_multi_attribute_command(
            {
                property_map[unit]: temperature,
                Property.ROOM_TEMPERATURE_UNIT: unit,
            }
        )

    async def set_room_water_heat_target_temperature_c(self, temperature: int) -> dict | None:
        return await self._set_room_water_heat_target_temperature(temperature, "C")

    async def set_room_water_heat_target_temperature_f(self, temperature: int) -> dict | None:
        return await self._set_room_water_heat_target_temperature(temperature, "F")

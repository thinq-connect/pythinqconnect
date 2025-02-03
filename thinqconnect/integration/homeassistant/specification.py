"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

# Specifications for entity setup.

from abc import ABC
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import time
from enum import StrEnum, auto

from thinqconnect import (
    AirConditionerDevice,
    AirPurifierDevice,
    AirPurifierFanDevice,
    ConnectBaseDevice,
    DeviceType,
    HumidifierDevice,
    RobotCleanerDevice,
)
from thinqconnect.devices.const import Property as ThinQProperty

from .property import PropertyOption


class ThinQPropertyEx(StrEnum):
    """Property definitions that extends the existing thinq properties."""

    CURRENT_JOB_MODE_STICK_CLEANER = auto()
    HUMIDITY_WARM_MODE = auto()
    ERROR = auto()
    NOTIFICATION = auto()
    ROOM_CURRENT_TEMPERATURE = auto()
    ROOM_TARGET_TEMPERATURE = auto()
    ROOM_AIR_CURRENT_TEMPERATURE = auto()
    ROOM_AIR_COOL_TARGET_TEMPERATURE = auto()
    ROOM_AIR_HEAT_TARGET_TEMPERATURE = auto()
    ROOM_AIR_HEAT_MAX_TEMPERATURE = auto()
    ROOM_AIR_HEAT_MIN_TEMPERATURE = auto()
    ROOM_AIR_COOL_MAX_TEMPERATURE = auto()
    ROOM_AIR_COOL_MIN_TEMPERATURE = auto()
    ROOM_IN_WATER_CURRENT_TEMPERATURE = auto()
    ROOM_OUT_WATER_CURRENT_TEMPERATURE = auto()
    ROOM_WATER_COOL_TARGET_TEMPERATURE = auto()
    ROOM_WATER_HEAT_TARGET_TEMPERATURE = auto()
    ROOM_WATER_HEAT_MAX_TEMPERATURE = auto()
    ROOM_WATER_HEAT_MIN_TEMPERATURE = auto()
    ROOM_WATER_COOL_MAX_TEMPERATURE = auto()
    ROOM_WATER_COOL_MIN_TEMPERATURE = auto()
    HOT_WATER_CURRENT_TEMPERATURE = auto()
    HOT_WATER_TARGET_TEMPERATURE = auto()
    HOT_WATER_MAX_TEMPERATURE = auto()
    HOT_WATER_MIN_TEMPERATURE = auto()


class ExtendedProperty(StrEnum):
    """Property definitions for complex entities."""

    CLIMATE_AIR_CONDITIONER = auto()
    CLIMATE_SYSTEM_BOILER = auto()
    FAN = auto()
    VACUUM = auto()
    WATER_BOILER = auto()
    WATER_HEATER = auto()


class TimerProperty(StrEnum):
    """Property definitions that combines timer properties."""

    ABSOLUTE_TO_START = auto()
    ABSOLUTE_TO_STOP = auto()
    LIGHT_END = auto()
    LIGHT_START = auto()
    RELATIVE_TO_START = auto()
    RELATIVE_TO_START_WM = auto()
    RELATIVE_TO_STOP = auto()
    RELATIVE_TO_STOP_WM = auto()
    RELATIVE_HOUR_TO_START_WM = auto()
    RELATIVE_HOUR_TO_STOP_WM = auto()
    SLEEP_TIMER_RELATIVE_TO_STOP = auto()
    REMAIN = auto()
    RUNNING = auto()
    TARGET = auto()
    TIMER = auto()
    TOTAL = auto()


@dataclass(kw_only=True, frozen=True)
class PropertyStateSpec(ABC):
    """The base specification."""

    target_devices: tuple[str, ...] = field(default_factory=tuple)
    preferred_unit_devices: tuple[str, ...] = field(default_factory=tuple)

    def is_target_device(self, device_type: str) -> bool:
        """Check whether the given device should use specification or not."""
        return not self.target_devices or device_type in self.target_devices

    def use_preferred_unit(self, device_type: str) -> bool:
        """Check whether to use the preferred unit on the specified device or not."""
        return device_type in self.preferred_unit_devices


@dataclass(kw_only=True, frozen=True)
class WaterHeaterPropertyStateSpec(PropertyStateSpec):
    """A specification to create water_heater property state."""

    power_keys: tuple[str, ...] = field(default_factory=tuple)
    job_mode_key: str | None = None
    current_temp_key: str
    target_temp_key: str
    target_temp_min_key: str | None = None
    target_temp_max_key: str | None = None
    unit_key: str | None = None


@dataclass(kw_only=True, frozen=True)
class ClimateTemperatureSpec:
    """A specification for climate temperature control."""

    current_temp_key: str
    target_temp_key_map: dict[str, str]
    target_temp_low_key_map: dict[str, str] = field(default_factory=dict)
    target_temp_low_min_key: str | None = None
    target_temp_low_max_key: str | None = None
    target_temp_high_key_map: dict[str, str] = field(default_factory=dict)
    target_temp_high_min_key: str | None = None
    target_temp_high_max_key: str | None = None
    unit_key: str | None = None


@dataclass(kw_only=True, frozen=True)
class ClimatePropertyStateSpec(PropertyStateSpec):
    """A specification to create climate property state."""

    power_key: str
    hvac_mode_key: str
    default_temperature_preset: str
    temperature_preset_key: str | None = None
    temperature_sub_preset_key: str | None = None
    temperature_specs: dict[str, ClimateTemperatureSpec]
    support_temperature_range: bool = False
    fan_mode_keys: tuple[str, ...] = field(default_factory=tuple)
    humidity_key: str | None = None
    swing_mode_key: str | None = None
    swing_horizontal_mode_key: str | None = None


CLIMATE_STATE_MAP = {
    ExtendedProperty.CLIMATE_AIR_CONDITIONER: ClimatePropertyStateSpec(
        power_key=ThinQProperty.AIR_CON_OPERATION_MODE,
        hvac_mode_key=ThinQProperty.CURRENT_JOB_MODE,
        default_temperature_preset="false",
        temperature_preset_key=ThinQProperty.TWO_SET_ENABLED,
        temperature_specs={
            "false": ClimateTemperatureSpec(
                current_temp_key=ThinQProperty.CURRENT_TEMPERATURE,
                target_temp_key_map={
                    "cool": ThinQProperty.TARGET_TEMPERATURE,
                    "heat": ThinQProperty.TARGET_TEMPERATURE,
                },
                target_temp_low_key_map={"heat": ThinQProperty.HEAT_TARGET_TEMPERATURE},
                target_temp_high_key_map={
                    "cool": ThinQProperty.COOL_TARGET_TEMPERATURE
                },
                unit_key=ThinQProperty.TEMPERATURE_UNIT,
            ),
            "true": ClimateTemperatureSpec(
                current_temp_key=ThinQProperty.CURRENT_TEMPERATURE,
                target_temp_key_map={
                    "cool": ThinQProperty.TWO_SET_COOL_TARGET_TEMPERATURE,
                    "heat": ThinQProperty.TWO_SET_HEAT_TARGET_TEMPERATURE,
                },
                target_temp_low_key_map={
                    "auto": ThinQProperty.TWO_SET_HEAT_TARGET_TEMPERATURE,
                    "heat": ThinQProperty.TWO_SET_HEAT_TARGET_TEMPERATURE,
                },
                target_temp_high_key_map={
                    "auto": ThinQProperty.TWO_SET_COOL_TARGET_TEMPERATURE,
                    "cool": ThinQProperty.TWO_SET_COOL_TARGET_TEMPERATURE,
                },
                unit_key=ThinQProperty.TWO_SET_TEMPERATURE_UNIT,
            ),
        },
        support_temperature_range=True,
        fan_mode_keys=(ThinQProperty.WIND_STEP, ThinQProperty.WIND_STRENGTH),
        humidity_key=ThinQProperty.HUMIDITY,
        swing_mode_key=ThinQProperty.WIND_ROTATE_UP_DOWN,
        swing_horizontal_mode_key=ThinQProperty.WIND_ROTATE_LEFT_RIGHT,
    ),
    ExtendedProperty.CLIMATE_SYSTEM_BOILER: ClimatePropertyStateSpec(
        power_key=ThinQProperty.BOILER_OPERATION_MODE,
        hvac_mode_key=ThinQProperty.CURRENT_JOB_MODE,
        temperature_preset_key=ThinQProperty.ROOM_TEMP_MODE,
        temperature_sub_preset_key=ThinQProperty.ROOM_WATER_MODE,
        default_temperature_preset="air",
        temperature_specs={
            "air": ClimateTemperatureSpec(
                current_temp_key=ThinQPropertyEx.ROOM_AIR_CURRENT_TEMPERATURE,
                target_temp_key_map={
                    "cool": ThinQPropertyEx.ROOM_TARGET_TEMPERATURE,
                    "heat": ThinQPropertyEx.ROOM_TARGET_TEMPERATURE,
                },
                target_temp_low_key_map={
                    "heat": ThinQPropertyEx.ROOM_AIR_HEAT_TARGET_TEMPERATURE
                },
                target_temp_low_min_key=ThinQPropertyEx.ROOM_AIR_HEAT_MIN_TEMPERATURE,
                target_temp_low_max_key=ThinQPropertyEx.ROOM_AIR_HEAT_MAX_TEMPERATURE,
                target_temp_high_key_map={
                    "cool": ThinQPropertyEx.ROOM_AIR_COOL_TARGET_TEMPERATURE
                },
                target_temp_high_min_key=ThinQPropertyEx.ROOM_AIR_COOL_MIN_TEMPERATURE,
                target_temp_high_max_key=ThinQPropertyEx.ROOM_AIR_COOL_MAX_TEMPERATURE,
                unit_key=ThinQProperty.ROOM_TEMPERATURE_UNIT,
            ),
            "water/in_water": ClimateTemperatureSpec(
                current_temp_key=ThinQPropertyEx.ROOM_IN_WATER_CURRENT_TEMPERATURE,
                target_temp_key_map={
                    "cool": ThinQPropertyEx.ROOM_TARGET_TEMPERATURE,
                    "heat": ThinQPropertyEx.ROOM_TARGET_TEMPERATURE,
                },
                target_temp_low_key_map={
                    "heat": ThinQPropertyEx.ROOM_WATER_HEAT_TARGET_TEMPERATURE
                },
                target_temp_low_min_key=ThinQPropertyEx.ROOM_WATER_HEAT_MIN_TEMPERATURE,
                target_temp_low_max_key=ThinQPropertyEx.ROOM_WATER_HEAT_MAX_TEMPERATURE,
                target_temp_high_key_map={
                    "cool": ThinQPropertyEx.ROOM_WATER_COOL_TARGET_TEMPERATURE
                },
                target_temp_high_min_key=ThinQPropertyEx.ROOM_WATER_COOL_MIN_TEMPERATURE,
                target_temp_high_max_key=ThinQPropertyEx.ROOM_WATER_COOL_MAX_TEMPERATURE,
                unit_key=ThinQProperty.ROOM_TEMPERATURE_UNIT,
            ),
            "water/out_water": ClimateTemperatureSpec(
                current_temp_key=ThinQPropertyEx.ROOM_OUT_WATER_CURRENT_TEMPERATURE,
                target_temp_key_map={
                    "cool": ThinQPropertyEx.ROOM_TARGET_TEMPERATURE,
                    "heat": ThinQPropertyEx.ROOM_TARGET_TEMPERATURE,
                },
                target_temp_low_key_map={
                    "heat": ThinQPropertyEx.ROOM_WATER_HEAT_TARGET_TEMPERATURE
                },
                target_temp_low_min_key=ThinQPropertyEx.ROOM_WATER_HEAT_MIN_TEMPERATURE,
                target_temp_low_max_key=ThinQPropertyEx.ROOM_WATER_HEAT_MAX_TEMPERATURE,
                target_temp_high_key_map={
                    "cool": ThinQPropertyEx.ROOM_WATER_COOL_TARGET_TEMPERATURE
                },
                target_temp_high_min_key=ThinQPropertyEx.ROOM_WATER_COOL_MIN_TEMPERATURE,
                target_temp_high_max_key=ThinQPropertyEx.ROOM_WATER_COOL_MAX_TEMPERATURE,
                unit_key=ThinQProperty.ROOM_TEMPERATURE_UNIT,
            ),
        },
    ),
}

WATER_HEATER_STATE_MAP = {
    ExtendedProperty.WATER_BOILER: WaterHeaterPropertyStateSpec(
        power_keys=(ThinQProperty.HOT_WATER_MODE, ThinQProperty.BOILER_OPERATION_MODE),
        job_mode_key=None,
        current_temp_key=ThinQPropertyEx.HOT_WATER_CURRENT_TEMPERATURE,
        target_temp_key=ThinQPropertyEx.HOT_WATER_TARGET_TEMPERATURE,
        target_temp_min_key=ThinQPropertyEx.HOT_WATER_MIN_TEMPERATURE,
        target_temp_max_key=ThinQPropertyEx.HOT_WATER_MAX_TEMPERATURE,
        unit_key=ThinQProperty.HOT_WATER_TEMPERATURE_UNIT,
    ),
    ExtendedProperty.WATER_HEATER: WaterHeaterPropertyStateSpec(
        power_keys=(ThinQProperty.WATER_HEATER_OPERATION_MODE,),
        job_mode_key=ThinQProperty.CURRENT_JOB_MODE,
        current_temp_key=ThinQProperty.CURRENT_TEMPERATURE,
        target_temp_key=ThinQProperty.TARGET_TEMPERATURE,
        unit_key=ThinQProperty.TEMPERATURE_UNIT,
    ),
}


@dataclass(kw_only=True, frozen=True)
class ExtendedPropertyStateSpec(PropertyStateSpec):
    """A specification to create fan, vacuum property state."""

    # vacuum
    state_key: str | None = None
    battery_keys: tuple[str, ...] = field(default_factory=tuple)
    operation_mode_key: str | None = None
    # fan
    power_key: str | None = None
    fan_mode_key: str | None = None


EXTENDED_STATE_MAP = {
    ExtendedProperty.VACUUM: ExtendedPropertyStateSpec(
        state_key=ThinQProperty.CURRENT_STATE,
        battery_keys=(ThinQProperty.BATTERY_PERCENT, ThinQProperty.BATTERY_LEVEL),
        operation_mode_key=ThinQProperty.CLEAN_OPERATION_MODE,
    ),
    ExtendedProperty.FAN: ExtendedPropertyStateSpec(
        power_key=ThinQProperty.CEILING_FAN_OPERATION_MODE,
        fan_mode_key=ThinQProperty.WIND_STRENGTH,
    ),
}


@dataclass(kw_only=True, frozen=True)
class TimerPropertyStateSpec(PropertyStateSpec):
    """A specification to create timer property state."""

    hour_key: str | None = None
    minute_key: str | None = None
    second_key: str | None = None
    time_format: str | None = None
    setter: Callable[[ConnectBaseDevice, time | None], Awaitable[None]] | None = None


async def set_absolute_time_to_start(
    api: ConnectBaseDevice, value: time | None
) -> None:
    """Set an absolute start timer."""
    if isinstance(
        api,
        (
            AirConditionerDevice,
            AirPurifierFanDevice,
            AirPurifierDevice,
            HumidifierDevice,
            RobotCleanerDevice,
        ),
    ):
        if value:
            await api.set_absolute_time_to_start(value.hour, value.minute)
        else:
            await api.set_absolute_time_to_start(-1, -1)


async def set_absolute_time_to_stop(api: ConnectBaseDevice, value: time | None) -> None:
    """Set an absolute stop timer."""
    if isinstance(
        api,
        (
            AirConditionerDevice,
            AirPurifierFanDevice,
            AirPurifierDevice,
            HumidifierDevice,
        ),
    ):
        if value:
            await api.set_absolute_time_to_stop(value.hour, value.minute)
        else:
            await api.set_absolute_time_to_stop(-1, -1)


TIMER_STATE_MAP = {
    TimerProperty.ABSOLUTE_TO_START: TimerPropertyStateSpec(
        hour_key=ThinQProperty.ABSOLUTE_HOUR_TO_START,
        minute_key=ThinQProperty.ABSOLUTE_MINUTE_TO_START,
        setter=set_absolute_time_to_start,
    ),
    TimerProperty.ABSOLUTE_TO_STOP: TimerPropertyStateSpec(
        hour_key=ThinQProperty.ABSOLUTE_HOUR_TO_STOP,
        minute_key=ThinQProperty.ABSOLUTE_MINUTE_TO_STOP,
        setter=set_absolute_time_to_stop,
    ),
    TimerProperty.LIGHT_END: TimerPropertyStateSpec(
        hour_key=ThinQProperty.END_HOUR,
        minute_key=ThinQProperty.END_MINUTE,
        time_format="%I:%M %p",
    ),
    TimerProperty.LIGHT_START: TimerPropertyStateSpec(
        hour_key=ThinQProperty.START_HOUR,
        minute_key=ThinQProperty.START_MINUTE,
        time_format="%I:%M %p",
    ),
    TimerProperty.RELATIVE_TO_START: TimerPropertyStateSpec(
        hour_key=ThinQProperty.RELATIVE_HOUR_TO_START,
        minute_key=ThinQProperty.RELATIVE_MINUTE_TO_START,
    ),
    TimerProperty.RELATIVE_TO_START_WM: TimerPropertyStateSpec(
        hour_key=ThinQProperty.RELATIVE_HOUR_TO_START,
        minute_key=ThinQProperty.RELATIVE_MINUTE_TO_START,
    ),
    TimerProperty.RELATIVE_TO_STOP: TimerPropertyStateSpec(
        hour_key=ThinQProperty.RELATIVE_HOUR_TO_STOP,
        minute_key=ThinQProperty.RELATIVE_MINUTE_TO_STOP,
    ),
    TimerProperty.RELATIVE_TO_STOP_WM: TimerPropertyStateSpec(
        hour_key=ThinQProperty.RELATIVE_HOUR_TO_STOP,
        minute_key=ThinQProperty.RELATIVE_MINUTE_TO_STOP,
    ),
    TimerProperty.SLEEP_TIMER_RELATIVE_TO_STOP: TimerPropertyStateSpec(
        hour_key=ThinQProperty.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP,
        minute_key=ThinQProperty.SLEEP_TIMER_RELATIVE_MINUTE_TO_STOP,
    ),
    TimerProperty.REMAIN: TimerPropertyStateSpec(
        hour_key=ThinQProperty.REMAIN_HOUR,
        minute_key=ThinQProperty.REMAIN_MINUTE,
        second_key=ThinQProperty.REMAIN_SECOND,
    ),
    TimerProperty.RUNNING: TimerPropertyStateSpec(
        hour_key=ThinQProperty.RUNNING_HOUR,
        minute_key=ThinQProperty.RUNNING_MINUTE,
    ),
    TimerProperty.TARGET: TimerPropertyStateSpec(
        hour_key=ThinQProperty.TARGET_HOUR,
        minute_key=ThinQProperty.TARGET_MINUTE,
    ),
    TimerProperty.TIMER: TimerPropertyStateSpec(
        hour_key=ThinQProperty.TIMER_HOUR,
        minute_key=ThinQProperty.TIMER_MINUTE,
    ),
    TimerProperty.TOTAL: TimerPropertyStateSpec(
        hour_key=ThinQProperty.TOTAL_HOUR,
        minute_key=ThinQProperty.TOTAL_MINUTE,
    ),
}


@dataclass(kw_only=True, frozen=True)
class SelectivePropertyStateSpec(PropertyStateSpec):
    """A specification to create selective property state."""

    origin_key: str
    selective_keys: tuple[str, ...] = field(default_factory=tuple)
    target_device: tuple[str, ...] = field(default_factory=tuple)


SELECTIVE_STATE_MAP = {
    ThinQProperty.BATTERY_PERCENT: SelectivePropertyStateSpec(
        origin_key=ThinQProperty.BATTERY_PERCENT,
        selective_keys=(
            ThinQProperty.BATTERY_PERCENT,
            ThinQProperty.BATTERY_LEVEL,
        ),
    ),
}


@dataclass(kw_only=True, frozen=True)
class TemperaturePropertyStateSpec(PropertyStateSpec):
    """A specification to create temperature property state."""

    origin_key: str
    unit_key: str | None = None


TEMPERATURE_STATE_MAP = {
    ThinQProperty.TARGET_TEMPERATURE: TemperaturePropertyStateSpec(
        origin_key=ThinQProperty.TARGET_TEMPERATURE,
        unit_key=ThinQProperty.TEMPERATURE_UNIT,
        preferred_unit_devices=(DeviceType.WATER_HEATER,),
    ),
    ThinQProperty.CURRENT_TEMPERATURE: TemperaturePropertyStateSpec(
        origin_key=ThinQProperty.CURRENT_TEMPERATURE,
        unit_key=ThinQProperty.TEMPERATURE_UNIT,
        preferred_unit_devices=(DeviceType.WATER_HEATER,),
    ),
    ThinQPropertyEx.ROOM_AIR_CURRENT_TEMPERATURE: TemperaturePropertyStateSpec(
        origin_key=ThinQPropertyEx.ROOM_AIR_CURRENT_TEMPERATURE,
        unit_key=ThinQProperty.TEMPERATURE_UNIT,
        preferred_unit_devices=(DeviceType.SYSTEM_BOILER,),
    ),
    ThinQPropertyEx.ROOM_IN_WATER_CURRENT_TEMPERATURE: TemperaturePropertyStateSpec(
        origin_key=ThinQPropertyEx.ROOM_IN_WATER_CURRENT_TEMPERATURE,
        unit_key=ThinQProperty.TEMPERATURE_UNIT,
        preferred_unit_devices=(DeviceType.SYSTEM_BOILER,),
    ),
    ThinQPropertyEx.ROOM_OUT_WATER_CURRENT_TEMPERATURE: TemperaturePropertyStateSpec(
        origin_key=ThinQPropertyEx.ROOM_OUT_WATER_CURRENT_TEMPERATURE,
        unit_key=ThinQProperty.TEMPERATURE_UNIT,
        preferred_unit_devices=(DeviceType.SYSTEM_BOILER,),
    ),
}


async def set_sleep_timer_relative_hour_to_stop(
    device: ConnectBaseDevice, value: int
) -> None:
    """Set a relative stop sleep timer with hour."""
    if isinstance(
        device, (AirConditionerDevice, AirPurifierFanDevice, HumidifierDevice)
    ):
        await device.set_sleep_timer_relative_time_to_stop(hour=value, minute=0)


PROPERTY_OPTION_MAP = {
    ThinQProperty.SLEEP_TIMER_RELATIVE_HOUR_TO_STOP: PropertyOption(
        alt_setter=set_sleep_timer_relative_hour_to_stop
    )
}

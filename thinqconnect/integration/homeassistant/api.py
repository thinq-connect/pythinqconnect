"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

# The extended api interface for Home Assistant.
from __future__ import annotations

import asyncio
import logging
from datetime import time
from enum import StrEnum, auto
from typing import Any, Final

from thinqconnect import (
    AirConditionerDevice,
    AirPurifierDevice,
    AirPurifierFanDevice,
    CeilingFanDevice,
    ConnectBaseDevice,
    CooktopDevice,
    DehumidifierDevice,
    DeviceType,
    DishWasherDevice,
    DryerDevice,
    HomeBrewDevice,
    HoodDevice,
    HumidifierDevice,
    KimchiRefrigeratorDevice,
    MicrowaveOvenDevice,
    OvenDevice,
    PlantCultivatorDevice,
    RefrigeratorDevice,
    RobotCleanerDevice,
    StickCleanerDevice,
    StylerDevice,
    SystemBoilerDevice,
    ThinQApi,
    ThinQAPIException,
    WashcomboMainDevice,
    WashcomboMiniDevice,
    WasherDevice,
    WashtowerDevice,
    WashtowerDryerDevice,
    WashtowerWasherDevice,
    WaterHeaterDevice,
    WaterPurifierDevice,
    WineCellarDevice,
)
from thinqconnect.devices.const import Location, Property as ThinQProperty

from .property import (
    ActiveMode,
    ClimatePropertyState,
    ClimatePropertyStateSpec,
    ClimateTemperatureSpec,
    ExtendedPropertyState,
    ExtendedPropertyStateSpec,
    PropertyHolder,
    PropertyOption,
    PropertyState,
    SelectivePropertyState,
    SelectivePropertyStateSpec,
    SinglePropertyState,
    TimerPropertyState,
    TimerPropertyStateSpec,
)

DEVICE_TYPE_API_MAP: Final = {
    DeviceType.AIR_CONDITIONER: AirConditionerDevice,
    DeviceType.AIR_PURIFIER_FAN: AirPurifierFanDevice,
    DeviceType.AIR_PURIFIER: AirPurifierDevice,
    DeviceType.CEILING_FAN: CeilingFanDevice,
    DeviceType.COOKTOP: CooktopDevice,
    DeviceType.DEHUMIDIFIER: DehumidifierDevice,
    DeviceType.DISH_WASHER: DishWasherDevice,
    DeviceType.DRYER: DryerDevice,
    DeviceType.HOME_BREW: HomeBrewDevice,
    DeviceType.HOOD: HoodDevice,
    DeviceType.HUMIDIFIER: HumidifierDevice,
    DeviceType.KIMCHI_REFRIGERATOR: KimchiRefrigeratorDevice,
    DeviceType.MICROWAVE_OVEN: MicrowaveOvenDevice,
    DeviceType.OVEN: OvenDevice,
    DeviceType.PLANT_CULTIVATOR: PlantCultivatorDevice,
    DeviceType.REFRIGERATOR: RefrigeratorDevice,
    DeviceType.ROBOT_CLEANER: RobotCleanerDevice,
    DeviceType.STICK_CLEANER: StickCleanerDevice,
    DeviceType.STYLER: StylerDevice,
    DeviceType.SYSTEM_BOILER: SystemBoilerDevice,
    DeviceType.WASHER: WasherDevice,
    DeviceType.WASHCOMBO_MAIN: WashcomboMainDevice,
    DeviceType.WASHCOMBO_MINI: WashcomboMiniDevice,
    DeviceType.WASHTOWER_DRYER: WashtowerDryerDevice,
    DeviceType.WASHTOWER: WashtowerDevice,
    DeviceType.WASHTOWER_WASHER: WashtowerWasherDevice,
    DeviceType.WATER_HEATER: WaterHeaterDevice,
    DeviceType.WATER_PURIFIER: WaterPurifierDevice,
    DeviceType.WINE_CELLAR: WineCellarDevice,
}

_LOGGER = logging.getLogger(__name__)


class ThinQPropertyEx(StrEnum):
    """The extended property definitions for common."""

    CURRENT_JOB_MODE_STICK_CLEANER = auto()
    HUMIDITY_WARM_MODE = auto()
    ERROR = auto()
    NOTIFICATION = auto()


class ExtendedProperty(StrEnum):
    """The extended property definitions for climate."""

    CLIMATE_AIR_CONDITIONER = auto()
    CLIMATE_SYSTEM_BOILER = auto()
    FAN = auto()
    VACUUM = auto()


CLIMATE_STATE_MAP = {
    ExtendedProperty.CLIMATE_AIR_CONDITIONER: ClimatePropertyStateSpec(
        power_key=ThinQProperty.AIR_CON_OPERATION_MODE,
        hvac_mode_key=ThinQProperty.CURRENT_JOB_MODE,
        temperature_specs=ClimateTemperatureSpec(
            current_temp_key=ThinQProperty.CURRENT_TEMPERATURE,
            target_temp_key=ThinQProperty.TARGET_TEMPERATURE,
            target_temp_low_key=ThinQProperty.COOL_TARGET_TEMPERATURE,
            target_temp_high_key=ThinQProperty.HEAT_TARGET_TEMPERATURE,
            unit_key=ThinQProperty.TEMPERATURE_UNIT,
        ),
        temperature_range_specs=ClimateTemperatureSpec(
            current_temp_key=ThinQProperty.TWO_SET_CURRENT_TEMPERATURE,
            target_temp_low_key=ThinQProperty.TWO_SET_HEAT_TARGET_TEMPERATURE,
            target_temp_high_key=ThinQProperty.TWO_SET_COOL_TARGET_TEMPERATURE,
            unit_key=ThinQProperty.TWO_SET_TEMPERATURE_UNIT,
        ),
        fan_mode_keys=(ThinQProperty.WIND_STEP, ThinQProperty.WIND_STRENGTH),
        humidity_key=ThinQProperty.HUMIDITY,
    ),
    ExtendedProperty.CLIMATE_SYSTEM_BOILER: ClimatePropertyStateSpec(
        power_key=ThinQProperty.BOILER_OPERATION_MODE,
        hvac_mode_key=ThinQProperty.CURRENT_JOB_MODE,
        temperature_specs=ClimateTemperatureSpec(
            current_temp_key=ThinQProperty.CURRENT_TEMPERATURE,
            target_temp_key=ThinQProperty.TARGET_TEMPERATURE,
            target_temp_low_key=ThinQProperty.COOL_TARGET_TEMPERATURE,
            target_temp_high_key=ThinQProperty.HEAT_TARGET_TEMPERATURE,
            unit_key=ThinQProperty.TEMPERATURE_UNIT,
        ),
    ),
}

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


class TimerProperty(StrEnum):
    """The extended property definitions for timer."""

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

SELECTIVE_STATE_MAP = {
    ThinQProperty.TARGET_TEMPERATURE: SelectivePropertyStateSpec(
        origin_key=ThinQProperty.TARGET_TEMPERATURE,
        selective_keys=(
            ThinQProperty.TARGET_TEMPERATURE_C,
            ThinQProperty.TARGET_TEMPERATURE_F,
        ),
    ),
    ThinQProperty.BATTERY_PERCENT: SelectivePropertyStateSpec(
        origin_key=ThinQProperty.BATTERY_PERCENT,
        selective_keys=(
            ThinQProperty.BATTERY_PERCENT,
            ThinQProperty.BATTERY_LEVEL,
        ),
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


class HABridge:
    """A bridge interface that communicates with Home Assistant.

    This is an API interface that acts as a bridge for data sync between ThinQ and
    Home Assistant. It is designed to pass data in accordance with the architecture and
    entity structure of Home Assistant.
    """

    def __init__(self, device: ConnectBaseDevice, *, sub_id: str | None = None) -> None:
        """Set up a bridge."""
        self.device = device
        self.sub_id = sub_id

        self.locations: list[str | None] = [None, *list(self.device.profiles.locations)]

        # The idx map contains all identifiers in order to get property states.
        # - idx == "{key}", for non-location property.
        # - idx == "{location}_{key}", for location property.
        self.idx_map: dict[str, list] = {}

        # The property map contains all properties. The key is idx.
        self.property_map: dict[str, PropertyHolder] = {}

        # The state map contains all states. The key is idx.
        self.state_map: dict[str, PropertyState] = {}

        self._setup_properties()
        self._setup_states()

    def _setup_properties(self) -> None:
        """Set up all properties in the device. Create idx map and property map."""
        # Create holders for non-location properties.
        for key, profile in self.device.profiles.property_map.items():
            idx = self._add_idx(key)
            self.property_map[idx] = PropertyHolder(
                key,
                self.device,
                profile,
                option=PROPERTY_OPTION_MAP.get(key),
            )

        # Create holders for location properties.
        for location in self.device.profiles.locations:
            if self.sub_id is not None and self.sub_id != location:
                continue

            sub_profile = self.device.profiles.get_sub_profile(location)
            if not sub_profile:
                continue

            for key, profile in sub_profile.property_map.items():
                idx = self._add_idx(key, location)
                self.property_map[idx] = PropertyHolder(
                    key, self.device, profile, location=location
                )

    def _setup_states(self) -> None:
        """Set up states of all properties."""
        for idx, holder in self.property_map.items():
            self.state_map[idx] = SinglePropertyState(holder)

        self._setup_selective_states()
        self._setup_climate_states()
        self._setup_extended_states()
        self._setup_timer_states()

    def _setup_selective_states(self) -> None:
        """Set up optional states for selective property."""
        for key, spec in SELECTIVE_STATE_MAP.items():
            for location in self.locations:
                if (
                    selective_state := self._create_selective_state(spec, location)
                ) is not None:
                    # Note that selective state can overwrite single state.
                    idx = self._add_idx(key, location)
                    self.state_map[idx] = selective_state

    def _create_selective_state(
        self, spec: SelectivePropertyStateSpec, location: str | None
    ) -> SelectivePropertyState | None:
        """Create selective state if possible."""
        holders = [
            holder
            for key in spec.selective_keys
            if (holder := self._get_holder(key, location)) is not None
        ]
        return SelectivePropertyState(spec.origin_key, holders) if holders else None

    def _setup_climate_states(self) -> None:
        """Set up optional states for climate."""
        for key, spec in CLIMATE_STATE_MAP.items():
            for location in self.locations:
                if (
                    climate_state := self._create_climate_state(spec, location)
                ) is not None:
                    idx = self._add_idx(key, location)
                    self.state_map[idx] = climate_state

    def _create_climate_state(
        self, spec: ClimatePropertyStateSpec, location: str | None
    ) -> ClimatePropertyState | None:
        """Create climate state if possible."""
        # Power and HVAC mode are required.
        power_holder = self._get_holder(spec.power_key, location)
        hvac_mode_holder = self._get_holder(spec.hvac_mode_key, location)
        if power_holder is None or hvac_mode_holder is None:
            return None

        temp_spec = spec.temperature_specs
        temp_range_spec = spec.temperature_range_specs

        # Current temp and target temp are required.
        current_temp_holder = self._get_holder(temp_spec.current_temp_key, location)
        target_temp_holder = self._get_holder(temp_spec.target_temp_key, location)
        if current_temp_holder is None or target_temp_holder is None:
            return None

        fan_mode_holder: PropertyHolder | None = None
        for fan_mode_key in spec.fan_mode_keys:
            if (
                fan_mode_holder := self._get_holder(fan_mode_key, location)
            ) is not None:
                break

        return ClimatePropertyState(
            power_holder,
            hvac_mode_holder,
            current_temp_holder,
            target_temp_holder,
            target_temp_low_holder=self._get_holder(
                temp_spec.target_temp_low_key, location
            ),
            target_temp_high_holder=self._get_holder(
                temp_spec.target_temp_high_key, location
            ),
            unit_holder=self._get_holder(temp_spec.unit_key, location),
            current_temp_range_holder=(
                self._get_holder(temp_range_spec.current_temp_key, location)
                if temp_range_spec is not None
                else None
            ),
            target_temp_low_range_holder=(
                self._get_holder(temp_range_spec.target_temp_low_key, location)
                if temp_range_spec is not None
                else None
            ),
            target_temp_high_range_holder=(
                self._get_holder(temp_range_spec.target_temp_high_key, location)
                if temp_range_spec is not None
                else None
            ),
            unit_range_holder=(
                self._get_holder(temp_range_spec.unit_key, location)
                if temp_range_spec is not None
                else None
            ),
            fan_mode_holder=fan_mode_holder,
            humidity_holder=self._get_holder(spec.humidity_key, location),
        )

    def _setup_extended_states(self) -> None:
        """Set up optional states for vacuum."""
        for key, spec in EXTENDED_STATE_MAP.items():
            for location in self.locations:
                if (state := self._create_extended_state(spec, location)) is not None:
                    idx = self._add_idx(key, location)
                    self.state_map[idx] = state

    def _create_extended_state(
        self, spec: ExtendedPropertyStateSpec, location: str | None
    ) -> ExtendedPropertyState | None:
        """Create vacuum state if possible."""
        # vacuum's state, battery, operation_mode.
        state_holder = (
            self._get_holder(spec.state_key, location)
            if spec.state_key is not None
            else None
        )

        battery_holder = (
            [
                holder
                for battery_key in spec.battery_keys
                if (holder := self._get_holder(battery_key, location)) is not None
            ]
            if spec.battery_keys is not None
            else None
        )

        clean_operation_mode_holder = (
            self._get_holder(spec.operation_mode_key, location)
            if spec.operation_mode_key is not None
            else None
        )
        # fan's power, fan
        power_holder = (
            self._get_holder(spec.power_key, location)
            if spec.power_key is not None
            else None
        )
        fan_mode_holder = (
            self._get_holder(spec.fan_mode_key, location)
            if spec.fan_mode_key is not None
            else None
        )
        if (
            state_holder is None
            or battery_holder is None
            or clean_operation_mode_holder is None
        ) and (power_holder is None or fan_mode_holder is None):
            return None

        return ExtendedPropertyState(
            state_holder=state_holder,
            battery_holders=battery_holder if battery_holder else None,
            clean_operation_mode_holder=clean_operation_mode_holder,
            fan_mode_holder=fan_mode_holder,
            power_holder=power_holder,
        )

    def _setup_timer_states(self) -> None:
        """Set up optional states for timer."""
        for key, spec in TIMER_STATE_MAP.items():
            for location in self.locations:
                hour_holder = self._get_holder(spec.hour_key, location)
                minute_holder = self._get_holder(spec.minute_key, location)
                second_holder = self._get_holder(spec.second_key, location)

                if minute_holder is not None:
                    idx = self._add_idx(key, location)
                    self.state_map[idx] = TimerPropertyState(
                        hour_holder,
                        minute_holder,
                        second_holder,
                        time_format=spec.time_format,
                        setter=spec.setter,
                    )

    def _get_holder(
        self, key: str | None, location: str | None = None
    ) -> PropertyHolder | None:
        """Return the property holder."""
        if key and (idx := self._get_idx(key, location)) in self.property_map:
            return self.property_map[idx]

        return None

    def _get_idx(self, key: str, location: str | None = None) -> str:
        """Return the idx matching the key and location."""
        if not location:
            return key

        return f"{location}_{key}"

    def _add_idx(self, key: str, location: str | None = None) -> str:
        """Add and return the idx matching the key and location to the map."""
        if key not in self.idx_map:
            self.idx_map[key] = []

        idx = self._get_idx(key, location)
        self.idx_map[key].append(idx)
        return idx

    def get_location_for_idx(self, idx: str) -> str | None:
        """Return the location for idx."""
        if (holder := self.property_map.get(idx)) is not None:
            return holder.location

        if (state := self.state_map.get(idx)) is not None:
            return state.location

        return None

    def get_active_idx(
        self, key: str, active_mode: ActiveMode | None = None
    ) -> list[str]:
        """Return active list of idx for the given key."""
        idx_list = self.idx_map.get(key, [])

        if active_mode is None and key in (ExtendedProperty, TimerProperty):
            return idx_list

        return [
            idx
            for idx in idx_list
            if (state := self.state_map.get(idx)) is not None
            and state.can_activate(active_mode)
        ]

    async def fetch_data(self) -> dict[str, PropertyState]:
        """Fetch data from API endpoint."""
        if (
            response := await self.device.thinq_api.async_get_device_status(
                self.device.device_id
            )
        ) is not None:
            self.device.set_status(response)

        # Update all states.
        for state in self.state_map.values():
            state.update()

        return self.state_map

    def update_status(
        self, status: dict[str, Any] | None
    ) -> dict[str, PropertyState] | None:
        """Update data manually."""
        if status is not None:
            self.device.update_status(status)

        # Update all states.
        for state in self.state_map.values():
            state.update()

        return self.state_map

    def update_notification(
        self, message: str | None
    ) -> dict[str, PropertyState] | None:
        """Update notification message manually."""
        if message and (state := self.state_map.get(ThinQPropertyEx.NOTIFICATION)):
            state.value = message.lower()
            return self.state_map

        return None

    async def post(self, idx: str, data: Any) -> None:
        """Post the data to API endpoint."""
        if state := self.state_map.get(idx):
            await state.async_set(data)
            return

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_turn_on(self, idx: str) -> None:
        """Turn on device."""
        await self.post(idx, "POWER_ON")

    async def async_turn_off(self, idx: str) -> None:
        """Turn off device."""
        await self.post(idx, "POWER_OFF")

    async def async_set_target_temperature(self, idx: str, value: float) -> None:
        """Set target temperature."""
        if (
            isinstance(state := self.state_map.get(idx), ClimatePropertyState)
            and (holder := state.get_target_temp_holder()) is not None
        ):
            return await holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_target_temperature_low(self, idx: str, value: float) -> None:
        """Set cool target temperature in range mode."""
        if (
            isinstance(state := self.state_map.get(idx), ClimatePropertyState)
            and (holder := state.get_target_temp_low_holder()) is not None
        ):
            return await holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_target_temperature_high(self, idx: str, value: float) -> None:
        """Set heat target temperature in range mode."""
        if (
            isinstance(state := self.state_map.get(idx), ClimatePropertyState)
            and (holder := state.get_target_temp_high_holder()) is not None
        ):
            return await holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_hvac_mode(self, idx: str, value: str) -> None:
        """Set hvac mode."""
        if isinstance(state := self.state_map.get(idx), ClimatePropertyState):
            return await state.hvac_mode_holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_fan_mode(self, idx: str, value: str) -> None:
        """Set fan mode."""
        if (
            isinstance(
                state := self.state_map.get(idx),
                (ClimatePropertyState, ExtendedPropertyState),
            )
            and state.fan_mode_holder is not None
        ):
            return await state.fan_mode_holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_clean_operation_mode(self, idx: str, value: str) -> None:
        """Set clean operation mode."""
        if (
            isinstance(state := self.state_map.get(idx), ExtendedPropertyState)
            and state.clean_operation_mode_holder is not None
        ):
            return await state.clean_operation_mode_holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})


async def async_get_ha_bridge_list(
    thinq_api: ThinQApi,
) -> list[HABridge]:
    """Return a list of bridges."""
    device_list = await thinq_api.async_get_device_list()
    if not device_list:
        return []

    ha_bridge_list: list[HABridge] = []
    task_list = [
        asyncio.create_task(_async_create_ha_bridges(thinq_api, device))
        for device in device_list
    ]
    task_result = await asyncio.gather(*task_list)
    for ha_bridges in task_result:
        ha_bridge_list.extend(ha_bridges)

    return ha_bridge_list


async def _async_create_ha_bridges(
    thinq_api: ThinQApi, device: dict[str, Any]
) -> list[HABridge]:
    """Create new HA Bridge per device."""
    device_id = device.get("deviceId")
    if not device_id:
        return []

    device_info = device.get("deviceInfo")
    if not device_info:
        return []

    # Get an appropriate class constructor for the device type.
    device_type = device_info.get("deviceType")
    constructor = DEVICE_TYPE_API_MAP.get(device_type)
    if constructor is None:
        return []

    # Get a device profile from the server.
    try:
        profile = await thinq_api.async_get_device_profile(device_id)
    except Exception:
        _LOGGER.exception("Cannot create ConnectDevice no profile info:%s", device_info)
        return []

    device_group_id = device_info.get("groupId")

    # Create new device api instance.
    try:
        connect_device: ConnectBaseDevice = (
            constructor(
                thinq_api=thinq_api,
                device_id=device_id,
                device_type=device_type,
                model_name=device_info.get("modelName"),
                alias=device_info.get("alias"),
                group_id=device_group_id,
                reportable=device_info.get("reportable"),
                profile=profile,
            )
            if device_group_id
            else constructor(
                thinq_api=thinq_api,
                device_id=device_id,
                device_type=device_type,
                model_name=device_info.get("modelName"),
                alias=device_info.get("alias"),
                reportable=device_info.get("reportable"),
                profile=profile,
            )
        )
    except Exception:
        _LOGGER.exception(
            "Cannot create ConnectDevice info:%s, profile:%s", device_info, profile
        )
        return []

    # For wash-WashtowerDevice, we need to create two ha bridges.
    if isinstance(connect_device, WashtowerDevice):
        dryer_ha_bridge = HABridge(connect_device, sub_id=Location.DRYER)
        washer_ha_bridge = HABridge(connect_device, sub_id=Location.WASHER)
        return [dryer_ha_bridge, washer_ha_bridge]

    return [HABridge(connect_device)]

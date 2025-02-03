"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

# The extended api interface for Home Assistant.
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any, Final

from thinqconnect import (
    PROPERTY_WRITABLE,
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
from thinqconnect.devices.const import Location

from .property import ActiveMode, PropertyHolder
from .specification import (
    CLIMATE_STATE_MAP,
    EXTENDED_STATE_MAP,
    PROPERTY_OPTION_MAP,
    SELECTIVE_STATE_MAP,
    TEMPERATURE_STATE_MAP,
    TIMER_STATE_MAP,
    WATER_HEATER_STATE_MAP,
    ClimatePropertyStateSpec,
    ClimateTemperatureSpec,
    ExtendedProperty,
    ExtendedPropertyStateSpec,
    PropertyStateSpec,
    SelectivePropertyStateSpec,
    TemperaturePropertyStateSpec,
    ThinQPropertyEx,
    TimerProperty,
    TimerPropertyStateSpec,
    WaterHeaterPropertyStateSpec,
)
from .state import (
    ClimatePropertyState,
    ExtendedPropertyState,
    PropertyState,
    SelectivePropertyState,
    SinglePropertyState,
    TemperaturePropertyState,
    TimerPropertyState,
    WaterHeaterPropertyState,
)
from .temperature import (
    ClimateTemperatureGroup,
    ClimateTemperatureMap,
    TemperatureGroup,
    TemperatureHolders,
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

        # A preferred units when retrieving temperature values.
        self.preferred_temperature_unit: str = "C"

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
        # Create single property states for all holders.
        for idx, holder in self.property_map.items():
            self.state_map[idx] = SinglePropertyState(holder)

        # Create specified properties.
        specifications = (
            (SELECTIVE_STATE_MAP, self._create_selective_state),
            (CLIMATE_STATE_MAP, self._create_climate_state),
            (TEMPERATURE_STATE_MAP, self._create_temperature_state),
            (TIMER_STATE_MAP, self._create_timer_states),
            (EXTENDED_STATE_MAP, self._create_extended_state),
            (WATER_HEATER_STATE_MAP, self._create_water_heater_state),
        )

        for specification in specifications:
            for key, spec in specification[0].items():
                if not spec.is_target_device(self.device.device_type):
                    continue

                self._setup_specified_states(key, spec, specification[1])

    def _setup_specified_states(
        self, key: str, spec: PropertyStateSpec, create_func: Callable
    ) -> None:
        """Set up specified states."""
        for location in self.locations:
            if (state := create_func(spec, location)) is not None:
                # Note that some type of state can overwrite single state.
                idx = self._add_idx(key, location)
                self.state_map[idx] = state

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

    def _create_climate_state(
        self, spec: ClimatePropertyStateSpec, location: str | None
    ) -> ClimatePropertyState | None:
        """Create climate state if possible."""
        # Power and HVAC mode are required.
        power_holder = self._get_holder(spec.power_key, location)
        hvac_mode_holder = self._get_holder(spec.hvac_mode_key, location)
        if power_holder is None or hvac_mode_holder is None:
            return None

        # Build climate temperature map.
        temperature_map: ClimateTemperatureMap = {}
        for key, temp_spec in spec.temperature_specs.items():
            if (
                group := self._create_climate_temperature_group(temp_spec, location)
            ) is not None:
                temperature_map[key] = group

        if not temperature_map:
            return None

        # Fan mode.
        fan_mode_holder: PropertyHolder | None = None
        for fan_mode_key in spec.fan_mode_keys:
            if (
                fan_mode_holder := self._get_holder(fan_mode_key, location)
            ) is not None:
                break

        return ClimatePropertyState(
            power_holder,
            hvac_mode_holder,
            temperature_map,
            spec.default_temperature_preset,
            support_temperature_range=spec.support_temperature_range,
            temperature_preset_holder=self._get_holder(
                spec.temperature_preset_key, location
            ),
            temperature_sub_preset_holder=self._get_holder(
                spec.temperature_sub_preset_key, location
            ),
            fan_mode_holder=fan_mode_holder,
            humidity_holder=self._get_holder(spec.humidity_key, location),
            swing_mode_holder=self._get_holder(spec.swing_mode_key, location),
            swing_horizontal_mode_holder=self._get_holder(
                spec.swing_horizontal_mode_key, location
            ),
            use_preferred_unit=True,
        )

    def _create_climate_temperature_group(
        self,
        spec: ClimateTemperatureSpec,
        location: str | None,
    ) -> ClimateTemperatureGroup | None:
        """Create a climate temperature group."""

        # Current temp is required.
        if not (
            current_temp_group := self._get_temperature_holder_group(
                spec.current_temp_key, location
            )
        ):
            return None

        return ClimateTemperatureGroup(
            current_temp_hvac_map={"_": current_temp_group},
            target_temp_hvac_map={
                hvac_mode: self._get_temperature_holder_group(key, location)
                for hvac_mode, key in spec.target_temp_key_map.items()
            },
            target_temp_low_hvac_map={
                hvac_mode: self._get_temperature_holder_group(
                    key,
                    location,
                    min_key=spec.target_temp_low_min_key,
                    max_key=spec.target_temp_low_max_key,
                )
                for hvac_mode, key in spec.target_temp_low_key_map.items()
            },
            target_temp_high_hvac_map={
                hvac_mode: self._get_temperature_holder_group(
                    key,
                    location,
                    min_key=spec.target_temp_high_min_key,
                    max_key=spec.target_temp_high_max_key,
                )
                for hvac_mode, key in spec.target_temp_high_key_map.items()
            },
            unit_holder=self._get_holder(spec.unit_key, location),
        )

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

    def _create_timer_states(
        self, spec: TimerPropertyStateSpec, location: str | None
    ) -> TimerPropertyState | None:
        """Create timer state if possible."""
        hour_holder = self._get_holder(spec.hour_key, location)
        minute_holder = self._get_holder(spec.minute_key, location)
        second_holder = self._get_holder(spec.second_key, location)

        if minute_holder is not None:
            return TimerPropertyState(
                hour_holder,
                minute_holder,
                second_holder,
                time_format=spec.time_format,
                setter=spec.setter,
            )

        return None

    def _create_temperature_state(
        self, spec: TemperaturePropertyStateSpec, location: str | None
    ) -> TemperaturePropertyState | None:
        """Create temperature state if possible."""
        if holder_map := self._get_temperature_holder_group(spec.origin_key, location):
            return TemperaturePropertyState(
                holder_map,
                unit_holder=self._get_holder(spec.unit_key, location),
                use_preferred_unit=spec.use_preferred_unit(self.device.device_type),
            )

        return None

    def _create_water_heater_state(
        self, spec: WaterHeaterPropertyStateSpec, location: str | None
    ) -> WaterHeaterPropertyState | None:
        """Create water_heater state if possible."""
        power_holder: PropertyHolder | None
        for power_key in spec.power_keys:
            if (power_holder := self._get_holder(power_key, location)) is not None:
                if power_key == spec.power_keys[-1]:
                    break
                if power_holder.profile.get(PROPERTY_WRITABLE):
                    break
        if power_holder is None:
            return None

        job_mode_holder = (
            self._get_holder(spec.job_mode_key, location)
            if spec.job_mode_key is not None
            else None
        )
        current_temp_holder_map = self._get_temperature_holder_group(
            key=spec.current_temp_key,
            location=location,
        )
        target_temp_holder_map = self._get_temperature_holder_group(
            key=spec.target_temp_key,
            location=location,
        )
        unit_holder = self._get_holder(spec.unit_key, location)
        return WaterHeaterPropertyState(
            power_holder=power_holder,
            job_mode_holder=job_mode_holder,
            current_temp_holder_map=current_temp_holder_map,
            target_temp_holder_map=target_temp_holder_map,
            unit_holder=unit_holder,
            use_preferred_unit=True,
        )

    def _get_holder(
        self, key: str | None, location: str | None = None, postfix: str | None = None
    ) -> PropertyHolder | None:
        """Return the property holder."""
        if key is not None and postfix is not None:
            key = f"{key}_{postfix}"

        if key and (idx := self._get_idx(key, location)) in self.property_map:
            return self.property_map[idx]

        return None

    def _get_temperature_holder_group(
        self,
        key: str,
        location: str | None = None,
        *,
        min_key: str | None = None,
        max_key: str | None = None,
    ) -> TemperatureGroup:
        """Return a group of temperature property holders."""
        holder_group = {}
        unit_postfix_pairs = {"C": "c", "F": "f", "_": None}
        for unit, postfix in unit_postfix_pairs.items():
            if (
                holders := self._build_temperature_holders(
                    key, location, postfix, min_key, max_key
                )
            ) is not None:
                holder_group[unit] = holders

        return holder_group

    def _build_temperature_holders(
        self,
        key: str | None,
        location: str | None,
        postfix: str | None,
        min_key: str | None,
        max_key: str | None,
    ) -> TemperatureHolders | None:
        """Build a set of temperature holders."""
        if (value_holder := self._get_holder(key, location, postfix)) is not None:
            holders = {"value": value_holder}
            if (min_holder := self._get_holder(min_key, location, postfix)) is not None:
                holders["min"] = min_holder
            if (max_holder := self._get_holder(max_key, location, postfix)) is not None:
                holders["max"] = max_holder
            return holders

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
            state.update(preferred_unit=self.preferred_temperature_unit)

        return self.state_map

    def update_status(
        self, status: dict[str, Any] | None
    ) -> dict[str, PropertyState] | None:
        """Update data manually."""
        if status is not None:
            self.device.update_status(status)

        # Update all states.
        for state in self.state_map.values():
            if isinstance(
                state,
                (
                    ClimatePropertyState,
                    TemperaturePropertyState,
                    WaterHeaterPropertyState,
                ),
            ):
                state.update(preferred_unit=self.preferred_temperature_unit)
            else:
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

    def set_preferred_temperature_unit(self, unit: str | None) -> None:
        """Set preferred temperature unit."""
        self.preferred_temperature_unit = unit if unit is not None else "C"

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
            isinstance(
                state := self.state_map.get(idx),
                (ClimatePropertyState, WaterHeaterPropertyState),
            )
            and (holder := state.get_target_temp_control_holder()) is not None
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

    async def async_set_swing_mode(self, idx: str, value: str) -> None:
        """Set swing mode."""
        if (
            isinstance(
                state := self.state_map.get(idx),
                (ClimatePropertyState,),
            )
            and state.swing_mode_holder is not None
        ):
            return await state.swing_mode_holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_swing_horizontal_mode(self, idx: str, value: str) -> None:
        """Set swing hor mode."""
        if (
            isinstance(
                state := self.state_map.get(idx),
                (ClimatePropertyState,),
            )
            and state.swing_horizontal_mode_holder is not None
        ):
            return await state.swing_horizontal_mode_holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_clean_operation_mode(self, idx: str, value: str) -> None:
        """Set clean operation mode."""
        if (
            isinstance(state := self.state_map.get(idx), ExtendedPropertyState)
            and state.clean_operation_mode_holder is not None
        ):
            return await state.clean_operation_mode_holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    async def async_set_job_mode(self, idx: str, value: str) -> None:
        """Set job mode."""
        if (
            isinstance(state := self.state_map.get(idx), WaterHeaterPropertyState)
            and state.job_mode_holder is not None
        ):
            return await state.job_mode_holder.async_set(value)

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

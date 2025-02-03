"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

# The property state interface for Home Assistant.

from collections import deque
from collections.abc import Awaitable, Callable, Iterable
from datetime import time
from typing import Any

from thinqconnect import ConnectBaseDevice, ThinQAPIException
from thinqconnect.devices.const import Property as ThinQProperty

from .property import ActiveMode, PropertyHolder
from .temperature import (
    ClimateTemperatureHelper,
    ClimateTemperatureMap,
    TemperatureGroup,
    TemperatureHvacMap,
    TemperatureHelper,
)


class PropertyState:
    """A class that represents state of property."""

    def __init__(self, holders: Iterable[PropertyHolder | None] | None = None) -> None:
        """Set up a state."""
        self.holders = self.retrieve_holders(holders)
        self.value: Any = None
        self.unit: str | None = None
        self.is_on: bool | None = None
        self.current_temp: float | None = None
        self.target_temp: float | None = None
        self.target_temp_high: float | None = None
        self.target_temp_low: float | None = None
        self.hvac_mode: str = "off"
        self.fan_mode: str | None = None
        self.humidity: int | None = None
        self.support_temperature_range: bool = False
        self.current_state: str | None = None
        self.battery: str | None = None
        self.job_mode: str | None = None
        self.swing_mode: str | None = None
        self.swing_horizontal_mode: str | None = None

    def retrieve_holders(
        self, holders: Iterable[PropertyHolder | None] | None
    ) -> deque[PropertyHolder]:
        """Return the deque from the given iterable."""
        if holders:
            holder_list = [holder for holder in holders if holder is not None]
            if holder_list:
                return deque(holder_list)

        return deque()

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return None

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        return None

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        return None

    @property
    def step(self) -> float | None:
        """Return the step value."""
        return None

    @property
    def location(self) -> str | None:
        """Return the location."""
        return None

    @property
    def hvac_modes(self) -> list[str]:
        """Return the hvac modes."""
        return []

    @property
    def fan_modes(self) -> list[str]:
        """Return the fan modes."""
        return []

    @property
    def swing_modes(self) -> list[str]:
        """Return the swing modes."""
        return []

    @property
    def swing_horizontal_modes(self) -> list[str]:
        """Return the swing horizontal modes."""
        return []

    @property
    def job_modes(self) -> list[str]:
        """Return the operation modes."""
        return []

    def can_activate(self, active_mode: ActiveMode | None) -> bool:
        """Check whether state can be activated with the given mode."""
        if active_mode is None:
            return True

        if not self.holders:
            return False

        # Check if whether all holders can set the given mode.
        for holder in self.holders:
            if not holder.can_activate(active_mode):
                return False

        for holder in self.holders:
            holder.set_rw_mode(active_mode)

        return True

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""

    def dump(self) -> str:
        """Dump the current status."""
        return "PropertyState(Empty)"


class SinglePropertyState(PropertyState):
    """A class that implements state that matches only one property."""

    def __init__(self, holder: PropertyHolder) -> None:
        """Set up a state."""
        super().__init__([holder])

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return self.holders[0].options

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        return self.holders[0].min

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        return self.holders[0].max

    @property
    def step(self) -> float | None:
        """Return the step value."""
        return self.holders[0].step

    @property
    def location(self) -> str | None:
        """Return the location."""
        return self.holders[0].location

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        self.value = self.holders[0].get_value()
        self.is_on = self.holders[0].get_value_as_bool()
        self.unit = self.holders[0].get_unit()

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        await self.holders[0].async_set(value)

    def dump(self) -> str:
        """Dump the current status."""
        return f"SinglePropertyState({self.holders[0].dump()})"


class SelectivePropertyState(PropertyState):
    """A class that implements state that select property on runtime."""

    def __init__(self, origin_key: str, holders: Iterable[PropertyHolder]) -> None:
        """Set up a state."""
        super().__init__(holders)

        self.origin_key = origin_key

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        for _ in range(len(self.holders)):
            # For target_temperature type dict
            if isinstance(value := self.holders[0].get_value(), dict):
                if (data := value.get(self.origin_key)) is not None:
                    self.value = data
                    self.is_on = PropertyHolder.to_boolean_value(data)
                    self.unit = value.get("unit")
                    return
            elif value is not None:
                self.value = value
                return

            self.holders.rotate(-1)

    def dump(self) -> str:
        """Dump the current status."""
        holder_dumps = [f"{holder.dump(),}" for holder in self.holders]
        message = "".join(holder_dumps)
        return f"SelectivePropertyState(origin_key={self.origin_key}/{message})"


class TimerPropertyState(PropertyState):
    """A class that implements state that has timer properties."""

    def __init__(
        self,
        hour_holder: PropertyHolder | None,
        minute_holder: PropertyHolder,
        second_holder: PropertyHolder | None,
        *,
        time_format: str | None = None,
        setter: (
            Callable[[ConnectBaseDevice, time | None], Awaitable[None]] | None
        ) = None,
    ) -> None:
        """Set up a state."""
        super().__init__([hour_holder, minute_holder, second_holder])
        self.hour_holder = hour_holder
        self.minute_holder = minute_holder
        self.second_holder = second_holder
        self.time_format = self.create_time_format_if_needed(time_format)
        self.setter = setter

    @property
    def location(self) -> str | None:
        """Return the location."""
        # Since all holders must be in the same location,
        # we only need to check the minute_holder's location.
        return self.minute_holder.location

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        hour = self.hour_holder.get_value() if self.hour_holder is not None else None
        minute = (
            self.minute_holder.get_value() if self.minute_holder is not None else None
        )
        second = (
            self.second_holder.get_value() if self.second_holder is not None else None
        )

        if not isinstance(hour, int):
            hour = None
        if not isinstance(minute, int):
            minute = None
        if not isinstance(second, int):
            second = None
        if all(v is None for v in [hour, minute, second]):
            self.value = None
        else:
            self.value = time(hour or 0, minute or 0, second or 0)

    def create_time_format_if_needed(self, time_format: str | None) -> str:
        """Return the default time format."""
        if time_format:
            return time_format

        time_format_list: list[str] = []
        if self.hour_holder is not None:
            time_format_list.append("%H")
        if self.minute_holder is not None:
            time_format_list.append("%M")
        if self.second_holder is not None:
            time_format_list.append("%S")
        return ":".join(time_format_list)

    def str_to_time(self, time_string: str) -> time | None:
        """Convert the given string to time."""
        hour, _, minute = time_string.partition(":")
        if hour and minute:
            try:
                return time(hour=int(hour), minute=int(minute))
            except (ValueError, TypeError):
                return None

        return None

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        if not self.setter:
            raise ThinQAPIException("0001", "The control command is not supported.", {})

        if not value:
            # Reset timer.
            await self.setter(self.minute_holder.api, None)
            return

        converted = value if isinstance(value, time) else self.str_to_time(value)
        if converted is not None:
            # Set timer.
            await self.setter(self.minute_holder.api, converted)
        else:
            raise ThinQAPIException(
                "0001", "The input value is not in the correct format.", {}
            )

    def dump(self) -> str:
        """Dump the current status."""
        messages: list[str] = []
        messages.append(f"TimerPropertyState(format={self.time_format}/")
        if self.hour_holder is not None:
            messages.append(f"{self.hour_holder.dump()},")
        if self.minute_holder is not None:
            messages.append(f"{self.minute_holder.dump()},")
        if self.second_holder is not None:
            messages.append(f"{self.second_holder.dump()},")
        return "".join(messages)


class TemperaturePropertyState(PropertyState):
    """A class that implements state that has temperature properties."""

    def __init__(
        self,
        holder_map: TemperatureGroup,
        *,
        unit_holder: PropertyHolder | None = None,
        use_preferred_unit: bool = False,
    ) -> None:
        """Set up a state."""
        super().__init__((next(iter(holder_map.values()))).values())

        self.holder_map = holder_map
        self.unit_holder = unit_holder

        # Set up temperature helpers.
        self.temp_helper = TemperatureHelper(
            holder_map, unit_holder=unit_holder, use_preferred_unit=use_preferred_unit
        )
        self.unit = "C"

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        if (holder := self.temp_helper.current_holder) is not None:
            return holder.min

        return None

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        if (holder := self.temp_helper.current_holder) is not None:
            return holder.max

        return None

    @property
    def step(self) -> float | None:
        """Return the step value."""
        if (holder := self.temp_helper.current_holder) is not None:
            return holder.step

        return None

    @property
    def location(self) -> str | None:
        """Return the location."""
        return self.holders[0].location

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        self.value = self.temp_helper.update(preferred_unit)
        self.unit = self.temp_helper.unit or "C"

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        if (holder := self.temp_helper.current_holder) is not None:
            return await holder.async_set(value)

        raise ThinQAPIException("0001", "The control command is not supported.", {})

    def dump(self) -> str:
        """Dump the current status."""
        holder_dumps = [f"{holder.dump(),}" for holder in self.holders]
        if self.unit_holder is not None:
            holder_dumps.append(f"{self.unit_holder.dump()},")
        message = "".join(holder_dumps)
        return f"TemperaturePropertyState({message})"


class ClimatePropertyState(PropertyState):
    """A class that implements state that has climate properties."""

    def __init__(
        self,
        power_holder: PropertyHolder,
        hvac_mode_holder: PropertyHolder,
        climate_temperature_map: ClimateTemperatureMap,
        default_temperature_preset: str,
        *,
        support_temperature_range: bool = False,
        temperature_preset_holder: PropertyHolder | None = None,
        temperature_sub_preset_holder: PropertyHolder | None = None,
        fan_mode_holder: PropertyHolder | None = None,
        humidity_holder: PropertyHolder | None = None,
        swing_mode_holder: PropertyHolder | None = None,
        swing_horizontal_mode_holder: PropertyHolder | None = None,
        use_preferred_unit: bool = False,
    ) -> None:
        """Set up a state."""
        super().__init__()

        self.power_holder = power_holder
        self.hvac_mode_holder = hvac_mode_holder
        self.default_temperature_preset = default_temperature_preset
        self.support_temperature_range = support_temperature_range
        self.temperature_preset_holder = temperature_preset_holder
        self.temperature_sub_preset_holder = temperature_sub_preset_holder
        self.fan_mode_holder = fan_mode_holder
        self.humidity_holder = humidity_holder
        self.swing_mode_holder = swing_mode_holder
        self.swing_horizontal_mode_holder = swing_horizontal_mode_holder
        self.use_preferred_unit = use_preferred_unit
        self.unit = "C"

        self.helpers = self._build_helpers(climate_temperature_map)
        self.current_preset = default_temperature_preset
        self.current_temp_helper = self.helpers[self.current_preset]["current_temp"]
        self.target_temp_helper = self.helpers[self.current_preset]["target_temp"]
        self.target_temp_low_helper = self.helpers[self.current_preset][
            "target_temp_low"
        ]
        self.target_temp_high_helper = self.helpers[self.current_preset][
            "target_temp_high"
        ]

    def _get_current_preset(self) -> str:
        """Return the current preset."""
        # No preset holder, return the default.
        if self.temperature_preset_holder is None:
            return self.default_temperature_preset

        # If only the main preset is available, return the main preset only.
        main_preset = self.temperature_preset_holder.get_value()
        if self.temperature_sub_preset_holder is None:
            if (preset := f"{main_preset}") in self.helpers:
                return preset

            return self.default_temperature_preset

        # If both the main and sub presets are available, return the
        # combination of them as preset.
        sub_preset = self.temperature_sub_preset_holder.get_value()
        if (preset := f"{main_preset}/{sub_preset}") in self.helpers:
            return preset

        # A sub preset may only be valid in a specific main_preset.
        # In this case, only the main preset should be returned.
        if (preset := f"{main_preset}") in self.helpers:
            return preset

        # Fallback
        return self.default_temperature_preset

    def _build_helpers(
        self, climate_temperature_map: ClimateTemperatureMap
    ) -> dict[str, dict[str, ClimateTemperatureHelper]]:
        """Build helper map for each preset."""
        helpers: dict[str, dict[str, ClimateTemperatureHelper]] = {}
        for preset, climate_group in climate_temperature_map.items():
            helpers[preset] = {
                "current_temp": self._build_helper(
                    climate_group.current_temp_hvac_map,
                    climate_group.unit_holder,
                    use_wildcard_holder=True,
                ),
                "target_temp": self._build_helper(
                    climate_group.target_temp_hvac_map, climate_group.unit_holder
                ),
                "target_temp_low": self._build_helper(
                    climate_group.target_temp_low_hvac_map, climate_group.unit_holder
                ),
                "target_temp_high": self._build_helper(
                    climate_group.target_temp_high_hvac_map, climate_group.unit_holder
                ),
            }
        return helpers

    def _build_helper(
        self,
        hvac_map: TemperatureHvacMap,
        unit_holder: PropertyHolder | None,
        *,
        use_wildcard_holder: bool = False,
    ) -> ClimateTemperatureHelper:
        """Build a helper."""
        return ClimateTemperatureHelper(
            hvac_map,
            unit_holder=unit_holder,
            use_preferred_unit=self.use_preferred_unit,
            use_wildcard_holder=use_wildcard_holder,
        )

    def get_target_temp_holder(self) -> PropertyHolder | None:
        """Return the current valid target temperature holder (for reading)."""
        return self.target_temp_helper.current_holder

    def get_target_temp_control_holder(self) -> PropertyHolder | None:
        """Return the current valid target temperature holder (for writing)."""
        if self.hvac_mode == "cool":
            return self.get_target_temp_high_holder()
        if self.hvac_mode == "heat":
            return self.get_target_temp_low_holder()

        return None

    def get_target_temp_low_holder(self) -> PropertyHolder | None:
        """Return the current valid target temperature low holder."""
        return self.target_temp_low_helper.current_holder

    def get_target_temp_high_holder(self) -> PropertyHolder | None:
        """Return the current valid target temperature high holder."""
        return self.target_temp_high_helper.current_holder

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        candidates: list[float] = []
        if self.target_temp_low_helper.min is not None:
            candidates.append(self.target_temp_low_helper.min)
        if self.target_temp_high_helper.min is not None:
            candidates.append(self.target_temp_high_helper.min)

        return min(candidates) if candidates else None

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        candidates: list[float] = []
        if self.target_temp_low_helper.max is not None:
            candidates.append(self.target_temp_low_helper.max)
        if self.target_temp_high_helper.max is not None:
            candidates.append(self.target_temp_high_helper.max)

        return max(candidates) if candidates else None

    @property
    def step(self) -> float | None:
        """Return the step value."""
        candidates: list[float] = []
        if self.target_temp_low_helper.step is not None:
            candidates.append(self.target_temp_low_helper.step)
        if self.target_temp_high_helper.step is not None:
            candidates.append(self.target_temp_high_helper.step)

        return max(candidates) if candidates else None

    @property
    def location(self) -> str | None:
        """Return the location."""
        # Since all holders must be in the same location,
        # we only need to check the power_holder's location.
        return self.power_holder.location

    @property
    def hvac_modes(self) -> list[str]:
        """Return the hvac modes."""
        return self.hvac_mode_holder.options or []

    @property
    def fan_modes(self) -> list[str]:
        """Return the fan modes."""
        if self.fan_mode_holder is None:
            return []

        return self.fan_mode_holder.options or []

    @property
    def swing_modes(self) -> list[str]:
        """Return the vertical swing modes."""
        if self.swing_mode_holder is None:
            return []

        return self.swing_mode_holder.options or []

    @property
    def swing_horizontal_modes(self) -> list[str]:
        """Return the horizontal swing modes."""
        if self.swing_horizontal_mode_holder is None:
            return []

        return self.swing_horizontal_mode_holder.options or []

    def _update_mode(self) -> None:
        """Update mode and all helpers."""
        self.current_preset = self._get_current_preset()
        self.current_temp_helper = self.helpers[self.current_preset]["current_temp"]
        self.target_temp_helper = self.helpers[self.current_preset]["target_temp"]
        self.target_temp_low_helper = self.helpers[self.current_preset][
            "target_temp_low"
        ]
        self.target_temp_high_helper = self.helpers[self.current_preset][
            "target_temp_high"
        ]

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        self._update_mode()
        self.is_on = self.power_holder.get_value_as_bool()
        self.hvac_mode = self.hvac_mode_holder.get_value() or "off"
        self.current_temp = self.current_temp_helper.update(
            self.hvac_mode, preferred_unit
        )

        if self.is_on:
            self.target_temp = self.target_temp_helper.update(
                self.hvac_mode, preferred_unit
            )
            self.target_temp_low = self.target_temp_low_helper.update(
                self.hvac_mode, preferred_unit
            )
            self.target_temp_high = self.target_temp_high_helper.update(
                self.hvac_mode, preferred_unit
            )
        else:
            self.target_temp = None
            self.target_temp_high = None
            self.target_temp_low = None

        # Set preferred unit if it exist. Otherwise set unit from unit_holder.
        if self.current_temp_helper.unit is not None:
            self.unit = self.current_temp_helper.unit
        else:
            self.unit = "C"  # This because climate attribute doesn't allow 'None' unit.

        if self.fan_mode_holder is not None:
            self.fan_mode = self.fan_mode_holder.get_value()
        if self.humidity_holder is not None:
            self.humidity = self.humidity_holder.get_value()
        if self.swing_mode_holder is not None:
            self.swing_mode = self.swing_mode_holder.get_value()
        if self.swing_horizontal_mode_holder is not None:
            self.swing_horizontal_mode = self.swing_horizontal_mode_holder.get_value()

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        await self.power_holder.async_set(value)

    def dump(self) -> str:
        """Dump the current status."""
        holder_dumps: list[str] = []
        holder_dumps.append("ClimatePropertyStateSpec(")
        holder_dumps.append(f"{self.power_holder.dump()},")
        holder_dumps.append(f"{self.hvac_mode_holder.dump()},")
        if (holder := self.current_temp_helper.current_holder) is not None:
            holder_dumps.append(f"{holder.dump()},")
        if (holder := self.target_temp_helper.current_holder) is not None:
            holder_dumps.append(f"{holder.dump()},")
        if (holder := self.target_temp_low_helper.current_holder) is not None:
            holder_dumps.append(f"{holder.dump()},")
        if (holder := self.target_temp_high_helper.current_holder) is not None:
            holder_dumps.append(f"{holder.dump()},")
        if self.fan_mode_holder is not None:
            holder_dumps.append(f"{self.fan_mode_holder.dump()},")
        if self.humidity_holder is not None:
            holder_dumps.append(f"{self.humidity_holder.dump()}")
        if self.temperature_preset_holder is not None:
            holder_dumps.append(f"{self.temperature_preset_holder.dump()}")
        return "".join(holder_dumps)


class ExtendedPropertyState(PropertyState):
    """A class that implements state that has vacuum properties."""

    def __init__(
        self,
        state_holder: PropertyHolder | None = None,
        battery_holders: Iterable[PropertyHolder] | None = None,
        clean_operation_mode_holder: PropertyHolder | None = None,
        power_holder: PropertyHolder | None = None,
        fan_mode_holder: PropertyHolder | None = None,
    ) -> None:
        """Set up a state."""
        super().__init__()

        self.state_holder = state_holder
        self.battery_holders = deque(battery_holders) if battery_holders else deque()
        self.clean_operation_mode_holder = clean_operation_mode_holder
        self.power_holder = power_holder
        self.fan_mode_holder = fan_mode_holder

    @property
    def fan_modes(self) -> list[str]:
        """Return the fan modes."""
        if self.fan_mode_holder is None:
            return []

        return self.fan_mode_holder.options or []

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        if self.state_holder is not None:
            self.current_state = self.state_holder.get_value()
        if self.battery_holders is not None:
            for _ in range(len(self.battery_holders)):
                if (value := self.battery_holders[0].get_value()) is not None:
                    self.battery = value
                    break
                self.battery_holders.rotate(-1)

        if self.power_holder is not None:
            self.is_on = self.power_holder.get_value_as_bool()
        if self.fan_mode_holder is not None:
            self.fan_mode = self.fan_mode_holder.get_value()

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        if self.power_holder is not None:
            await self.power_holder.async_set(value)

    def dump(self) -> str:
        """Dump the current status."""
        holder_dumps: list[str] = []
        holder_dumps.append("ExtendedPropertyStateSpec(")
        if self.state_holder is not None:
            holder_dumps.append(f"{self.state_holder.dump()},")
        if self.battery_holders:
            holder_dumps.append(f"{self.battery_holders[0].dump()},")
        if self.power_holder is not None:
            holder_dumps.append(f"{self.power_holder.dump()},")
        if self.fan_mode_holder is not None:
            holder_dumps.append(f"{self.fan_mode_holder.dump()},")
        return "".join(holder_dumps)


class WaterHeaterPropertyState(PropertyState):
    """A class that implements state that has water_heater properties."""

    def __init__(
        self,
        power_holder: PropertyHolder,
        job_mode_holder: PropertyHolder | None = None,
        *,
        current_temp_holder_map: TemperatureGroup,
        target_temp_holder_map: TemperatureGroup,
        unit_holder: PropertyHolder | None = None,
        use_preferred_unit: bool = False,
    ) -> None:
        """Set up a state."""
        super().__init__()

        self.power_holder = power_holder
        self.job_mode_holder = job_mode_holder

        # Set up temperature helpers.
        self.current_temp_helper = TemperatureHelper(
            current_temp_holder_map,
            unit_holder=unit_holder,
            use_preferred_unit=use_preferred_unit,
        )
        self.target_temp_helper = TemperatureHelper(
            target_temp_holder_map,
            unit_holder=unit_holder,
            use_preferred_unit=use_preferred_unit,
        )

    def get_target_temp_control_holder(self) -> PropertyHolder | None:
        """Return the current valid target temperature holder (for writing)."""
        return self.target_temp_helper.current_holder

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        if (holder := self.target_temp_helper.current_holder) is not None:
            return holder.min

        return None

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        if (holder := self.target_temp_helper.current_holder) is not None:
            return holder.max

        return None

    @property
    def step(self) -> float | None:
        """Return the step value."""
        if (holder := self.target_temp_helper.current_holder) is not None:
            return holder.step

        return None

    @property
    def location(self) -> str | None:
        """Return the location."""
        # Since all holders must be in the same location,
        # we only need to check the power_holder's location.
        return self.power_holder.location

    @property
    def job_modes(self) -> list[str]:
        """Return the operation modes."""
        if self.job_mode_holder is None:
            return []

        return self.job_mode_holder.options or []

    def update(self, *, preferred_unit: str | None = None) -> None:
        """Update the state."""
        if self.power_holder is not None:
            self.is_on = self.power_holder.get_value_as_bool()
        if self.job_mode_holder is not None:
            self.job_mode = self.job_mode_holder.get_value() or "off"
        self.current_temp = self.current_temp_helper.update(preferred_unit)
        if self.is_on:
            self.target_temp = self.target_temp_helper.update(preferred_unit)
        else:
            self.target_temp = None

        # Set preferred unit if it exist. Otherwise set unit from unit_holder.
        if self.current_temp_helper.unit is not None:
            self.unit = self.current_temp_helper.unit
        else:
            self.unit = "C"  # This because climate attribute doesn't allow 'None' unit.

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        if self.power_holder.key == ThinQProperty.HOT_WATER_MODE:
            value = "ON" if value == "POWER_ON" else "OFF"
        await self.power_holder.async_set(value)

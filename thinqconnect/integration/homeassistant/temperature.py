"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

# Temperature logics.

from abc import ABC
from typing import Any, TypeAlias

from .property import PropertyHolder

# TypeAlias for a set of temperature holders.
#
# holders = {
#     "value": PropertyHolder(key=cool_target_temperature_c)
#     "min": PropertyHolder(key=cool_min_temperature_c)
#     "max": PropertyHolder(key=cool_max_temperature_c)
# }
TemperatureHolders: TypeAlias = dict[str, PropertyHolder]

# TypeAlias for a group of temperature holders.
#
# group = {
#   "C": [holders_celsius],
#   "F": [holders_fahrenheit],
#   "_": [holders_legacy]
# }

TemperatureGroup: TypeAlias = dict[str, TemperatureHolders]

# TypeAlias for hvac mode and temperature map.
#
# temperature/hvac_map = {
#   "cool": [group_cool],
#   "heat": [group_heat],
#   "auto": [group_auto],
# }
TemperatureHvacMap: TypeAlias = dict[str, TemperatureGroup]


class ClimateTemperatureGroup:
    """A group that contains a set of temperature holders to control climate."""

    def __init__(
        self,
        current_temp_hvac_map: TemperatureHvacMap,
        target_temp_hvac_map: TemperatureHvacMap,
        target_temp_low_hvac_map: TemperatureHvacMap,
        target_temp_high_hvac_map: TemperatureHvacMap,
        unit_holder: PropertyHolder | None = None,
    ) -> None:
        """Initialize."""
        self.current_temp_hvac_map = current_temp_hvac_map
        self.target_temp_hvac_map = target_temp_hvac_map
        self.target_temp_low_hvac_map = target_temp_low_hvac_map
        self.target_temp_high_hvac_map = target_temp_high_hvac_map
        self.unit_holder = unit_holder


# TypeAlias for preset mode and temperature/hvac_map.
#
# hvac_map = {
#   "air": [temperature/hvac_map_AIR],
#   "water/in_water": [temperature/hvac_map_WATER_IN],
#   "water/out_water": [temperature/hvac_map_WATER_OUT],
# }
ClimateTemperatureMap: TypeAlias = dict[str, ClimateTemperatureGroup]


class TemperatureHelperBase(ABC):
    """The base temperature helper class."""

    def __init__(
        self, unit_holder: PropertyHolder | None, use_preferred_unit: bool
    ) -> None:
        """Set up."""
        self.unit_holder = unit_holder
        self.use_preferred_unit = use_preferred_unit
        self.current_holder: PropertyHolder | None = None
        self.value: float | None = None
        self.unit: str | None = None
        self.min_value: float | None = None
        self.max_value: float | None = None

    @property
    def is_active(self) -> bool:
        """Check whether this helper is active or not."""
        return self.current_holder is not None

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        if self.current_holder is None:
            return None

        if PropertyHolder.is_valid_range(self.min_value, self.max_value):
            return self.min_value

        return self.current_holder.min

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        if self.current_holder is None:
            return None

        if PropertyHolder.is_valid_range(self.min_value, self.max_value):
            return self.max_value

        return self.current_holder.max

    @property
    def step(self) -> float | None:
        """Return the step value."""
        if self.current_holder is None:
            return None

        return self.current_holder.step

    def _get_target_unit(self, preferred_unit: str | None = None) -> str | None:
        """Return the target unit to calculate."""
        if self.use_preferred_unit and preferred_unit is not None:
            return preferred_unit

        if self.unit_holder is not None and isinstance(
            target_unit := self.unit_holder.get_value(), str
        ):
            return target_unit.upper()

        return None

    def _update(
        self, holder_group: TemperatureGroup | None, preferred_unit: str | None = None
    ) -> float | None:
        """Internal update logic."""
        holder: PropertyHolder | None = None
        value: Any = None
        unit: str | None = None
        min_value: float | None = None
        max_value: float | None = None

        if holder_group:
            if (
                preferred_unit is not None
                and (holders := holder_group.get(preferred_unit)) is not None
                and (holder := holders.get("value")) is not None
            ):
                value = holder.get_value()
                unit = preferred_unit

                if (min_holder := holders.get("min")) is not None:
                    min_value = min_holder.get_value()
                if (max_holder := holders.get("max")) is not None:
                    max_value = max_holder.get_value()
            elif (holders := holder_group.get("_")) is not None and (
                holder := holders.get("value")
            ) is not None:
                value = holder.get_value()
                unit = holder.get_unit()

                if (min_holder := holders.get("min")) is not None:
                    min_value = min_holder.get_value()
                if (max_holder := holders.get("max")) is not None:
                    max_value = max_holder.get_value()

        self.current_holder = holder
        self.value = value
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        return value


class TemperatureHelper(TemperatureHelperBase):
    """A helper class that select a temperature property holder that is valid."""

    def __init__(
        self,
        holder_group: TemperatureGroup,
        *,
        unit_holder: PropertyHolder | None = None,
        use_preferred_unit: bool = False,
    ) -> None:
        """Set up."""
        super().__init__(unit_holder, use_preferred_unit)

        self.holder_group = holder_group

    def update(self, preferred_unit: str | None = None) -> float | None:
        """Actually update holder, value and unit."""
        return self._update(self.holder_group, self._get_target_unit(preferred_unit))


class ClimateTemperatureHelper(TemperatureHelperBase):
    """A helper class that select a temperature property holder that is valid."""

    def __init__(
        self,
        hvac_temperature_map: TemperatureHvacMap,
        *,
        unit_holder: PropertyHolder | None = None,
        use_preferred_unit: bool = False,
        use_wildcard_holder: bool = False,
    ) -> None:
        """Set up."""
        super().__init__(unit_holder, use_preferred_unit)

        self.hvac_temperature_map = hvac_temperature_map
        self.use_wildcard_holder = use_wildcard_holder

    def update(self, hvac_mode: str, preferred_unit: str | None) -> float | None:
        """Update the current holder and then return the value."""
        # In this case, use only one holder(key: "_") regardless of hvac mode.
        if self.use_wildcard_holder:
            hvac_mode = "_"

        return self._update(
            self.hvac_temperature_map.get(hvac_mode),
            self._get_target_unit(preferred_unit),
        )

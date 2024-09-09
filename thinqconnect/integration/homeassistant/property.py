from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
"""The extended property interface for Home Assistant."""

import inspect
from enum import Enum, auto
from collections import deque
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from datetime import time
from typing import Any

from thinqconnect import PROPERTY_READABLE, PROPERTY_WRITABLE, ConnectBaseDevice
from thinqconnect.devices.const import Location
from thinqconnect.devices.const import Property as ThinQPropety


class ActiveMode(Enum):
    """A list of mode that represents read-write mode of property/state."""

    READ_ONLY = auto()
    WRITE_ONLY = auto()
    READABLE = auto()
    WRITABLE = auto()
    READ_WRITE = auto()


@dataclass(kw_only=True, frozen=True)
class PropertyOption:
    """A class tha contains options for creating property holder."""

    alt_setter: Callable[[ConnectBaseDevice, Any], Awaitable[None]] | None = None


class PropertyHolder:
    """A class that represents lg thinq property."""

    def __init__(
        self,
        key: str,
        device_api: ConnectBaseDevice,
        profile: dict[str, Any],
        *,
        location: str | None = None,
        option: PropertyOption | None = None,
    ) -> None:
        """Initialize a property."""
        super().__init__()

        self.key = key
        self.api = (
            device_api.get_sub_device(Location(location))
            if location is not None and location in Location
            else None
        ) or device_api
        self.profile = profile or {}
        self.location = location
        self.setter = self._retrieve_setter()
        self.option = option or PropertyOption()
        self.data_type = self.profile.get("type")
        self.rw_mode: str | None = None

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        data = self._get_profile_data()

        if self.data_type == "enum" and isinstance(data, list):
            return [item.lower() if isinstance(item, str) else item for item in data]

        if self.data_type == "boolean" and data is True:
            return ["false", "true"]

        return None

    @property
    def min(self) -> float | None:
        """Return the minimim value."""
        if isinstance(data := self._get_profile_data(), dict):
            return data.get("min")

        return None

    @property
    def max(self) -> float | None:
        """Return the maximim value."""
        if isinstance(data := self._get_profile_data(), dict):
            return data.get("max")

        return None

    @property
    def step(self) -> float | None:
        """Return the step value."""
        if isinstance(data := self._get_profile_data(), dict):
            return data.get("step")

        return None

    @property
    def unit(self) -> str | None:
        """Return the unit."""
        if isinstance(unit := self.profile.get("unit"), dict) and isinstance(
            unit_value := unit.get("value"), dict
        ):
            unit = unit_value.get(PROPERTY_WRITABLE) or unit_value.get(
                PROPERTY_READABLE
            )

        return str(unit) if unit else None

    def _get_profile_data(self) -> Any | None:
        """Return the data of profile."""
        if self.rw_mode:
            return self.profile.get(self.rw_mode)

        return self.profile.get(PROPERTY_WRITABLE) or self.profile.get(
            PROPERTY_READABLE
        )

    def _retrieve_setter(self) -> Callable[[Any], Awaitable[Any]] | None:
        """Retrieve the setter method."""
        for name, func in inspect.getmembers(self.api):
            if inspect.iscoroutinefunction(func) and name == f"set_{self.key}":
                return func

        return None

    def is_mode_available(self, active_mode: ActiveMode | None) -> bool:
        """Check whether if mode is available."""
        readable = self.profile.get(PROPERTY_READABLE, False)
        writable = self.profile.get(PROPERTY_WRITABLE, False)

        if active_mode is ActiveMode.READ_ONLY:
            return readable and not writable

        if active_mode is ActiveMode.WRITE_ONLY:
            return not readable and writable

        if active_mode is ActiveMode.READABLE:
            return readable

        if active_mode is ActiveMode.WRITABLE:
            return writable

        if active_mode is ActiveMode.READ_WRITE:
            return readable and writable

        return True

    def set_rw_mode(self, active_mode: ActiveMode | None) -> None:
        """Set read-write mode from the given active mode."""
        if not self.is_mode_available(active_mode):
            return

        if active_mode in (ActiveMode.READ_ONLY, ActiveMode.READABLE):
            self.rw_mode = PROPERTY_READABLE
        else:
            self.rw_mode = PROPERTY_WRITABLE

    def get_value(self) -> Any:
        """Return the value of property."""
        if self.key not in ThinQPropety:
            return None

        status = self.api.get_status(ThinQPropety(self.key))
        if status is not None and self.data_type in ["enum", "boolean"]:
            return str(status).lower()

        return status

    def get_value_as_bool(self) -> bool:
        """Return the value as boolean type."""
        return PropertyHolder.to_boolean_value(self.get_value())

    def get_unit(self) -> Any:
        """Return the unit on runtime."""
        if self.key in ThinQPropety and isinstance(
            value := self.api.get_status(ThinQPropety(self.key)), dict
        ):
            return value.get("unit")

        return self.unit

    async def async_set(self, value: Any) -> None:
        """Set the value of property."""
        value = self._convert_value(value)

        if self.option.alt_setter is not None:
            await self.option.alt_setter(self.api, value)
        elif self.setter is not None:
            await self.setter(value)

    def _convert_value(self, value: Any) -> Any:
        """Convert the given value to acceptable value for thinq api."""
        if (
            isinstance(value, (int, float))
            and self.step is not None
            and self.step.is_integer()
        ):
            return int(value)

        if isinstance(value, str):
            if self.data_type == "enum":
                return value.upper()

            if self.data_type == "boolean" and value in ("false", "true"):
                return value == "true"

        return value

    @staticmethod
    def to_boolean_value(value: Any) -> bool:
        """Convert the given value to boolean type."""
        if not value:
            return False

        if isinstance(value, str):
            return value.lower() == "power_on" or value.lower() == "true"

        return bool(value)

    def dump(self) -> str:
        """Dump the current status."""
        messages: list[str] = []
        messages.append(f"{self.key}:{self.location}[")
        messages.append(f"options={self.options},")
        messages.append(f"range={self.min}-{self.max}:{self.step},")
        messages.append(f"unit(profile)={self.unit},unit(runtime)={self.get_unit()},")
        messages.append(f"type={self.data_type},value={self.get_value()}]")
        return "".join(messages)


class PropertyState:
    """A class that represents state of property."""

    def __init__(self, holders: Iterable[PropertyHolder] | None = None) -> None:
        """Set up a state."""
        self.mode = None
        self.holders = deque(holders) if holders else deque()
        self.value: Any = None
        self.unit: str | None = None
        self.is_on: bool | None = None
        self.current_temp: float | None = None
        self.target_temp: float | None = None
        self.target_temp_high: float | None = None
        self.target_temp_low: float | None = None
        self.hvac_mode: str | None = None
        self.fan_mode: str | None = None
        self.humidity: int | None = None
        self.support_temperature_range: bool = False

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return None

    @property
    def min(self) -> float | None:
        """Return the minimim value."""
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

    def can_activate(self, active_mode: ActiveMode | None) -> bool:
        """Check whether state can be activated with the given mode."""
        if active_mode is None:
            return True

        if not self.holders:
            return False

        # Check if whether all holders can set the given mode.
        for holder in self.holders:
            if not holder.is_mode_available(active_mode):
                return False

        for holder in self.holders:
            holder.set_rw_mode(active_mode)

        return True

    def update(self) -> None:
        """Update the state."""

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""

    def dump(self) -> str:
        """Dump the current status."""
        return "PropertyState(Empty)"


class SinglePropertyState(PropertyState):
    """A class that implementats state that matches only one property."""

    def __init__(self, holder: PropertyHolder) -> None:
        """Set up a state."""
        super().__init__([holder])

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return self.holders[0].options

    @property
    def min(self) -> float | None:
        """Return the minimim value."""
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

    def update(self) -> None:
        """Update the state."""
        self.value = self.holders[0].get_value()
        self.is_on = self.holders[0].get_value_as_bool()
        self.unit = self.holders[0].get_unit()

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        return await self.holders[0].async_set(value)

    def dump(self) -> str:
        """Dump the current status."""
        return f"SinglePropertyState({self.holders[0].dump()})"


@dataclass(kw_only=True, frozen=True)
class SelectivePropertyStateSpec:
    """A specification to create selective property state."""

    origin_key: str
    selective_keys: tuple[str, ...] = field(default_factory=tuple)


class SelectivePropertyState(PropertyState):
    """A class that implementats state that select property on runtime."""

    def __init__(self, origin_key: str, holders: Iterable[PropertyHolder]) -> None:
        """Set up a state."""
        super().__init__(holders)

        self.origin_key = origin_key

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return self.holders[0].options

    @property
    def min(self) -> float | None:
        """Return the minimim value."""
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

    def update(self) -> None:
        """Update the state."""
        for _ in range(len(self.holders)):
            if (
                isinstance(value := self.holders[0].get_value(), dict)
                and (data := value.get(self.origin_key)) is not None
            ):
                self.value = data
                self.is_on = PropertyHolder.to_boolean_value(data)
                self.unit = value.get("unit")
                return

            self.holders.rotate(-1)

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        return await self.holders[0].async_set(value)

    def dump(self) -> str:
        """Dump the current status."""
        holder_dumps = [f"{holder.dump(),}" for holder in self.holders]
        message = "".join(holder_dumps)
        return f"SelectivePropertyState(origin_key={self.origin_key}/{message})"


@dataclass(kw_only=True, frozen=True)
class TimerPropertyStateSpec:
    """A specification to create timer property state."""

    hour_key: str
    minute_key: str
    time_format: str | None = None


class TimerPropertyState(PropertyState):
    """A class that implementats state that has timer properties."""

    def __init__(
        self,
        hour_holder: PropertyHolder,
        minute_holder: PropertyHolder,
        *,
        time_format: str | None = None,
    ) -> None:
        """Set up a state."""
        super().__init__([hour_holder, minute_holder])

        self.hour_holder = hour_holder
        self.minute_holder = minute_holder
        self.time_format = "%H:%M" if time_format is None else time_format

    @property
    def location(self) -> str | None:
        """Return the location."""
        # Since all holders must be in the same location,
        # we only need to check the hour_holder's location.
        return self.hour_holder.location

    def update(self) -> None:
        """Update the state."""
        hour = self.hour_holder.get_value()
        minute = self.minute_holder.get_value()

        if not isinstance(hour, int):
            hour = 0
        if not isinstance(minute, int):
            minute = 0

        self.value = time(hour, minute).strftime(self.time_format)

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""

    def dump(self) -> str:
        """Dump the current status."""
        messages: list[str] = []
        messages.append(f"TimerPropertyState(format={self.time_format}/")
        messages.append(f"{self.hour_holder.dump()},{self.minute_holder.dump()})")
        return "".join(messages)


@dataclass(kw_only=True, frozen=True)
class ClimateTemperatureSpec:
    """A specification for climate temperature controll."""

    current_temp_key: str
    target_temp_key: str | None = None
    target_temp_low_key: str | None = None
    target_temp_high_key: str | None = None
    unit_key: str | None = None


@dataclass(kw_only=True, frozen=True)
class ClimatePropertyStateSpec:
    """A specification to create climate property state."""

    power_key: str
    hvac_mode_key: str
    temperature_specs: ClimateTemperatureSpec
    temperature_range_specs: ClimateTemperatureSpec | None = None
    fan_mode_keys: tuple[str, ...] = field(default_factory=tuple)
    humidity_key: str | None = None


class ClimatePropertyState(PropertyState):
    """A class that implementats state that has climate properties."""

    def __init__(
        self,
        power_holder: PropertyHolder,
        hvac_mode_holder: PropertyHolder,
        current_temp_holder: PropertyHolder,
        target_temp_holder: PropertyHolder,
        *,
        target_temp_low_holder: PropertyHolder | None = None,
        target_temp_high_holder: PropertyHolder | None = None,
        unit_holder: PropertyHolder | None = None,
        current_temp_range_holder: PropertyHolder | None = None,
        target_temp_low_range_holder: PropertyHolder | None = None,
        target_temp_high_range_holder: PropertyHolder | None = None,
        unit_range_holder: PropertyHolder | None = None,
        fan_mode_holder: PropertyHolder | None = None,
        humidity_holder: PropertyHolder | None = None,
    ) -> None:
        """Set up a state."""
        super().__init__()

        self.power_holder = power_holder
        self.hvac_mode_holder = hvac_mode_holder
        self.current_temp_holder = current_temp_holder
        self.target_temp_holder = target_temp_holder
        self.target_temp_low_holder = target_temp_low_holder
        self.target_temp_high_holder = target_temp_high_holder
        self.unit_holder = unit_holder
        self.current_temp_range_holder = current_temp_range_holder
        self.target_temp_low_range_holder = target_temp_low_range_holder
        self.target_temp_high_range_holder = target_temp_high_range_holder
        self.unit_range_holder = unit_range_holder
        self.fan_mode_holder = fan_mode_holder
        self.humidity_holder = humidity_holder
        self.support_temperature_range = (
            self.target_temp_low_range_holder is not None
            and self.target_temp_high_range_holder is not None
        )

    @property
    def min(self) -> float | None:
        """Return the minimim value."""
        if (
            self.support_temperature_range
            and self.hvac_mode == "auto"
            and self.target_temp_low_range_holder is not None
        ):
            return self.target_temp_low_range_holder.min

        if self.hvac_mode == "cool" and self.target_temp_low_holder is not None:
            return self.target_temp_low_holder.min
        if self.hvac_mode == "heat" and self.target_temp_high_holder is not None:
            return self.target_temp_high_holder.min

        return self.target_temp_holder.min

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
        if (
            self.support_temperature_range
            and self.hvac_mode == "auto"
            and self.target_temp_high_range_holder is not None
        ):
            return self.target_temp_high_range_holder.max

        if self.hvac_mode == "cool" and self.target_temp_low_holder is not None:
            return self.target_temp_low_holder.max
        if self.hvac_mode == "heat" and self.target_temp_high_holder is not None:
            return self.target_temp_high_holder.max

        return self.target_temp_holder.max

    @property
    def step(self) -> float | None:
        """Return the step value."""
        if self.support_temperature_range and self.hvac_mode == "auto":
            if self.target_temp_low_range_holder is not None:
                return self.target_temp_low_range_holder.step
            if self.target_temp_high_range_holder is not None:
                return self.target_temp_high_range_holder.step

        if self.hvac_mode == "cool" and self.target_temp_low_holder is not None:
            return self.target_temp_low_holder.step
        if self.hvac_mode == "heat" and self.target_temp_high_holder is not None:
            return self.target_temp_high_holder.step

        return self.target_temp_holder.step

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

    def update(self) -> None:
        """Update the state."""
        self.is_on = self.power_holder.get_value_as_bool()
        self.hvac_mode = self.hvac_mode_holder.get_value()
        self.current_temp = self.current_temp_holder.get_value()

        if self.support_temperature_range and self.hvac_mode == "auto":
            # Device operates in two_set temperature mode.
            if self.target_temp_low_range_holder is not None:
                self.target_temp_low = self.target_temp_low_range_holder.get_value()
            if self.target_temp_high_range_holder is not None:
                self.target_temp_high = self.target_temp_high_range_holder.get_value()
            if self.unit_range_holder is not None:
                self.unit = self.unit_range_holder.get_value()
        else:
            self.target_temp = self.target_temp_holder.get_value()

            if self.unit_holder is not None:
                self.unit = self.unit_holder.get_value()

        if self.fan_mode_holder is not None:
            self.fan_mode = self.fan_mode_holder.get_value()

        if self.humidity_holder is not None:
            self.humidity = self.humidity_holder.get_value()

    async def async_set(self, value: Any) -> None:
        """Set the value of state."""
        await self.power_holder.async_set(value)

    def dump(self) -> str:
        """Dump the current status."""
        holder_dumps: list[str] = []
        holder_dumps.append("ClimatePropertyStateSpec(")
        holder_dumps.append(f"{self.power_holder.dump()},")
        holder_dumps.append(f"{self.hvac_mode_holder.dump()},")
        holder_dumps.append(f"{self.current_temp_holder.dump()},")
        holder_dumps.append(f"{self.target_temp_holder.dump()},")
        if self.target_temp_low_holder is not None:
            holder_dumps.append(f"{self.target_temp_low_holder.dump()},")
        if self.target_temp_high_holder is not None:
            holder_dumps.append(f"{self.target_temp_high_holder.dump()},")
        if self.unit_holder is not None:
            holder_dumps.append(f"{self.unit_holder.dump()},")
        if self.current_temp_range_holder is not None:
            holder_dumps.append(f"{self.current_temp_range_holder.dump()},")
        if self.target_temp_low_range_holder is not None:
            holder_dumps.append(f"{self.target_temp_low_range_holder.dump()},")
        if self.target_temp_high_range_holder is not None:
            holder_dumps.append(f"{self.target_temp_high_range_holder.dump()},")
        if self.unit_range_holder is not None:
            holder_dumps.append(f"{self.unit_range_holder.dump()},")
        if self.fan_mode_holder is not None:
            holder_dumps.append(f"{self.fan_mode_holder.dump()},")
        if self.humidity_holder is not None:
            holder_dumps.append(f"{self.humidity_holder.dump()}")
        return "".join(holder_dumps)

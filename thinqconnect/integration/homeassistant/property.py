"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

# The extended property interface for Home Assistant.

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from thinqconnect import (
    PROPERTY_READABLE,
    PROPERTY_WRITABLE,
    ConnectBaseDevice,
)
from thinqconnect.devices.const import Location
from thinqconnect.devices.const import Property as ThinQProperty


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

        if self.key == ThinQProperty.WIND_STEP and self.data_type == "range":
            if self.min is not None and self.max is not None:
                return [str(i) for i in range(int(self.min), int(self.max) + 1)]

        return None

    @property
    def min(self) -> float | None:
        """Return the minimum value."""
        if isinstance(data := self._get_profile_data(), dict):
            return data.get("min")

        return None

    @property
    def max(self) -> float | None:
        """Return the maximum value."""
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

    def can_activate(self, active_mode: ActiveMode | None) -> bool:
        """Check whether the requested active mode is available or not."""
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
        if not self.can_activate(active_mode):
            return

        if active_mode in (ActiveMode.READ_ONLY, ActiveMode.READABLE):
            self.rw_mode = PROPERTY_READABLE
        else:
            self.rw_mode = PROPERTY_WRITABLE

    def get_value(self) -> Any:
        """Return the value of property."""
        status = self.api.get_status(self.key)  # type: ignore[arg-type]
        if status is None:
            return None

        if self.data_type in ["enum", "boolean"]:
            return str(status).lower()

        if self.key == ThinQProperty.WIND_STEP and self.data_type == "range":
            return str(status)

        return status

    def get_value_as_bool(self) -> bool:
        """Return the value as boolean type."""
        return PropertyHolder.to_boolean_value(self.get_value())

    def get_unit(self) -> Any:
        """Return the unit on runtime."""
        if self.key in ThinQProperty and isinstance(
            value := self.api.get_status(ThinQProperty(self.key)), dict
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
            if self.data_type == "range":
                return int(value)
            if self.data_type == "boolean" and value in ("false", "true"):
                return value == "true"

        return value

    @staticmethod
    def to_boolean_value(value: Any) -> bool:
        """Convert the given value to boolean type."""
        if not value:
            return False

        if isinstance(value, str):
            return (
                value.lower() == "power_on"
                or value.lower() == "true"
                or value.lower() == "on"
            )

        return bool(value)

    @staticmethod
    def is_valid_range(min: float | None, max: float | None) -> bool:
        """Check whether the given values are valid range or not."""
        return min is not None and max is not None and min < max

    def dump(self) -> str:
        """Dump the current status."""
        messages: list[str] = []
        messages.append(f"{str(self)}<")
        messages.append(f"type={self.data_type},")
        messages.append(f"options={self.options},")
        messages.append(f"range={self.min}-{self.max}:{self.step},")
        messages.append(f"unit(profile)={self.unit},unit(runtime)={self.get_unit()},")
        messages.append(f"value={self.get_value()}>")
        return "".join(messages)

    def __str__(self) -> str:
        """Return the short string."""
        if self.location:
            return f"PropertyHolder({self.api.alias}/{self.location}:{self.key})"

        return f"PropertyHolder({self.api.alias}:{self.key}:)"

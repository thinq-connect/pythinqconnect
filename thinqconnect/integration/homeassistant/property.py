"""The extended property interface for Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
import inspect
from collections.abc import Callable, Awaitable
from typing import Any
from thinqconnect import PROPERTY_READABLE, PROPERTY_WRITABLE
from thinqconnect.devices.connect_device import ConnectBaseDevice


class PropertyHolder:
    """A class that represents lg thinq property."""

    def __init__(
        self,
        key: str,
        device_api: ConnectBaseDevice,
        profile: dict[str, Any],
        location: str | None = None,
    ) -> None:
        """Initialize a property."""
        super().__init__()

        self.key = key
        self.api = device_api.get_sub_device(location) or device_api
        self.profile = profile or {}
        self.location = location
        self.setter = self._retrieve_setter()

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        data_type = self.profile.get("type")
        data = self.profile.get(PROPERTY_WRITABLE) or self.profile.get(
            PROPERTY_READABLE
        )

        if data_type == "enum" and isinstance(data, list):
            return list(data)

        if data_type == "boolean" and data is True:
            return [str(False), str(True)]

        return None

    @property
    def min(self) -> Any:
        """Return the minimim value."""
        data = self.profile.get(PROPERTY_WRITABLE) or self.profile.get(
            PROPERTY_READABLE
        )
        return data.get("min") if isinstance(data, dict) else None

    @property
    def max(self) -> Any:
        """Return the maximim value."""
        data = self.profile.get(PROPERTY_WRITABLE) or self.profile.get(
            PROPERTY_READABLE
        )
        return data.get("max") if isinstance(data, dict) else None

    @property
    def step(self) -> Any:
        """Return the step value."""
        data = self.profile.get(PROPERTY_WRITABLE) or self.profile.get(
            PROPERTY_READABLE
        )
        return data.get("step") if isinstance(data, dict) else None

    @property
    def unit(self) -> str | None:
        """Return the unit."""
        unit = self.profile.get("unit")

        if isinstance(unit, dict):
            unit = unit.get("value")
            if isinstance(unit, dict):
                unit = unit.get(PROPERTY_WRITABLE) or unit.get(PROPERTY_READABLE)

        if isinstance(unit, str):
            return unit

        return None

    def _retrieve_setter(self) -> Callable[[Any], Awaitable[Any]] | None:
        """Retrieve the setter method."""
        for name, func in inspect.getmembers(self.api):
            if inspect.iscoroutinefunction(func) and name == f"set_{self.key}":
                return func

        return None

    def get(self) -> Any:
        """Return the value of property."""
        return self.api.get_status(self.key)

    async def async_set(self, value: Any) -> Awaitable[None]:
        """Set the value of property."""
        return await self.setter(value)


class PropertyState:
    """A class that represents state of property."""

    def __init__(self) -> None:
        """Set up a state."""
        self.value: Any = None
        self.unit: str | None = None

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return None

    @property
    def min(self) -> Any:
        """Return the minimim value."""
        return None

    @property
    def max(self) -> Any:
        """Return the minimim value."""
        return None

    @property
    def step(self) -> Any:
        """Return the minimim value."""
        return None

    @property
    def location(self) -> str | None:
        """Return the minimim value."""
        return None

    @property
    def is_on(self) -> bool:
        """Return the value as boolean type."""
        return False

    def update(self) -> None:
        """Update the state."""

    async def async_set(self, value: Any) -> Awaitable[None]:
        """Set the value of state."""


class SinglePropertyState(PropertyState):
    """A class that implementats state that matches only one property."""

    def __init__(self, holder: PropertyHolder) -> None:
        """Set up a state."""
        super().__init__()

        self.holder = holder

    @property
    def options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        return self.holder.options

    @property
    def min(self) -> Any:
        """Return the minimim value."""
        return self.holder.min

    @property
    def max(self) -> Any:
        """Return the minimim value."""
        return self.holder.max

    @property
    def step(self) -> Any:
        """Return the minimim value."""
        return self.holder.step

    @property
    def location(self) -> str | None:
        """Return the minimim value."""
        return self.holder.location

    @property
    def is_on(self) -> bool:
        """Return the value as power state."""
        if self.value is None:
            return False

        if isinstance(self.value, str):
            return self.value == "POWER_ON" or self.value.lower() == "true"

        return bool(self.value)

    def update(self) -> None:
        """Update the state."""
        self.value = self.holder.get()

    async def async_set(self, value: Any) -> Awaitable[None]:
        """Set the value of state."""
        return await self.holder.async_set(value)


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
        super().__init__()

        self.hour_holder = hour_holder
        self.minute_holder = minute_holder
        self.time_format = "%H:%M" if time_format is None else time_format

    def update(self) -> None:
        """Update the state."""
        hour = self.hour_holder.get()
        minute = self.minute_holder.get()

        if not isinstance(hour, int):
            hour = 0
        if not isinstance(minute, int):
            minute = 0

        self.value = time(hour, minute).strftime(self.time_format)

    async def async_set(self, value: Any) -> Awaitable[None]:
        """Set the value of state."""

"""Property in LG ThinQ device profile."""

from __future__ import annotations

import inspect
import logging
import math
from collections import deque
from collections.abc import Awaitable, Callable
from enum import Enum, auto
from typing import Any

from ... import PROPERTY_READABLE, PROPERTY_WRITABLE, ThinQAPIException
from ...devices.connect_device import TYPE, UNIT, ConnectBaseDevice, ConnectDeviceProfile
from ...devices.const import Property as propertyc

_LOGGER = logging.getLogger(__name__)


POWER_ON = "POWER_ON"
NONE_KEY = "_"


class Range:
    """Contains a range type of data."""

    def __init__(self, value: dict) -> None:
        """Initialize values."""
        self._max = value.get("max", 1)
        self._min = value.get("min", 0)
        self._step = value.get("step", 1)

    @property
    def max(self) -> int | float:
        """Return the maximum value."""
        return self._max

    @property
    def min(self) -> int | float:
        """Return the minimum value."""
        return self._min

    @min.setter
    def min(self, value: float):
        """Return the minimum value."""
        self._min = value

    @property
    def step(self) -> int | float:
        """Returns the step value."""
        return self._step

    def validate(self, value: Any) -> bool:
        """Check if the given value is valid."""
        if (isinstance(value, (int, float))) and math.isclose(value % self.step, 0):
            return self.min <= value <= self.max

        return False

    def clamp(self, value: float) -> int | float:
        """Force to clamp the value."""
        candidate: float = int(value // self.step) * self.step
        return max(min(candidate, self.max), self.min)

    def to_options(self) -> list[str]:
        """Convert data to options list."""
        options: list[str] = []

        value = self.min
        while value < self.max:
            options.append(str(value))
            value += self.step

        options.append(str(self.max))
        return options

    @classmethod
    def create(cls, profile: dict[str, Any]) -> Range | None:
        """Create a range instance."""
        value: Any = profile.get(PROPERTY_WRITABLE) or profile.get(PROPERTY_READABLE)
        return cls(value) if isinstance(value, dict) else None

    @staticmethod
    def range_to_options(profile: dict[str, Any]) -> list[str]:
        """Create a range instance and then convert it to options."""
        value_range = Range.create(profile)
        return value_range.to_options() if value_range else []

    def __str__(self) -> str:
        """Return a string representation."""
        return f"Range(max={self._max}, min={self._min}, step={self._step})"


class PropertyMode(Enum):
    """Modes for how to control properties."""

    # The default operation mode.
    DEFAULT = auto()

    # A mode that dynamically selects from the list of keys assigned to
    # children.
    SELECTIVE = auto()

    # A mode that combines the key list assigned to children and
    # operates like a single property.
    COMBINED = auto()

    # A mode that has several child properties with feature assigned to
    # featured map.
    FEATURED = auto()


class Property:
    """A class that implementats lg thinq property."""

    def __init__(
        self,
        key: str,
        device_api: ConnectBaseDevice,
        *,
        profile: dict[str, Any] | None = None,
        location: str | None = None,
    ) -> None:
        """Initialize a property."""
        self._key: str = key
        self._profile: dict[str, Any] = profile or {}

        # If location is NONE_KEY("_") then it should be None.
        self._location: str | None = None if location == NONE_KEY else location
        self._api: ConnectBaseDevice = device_api.get_sub_device(self._location) or device_api

        self._children: deque[Property] = deque()
        self._getter_name: str | None = self._retrieve_getter_name()
        self._setter_name: str | None = self._retrieve_setter_name()
        self._setter: Callable[[Any], Awaitable] | None = self._retrieve_setter()
        self._unit: str | None = self._retrieve_unit()
        self._unit_provider: Property | None = None
        self._range: Range | None = self._retrieve_range()
        self._options: list[str] | None = self._retrieve_options()

    @property
    def api(self) -> ConnectBaseDevice:
        """Returns the device api."""
        return self._api

    @property
    def profile(self) -> dict[str, Any]:
        """Returns the profile data."""
        return self._profile

    @property
    def location(self) -> str | None:
        """Returns the location."""
        return self._location

    @property
    def key(self) -> str:
        """Returns the key."""
        return self._key

    @property
    def range(self) -> Range | None:
        """Returns the range if exist."""
        return self._range

    @property
    def options(self) -> list[str] | None:
        """Returns the options if exist."""
        return self._options

    @property
    def unit(self) -> str | None:
        """Returns the unit if exist."""
        return self._unit

    @property
    def readable(self) -> bool:
        """Returns ture if readable property, otherwise false."""
        return self.profile.get(PROPERTY_READABLE, False)

    @property
    def writable(self) -> bool:
        """Returns ture if writable property, otherwise false."""
        return self.profile.get(PROPERTY_WRITABLE, False)

    @property
    def children(self) -> Property | None:
        """Check whether the property has a child."""
        return self._children

    @property
    def has_child(self) -> bool:
        """Check whether the property has a child."""
        return bool(self._children)

    @property
    def tag(self) -> str:
        """Returns the tag string."""
        if self.location:
            return f"[{self.api.alias}][{self.location}][{self.key}]"

        return f"[{self.api.alias}][{self.key}]"

    def add_child(self, child: Property) -> None:
        """Add a child property."""
        self._children.append(child)

    def set_unit_provider(self, unit_provider: Property) -> None:
        """Set an unit provider."""
        self._unit_provider = unit_provider

    def _retrieve_getter_name(self) -> str:
        """Retrieve the getter name."""
        return self.key

    def _retrieve_setter_name(self) -> str:
        """Retrieve the setter name."""
        return f"set_{self.key}"

    def _retrieve_setter(self) -> Callable[[Any], Awaitable] | None:
        """Retrieve the setter method."""
        for name, func in inspect.getmembers(self.api):
            if inspect.iscoroutinefunction(func) and name == self._setter_name:
                return func

        return None

    def _retrieve_unit(self) -> str | None:
        """Retrieve a unit of data from the given profile."""
        unit: Any = self.profile.get(UNIT)

        if isinstance(unit, dict):
            unit = unit.get("value")
            if isinstance(unit, dict):
                unit = unit.get(PROPERTY_WRITABLE) or unit.get(PROPERTY_READABLE)

        if isinstance(unit, str):
            _LOGGER.debug("%s _retrieve_unit: %s", self.tag, unit)
            return unit

        return None

    def _retrieve_range(self) -> Range | None:
        """Retrieve a range type of data from the given profile."""
        value_range = Range.create(self.profile)
        if value_range:
            _LOGGER.debug("%s retrieve_range: %s", self.tag, value_range)
            return value_range

        return None

    def _retrieve_options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        options: list[str] | None = None

        value_type: Any = self.profile.get(TYPE)
        value: Any = self.profile.get(PROPERTY_WRITABLE) or self.profile.get(PROPERTY_READABLE)

        if value_type == "enum" and isinstance(value, list):
            options = list(value)
        elif value_type == "boolean" and value is True:
            options = [str(False), str(True)]
        else:
            return None

        _LOGGER.debug("%s retrieve_options: %s", self.tag, options)
        return options

    def _validate_value(self, value: Any) -> bool:
        """Validate the given value."""
        if self.range:
            return self.range.validate(value)

        if self.options and isinstance(value, str):
            return value in self.options

        return True

    def _get_value(self, key_for_dict_value: str | None) -> Any:
        """Get the value from the api and update unit internally."""
        value: Any = self.api.get_status(self._getter_name)

        # The data of some properties has both value and unit in
        # dictionary. In this case, the unit in the dictionary has
        # higher priority than the unit provided by the unit provider.
        if isinstance(value, dict):
            self._unit = value.get(UNIT)
            value = value.get(key_for_dict_value)
        elif self._unit_provider:
            self._unit = self._unit_provider.get_value()

        _LOGGER.debug("%s get_value: %s (%s)", self.tag, value, self._getter_name)
        return value

    def get_value(self, key_for_dict_value: str | None = None) -> Any:
        """Return the value of property."""
        return self._get_value(key_for_dict_value)

    def get_value_as_bool(self) -> bool:
        """Return the value of property as boolean type."""
        value: Any = self.get_value()
        if isinstance(value, str):
            return value == POWER_ON or value.lower() == "true"

        return bool(value)

    async def _async_post_value(self, value: Any) -> dict | None:
        """Post the value."""
        if value is None:
            raise ValueError("value is not exist.")
        if not self._setter:
            raise TypeError(f"{self._setter_name} is not exist.")

        _LOGGER.debug(
            "%s async_post_value: %s (%s)",
            self.tag,
            value,
            self._setter_name,
        )
        return await self._setter(value)

    async def async_post_value(self, value: Any) -> None:
        """Request to post the property value."""
        if not self.writable:
            _LOGGER.warning("%s Failed to async_post_value: %s", self.tag, "not writable.")
            raise ThinQAPIException(
                code="0001",
                message="The control command is not supported.",
                headers=None,
            )

        try:
            await self._async_post_value(value)
        except ValueError as e:
            _LOGGER.warning(
                "%s Failed to async_post_value: %s, %s",
                self.tag,
                value,
                e,
            )
        except TypeError as e:
            _LOGGER.warning(
                "%s Failed to async_post_value: %s (%s), %s",
                self.tag,
                value,
                self._setter_name,
                e,
            )
        except Exception:
            raise

    def __str__(self) -> str:
        """Return a string expression."""
        if self.location:
            return f"Property({self.api.alias}:{self.location}:{self.key})"

        return f"Property({self.api.alias}:{self.key})"


class CombinedProperty(Property):
    """A property that operates by combining several properties."""

    @property
    def readable(self) -> bool:
        """Returns ture if readable property, otherwise false."""
        return all(child.readable for child in self._children)

    @property
    def writable(self) -> bool:
        """Returns ture if writable property, otherwise false."""
        return all(child.writable for child in self._children)

    def _retrieve_range(self) -> Range | None:
        """Retrieve a range type of data from the given profile."""
        # Range not applicatble for combinded property.
        return None

    def _retrieve_options(self) -> list[str] | None:
        """Retrieve a list of options from the given profile."""
        # Options not applicatble for combinded property.
        return None

    def _get_value(self, key_for_dict_value: str | None) -> Any:
        """Get the value from the api and update unit internally."""
        values: list[str] = [child.get_value(self.key) for child in self._children]

        _LOGGER.debug("%s get_value: %s", self.tag, values)
        return values

    def __str__(self) -> str:
        """Return a string expression."""
        children_names: list[str] = [child.key for child in self._children]
        return f"{super().__str__()} {children_names}"


class SelectiveProperty(Property):
    """A property that operates by selecting one of several properties."""

    @property
    def range(self) -> Range | None:
        """Returns the range if exist."""
        if self._children:
            return self._children[0].range

        return super().range

    @property
    def options(self) -> list[str] | None:
        """Returns the options if exist."""
        if self._children:
            return self._children[0].options

        return super().options

    @property
    def unit(self) -> str | None:
        """Returns the unit if exist."""
        if self._children:
            return self._children[0].unit

        return self._unit

    @property
    def readable(self) -> bool:
        """Returns ture if readable property, otherwise false."""
        if self._children:
            return self._children[0].readable

        return super().readable

    @property
    def writable(self) -> bool:
        """Returns ture if writable property, otherwise false."""
        if self._children:
            return self._children[0].writable

        return super().writable

    def _get_value(self, key_for_dict_value: str | None) -> Any:
        """Get the value from the api and update unit internally."""

        # Iterates over the children to find one which has a value.
        if self._children:
            for _ in range(len(self._children)):
                value = self._children[0].get_value(self.key)
                if value is not None:
                    return value

                self._children.rotate(-1)

            return None

        return super()._get_value(self.key)

    async def _async_post_value(self, value: Any) -> dict | None:
        """Post the value."""
        if self._children:
            return await self._children[0].async_post_value(value)

        return await super()._async_post_value(value)

    def __str__(self) -> str:
        """Return a string expression."""
        children_names: list[str] = [child.key for child in self._children]
        return f"{super().__str__()} {children_names}"


# A type map for creating property.
PROPERTY_MODE_TYPE_MAP: dict[PropertyMode, type[Property]] = {
    PropertyMode.COMBINED: CombinedProperty,
    PropertyMode.SELECTIVE: SelectiveProperty,
}


def get_prop_profile(profiles: ConnectDeviceProfile, location: str, name: str) -> dict[str, Any] | None:
    """Return the profile for the given location and name."""
    prop_map = (
        profiles.get_sub_profile(location).property_map if location in profiles.locations else profiles.property_map
    )
    return prop_map.get(name) if prop_map else None


def get_profiles(profiles: ConnectDeviceProfile, name: str) -> dict[str, dict[str, Any] | None]:
    """Return the profile map with location as key for the given name."""
    result: dict = {}
    if name in profiles.property_map:
        result[NONE_KEY] = profiles.property_map.get(name)
    for location in profiles.locations:
        sub_profile = profiles.get_sub_profile(location)
        if name in sub_profile.property_map:
            result[location] = sub_profile.property_map.get(name)
    return result


def create_properties(
    device_api: ConnectBaseDevice,
    key: str,
    children_keys: list | None,
    rw_type: str | None,
    mode: PropertyMode = PropertyMode.DEFAULT,
) -> list[Property] | None:
    """Create properties."""
    try:
        profiles = get_profiles(device_api.profiles, key)

        properties: list[Property] = []
        for location, profile in profiles.items():
            if validate_platform_creation(mode, rw_type, profile):
                property = create_property(key, device_api, mode, profile, location)
                properties.append(property)

        # If mode is combined or selective, the parent property can be
        # an empty property. In this case, create virtual profiles only
        # contains location informations from the first child.
        parent: Property = None
        if not profiles and children_keys:
            if validate_platform_creation(mode, rw_type, None):
                parent = create_property(key, device_api, mode, None, NONE_KEY)
                properties.append(parent)
                mode = PropertyMode.DEFAULT
                for child_key in children_keys:
                    if child_profiles := get_profiles(device_api.profiles, child_key):
                        for location, child_profile in child_profiles.items():
                            if validate_platform_creation(PropertyMode.DEFAULT, rw_type, child_profile):
                                child = create_property(
                                    child_key,
                                    device_api,
                                    mode,
                                    child_profile,
                                    location,
                                )
                                parent.add_child(child)

        if not properties:
            _LOGGER.debug(
                "[%s] Failed to create properties: %s, %s",
                device_api.alias,
                key,
                f"No profile. {key}",
            )
            return None

        # Create properties.
        _LOGGER.warning("create_properties key:%s, children_keys:%s", key, children_keys)

        # Filter out invalid properties.
        # A property must have its own profile or at least one child.
        properties = list(filter(lambda p: p.profile or p.has_child, properties))

        _LOGGER.debug(
            "[%s] Creating properties: [%s]",
            device_api.alias,
            ",".join(map(str, properties)),
        )

    except RuntimeError as e:
        _LOGGER.debug(
            "[%s] Failed to create properties: %s, %s",
            device_api.alias,
            key,
            e,
        )
        return None

    return properties


def create_property(
    key: str,
    device_api: ConnectBaseDevice,
    mode: PropertyMode | None,
    profile: dict[str, Any] | None,
    location: str,
) -> Property:
    """Create a property."""
    constructor = PROPERTY_MODE_TYPE_MAP.get(mode, Property)
    prop = constructor(key, device_api, profile=profile, location=location)
    if profile and UNIT in profile:
        unit_profile = get_prop_profile(device_api.profiles, location, propertyc.TEMPERATURE_UNIT)
        if unit_profile:
            prop.set_unit_provider(
                Property(
                    key=propertyc.TEMPERATURE_UNIT,
                    device_api=device_api,
                    profile=unit_profile,
                    location=location,
                )
            )

    return prop


def validate_platform_creation(mode: PropertyMode | None, rw_type: str | None, profile: dict[str, Any] | None) -> bool:
    """Validate whether property can be created for the platform."""
    if not profile:
        # Allow creation for the type which has children.
        return mode != PropertyMode.DEFAULT

    readable: bool = profile.get(PROPERTY_READABLE, False)
    writable: bool = profile.get(PROPERTY_WRITABLE, False)

    # A property must have at least one mode: read or write.
    if not readable and not writable:
        return False

    if rw_type == PROPERTY_WRITABLE:
        return writable

    if rw_type == PROPERTY_READABLE:
        return readable and not writable

    # It is hard to validate for complex type of platform, so pass it.
    return True

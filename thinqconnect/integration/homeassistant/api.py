"""The extended api interface for HomeAssistant."""

from __future__ import annotations

import asyncio
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
from thinqconnect.devices.const import Property as ThinQProperty

from .property import (
    PropertyHolder,
    PropertyState,
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


class ThinQPropertyEx(StrEnum):
    """The extended property definitions for common."""

    CURRENT_JOB_MODE_STICK_CLEANER = auto()
    ERROR = auto()
    NOTIFICATION = auto()


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


TIMER_STATE_MAP = {
    TimerProperty.ABSOLUTE_TO_START: TimerPropertyStateSpec(
        hour_key=ThinQProperty.ABSOLUTE_HOUR_TO_START,
        minute_key=ThinQProperty.ABSOLUTE_MINUTE_TO_START,
        time_format="%I:%M %p",
    ),
    TimerProperty.ABSOLUTE_TO_STOP: TimerPropertyStateSpec(
        hour_key=ThinQProperty.ABSOLUTE_HOUR_TO_STOP,
        minute_key=ThinQProperty.ABSOLUTE_MINUTE_TO_STOP,
        time_format="%I:%M %p",
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

        self.locations = [None] + list(self.device.profiles.locations)

        # The idx map contains all idenfiers in order to get property states.
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
            self.property_map[idx] = PropertyHolder(key, self.device, profile)

        # Create holders for location properties.
        for location in self.device.profiles.locations:
            sub_profile = self.device.profiles.get_sub_profile(location)

            for key, profile in sub_profile.property_map.items():
                idx = self._add_idx(key, location)
                self.property_map[idx] = PropertyHolder(
                    key, self.device, profile, location
                )

    def _setup_states(self) -> None:
        """Set up states of all properties."""
        # Create single property states.
        for idx, holder in self.property_map.items():
            if idx == ThinQPropertyEx.NOTIFICATION:
                # The notification does not stored in device_api.
                # So we create empty state and set value manually.
                self.state_map[idx] = PropertyState()
            else:
                self.state_map[idx] = SinglePropertyState(holder)

        # Create timer property states.
        for key, spec in TIMER_STATE_MAP.items():
            for location in self.locations:
                hour_idx = self._get_idx(spec.hour_key, location)
                minute_idx = self._get_idx(spec.minute_key, location)

                if hour_idx in self.property_map and minute_idx in self.property_map:
                    idx = self._add_idx(key, location)
                    self.state_map[idx] = TimerPropertyState(
                        self.property_map[hour_idx],
                        self.property_map[minute_idx],
                        time_format=spec.time_format,
                    )

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
        holder = self.property_map.get(idx)
        if holder is None:
            return None

        return holder.location

    def get_active_idx(self, key: str) -> list[str]:
        """Return active list of idx for the given key."""
        return self.idx_map.get(key, [])

    async def fetch_data(self) -> dict[str, PropertyState]:
        """Fetch data from API endpoint."""
        response = await self.device.thinq_api.async_get_device_status(
            self.device.device_id
        )
        self.device.set_status(response)

        # Update all states.
        for state in self.state_map.values():
            state.update()

        return self.state_map

    def update_status(self, status: dict[str, Any]) -> dict[str, PropertyState] | None:
        """Update data manually."""
        status = status.get(self.sub_id) if self.sub_id else status
        if not status:
            return None

        self.device.update_status(status)

        # Update all states.
        for state in self.state_map.values():
            state.update()

        return self.state_map

    def update_notification(
        self, message: str | None
    ) -> dict[str, PropertyState] | None:
        """Update notification message manually."""
        state = self.state_map.get(ThinQPropertyEx.NOTIFICATION)
        if state is None:
            return None

        state.value = message
        return self.state_map

    async def post(self, idx: str, data: Any) -> None:
        """Post the data to API endpoint."""
        prop = self.state_map.get(idx)
        if prop is None:
            raise ThinQAPIException(
                code="0001",
                message="The control command is not supported.",
                headers=None,
            )

        await prop.async_set(data)

    async def async_turn_on(self, idx: str) -> None:
        """Turn on device."""
        await self.post(idx, "POWER_ON")

    async def async_turn_off(self, idx: str) -> None:
        """Turn off device."""
        await self.post(idx, "POWER_OFF")


async def async_get_ha_bridge_list(
    thinq_api: ThinQApi,
) -> list[HABridge]:
    """Retrurns a list of bridges."""
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
    except ThinQAPIException:
        return []

    device_group_id = device_info.get("groupId")

    # Create new device api instance.
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

    # For wash-WashtowerDevice, we need to create two ha bridges.
    if isinstance(connect_device, WashtowerDevice):
        dryer_device = connect_device.get_sub_device("dryer")
        dryer_ha_bridge = HABridge(dryer_device, sub_id="dryer")

        washer_device = connect_device.get_sub_device("washer")
        washer_ha_bridge = HABridge(washer_device, sub_id="washer")

        return [dryer_ha_bridge, washer_ha_bridge]

    return [HABridge(connect_device)]

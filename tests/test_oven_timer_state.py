"""Test oven timer state through the public Home Assistant bridge."""

import asyncio
import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from freezegun import freeze_time

from thinqconnect import ThinQAPIErrorCodes, ThinQAPIException
from thinqconnect.devices.oven import OvenDevice
from thinqconnect.integration import (
    HABridge,
    NotConnectedDeviceError,
    OvenTimerPropertyState,
    TimerProperty,
)

START = datetime(2026, 9, 7, 18, 30, tzinfo=timezone.utc)
FIXTURES = Path(__file__).parent / "fixtures" / "oven"


def load_fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


@pytest.fixture
def freezer():
    with freeze_time(START) as frozen:
        yield frozen


@pytest.fixture(params=["UPPER", "LOWER", "OVEN"])
def cavity(request):
    return request.param


@pytest.fixture
def bridge(freezer, cavity):
    device_info = load_fixture("device")
    profile = load_fixture("profile")
    status = load_fixture("status")
    if cavity == "OVEN":
        profile["property"][0]["location"]["locationName"] = "OVEN"
        status[0]["location"]["locationName"] = "OVEN"
    api = AsyncMock()
    api.async_get_device_status.return_value = status
    device = OvenDevice(
        thinq_api=api,
        device_id=device_info["deviceId"],
        device_type=device_info["deviceInfo"]["deviceType"],
        model_name=device_info["deviceInfo"]["modelName"],
        alias=device_info["deviceInfo"]["alias"],
        profile=profile,
        energy_profile=None,
    )
    device.set_status(status)
    result = HABridge(device)
    result.update_status(None)
    return result


@pytest.fixture
def timer(bridge, cavity):
    result = bridge.state_map[f"{cavity.lower()}_{TimerProperty.REMAIN}"]
    assert isinstance(result, OvenTimerPropertyState)
    return result


def push(bridge, cavity, **fields):
    return bridge.update_status([{"location": {"locationName": cavity}, **fields}])


def test_initial_timer_and_stable_countdown(bridge, cavity, timer, freezer):
    assert timer.value == time(0, 10)
    assert timer.end_time == START + timedelta(minutes=10)
    freezer.move_to(START + timedelta(minutes=1, seconds=2))
    push(bridge, cavity, timer={"remainMinute": 9})
    assert timer.value == time(0, 9)
    assert timer.end_time == START + timedelta(minutes=10)
    freezer.move_to(START + timedelta(minutes=2))
    push(bridge, cavity, runState={"currentState": "COOKING_IN_PROGRESS"})
    bridge.update_status(None)
    assert timer.end_time == START + timedelta(minutes=10)


@pytest.mark.parametrize("inactive", ["INITIAL", "DONE", "COOLING"])
@pytest.mark.parametrize("active", ["PREHEATING", "COOKING_IN_PROGRESS"])
def test_restart_requires_fresh_timer(bridge, cavity, timer, freezer, inactive, active):
    push(bridge, cavity, runState={"currentState": inactive})
    assert timer.end_time is None
    freezer.move_to(START + timedelta(minutes=20))
    push(bridge, cavity, runState={"currentState": active})
    assert timer.end_time is None
    push(bridge, cavity, timer={"targetMinute": 10})
    assert timer.end_time is None
    push(bridge, cavity, timer={"remainMinute": 10})
    assert timer.end_time == START + timedelta(minutes=30)


@pytest.mark.parametrize("minutes", [0, 5, 10, 20])
def test_adjustment_and_cancellation(bridge, cavity, timer, freezer, minutes):
    freezer.move_to(START + timedelta(minutes=1))
    push(bridge, cavity, timer={"remainMinute": minutes})
    expected = START + timedelta(minutes=1 + minutes) if minutes else None
    assert timer.end_time == expected


def test_timer_received_while_inactive(bridge, cavity, timer):
    push(bridge, cavity, runState={"currentState": "DONE"}, timer={"remainMinute": 8})
    assert timer.end_time is None
    push(bridge, cavity, runState={"currentState": "PREHEATING"})
    assert timer.end_time is None


def test_other_cavity_does_not_extend_timer(bridge, cavity, timer, freezer):
    other = "LOWER" if cavity != "LOWER" else "UPPER"
    freezer.move_to(START + timedelta(minutes=3))
    push(bridge, other, timer={"remainMinute": 5})
    assert timer.end_time == START + timedelta(minutes=10)
    assert bridge.state_map[
        f"{other.lower()}_{TimerProperty.REMAIN}"
    ].end_time == START + timedelta(minutes=8)


def test_full_response_restores_new_timer(bridge, cavity, timer, freezer):
    push(bridge, cavity, runState={"currentState": "DONE"})
    assert timer.end_time is None
    freezer.move_to(START + timedelta(minutes=20))
    asyncio.run(bridge.fetch_data())
    assert timer.end_time == START + timedelta(minutes=30)


@pytest.mark.parametrize("response", [None, []])
def test_empty_refresh_cannot_restore_cached_timer(bridge, cavity, timer, response):
    push(bridge, cavity, runState={"currentState": "DONE"})
    push(bridge, cavity, runState={"currentState": "COOKING_IN_PROGRESS"})
    bridge.device.thinq_api.async_get_device_status.return_value = response
    asyncio.run(bridge.fetch_data())
    assert timer.end_time is None


def test_fetch_preserves_disconnected_error(bridge):
    bridge.device.thinq_api.async_get_device_status.side_effect = ThinQAPIException(
        ThinQAPIErrorCodes.NOT_CONNECTED_DEVICE, "Not connected", {}
    )
    with pytest.raises(NotConnectedDeviceError):
        asyncio.run(bridge.fetch_data())

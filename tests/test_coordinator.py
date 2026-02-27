"""Tests for Trinnov Altitude coordinator behavior."""

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from homeassistant.core import HomeAssistant

from custom_components.trinnov_altitude.commands import TrinnovAltitudeCommands
from custom_components.trinnov_altitude.coordinator import TrinnovAltitudeCoordinator


def _build_mock_client() -> MagicMock:
    """Build a mock client with realistic v2 surface area for coordinator tests."""
    client = MagicMock()
    client.logger = logging.getLogger("test.trinnov_altitude.coordinator")
    client.state = SimpleNamespace(
        id="ABC123",
        version="4.2.9",
        source="Kaleidescape",
        sources={0: "Kaleidescape", 1: "Apple TV"},
        preset="Movies",
        presets={0: "Built-in", 1: "Movies"},
        synced=True,
    )
    client.start = AsyncMock()
    client.wait_synced = AsyncMock()
    client.stop = AsyncMock()
    client.register_callback = MagicMock()
    client.deregister_callback = MagicMock()
    return client


async def test_coordinator_start_and_shutdown(hass: HomeAssistant) -> None:
    """Coordinator starts client, seeds snapshot, and shuts down cleanly."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )

    await coordinator.async_start(sync_timeout=15.0)

    client.register_callback.assert_called_once()
    client.start.assert_called_once()
    client.wait_synced.assert_called_once_with(15.0)
    assert coordinator.data is not None
    assert coordinator.data.source == "Kaleidescape"

    await coordinator.async_shutdown()
    client.deregister_callback.assert_called_once()
    client.stop.assert_called_once()


async def test_coordinator_push_updates_from_callback(hass: HomeAssistant) -> None:
    """Received-message callbacks should push fresh state snapshots to entities."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    await coordinator.async_start()

    callback = client.register_callback.call_args[0][0]
    client.state.source = "Apple TV"
    callback("received_message", None)
    await hass.async_block_till_done()

    assert coordinator.data is not None
    assert coordinator.data.source == "Apple TV"


async def test_coordinator_ignores_unrelated_events(hass: HomeAssistant) -> None:
    """Unrelated client events should not trigger coordinator updates."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    await coordinator.async_start()
    assert coordinator.data is not None

    original_source = coordinator.data.source
    callback = client.register_callback.call_args[0][0]

    client.state.source = "Apple TV"
    callback("command_sent", None)
    await hass.async_block_till_done()

    assert coordinator.data.source == original_source

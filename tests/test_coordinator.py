"""Tests for Trinnov Altitude coordinator behavior."""

import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant
from trinnov_altitude.exceptions import ConnectionFailedError

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
    client.register_adapter_callback = MagicMock()
    client.deregister_adapter_callback = MagicMock()
    return client


async def test_coordinator_start_and_shutdown(hass: HomeAssistant) -> None:
    """Coordinator starts client, seeds snapshot, and shuts down cleanly."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )

    await coordinator.async_start(sync_timeout=15.0)

    client.register_callback.assert_called_once()
    client.register_adapter_callback.assert_called_once()
    client.start.assert_called_once()
    client.wait_synced.assert_called_once_with(15.0)
    assert coordinator.data is not None
    assert coordinator.data.source == "Kaleidescape"

    await coordinator.async_shutdown()
    client.deregister_callback.assert_called_once()
    client.deregister_adapter_callback.assert_called_once()
    client.stop.assert_called_once()


async def test_coordinator_push_updates_from_callback(hass: HomeAssistant) -> None:
    """Received-message callbacks should push fresh state snapshots to entities."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    await coordinator.async_start()

    callback = client.register_adapter_callback.call_args[0][1]
    client.state.source = "Apple TV"
    callback(None, [], [])
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


async def test_coordinator_updates_on_connection_events(hass: HomeAssistant) -> None:
    """Connected/disconnected events should also push fresh snapshots."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    await coordinator.async_start()
    assert coordinator.data is not None

    callback = client.register_callback.call_args[0][0]
    client.state.source = "Apple TV"
    callback("disconnected", None)
    await hass.async_block_till_done()

    assert coordinator.data.source == "Apple TV"


async def test_coordinator_adapter_update_pushes_snapshot(
    hass: HomeAssistant,
) -> None:
    """Adapter updates should publish latest state snapshots."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    await coordinator.async_start()

    callback = client.register_adapter_callback.call_args[0][1]
    client.state.source = "Blu-ray"
    callback(None, [], [])
    await hass.async_block_till_done()

    assert coordinator.data is not None
    assert coordinator.data.source == "Blu-ray"


async def test_coordinator_shutdown_noop_when_never_started(
    hass: HomeAssistant,
) -> None:
    """Shutdown should be a no-op if startup never ran."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )

    await coordinator.async_shutdown()

    client.deregister_callback.assert_not_called()
    client.deregister_adapter_callback.assert_not_called()
    client.stop.assert_not_called()


async def test_coordinator_async_update_data_returns_snapshot(
    hass: HomeAssistant,
) -> None:
    """Internal update method should return current state snapshot."""
    client = _build_mock_client()
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    await coordinator.async_start()

    snapshot = await coordinator._async_update_data()
    assert snapshot.source == "Kaleidescape"


async def test_coordinator_retry_bootstrap_until_synced_success(
    hass: HomeAssistant,
) -> None:
    """Retry loop should recover after transient connection failures."""
    client = _build_mock_client()
    client.connected = False
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    coordinator._running = True

    attempts = {"count": 0}

    async def start_side_effect() -> None:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise ConnectionFailedError(OSError("network down"))
        client.connected = True

    client.start = AsyncMock(side_effect=start_side_effect)
    client.wait_synced = AsyncMock()

    with patch("custom_components.trinnov_altitude.coordinator.asyncio.sleep", new=AsyncMock()):
        await coordinator._async_retry_bootstrap_until_synced(sync_timeout=5.0)

    assert attempts["count"] == 2
    client.wait_synced.assert_called_once_with(5.0)


async def test_coordinator_retry_bootstrap_handles_cancelled_sleep(
    hass: HomeAssistant,
) -> None:
    """Retry loop should stop cleanly on cancellation."""
    client = _build_mock_client()
    client.connected = False
    client.start = AsyncMock(side_effect=ConnectionFailedError(OSError("offline")))
    coordinator = TrinnovAltitudeCoordinator(
        hass, client, TrinnovAltitudeCommands(client)
    )
    coordinator._running = True

    with patch(
        "custom_components.trinnov_altitude.coordinator.asyncio.sleep",
        new=AsyncMock(side_effect=asyncio.CancelledError),
    ):
        await coordinator._async_retry_bootstrap_until_synced(sync_timeout=5.0)

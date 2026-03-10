"""Coordinator for Trinnov Altitude integration."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from trinnov_altitude.adapter import AltitudeStateAdapter
from trinnov_altitude.exceptions import ConnectionFailedError, ConnectionTimeoutError
from trinnov_altitude.state import AltitudeState

from .lifecycle import PowerStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from trinnov_altitude.client import TrinnovAltitudeClient
    from trinnov_altitude.protocol import Message

    from .commands import TrinnovAltitudeCommands


class TrinnovAltitudeCoordinator(DataUpdateCoordinator[AltitudeState]):
    """Push coordinator for Trinnov Altitude state."""

    _BOOTSTRAP_RETRY_INTERVAL_SECONDS = 5.0

    def __init__(
        self,
        hass: HomeAssistant,
        client: TrinnovAltitudeClient,
        commands: TrinnovAltitudeCommands,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(hass, logger=client.logger, name="trinnov_altitude")
        self.client = client
        self.commands = commands
        self._state_adapter = AltitudeStateAdapter()
        self._callback_registered = False
        self._adapter_callback_registered = False
        self._adapter_callback_handle: Callable[[str, Message | None], None] | None = (
            None
        )
        self._running = False
        self._bootstrap_retry_task: asyncio.Task[None] | None = None
        self._power_status_override: PowerStatus | None = None

    async def async_start(self, sync_timeout: float | None = 10.0) -> None:
        """Start push updates and attempt initial client bootstrap."""
        if not self._callback_registered:
            self.client.register_callback(self._handle_client_event)
            self._callback_registered = True
        if not self._adapter_callback_registered:
            self._adapter_callback_handle = self.client.register_adapter_callback(
                self._state_adapter, self._handle_adapter_update
            )
            self._adapter_callback_registered = True

        self._running = True
        # Publish initial disconnected snapshot so entities can expose turn_on/WOL.
        self.async_set_updated_data(self._snapshot_state())

        try:
            await self.client.start()
            await self.client.wait_synced(sync_timeout)
            self.async_set_updated_data(self._snapshot_state())
        except (ConnectionFailedError, ConnectionTimeoutError, TimeoutError):
            self.client.logger.warning(
                "Initial Trinnov bootstrap failed; keeping integration loaded and retrying in background."
            )
            self._schedule_bootstrap_retry(sync_timeout)

    async def async_shutdown(self) -> None:
        """Stop client and deregister callback."""
        if (
            not self._running
            and not self._callback_registered
            and not self._adapter_callback_registered
        ):
            return

        if self._bootstrap_retry_task is not None:
            self._bootstrap_retry_task.cancel()
            self._bootstrap_retry_task = None

        if self._callback_registered:
            self.client.deregister_callback(self._handle_client_event)
            self._callback_registered = False
        if (
            self._adapter_callback_registered
            and self._adapter_callback_handle is not None
        ):
            self.client.deregister_adapter_callback(self._adapter_callback_handle)
            self._adapter_callback_registered = False
            self._adapter_callback_handle = None
        await self.client.stop()
        self._running = False

    async def _async_update_data(self) -> AltitudeState:
        """Return latest state snapshot."""
        return self._snapshot_state()

    def _snapshot_state(self) -> AltitudeState:
        """Create a stable snapshot for entity reads."""
        return deepcopy(self.client.state)

    @property
    def power_status(self) -> PowerStatus:
        """Return lifecycle state for primary power entities."""
        if self._power_status_override is not None:
            return self._power_status_override

        state = self.data if self.data is not None else self.client.state
        if not self.client.connected:
            return PowerStatus.OFF
        if not state.synced:
            return PowerStatus.BOOTING
        return PowerStatus.READY

    def set_power_status_override(self, status: PowerStatus | None) -> None:
        """Force a temporary lifecycle state until transport catches up."""
        self._power_status_override = status
        self.async_set_updated_data(self._snapshot_state())

    def _handle_client_event(self, event: str, _message: object | None = None) -> None:
        """Forward connection lifecycle events into coordinator updates."""
        if event in {"connected", "disconnected"}:
            self._power_status_override = None
            self.hass.add_job(self._async_push_update)

    def _handle_adapter_update(
        self, _snapshot: object, _deltas: object, _events: object
    ) -> None:
        """Forward adapter updates into coordinator snapshots."""
        if self.client.connected and self.client.state.synced:
            self._power_status_override = None
        self.hass.add_job(self._async_push_update)

    async def _async_push_update(self) -> None:
        """Publish latest client state to entities."""
        self.async_set_updated_data(self._snapshot_state())

    def _schedule_bootstrap_retry(self, sync_timeout: float | None) -> None:
        """Start background bootstrap retries if one is not already running."""
        if (
            self._bootstrap_retry_task is not None
            and not self._bootstrap_retry_task.done()
        ):
            return
        self._bootstrap_retry_task = self.hass.async_create_background_task(
            self._async_retry_bootstrap_until_synced(sync_timeout),
            "trinnov_altitude bootstrap retry",
        )

    async def _async_retry_bootstrap_until_synced(
        self, sync_timeout: float | None
    ) -> None:
        """Retry initial bootstrap so offline-at-start devices recover automatically."""
        try:
            while self._running and not self.client.connected:
                try:
                    await self.client.start()
                    await self.client.wait_synced(sync_timeout)
                    self.async_set_updated_data(self._snapshot_state())
                    return
                except (ConnectionFailedError, ConnectionTimeoutError, TimeoutError):
                    await asyncio.sleep(self._BOOTSTRAP_RETRY_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            return

"""Base Entity for Trinnov Altitude."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, NAME
from .coordinator import TrinnovAltitudeCoordinator

if TYPE_CHECKING:
    from trinnov_altitude.client import TrinnovAltitudeClient
    from trinnov_altitude.state import AltitudeState

    from .commands import TrinnovAltitudeCommands

_LOGGER = logging.getLogger(__name__)


class TrinnovAltitudeEntity(CoordinatorEntity[TrinnovAltitudeCoordinator]):
    """Defines a base Trinnov Altitude entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: TrinnovAltitudeCoordinator) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self._client: TrinnovAltitudeClient = coordinator.client
        self._commands: TrinnovAltitudeCommands = coordinator.commands

        device_id = str(self._client.state.id or "unknown")
        self._attr_unique_id = device_id
        host = self._client.host.strip() if self._client.host else "trinnov"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"{NAME} ({host})",
            model=MODEL,
            manufacturer=MANUFACTURER,
            sw_version=self._client.state.version,
            configuration_url=f"http://{self._client.host}",
        )

    @property
    def _state(self) -> AltitudeState:
        """Return latest coordinator-backed state."""
        if self.coordinator.data is not None:
            return self.coordinator.data
        return self._client.state

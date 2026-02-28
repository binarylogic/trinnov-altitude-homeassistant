"""Sensor platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .coordinator import TrinnovAltitudeCoordinator
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData
from .resolvers import resolve_preset_name, resolve_source_name, resolve_upmixer_value

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from trinnov_altitude.state import AltitudeState


class PowerStatus(StrEnum):
    """Power status states."""

    OFF = "off"
    BOOTING = "booting"
    READY = "ready"


class ConnectionStatus(StrEnum):
    """Connection status states."""

    DISCONNECTED = "disconnected"
    CONNECTED = "connected"


class SyncStatus(StrEnum):
    """Sync status states."""

    SYNCING = "syncing"
    SYNCED = "synced"


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeSensorEntityDescription(SensorEntityDescription):
    """Describes Trinnov Altitude sensor entity."""

    value_fn: Callable[[AltitudeState], StateType]


POWER_STATUS_ICONS = {
    PowerStatus.OFF: "mdi:power-off",
    PowerStatus.BOOTING: "mdi:power-settings",
    PowerStatus.READY: "mdi:power-on",
}


SENSORS: tuple[TrinnovAltitudeSensorEntityDescription, ...] = (
    TrinnovAltitudeSensorEntityDescription(
        key="power_status",
        translation_key="power_status",
        name="Power Status",
        device_class=SensorDeviceClass.ENUM,
        options=[status.value for status in PowerStatus],
        value_fn=lambda _state: PowerStatus.READY,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="audiosync",
        translation_key="audiosync",
        name="Audiosync",
        value_fn=lambda state: state.audiosync,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="connection_status",
        translation_key="connection_status",
        name="Connection Status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[status.value for status in ConnectionStatus],
        value_fn=lambda _state: ConnectionStatus.CONNECTED,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="sync_status",
        translation_key="sync_status",
        name="Sync Status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[status.value for status in SyncStatus],
        value_fn=lambda state: (
            SyncStatus.SYNCED if state.synced else SyncStatus.SYNCING
        ),
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="version",
        translation_key="version",
        name="Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.version,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="device_id",
        translation_key="device_id",
        name="Device ID",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda state: state.id,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="decoder",
        translation_key="decoder",
        name="Decoder",
        value_fn=lambda state: state.decoder,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="preset",
        translation_key="preset",
        name="Preset",
        value_fn=resolve_preset_name,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="source",
        translation_key="source",
        name="Source",
        value_fn=resolve_source_name,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="source_format",
        translation_key="source_format",
        name="Source Format",
        value_fn=lambda state: state.source_format,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="upmixer",
        translation_key="upmixer",
        name="Upmixer",
        value_fn=resolve_upmixer_value,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="volume",
        translation_key="volume",
        name="Volume",
        value_fn=lambda state: state.volume,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeSensor(data.coordinator, description) for description in SENSORS
    )


class TrinnovAltitudeSensor(TrinnovAltitudeEntity, SensorEntity):
    """Representation of a Trinnov Altitude sensor."""

    entity_description: TrinnovAltitudeSensorEntityDescription

    def __init__(
        self,
        coordinator: TrinnovAltitudeCoordinator,
        entity_description: TrinnovAltitudeSensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    @property
    def native_value(self) -> StateType:
        """Return value of sensor."""
        if self.entity_description.key == "power_status":
            if not self._client.connected:
                return PowerStatus.OFF
            if not self._state.synced:
                return PowerStatus.BOOTING
            return PowerStatus.READY
        if self.entity_description.key == "connection_status":
            return (
                ConnectionStatus.CONNECTED
                if self._client.connected
                else ConnectionStatus.DISCONNECTED
            )
        return self.entity_description.value_fn(self._state)

    @property
    def icon(self) -> str | None:
        """Return dynamic icon for power_status sensor."""
        if self.entity_description.key == "power_status":
            return POWER_STATUS_ICONS.get(self.native_value)
        return None

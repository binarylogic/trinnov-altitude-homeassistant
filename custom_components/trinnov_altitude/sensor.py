"""Sensor platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory

from trinnov_altitude.lifecycle import (
    ControlHealth,
    PowerState,
    SyncState,
    TransportState,
)

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

    from trinnov_altitude.adapter import AltitudeSnapshot


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeSensorEntityDescription(SensorEntityDescription):
    """Describes Trinnov Altitude sensor entity."""

    value_fn: Callable[[AltitudeSnapshot], StateType]


POWER_STATUS_ICONS = {
    PowerState.OFF: "mdi:power-off",
    PowerState.WAKING: "mdi:power-settings",
    PowerState.READY: "mdi:power-on",
    PowerState.UNKNOWN: "mdi:power-alert",
}


SENSORS: tuple[TrinnovAltitudeSensorEntityDescription, ...] = (
    TrinnovAltitudeSensorEntityDescription(
        key="power_status",
        translation_key="power_status",
        name="Power Status",
        device_class=SensorDeviceClass.ENUM,
        options=[status.value for status in PowerState],
        value_fn=lambda _state: PowerState.UNKNOWN,
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
        options=[status.value for status in TransportState],
        value_fn=lambda _state: TransportState.DISCONNECTED,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="sync_status",
        translation_key="sync_status",
        name="Sync Status",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[status.value for status in SyncState],
        value_fn=lambda _state: SyncState.UNSYNCED,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="control_health",
        translation_key="control_health",
        name="Control Health",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=[status.value for status in ControlHealth],
        value_fn=lambda _state: ControlHealth.UNAVAILABLE,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="last_error",
        translation_key="last_error",
        name="Last Error",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda _state: None,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="last_error_kind",
        translation_key="last_error_kind",
        name="Last Error Kind",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda _state: None,
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
            return self.coordinator.power_status.value
        if self.entity_description.key == "connection_status":
            return self._snapshot_state.runtime.transport.value
        if self.entity_description.key == "sync_status":
            return self._snapshot_state.runtime.sync.value
        if self.entity_description.key == "control_health":
            return self._snapshot_state.runtime.control.value
        if self.entity_description.key == "last_error":
            error = self._snapshot_state.runtime.last_error
            return error.message if error is not None else None
        if self.entity_description.key == "last_error_kind":
            error = self._snapshot_state.runtime.last_error
            return error.kind.value if error is not None else None
        return self.entity_description.value_fn(self._state)

    @property
    def icon(self) -> str | None:
        """Return dynamic icon for power_status sensor."""
        if self.entity_description.key == "power_status":
            return POWER_STATUS_ICONS.get(self.coordinator.power_status)
        return None

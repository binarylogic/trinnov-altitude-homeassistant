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

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity


class PowerStatus(StrEnum):
    """Power status states."""

    OFF = "off"
    BOOTING = "booting"
    READY = "ready"


if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from trinnov_altitude.trinnov_altitude import TrinnovAltitude


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeSensorEntityDescription(SensorEntityDescription):
    """Describes Trinnov Altitude sensor entity."""

    value_fn: Callable[[TrinnovAltitude], StateType]


def _get_power_status(device: TrinnovAltitude) -> str:
    """Determine the power status of the device."""
    if not device.connected():
        return PowerStatus.OFF
    if not device._initial_sync.is_set():
        return PowerStatus.BOOTING
    return PowerStatus.READY


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
        value_fn=_get_power_status,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="audiosync",
        translation_key="audiosync",
        name="Audiosync",
        value_fn=lambda device: device.audiosync,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="decoder",
        translation_key="decoder",
        name="Decoder",
        value_fn=lambda device: device.decoder,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="preset",
        translation_key="preset",
        name="Preset",
        value_fn=lambda device: device.preset,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="source",
        translation_key="source",
        name="Source",
        value_fn=lambda device: device.source,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="source_format",
        translation_key="source_format",
        name="Source Format",
        value_fn=lambda device: device.source_format,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="upmixer",
        translation_key="upmixer",
        name="Upmixer",
        value_fn=lambda device: device.upmixer,
    ),
    TrinnovAltitudeSensorEntityDescription(
        key="volume",
        translation_key="volume",
        name="Volume",
        value_fn=lambda device: device.volume,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    device: TrinnovAltitude = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeSensor(device, description) for description in SENSORS
    )


class TrinnovAltitudeSensor(TrinnovAltitudeEntity, SensorEntity):
    """Representation of a Trinnov Altitude sensor."""

    entity_description: TrinnovAltitudeSensorEntityDescription

    def __init__(
        self,
        device: TrinnovAltitude,
        entity_description: TrinnovAltitudeSensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(device)
        self.entity_description = entity_description  # type: ignore
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    @property
    def native_value(self) -> StateType:  # type: ignore
        """Return value of sensor."""
        return self.entity_description.value_fn(self._device)

    @property
    def icon(self) -> str | None:
        """Return dynamic icon for power_status sensor."""
        if self.entity_description.key == "power_status":
            return POWER_STATUS_ICONS.get(self.native_value)  # type: ignore
        return None

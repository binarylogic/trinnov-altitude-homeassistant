"""Binary sensor platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.const import PERCENTAGE, EntityCategory

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from trinnov_altitude.trinnov_altitude import TrinnovAltitude

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Trinnov Altitude binary sensor entity."""

    value_fn: Callable[[TrinnovAltitude], bool]


SENSOR_TYPES: tuple[TrinnovAltitudeBinarySensorEntityDescription, ...] = (
    TrinnovAltitudeBinarySensorEntityDescription(
        key="bypass",
        translation_key="bypass",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.bypass or False,
    ),
    TrinnovAltitudeBinarySensorEntityDescription(
        key="dim",
        translation_key="dim",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.dim or False,
    ),
    TrinnovAltitudeBinarySensorEntityDescription(
        key="mute",
        translation_key="mute",
        value_fn=lambda device: device.mute or False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    device: TrinnovAltitude = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeBinarySensor(device, description) for description in SENSOR_TYPES
    )


class TrinnovAltitudeBinarySensor(TrinnovAltitudeEntity, BinarySensorEntity):
    """Representation of a Trinnov Altitude binary sensor."""

    entity_description: TrinnovAltitudeBinarySensorEntityDescription

    def __init__(
        self,
        device: TrinnovAltitude,
        entity_description: TrinnovAltitudeBinarySensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(device)
        self.entity_description = entity_description  # type: ignore
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if binary sensor is on."""
        return self.entity_description.value_fn(self._device)

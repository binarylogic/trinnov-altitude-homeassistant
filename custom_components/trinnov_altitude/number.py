"""Number platform for Trinnov Altitude integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfSoundPressure

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from trinnov_altitude.trinnov_altitude import TrinnovAltitude


# Volume range: -120 dB to 0 dB (capped at 0 for safety)
# Reference level (0 dB) is very loud. Values above 0 dB can damage speakers/hearing.
VOLUME_MIN = -120.0
VOLUME_MAX = 0.0


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    device: TrinnovAltitude = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TrinnovAltitudeVolumeNumber(device)])


class TrinnovAltitudeVolumeNumber(TrinnovAltitudeEntity, NumberEntity):
    """Representation of a Trinnov Altitude volume number entity."""

    _attr_native_min_value = VOLUME_MIN
    _attr_native_max_value = VOLUME_MAX
    _attr_native_step = 0.5
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = UnitOfSoundPressure.DECIBEL
    _attr_translation_key = "volume"
    _attr_name = "Volume"

    def __init__(self, device: TrinnovAltitude) -> None:
        """Initialize number entity."""
        super().__init__(device)
        self._attr_unique_id = f"{self._attr_unique_id}-volume-number"

    @property
    def native_value(self) -> float | None:
        """Return the current volume in dB."""
        return self._device.volume

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume to the specified dB level."""
        await self._device.volume_set(value)

"""Select platform for Trinnov Altitude integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity

if TYPE_CHECKING:
    from trinnov_altitude.trinnov_altitude import TrinnovAltitude

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    device: TrinnovAltitude = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TrinnovAltitudeSourceSelect(device)])


class TrinnovAltitudeSourceSelect(TrinnovAltitudeEntity, SelectEntity):
    """Representation of a Trinnov Altitude source select entity."""

    _attr_translation_key = "source"

    def __init__(self, device: TrinnovAltitude) -> None:
        """Initialize select entity."""
        super().__init__(device)
        self._attr_unique_id = f"{self._attr_unique_id}-source-select"

    @property
    def current_option(self) -> str | None:
        """Return the current source."""
        return self._device.source

    @property
    def options(self) -> list[str]:
        """Return the list of available sources."""
        return list(self._device.sources.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected source."""
        await self._device.source_set_by_name(option)

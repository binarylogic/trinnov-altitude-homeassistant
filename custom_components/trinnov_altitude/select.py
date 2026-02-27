"""Select platform for Trinnov Altitude integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.exceptions import HomeAssistantError

from trinnov_altitude.const import UpmixerMode

from .const import DOMAIN
from .coordinator import TrinnovAltitudeCoordinator
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TrinnovAltitudeSourceSelect(data.coordinator),
            TrinnovAltitudePresetSelect(data.coordinator),
            TrinnovAltitudeUpmixerSelect(data.coordinator),
        ]
    )


class TrinnovAltitudeSourceSelect(TrinnovAltitudeEntity, SelectEntity):
    """Representation of a Trinnov Altitude source select entity."""

    _attr_translation_key = "source"
    _attr_name = "Source"

    def __init__(self, coordinator: TrinnovAltitudeCoordinator) -> None:
        """Initialize select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._attr_unique_id}-source-select"

    @property
    def current_option(self) -> str | None:
        """Return the current source."""
        return self._state.source

    @property
    def options(self) -> list[str]:
        """Return the list of available sources."""
        return list(self._state.sources.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected source."""
        try:
            await self._commands.invoke("source_set_by_name", option, require_ack=True)
        except ValueError as exc:
            raise HomeAssistantError(str(exc)) from exc


class TrinnovAltitudePresetSelect(TrinnovAltitudeEntity, SelectEntity):
    """Representation of a Trinnov Altitude preset select entity."""

    _attr_translation_key = "preset"
    _attr_name = "Preset"

    def __init__(self, coordinator: TrinnovAltitudeCoordinator) -> None:
        """Initialize select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._attr_unique_id}-preset-select"

    @property
    def current_option(self) -> str | None:
        """Return the current preset."""
        return self._state.preset

    @property
    def options(self) -> list[str]:
        """Return the list of available presets."""
        return list(self._state.presets.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected preset."""
        # Find the preset ID from the name
        for pid, name in self._state.presets.items():
            if name == option:
                await self._commands.invoke("preset_set", pid, require_ack=True)
                return


class TrinnovAltitudeUpmixerSelect(TrinnovAltitudeEntity, SelectEntity):
    """Representation of a Trinnov Altitude upmixer select entity."""

    _attr_translation_key = "upmixer"
    _attr_name = "Upmixer"

    def __init__(self, coordinator: TrinnovAltitudeCoordinator) -> None:
        """Initialize select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._attr_unique_id}-upmixer-select"

    @property
    def current_option(self) -> str | None:
        """Return the current upmixer."""
        if self._state.upmixer is None:
            return None
        # Normalize to lowercase to match enum values
        upmixer_lower = self._state.upmixer.lower().replace(" ", "_")
        for mode in UpmixerMode:
            if mode.value == upmixer_lower:
                return mode.value
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available upmixer modes."""
        return [mode.value for mode in UpmixerMode]

    async def async_select_option(self, option: str) -> None:
        """Change the selected upmixer."""
        for mode in UpmixerMode:
            if mode.value == option:
                await self._commands.invoke("upmixer_set", mode, require_ack=True)
                return

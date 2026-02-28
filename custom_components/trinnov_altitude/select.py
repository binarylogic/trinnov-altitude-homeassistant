"""Select platform for Trinnov Altitude integration."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.exceptions import HomeAssistantError

from trinnov_altitude.const import UpmixerMode

from .const import DOMAIN
from .coordinator import TrinnovAltitudeCoordinator
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData
from .resolvers import resolve_preset_name, resolve_source_name, resolve_upmixer_value

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
        return resolve_source_name(self._state)

    @property
    def options(self) -> list[str]:
        """Return the list of available sources."""
        sources = self._source_options()
        return list(sources.keys())

    async def async_select_option(self, option: str) -> None:
        """Change the selected source."""
        source_options = self._source_options()
        source_id = source_options.get(option)
        if source_id is None:
            raise HomeAssistantError(f"Unknown source option: {option}")
        try:
            await self._commands.invoke("source_set", source_id, require_ack=True)
            self._client.state.current_source_index = source_id
            self._client.state.source = option
            self.coordinator.async_set_updated_data(deepcopy(self._client.state))
        except ValueError as exc:
            raise HomeAssistantError(str(exc)) from exc

    def _source_options(self) -> dict[str, int]:
        """Build stable source options keyed by display name."""
        options: dict[str, int] = {}
        sources = getattr(self._state, "sources", {})
        if isinstance(sources, dict):
            for source_id, source_name in sources.items():
                options[str(source_name)] = int(source_id)

        index = getattr(self._state, "current_source_index", None)
        if isinstance(index, int) and index >= 0 and index not in options.values():
            options[f"Source {index}"] = index

        return options


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
        return resolve_preset_name(self._state)

    @property
    def options(self) -> list[str]:
        """Return the list of available presets."""
        presets = self._preset_options()
        return list(presets.keys())

    async def async_select_option(self, option: str) -> None:
        """Change the selected preset."""
        preset_options = self._preset_options()
        preset_id = preset_options.get(option)
        if preset_id is None:
            raise HomeAssistantError(f"Unknown preset option: {option}")
        await self._commands.invoke("preset_set", preset_id, require_ack=True)
        self._client.state.current_preset_index = preset_id
        self._client.state.preset = option
        self.coordinator.async_set_updated_data(deepcopy(self._client.state))

    def _preset_options(self) -> dict[str, int]:
        """Build stable preset options keyed by display name."""
        options: dict[str, int] = {}
        presets = getattr(self._state, "presets", {})
        if isinstance(presets, dict):
            for preset_id, preset_name in presets.items():
                options[str(preset_name)] = int(preset_id)

        index = getattr(self._state, "current_preset_index", None)
        if isinstance(index, int) and index >= 0 and index not in options.values():
            options[f"Preset {index}"] = index

        return options


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
        return resolve_upmixer_value(self._state)

    @property
    def options(self) -> list[str]:
        """Return the list of available upmixer modes."""
        options = [mode.value for mode in UpmixerMode]
        current = resolve_upmixer_value(self._state)
        if current and current not in options:
            options.append(current)
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the selected upmixer."""
        for mode in UpmixerMode:
            if mode.value == option:
                await self._commands.invoke("upmixer_set", mode, require_ack=True)
                self._client.state.upmixer = option
                self.coordinator.async_set_updated_data(deepcopy(self._client.state))
                return
        raise HomeAssistantError(f"Unknown upmixer option: {option}")

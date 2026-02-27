"""Trinnov Altitude Media Player."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN][entry.entry_id]
    entities = [TrinnovAltitudeMediaPlayer(data.coordinator)]
    async_add_entities(entities)


class TrinnovAltitudeMediaPlayer(TrinnovAltitudeEntity, MediaPlayerEntity):
    """Representation of a Trinnov Altitude device."""

    _attr_device_class = MediaPlayerDeviceClass.RECEIVER
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
    )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        await self._commands.invoke("mute_set", mute)

    async def async_select_source(self, source: str) -> None:
        """Select source."""
        try:
            await self._commands.invoke("source_set_by_name", source, require_ack=True)
        except ValueError as exc:
            raise HomeAssistantError(str(exc)) from exc

    async def async_turn_on(self) -> None:
        """Power on command."""
        self._client.power_on()

    async def async_turn_off(self) -> None:
        """Power off command."""
        await self._commands.invoke("power_off", require_ack=True)

    async def async_volume_up(self) -> None:
        """Turn volume up for media player."""
        await self._commands.invoke("volume_up")

    async def async_volume_down(self) -> None:
        """Turn volume down for media player."""
        await self._commands.invoke("volume_down")

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        percentage = volume * 100.0
        await self._commands.invoke("volume_percentage_set", percentage)

    @property
    def available(self) -> bool:
        """Return if device is available."""
        return self._client.power_on_available() or self._client.connected

    @property
    def input_source(self) -> str | None:
        """Current source."""
        return self._state.source

    @property
    def input_source_list(self) -> list[str] | None:
        """Current source."""
        return list(self._state.sources.values())

    @property
    def is_volume_muted(self) -> bool | None:
        """Boolean if volume is currently muted."""
        return self._state.mute

    @property
    def state(self) -> MediaPlayerState:
        """State of device."""
        if not self._client.connected or not self._state.synced:
            return MediaPlayerState.OFF
        if self._state.source_format:
            return MediaPlayerState.PLAYING
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        percentage = self._client.volume_percentage
        if percentage is None:
            return None
        else:
            return percentage / 100.0

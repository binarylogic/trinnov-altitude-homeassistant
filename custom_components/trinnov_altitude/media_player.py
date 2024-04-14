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
from homeassistant.util.dt import utcnow

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    entities = [TrinnovAltitudeMediaPlayer(hass.data[DOMAIN][entry.entry_id])]
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
        await self._device.mute_set(mute)

    async def async_select_source(self, source: str) -> None:
        """Select source."""
        await self._device.source_set_by_name(source)

    async def async_turn_on(self) -> None:
        """Power on command."""
        self._device.power_on()

    async def async_turn_off(self) -> None:
        """Power off command."""
        await self._device.power_off()

    async def async_volume_up(self) -> None:
        """Turn volume up for media player."""
        await self._device.volume_up()

    async def async_volume_down(self) -> None:
        """Turn volume down for media player."""
        await self._device.volume_down()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        percentage = volume * 100.0
        await self._device.volume_percentage_set(percentage)

    @property
    def available(self) -> bool:  # type: ignore
        """Return if device is available."""
        return self._device.power_on_available() || self._device.connected()

    @property
    def input_source(self) -> str | None:  # type: ignore
        """Current source."""
        return self._device.source

    @property
    def input_source_list(self) -> list[str] | None:  # type: ignore
        """Current source."""
        return list(self._device.sources.values())

    @property
    def is_volume_muted(self) -> bool | None:  # type: ignore
        """Boolean if volume is currently muted."""
        return self._device.mute

    @property
    def state(self) -> MediaPlayerState:  # type: ignore
        """State of device."""
        if self._device.source_format:
            return MediaPlayerState.PLAYING
        if self._device.connected():
            return MediaPlayerState.IDLE
        return MediaPlayerState.OFF

    @property
    def volume_level(self) -> float | None:  # type: ignore
        """Volume level of the media player (0..1)."""
        percentage = self._device.volume_percentage()
        if percentage is None:
            return None
        else:
            return percentage / 100.0

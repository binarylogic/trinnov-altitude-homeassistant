"""Switch platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from trinnov_altitude.trinnov_altitude import TrinnovAltitude


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeSwitchEntityDescription(SwitchEntityDescription):
    """Describes Trinnov Altitude switch entity."""

    value_fn: Callable[[TrinnovAltitude], bool]
    turn_on_fn: Callable[[TrinnovAltitude], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[TrinnovAltitude], Coroutine[Any, Any, None]]


SWITCHES: tuple[TrinnovAltitudeSwitchEntityDescription, ...] = (
    TrinnovAltitudeSwitchEntityDescription(
        key="mute",
        translation_key="mute",
        name="Mute",
        value_fn=lambda device: device.mute or False,
        turn_on_fn=lambda device: device.mute_on(),
        turn_off_fn=lambda device: device.mute_off(),
    ),
    TrinnovAltitudeSwitchEntityDescription(
        key="dim",
        translation_key="dim",
        name="Dim",
        value_fn=lambda device: device.dim or False,
        turn_on_fn=lambda device: device.dim_on(),
        turn_off_fn=lambda device: device.dim_off(),
    ),
    TrinnovAltitudeSwitchEntityDescription(
        key="bypass",
        translation_key="bypass",
        name="Bypass",
        value_fn=lambda device: device.bypass or False,
        turn_on_fn=lambda device: device.bypass_on(),
        turn_off_fn=lambda device: device.bypass_off(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    device: TrinnovAltitude = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeSwitch(device, description) for description in SWITCHES
    )


class TrinnovAltitudeSwitch(TrinnovAltitudeEntity, SwitchEntity):
    """Representation of a Trinnov Altitude switch."""

    entity_description: TrinnovAltitudeSwitchEntityDescription

    def __init__(
        self,
        device: TrinnovAltitude,
        entity_description: TrinnovAltitudeSwitchEntityDescription,
    ) -> None:
        """Initialize switch."""
        super().__init__(device)
        self.entity_description = entity_description
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.entity_description.value_fn(self._device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(self._device)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(self._device)

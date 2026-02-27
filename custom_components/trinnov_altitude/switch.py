"""Switch platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN
from .coordinator import TrinnovAltitudeCoordinator
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeSwitchEntityDescription(SwitchEntityDescription):
    """Describes Trinnov Altitude switch entity."""

    value_fn: Callable[[TrinnovAltitudeSwitch], bool]
    turn_on_fn: Callable[[TrinnovAltitudeSwitch], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[TrinnovAltitudeSwitch], Coroutine[Any, Any, None]]


SWITCHES: tuple[TrinnovAltitudeSwitchEntityDescription, ...] = (
    TrinnovAltitudeSwitchEntityDescription(
        key="mute",
        translation_key="mute",
        name="Mute",
        value_fn=lambda entity: entity._state.mute or False,
        turn_on_fn=lambda entity: entity._commands.invoke("mute_on"),
        turn_off_fn=lambda entity: entity._commands.invoke("mute_off"),
    ),
    TrinnovAltitudeSwitchEntityDescription(
        key="dim",
        translation_key="dim",
        name="Dim",
        value_fn=lambda entity: entity._state.dim or False,
        turn_on_fn=lambda entity: entity._commands.invoke("dim_on"),
        turn_off_fn=lambda entity: entity._commands.invoke("dim_off"),
    ),
    TrinnovAltitudeSwitchEntityDescription(
        key="bypass",
        translation_key="bypass",
        name="Bypass",
        value_fn=lambda entity: entity._state.bypass or False,
        turn_on_fn=lambda entity: entity._commands.invoke("bypass_on"),
        turn_off_fn=lambda entity: entity._commands.invoke("bypass_off"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeSwitch(data.coordinator, description) for description in SWITCHES
    )


class TrinnovAltitudeSwitch(TrinnovAltitudeEntity, SwitchEntity):
    """Representation of a Trinnov Altitude switch."""

    entity_description: TrinnovAltitudeSwitchEntityDescription

    def __init__(
        self,
        coordinator: TrinnovAltitudeCoordinator,
        entity_description: TrinnovAltitudeSwitchEntityDescription,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.entity_description.value_fn(self)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(self)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(self)

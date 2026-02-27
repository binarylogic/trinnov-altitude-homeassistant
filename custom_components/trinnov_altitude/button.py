"""Button platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .const import DOMAIN
from .coordinator import TrinnovAltitudeCoordinator
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from typing import Any

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeButtonEntityDescription(ButtonEntityDescription):
    """Describes Trinnov Altitude button entity."""

    press_fn: Callable[[TrinnovAltitudeButton], Coroutine[Any, Any, None]]


BUTTONS: tuple[TrinnovAltitudeButtonEntityDescription, ...] = (
    TrinnovAltitudeButtonEntityDescription(
        key="acoustic_correction_toggle",
        translation_key="acoustic_correction_toggle",
        name="Acoustic Correction Toggle",
        press_fn=lambda entity: entity._commands.invoke("acoustic_correction_toggle"),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="front_display_toggle",
        translation_key="front_display_toggle",
        name="Front Display Toggle",
        press_fn=lambda entity: entity._commands.invoke("front_display_toggle"),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="level_alignment_toggle",
        translation_key="level_alignment_toggle",
        name="Level Alignment Toggle",
        press_fn=lambda entity: entity._commands.invoke("level_alignment_toggle"),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="optimization_toggle",
        translation_key="optimization_toggle",
        name="Optimization Toggle",
        press_fn=lambda entity: entity._commands.invoke("optimization_toggle"),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="time_alignment_toggle",
        translation_key="time_alignment_toggle",
        name="Time Alignment Toggle",
        press_fn=lambda entity: entity._commands.invoke("time_alignment_toggle"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeButton(data.coordinator, description) for description in BUTTONS
    )


class TrinnovAltitudeButton(TrinnovAltitudeEntity, ButtonEntity):
    """Representation of a Trinnov Altitude button."""

    entity_description: TrinnovAltitudeButtonEntityDescription

    def __init__(
        self,
        coordinator: TrinnovAltitudeCoordinator,
        entity_description: TrinnovAltitudeButtonEntityDescription,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self)

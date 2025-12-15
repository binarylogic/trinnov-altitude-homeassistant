"""Button platform for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from typing import Any

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from trinnov_altitude.trinnov_altitude import TrinnovAltitude


@dataclass(frozen=True, kw_only=True)
class TrinnovAltitudeButtonEntityDescription(ButtonEntityDescription):
    """Describes Trinnov Altitude button entity."""

    press_fn: Callable[[TrinnovAltitude], Coroutine[Any, Any, None]]


BUTTONS: tuple[TrinnovAltitudeButtonEntityDescription, ...] = (
    TrinnovAltitudeButtonEntityDescription(
        key="acoustic_correction_toggle",
        translation_key="acoustic_correction_toggle",
        name="Acoustic Correction Toggle",
        press_fn=lambda device: device.acoustic_correction_toggle(),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="front_display_toggle",
        translation_key="front_display_toggle",
        name="Front Display Toggle",
        press_fn=lambda device: device.front_display_toggle(),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="level_alignment_toggle",
        translation_key="level_alignment_toggle",
        name="Level Alignment Toggle",
        press_fn=lambda device: device.level_alignment_toggle(),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="quick_optimized_toggle",
        translation_key="quick_optimized_toggle",
        name="Quick Optimized Toggle",
        press_fn=lambda device: device.quick_optimized_toggle(),
    ),
    TrinnovAltitudeButtonEntityDescription(
        key="time_alignment_toggle",
        translation_key="time_alignment_toggle",
        name="Time Alignment Toggle",
        press_fn=lambda device: device.time_alignment_toggle(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    device: TrinnovAltitude = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TrinnovAltitudeButton(device, description) for description in BUTTONS
    )


class TrinnovAltitudeButton(TrinnovAltitudeEntity, ButtonEntity):
    """Representation of a Trinnov Altitude button."""

    entity_description: TrinnovAltitudeButtonEntityDescription

    def __init__(
        self,
        device: TrinnovAltitude,
        entity_description: TrinnovAltitudeButtonEntityDescription,
    ) -> None:
        """Initialize button."""
        super().__init__(device)
        self.entity_description = entity_description  # type: ignore
        self._attr_unique_id = f"{self._attr_unique_id}-{entity_description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self._device)

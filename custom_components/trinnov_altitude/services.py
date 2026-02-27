"""Domain services for Trinnov Altitude integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv

from trinnov_altitude.command_bridge import parse_upmixer_mode
from trinnov_altitude.const import UpmixerMode

from .const import (
    ATTR_ENTRY_ID,
    ATTR_PRESET_ID,
    ATTR_SOURCE,
    ATTR_UPMIXER,
    DOMAIN,
    SERVICE_SET_PRESET,
    SERVICE_SET_SOURCE_BY_NAME,
    SERVICE_SET_UPMIXER,
)
from .models import TrinnovAltitudeIntegrationData

SERVICES_DATA_KEY = f"{DOMAIN}_services_registered"


def _resolve_entry_data(
    hass: HomeAssistant, entry_id: str | None
) -> TrinnovAltitudeIntegrationData:
    entries: dict[str, TrinnovAltitudeIntegrationData] = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("No Trinnov Altitude entries are loaded")

    if entry_id:
        data = entries.get(entry_id)
        if data is None:
            raise ServiceValidationError(
                f"Unknown Trinnov Altitude entry_id: {entry_id}",
                translation_domain=DOMAIN,
                translation_key="invalid_entry_id",
                translation_placeholders={"entry_id": entry_id},
            )
        return data

    if len(entries) == 1:
        return next(iter(entries.values()))

    raise ServiceValidationError(
        "Multiple Trinnov Altitude entries loaded; provide entry_id.",
        translation_domain=DOMAIN,
        translation_key="entry_id_required",
    )


async def _async_set_source_by_name(hass: HomeAssistant, call: ServiceCall) -> None:
    entry_id = call.data.get(ATTR_ENTRY_ID)
    source = call.data[ATTR_SOURCE]
    data = _resolve_entry_data(hass, entry_id)
    try:
        await data.commands.invoke("source_set_by_name", source, require_ack=True)
    except ValueError as exc:
        raise ServiceValidationError(str(exc)) from exc


async def _async_set_preset(hass: HomeAssistant, call: ServiceCall) -> None:
    entry_id = call.data.get(ATTR_ENTRY_ID)
    preset_id = call.data[ATTR_PRESET_ID]
    data = _resolve_entry_data(hass, entry_id)
    await data.commands.invoke("preset_set", preset_id, require_ack=True)


async def _async_set_upmixer(hass: HomeAssistant, call: ServiceCall) -> None:
    entry_id = call.data.get(ATTR_ENTRY_ID)
    upmixer = call.data[ATTR_UPMIXER]
    data = _resolve_entry_data(hass, entry_id)
    try:
        mode = parse_upmixer_mode(upmixer)
    except ValueError as exc:
        valid = ", ".join(mode.value for mode in UpmixerMode)
        raise ServiceValidationError(
            str(exc),
            translation_domain=DOMAIN,
            translation_key="invalid_upmixer",
            translation_placeholders={"upmixer": upmixer, "valid": valid},
        ) from exc
    await data.commands.invoke("upmixer_set", mode, require_ack=True)


def async_setup_services(hass: HomeAssistant) -> None:
    """Register domain services once."""
    if hass.data.get(SERVICES_DATA_KEY):
        return

    schema_source = vol.Schema(
        {vol.Optional(ATTR_ENTRY_ID): cv.string, vol.Required(ATTR_SOURCE): cv.string}
    )
    schema_preset = vol.Schema(
        {
            vol.Optional(ATTR_ENTRY_ID): cv.string,
            vol.Required(ATTR_PRESET_ID): vol.Coerce(int),
        }
    )
    schema_upmixer = vol.Schema(
        {vol.Optional(ATTR_ENTRY_ID): cv.string, vol.Required(ATTR_UPMIXER): cv.string}
    )

    async def handle_set_source_by_name(call: ServiceCall) -> None:
        await _async_set_source_by_name(hass, call)

    async def handle_set_preset(call: ServiceCall) -> None:
        await _async_set_preset(hass, call)

    async def handle_set_upmixer(call: ServiceCall) -> None:
        await _async_set_upmixer(hass, call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SOURCE_BY_NAME,
        handle_set_source_by_name,
        schema=schema_source,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PRESET,
        handle_set_preset,
        schema=schema_preset,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_UPMIXER,
        handle_set_upmixer,
        schema=schema_upmixer,
    )
    hass.data[SERVICES_DATA_KEY] = True


def async_unload_services(hass: HomeAssistant) -> None:
    """Unregister domain services."""
    if not hass.data.get(SERVICES_DATA_KEY):
        return
    hass.services.async_remove(DOMAIN, SERVICE_SET_SOURCE_BY_NAME)
    hass.services.async_remove(DOMAIN, SERVICE_SET_PRESET)
    hass.services.async_remove(DOMAIN, SERVICE_SET_UPMIXER)
    hass.data.pop(SERVICES_DATA_KEY, None)

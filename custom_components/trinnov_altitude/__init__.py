"""The Trinnov Altitude integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC, EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from trinnov_altitude.client import TrinnovAltitudeClient
from trinnov_altitude.exceptions import ConnectionFailedError, ConnectionTimeoutError

from .commands import TrinnovAltitudeCommands
from .const import CLIENT_ID, DOMAIN
from .coordinator import TrinnovAltitudeCoordinator
from .models import TrinnovAltitudeIntegrationData
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = [
    Platform.BUTTON,
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.REMOTE,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for Trinnov Altitude."""

    host = entry.data[CONF_HOST].strip()

    # Optional attributes may not be present
    mac = entry.data.get(CONF_MAC)
    mac = mac.strip() if mac else None

    device = TrinnovAltitudeClient(host=host, mac=mac, client_id=CLIENT_ID)
    commands = TrinnovAltitudeCommands(device)

    # Force set the id from the config flow since the device is not guaranteed
    # to be online. This ensures that entities have an id to work with.
    device.state.id = entry.unique_id

    coordinator = TrinnovAltitudeCoordinator(hass, device, commands)

    try:
        await coordinator.async_start()
    except (ConnectionFailedError, ConnectionTimeoutError) as exc:
        await coordinator.async_shutdown()
        raise ConfigEntryNotReady(
            f"Could not connect to Trinnov Altitude at {host}"
        ) from exc
    except TimeoutError as exc:
        await coordinator.async_shutdown()
        raise ConfigEntryNotReady(
            f"Timed out waiting for Trinnov Altitude sync at {host}"
        ) from exc
    except Exception:
        await coordinator.async_shutdown()
        _LOGGER.exception("Unexpected error while starting Trinnov Altitude client")
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = TrinnovAltitudeIntegrationData(
        client=device, coordinator=coordinator, commands=commands
    )
    async_setup_services(hass)

    # Ensure the client is stopped when Home Assistant is stopped.
    async def unload(event: Event) -> None:
        await coordinator.async_shutdown()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, unload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Trinnov Altitude config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN].pop(entry.entry_id)
        await data.coordinator.async_shutdown()
        if not hass.data[DOMAIN]:
            async_unload_services(hass)
            hass.data.pop(DOMAIN, None)

    return unload_ok

"""The Trinnov Altitude integration."""

from __future__ import annotations

from trinnov_altitude.trinnov_altitude import TrinnovAltitude

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC, EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant

from .const import CLIENT_ID, DOMAIN

PLATFORMS: list[str] = [Platform.BINARY_SENSOR, Platform.MEDIA_PLAYER, Platform.REMOTE, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for Trinnov Altitude."""

    host = entry.data[CONF_HOST].strip()

    # Optional attributes may not be present
    mac = entry.data.get(CONF_MAC)
    if mac:
        mac = mac.strip()
    else:
        mac = None

    device = TrinnovAltitude(host=host, mac=mac, client_id=CLIENT_ID)

    # Force set the id from the config glow since the device is not guaranteed
    # to be online. This ensures that entities have an id to work with.
    device.id = entry.unique_id

    # Spawn a task to connect and start listening for events from the device
    device.start_listening(reconnect=True)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device

    # If the device is connected, ensure that we disconnect when Home Assistant is stopped
    async def unload(event: Event) -> None:
        await device.stop_listening()
        await device.disconnect()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, unload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Trinnov Altitude config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await client.stop_listening()
        await client.disconnect()

    return unload_ok

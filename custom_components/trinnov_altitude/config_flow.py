"""Config flow for Trinnov Altitude integration."""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Sequence
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_MAC

from trinnov_altitude.client import TrinnovAltitudeClient
from trinnov_altitude.exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    MalformedMacAddressError,
)

from .const import CLIENT_ID, DOMAIN, NAME

_LOGGER = logging.getLogger(__name__)
DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_MAC): str})
_MAC_PATTERN = re.compile(r"(?i)([0-9a-f]{2}(?::[0-9a-f]{2}){5})")


class TrinnovAltitudeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Trinnov Altitude."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TrinnovAltitudeOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors = {}
        device = None
        if user_input is not None:
            # Required attribute will always be present
            host = user_input[CONF_HOST].strip()
            manual_mac = user_input.get(CONF_MAC)

            try:
                mac = _normalize_manual_mac(manual_mac)
                device = TrinnovAltitudeClient(host=host, client_id=CLIENT_ID)
                await device.start()
                await device.wait_synced()
                if mac is None:
                    mac = await async_discover_mac_address(host)
            except MalformedMacAddressError:
                errors[CONF_MAC] = "invalid_mac"
            except ConnectionFailedError:
                errors[CONF_HOST] = "invalid_host"
            except ConnectionTimeoutError:
                errors["base"] = "cannot_connect"
            except TimeoutError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during Trinnov Altitude setup")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(device.state.id, raise_on_progress=False)
                processed_input = {CONF_HOST: host, CONF_MAC: mac}
                self._abort_if_unique_id_configured(processed_input)
                return self.async_create_entry(
                    title=f"{NAME} ({host})", data=processed_input
                )
            finally:
                if device:
                    await device.stop()

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class TrinnovAltitudeOptionsFlow(OptionsFlow):
    """Handle Trinnov Altitude options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                mac = _normalize_manual_mac(user_input.get(CONF_MAC))
            except MalformedMacAddressError:
                errors[CONF_MAC] = "invalid_mac"
            else:
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data={**self._config_entry.data, CONF_MAC: mac},
                )
                self.hass.config_entries.async_schedule_reload(
                    self._config_entry.entry_id
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MAC,
                        default=self._config_entry.data.get(CONF_MAC, ""),
                    ): str
                }
            ),
            errors=errors,
        )


async def async_discover_mac_address(host: str) -> str | None:
    """Best-effort discovery of a MAC address for a reachable local-network host."""
    for command in (
        ("arp", "-an", host),
        ("ip", "neigh", "show", host),
    ):
        output = await _async_run_command(command)
        if output is None:
            continue
        mac = _extract_mac_address(output)
        if mac is not None:
            return mac
    return None


async def _async_run_command(command: Sequence[str]) -> str | None:
    """Run a local network discovery command and return stdout."""
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except (FileNotFoundError, OSError):
        return None

    stdout, _stderr = await process.communicate()
    if process.returncode != 0:
        return None

    text = stdout.decode(errors="ignore").strip()
    return text or None


def _extract_mac_address(output: str) -> str | None:
    """Extract and normalize the first MAC address from command output."""
    match = _MAC_PATTERN.search(output.replace("-", ":"))
    if match is None:
        return None
    mac = match.group(1)
    try:
        return _normalize_manual_mac(mac)
    except MalformedMacAddressError:
        return None


def _normalize_manual_mac(raw_mac: str | None) -> str | None:
    """Normalize a manually supplied MAC address or return None when blank."""
    if raw_mac is None:
        return None

    mac = raw_mac.strip()
    if not mac:
        return None

    normalized = mac.replace("-", ":").lower()
    TrinnovAltitudeClient.validate_mac(normalized)
    return normalized

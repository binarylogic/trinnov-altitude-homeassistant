"""Config flow for Trinnov Altitude integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_MAC

from trinnov_altitude.client import TrinnovAltitudeClient
from trinnov_altitude.exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    MalformedMacAddressError,
)

from .const import CLIENT_ID, DOMAIN, NAME  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)
DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_MAC): str})


class TrinnovAltitudeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Trinnov Altitude."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors = {}
        device = None
        if user_input is not None:
            # Required attribute will always be present
            host = user_input[CONF_HOST].strip()

            # Optional attributes may not be present
            mac = user_input.get(CONF_MAC)
            mac = mac.strip() if mac else None

            try:
                device = TrinnovAltitudeClient(host=host, mac=mac, client_id=CLIENT_ID)
                await device.start()
                await device.wait_synced()
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
                    title=f"{NAME} ({device.state.id})", data=processed_input
                )
            finally:
                if device:
                    await device.stop()

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

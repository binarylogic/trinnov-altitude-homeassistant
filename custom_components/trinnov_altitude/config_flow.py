"""Config flow for Hello World integration."""

from __future__ import annotations

import logging
from typing import Any

from trinnov_altitude.exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    MalformedMacAddressError,
)
import voluptuous as vol

from homeassistant.config_entries import (
    CONN_CLASS_LOCAL_PUSH,
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import CONF_HOST, CONF_MAC

from . import TrinnovAltitude
from .const import CLIENT_ID, DOMAIN, NAME  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)
DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_MAC): str})


class TrinnovAltitudeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Trinnov Altitude."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_PUSH

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
            if mac:
                mac = mac.strip()
            else:
                mac = None

            try:
                device = TrinnovAltitude(host=host, mac=mac, client_id=CLIENT_ID)
                await device.connect()
                device.start_listening()
                await device.wait_for_initial_sync()
            except MalformedMacAddressError:
                errors[CONF_MAC] = "invalid_mac"
            except ConnectionFailedError:
                errors[CONF_HOST] = "invalid_host"
            except ConnectionTimeoutError:
                errors["base"] = "cannot_connect"
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception(f"Unexpected exception: {e}")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(device.id, raise_on_progress=False)
                processed_input = {CONF_HOST: host, CONF_MAC: mac}
                self._abort_if_unique_id_configured(processed_input)
                return self.async_create_entry(
                    title=f"{NAME} ({device.id})", data=processed_input
                )
            finally:
                if device:
                    await device.stop_listening()
                    await device.disconnect()

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

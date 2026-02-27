"""Remote for Trinnov integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.exceptions import HomeAssistantError

from trinnov_altitude.const import RemappingMode, UpmixerMode
from trinnov_altitude.exceptions import NoMacAddressError, NotConnectedError

from .const import DOMAIN
from .entity import TrinnovAltitudeEntity
from .models import TrinnovAltitudeIntegrationData

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from a config entry."""
    data: TrinnovAltitudeIntegrationData = hass.data[DOMAIN][entry.entry_id]
    entities = [TrinnovAltitudeRemote(data.coordinator)]
    async_add_entities(entities)


VALID_COMMANDS = {
    "acoustic_correction_off",
    "acoustic_correction_on",
    "acoustic_correction_toggle",
    "bypass_off",
    "bypass_on",
    "bypass_toggle",
    "dim_off",
    "dim_on",
    "dim_toggle",
    "front_display_off",
    "front_display_on",
    "front_display_toggle",
    "level_alignment_off",
    "level_alignment_on",
    "level_alignment_toggle",
    "mute_off",
    "mute_on",
    "mute_toggle",
    "page_down",
    "page_up",
    "preset_set",
    "optimization_off",
    "optimization_on",
    "optimization_toggle",
    "remapping_mode_set",
    "source_set",
    "source_set_by_name",
    "time_alignment_off",
    "time_alignment_on",
    "time_alignment_toggle",
    "upmixer_set",
    "volume_adjust",
    "volume_down",
    "volume_percentage_set",
    "volume_ramp",
    "volume_set",
    "volume_up",
}

ACK_REQUIRED_COMMANDS = {
    "power_off",
    "preset_set",
    "source_set",
    "source_set_by_name",
    "upmixer_set",
}


class TrinnovAltitudeRemote(TrinnovAltitudeEntity, RemoteEntity):
    """Representation of a Trinnov Altitude device."""

    _attr_name = None
    _attr_supported_features = RemoteEntityFeature.ACTIVITY

    @property
    def activity_list(self) -> list[str] | None:
        """Returns the list of sources"""
        return list(self._state.sources.values())

    @property
    def current_activity(self) -> str | None:
        """Return the source as the current activity."""
        return self._state.source

    @property
    def is_on(self) -> bool:
        """Return true if device is on and ready."""
        return self._client.connected and self._state.synced

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        if self._client.connected:
            return

        try:
            self._client.power_on()
        except NoMacAddressError as exc:
            raise HomeAssistantError(
                "Trinnov Altitude is not configured with a mac address, which is required to power it on."
            ) from exc

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self._commands.invoke("power_off", require_ack=True)

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to a device."""
        for cmd in command:
            try:
                cmd_parts = cmd.split()  # Split the cmd string by spaces
                method_name = cmd_parts[0]  # The first token is the method name
                args_strings = cmd_parts[1:]  # The rest of the tokens are the arguments

                if method_name not in VALID_COMMANDS:
                    raise HomeAssistantError(
                        f"'{method_name}' is not a valid Trinnov Altitude command"
                    )

                # Convert string arguments to enum types for commands that require them
                typed_args = self._convert_args(method_name, args_strings)
                await self._commands.invoke(
                    method_name,
                    *typed_args,
                    require_ack=method_name in ACK_REQUIRED_COMMANDS,
                )
            except NotConnectedError as exc:
                raise HomeAssistantError(
                    "Trinnov Altitude must be powered on before sending commands"
                ) from exc
            except TypeError as exc:
                raise HomeAssistantError(
                    f"Invalid arguments for command '{method_name}'. Expected format: {method_name} <arg1> <arg2> ..."
                ) from exc
            except ValueError as exc:
                raise HomeAssistantError(str(exc)) from exc

    def _convert_args(self, method_name: str, args: list[str]) -> list[Any]:
        """Convert string arguments to appropriate types based on command."""
        if method_name == "source_set_by_name" and args:
            return [" ".join(args)]
        if method_name == "upmixer_set" and args:
            return [self._string_to_upmixer_mode(args[0])]
        if method_name == "remapping_mode_set" and args:
            return [self._string_to_remapping_mode(args[0])]
        return [self._cast_to_primitive_type(arg) for arg in args]

    def _string_to_upmixer_mode(self, value: str) -> UpmixerMode:
        """Convert a string to UpmixerMode enum (case-insensitive)."""
        value_lower = value.lower()
        for mode in UpmixerMode:
            if mode.value == value_lower:
                return mode
        valid_modes = [mode.value for mode in UpmixerMode]
        raise HomeAssistantError(
            f"Invalid upmixer mode '{value}'. Valid modes are: {', '.join(valid_modes)}"
        )

    def _string_to_remapping_mode(self, value: str) -> RemappingMode:
        """Convert a string to RemappingMode enum (case-insensitive)."""
        value_lower = value.lower()
        for mode in RemappingMode:
            if mode.value.lower() == value_lower:
                return mode
        valid_modes = [mode.value for mode in RemappingMode]
        raise HomeAssistantError(
            f"Invalid remapping mode '{value}'. Valid modes are: {', '.join(valid_modes)}"
        )

    def _cast_to_primitive_type(self, arg: str) -> bool | int | float | str:
        """Casts command arguments to primitive types that the device expects."""

        # Convert to lowercase for boolean checks
        arg_lower = arg.lower()

        if arg_lower == "true":
            return True

        if arg_lower == "false":
            return False

        # Attempt to convert to int or float
        try:
            return int(arg)
        except ValueError:
            pass

        try:
            return float(arg)
        except ValueError:
            pass

        # Return as string if all else fails
        return arg

"""Tests for Trinnov Altitude command service."""

from unittest.mock import AsyncMock, MagicMock

from trinnov_altitude.const import RemappingMode

from custom_components.trinnov_altitude.commands import TrinnovAltitudeCommands


def _mock_client() -> MagicMock:
    client = MagicMock()
    client.command_timeout = 2.0
    client.command = AsyncMock()
    client.mute_on = AsyncMock()
    client.preset_set = AsyncMock()
    client.state.sources = {0: "Kaleidescape", 1: "Apple TV"}
    return client


async def test_invoke_with_ack_for_power_off() -> None:
    """Power off should use raw command + ACK flow when required."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("power_off", require_ack=True)

    client.command.assert_called_once_with(
        "power_off_SECURED_FHZMCH48FE", wait_for_ack=True, ack_timeout=2.0
    )


async def test_invoke_with_ack_for_preset_set() -> None:
    """Preset set should use ACK flow when required."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("preset_set", 3, require_ack=True)

    client.command.assert_called_once_with(
        "loadp 3", wait_for_ack=True, ack_timeout=2.0
    )


async def test_invoke_without_ack_calls_client_method() -> None:
    """Non-ACK call should dispatch to client method."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("mute_on")

    client.mute_on.assert_called_once_with()


async def test_invoke_with_ack_for_source_set_by_name() -> None:
    """Source set by name should resolve to profile id and use ACK flow."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("source_set_by_name", "Apple TV", require_ack=True)

    client.command.assert_called_once_with(
        "profile 1", wait_for_ack=True, ack_timeout=2.0
    )


async def test_invoke_with_ack_for_remapping_mode_set() -> None:
    """Remapping mode should serialize enum value for ACK flow."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke(
        "remapping_mode_set", RemappingMode.MODE_MANUAL, require_ack=True
    )

    client.command.assert_called_once_with(
        "remapping_mode manual", wait_for_ack=True, ack_timeout=2.0
    )

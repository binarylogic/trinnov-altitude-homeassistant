"""Tests for Trinnov Altitude command service."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from trinnov_altitude.const import RemappingMode

from custom_components.trinnov_altitude.commands import TrinnovAltitudeCommands


def _mock_client() -> MagicMock:
    client = MagicMock()
    client.command_timeout = 2.0
    client.command = AsyncMock()
    client.mute_on = AsyncMock()
    client.preset_set = AsyncMock()
    client.source_set = AsyncMock()
    client.source_set_by_name = AsyncMock()
    client.upmixer_set = AsyncMock()
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
    """Preset set should delegate to the client convergence path."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("preset_set", 3, require_ack=True)

    client.preset_set.assert_called_once_with(3)
    client.command.assert_not_called()


async def test_invoke_without_ack_calls_client_method() -> None:
    """Non-ACK call should dispatch to client method."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("mute_on")

    client.mute_on.assert_called_once_with()


async def test_invoke_with_ack_for_source_set_by_name() -> None:
    """Source set by name should delegate to the client convergence path."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("source_set_by_name", "Apple TV", require_ack=True)

    client.source_set.assert_called_once_with(1)
    client.command.assert_not_called()


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


async def test_invoke_with_ack_for_upmixer_set() -> None:
    """Upmixer set should delegate to the client convergence path."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("upmixer_set", "dolby", require_ack=True)

    client.upmixer_set.assert_called_once_with("dolby")
    client.command.assert_not_called()


async def test_invoke_source_set_by_name_unknown_source_raises() -> None:
    """Unknown source names should fail before dispatching to the client."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    with pytest.raises(ValueError, match="Unknown source name: Missing"):
        await commands.invoke("source_set_by_name", "Missing", require_ack=True)


async def test_invoke_source_set_by_name_requires_single_arg() -> None:
    """Source-by-name requires exactly one argument."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    with pytest.raises(ValueError, match="expects exactly one source name"):
        await commands.invoke(
            "source_set_by_name", "Apple TV", "Extra", require_ack=True
        )


async def test_invoke_with_ack_for_unknown_method_falls_back_to_client_method() -> None:
    """Unknown ACK methods should call the client method directly when no raw line exists."""
    client = _mock_client()
    client.page_up = AsyncMock()
    commands = TrinnovAltitudeCommands(client)

    await commands.invoke("page_up", require_ack=True)

    client.page_up.assert_called_once_with()
    client.command.assert_not_called()


def test_build_line_source_set_by_name_resolves_profile() -> None:
    """Raw line builder should resolve source names to profile ids."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    assert commands._build_line("source_set_by_name", ("Apple TV",)) == "profile 1"


def test_build_line_source_set_by_name_unknown_source_raises() -> None:
    """Raw line builder should reject unknown source names."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    with pytest.raises(ValueError, match="Unknown source name: Missing"):
        commands._build_line("source_set_by_name", ("Missing",))


def test_build_line_upmixer_uses_raw_string_when_value_attr_missing() -> None:
    """Raw line builder should accept plain string upmixer values."""
    client = _mock_client()
    commands = TrinnovAltitudeCommands(client)

    assert commands._build_line("upmixer_set", ("dolby",)) == "upmixer dolby"

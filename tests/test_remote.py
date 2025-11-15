"""Test the Trinnov Altitude remote platform."""

from unittest.mock import AsyncMock

import pytest
from trinnov_altitude.exceptions import NoMacAddressError, NotConnectedError

from homeassistant.components.remote import (
    ATTR_ACTIVITY,
    ATTR_COMMAND,
    SERVICE_SEND_COMMAND,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .test_init import mock_config_entry


async def test_remote(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test remote entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test remote entity
    state = hass.states.get("remote.trinnov_altitude_abc123")
    assert state
    assert state.state == "on"  # connected() returns True
    assert state.attributes.get(ATTR_ACTIVITY) == "Kaleidescape"
    assert state.attributes.get("activity_list") == ["Kaleidescape", "Apple TV", "Blu-ray"]


async def test_remote_turn_on(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test turning on remote (power on device)."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "remote",
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
        },
        blocking=True,
    )

    mock_device.power_on.assert_called_once()


async def test_remote_turn_on_no_mac(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test turning on remote without MAC address raises error."""
    mock_device = mock_setup_entry.return_value
    mock_device.power_on.side_effect = NoMacAddressError

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError, match="mac address"):
        await hass.services.async_call(
            "remote",
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
            },
            blocking=True,
        )


async def test_remote_turn_off(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test turning off remote (power off device)."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "remote",
        SERVICE_TURN_OFF,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
        },
        blocking=True,
    )

    mock_device.power_off.assert_called_once()


async def test_remote_send_command_simple(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending simple commands."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Send mute_on command
    await hass.services.async_call(
        "remote",
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
            ATTR_COMMAND: ["mute_on"],
        },
        blocking=True,
    )

    mock_device.mute_on.assert_called_once()


async def test_remote_send_command_with_args(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending commands with arguments."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Send volume_set command with dB value
    await hass.services.async_call(
        "remote",
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
            ATTR_COMMAND: ["volume_set -35.5"],
        },
        blocking=True,
    )

    mock_device.volume_set.assert_called_once_with(-35.5)


async def test_remote_send_command_with_int_arg(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending commands with integer arguments."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Send preset_set command with integer
    await hass.services.async_call(
        "remote",
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
            ATTR_COMMAND: ["preset_set 2"],
        },
        blocking=True,
    )

    mock_device.preset_set.assert_called_once_with(2)


async def test_remote_send_command_with_string_arg(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending commands with string arguments."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value
    mock_device.upmixer_set = AsyncMock()

    # Send upmixer_set command with string
    await hass.services.async_call(
        "remote",
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
            ATTR_COMMAND: ["upmixer_set Native"],
        },
        blocking=True,
    )

    mock_device.upmixer_set.assert_called_once_with("Native")


async def test_remote_send_multiple_commands(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending multiple commands."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Send multiple commands
    await hass.services.async_call(
        "remote",
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
            ATTR_COMMAND: ["mute_on", "volume_set -40.0", "source_set 1"],
        },
        blocking=True,
    )

    mock_device.mute_on.assert_called_once()
    mock_device.volume_set.assert_called_once_with(-40.0)
    mock_device.source_set.assert_called_once_with(1)


async def test_remote_send_invalid_command(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending invalid command raises error."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError, match="not a valid"):
        await hass.services.async_call(
            "remote",
            SERVICE_SEND_COMMAND,
            {
                ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
                ATTR_COMMAND: ["invalid_command"],
            },
            blocking=True,
        )


async def test_remote_send_command_not_connected(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending command when device not connected raises error."""
    mock_device = mock_setup_entry.return_value
    mock_device.mute_on = AsyncMock(side_effect=NotConnectedError)

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError, match="powered on"):
        await hass.services.async_call(
            "remote",
            SERVICE_SEND_COMMAND,
            {
                ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
                ATTR_COMMAND: ["mute_on"],
            },
            blocking=True,
        )


async def test_remote_send_command_invalid_args(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sending command with invalid arguments raises error."""
    mock_device = mock_setup_entry.return_value
    mock_device.volume_set = AsyncMock(side_effect=TypeError("Invalid argument"))

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError, match="Invalid arguments"):
        await hass.services.async_call(
            "remote",
            SERVICE_SEND_COMMAND,
            {
                ATTR_ENTITY_ID: "remote.trinnov_altitude_abc123",
                ATTR_COMMAND: ["volume_set invalid"],
            },
            blocking=True,
        )


async def test_remote_is_off_when_disconnected(hass: HomeAssistant, mock_config_entry, mock_trinnov_device_offline, mock_setup_entry):
    """Test remote shows off state when device is disconnected."""
    mock_setup_entry.return_value = mock_trinnov_device_offline

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("remote.trinnov_altitude_abc123")
    assert state.state == "off"

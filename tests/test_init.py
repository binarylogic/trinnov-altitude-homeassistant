"""Test the Trinnov Altitude integration initialization."""

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.trinnov_altitude.const import CLIENT_ID, DOMAIN


async def test_async_setup_entry(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test setting up the integration."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify device was created with correct parameters
    mock_setup_entry.assert_called_once_with(
        host="192.168.1.100",
        mac="00:11:22:33:44:55",
        client_id=CLIENT_ID,
    )

    # Verify device started listening
    mock_device = mock_setup_entry.return_value
    mock_device.start_listening.assert_called_once_with(reconnect=True)

    # Verify platforms were set up
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]


async def test_async_setup_entry_without_mac(hass: HomeAssistant, mock_setup_entry):
    """Test setting up the integration without MAC address."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Trinnov Altitude (ABC123)",
        data={
            CONF_HOST: "192.168.1.100",
        },
        unique_id="ABC123",
    )
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify device was created with None MAC
    mock_setup_entry.assert_called_once_with(
        host="192.168.1.100",
        mac=None,
        client_id=CLIENT_ID,
    )


async def test_async_unload_entry(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test unloading the integration."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Unload the entry
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify cleanup
    mock_device.stop_listening.assert_called_once()
    mock_device.disconnect.assert_called_once()

    # Verify entry removed from hass.data
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]

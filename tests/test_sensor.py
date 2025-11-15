"""Test the Trinnov Altitude sensor platform."""

from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.core import HomeAssistant

from custom_components.trinnov_altitude.const import DOMAIN

from .test_init import mock_config_entry


async def test_sensors(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sensor entities are created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test audiosync sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_audiosync")
    assert state
    assert state.state == "Master"

    # Test decoder sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_decoder")
    assert state
    assert state.state == "Dolby Atmos"

    # Test preset sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_preset")
    assert state
    assert state.state == "Movies"

    # Test source sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_source")
    assert state
    assert state.state == "Kaleidescape"

    # Test source_format sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_source_format")
    assert state
    assert state.state == "Dolby TrueHD 7.1"

    # Test upmixer sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_upmixer")
    assert state
    assert state.state == "Native"

    # Test volume sensor
    state = hass.states.get("sensor.trinnov_altitude_abc123_volume")
    assert state
    assert state.state == "-40.0"


async def test_sensor_updates(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sensor entities update when device state changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Simulate device state change
    mock_device.source = "Apple TV"
    mock_device.volume = -35.5

    # Trigger callback
    callback = mock_device.register_callback.call_args[0][0]
    callback("state_changed", None)
    await hass.async_block_till_done()

    # Verify sensor updated
    state = hass.states.get("sensor.trinnov_altitude_abc123_source")
    assert state.state == "Apple TV"

    state = hass.states.get("sensor.trinnov_altitude_abc123_volume")
    assert state.state == "-35.5"


async def test_sensor_none_values(hass: HomeAssistant, mock_config_entry, mock_trinnov_device_offline, mock_setup_entry):
    """Test sensors handle None values correctly."""
    # Override mock to return offline device
    mock_setup_entry.return_value = mock_trinnov_device_offline

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Sensors with None values should show as 'unknown'
    state = hass.states.get("sensor.trinnov_altitude_abc123_source")
    assert state
    assert state.state == "unknown"

    state = hass.states.get("sensor.trinnov_altitude_abc123_volume")
    assert state
    assert state.state == "unknown"

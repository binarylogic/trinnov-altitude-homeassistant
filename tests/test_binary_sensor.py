"""Test the Trinnov Altitude binary sensor platform."""

from homeassistant.core import HomeAssistant


async def test_binary_sensors(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test binary sensor entities are created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test bypass binary sensor
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_bypass")
    assert state
    assert state.state == "off"  # bypass is False

    # Test dim binary sensor
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_dim")
    assert state
    assert state.state == "off"  # dim is False

    # Test mute binary sensor
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_mute")
    assert state
    assert state.state == "off"  # mute is False


async def test_binary_sensor_on_state(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test binary sensors show 'on' when True."""
    mock_device = mock_setup_entry.return_value
    mock_device.bypass = True
    mock_device.dim = True
    mock_device.mute = True

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # All sensors should be "on"
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_bypass")
    assert state.state == "on"

    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_dim")
    assert state.state == "on"

    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_mute")
    assert state.state == "on"


async def test_binary_sensor_updates(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test binary sensor entities update when device state changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Verify initial state
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_mute")
    assert state.state == "off"

    # Simulate mute toggle
    mock_device.mute = True

    # Trigger callback
    callback = mock_device.register_callback.call_args[0][0]
    callback("state_changed", None)
    await hass.async_block_till_done()

    # Verify sensor updated
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_mute")
    assert state.state == "on"


async def test_binary_sensor_none_values(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test binary sensors handle None values correctly (should treat as False)."""
    mock_device = mock_setup_entry.return_value
    mock_device.bypass = None
    mock_device.dim = None
    mock_device.mute = None

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # None values should be treated as "off"
    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_bypass")
    assert state.state == "off"

    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_dim")
    assert state.state == "off"

    state = hass.states.get("binary_sensor.trinnov_altitude_abc123_mute")
    assert state.state == "off"

"""Test the Trinnov Altitude sensor platform."""

from homeassistant.core import HomeAssistant


async def test_power_status_ready(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test power_status sensor shows 'ready' when connected and synced."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert state
    assert state.state == "ready"


async def test_power_status_off(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test power_status sensor shows 'off' when not connected."""
    mock_device = mock_setup_entry.return_value
    mock_device.connected = False

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert state
    assert state.state == "off"


async def test_power_status_booting(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test power_status sensor shows 'booting' when connected but not synced."""
    mock_device = mock_setup_entry.return_value
    mock_device.connected = True
    mock_device.state.synced = False

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert state
    assert state.state == "booting"


async def test_power_status_transitions(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test power_status sensor transitions through states correctly."""
    mock_device = mock_setup_entry.return_value
    mock_device.connected = False
    mock_device.state.synced = False

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Initially off
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert state
    assert state.state == "off"

    # Simulate connection (but not synced yet)
    mock_device.connected = True
    callback = mock_device.register_callback.call_args[0][0]
    callback("connected", None)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert state
    assert state.state == "booting"

    # Simulate sync complete
    mock_device.state.synced = True
    callback = mock_device.register_adapter_callback.call_args[0][1]
    callback(None, [], [])
    await hass.async_block_till_done()

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert state
    assert state.state == "ready"


async def test_sensors(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sensor entities are created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test audiosync sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_audiosync")
    assert state
    assert state.state == "Master"

    # Test decoder sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_decoder")
    assert state
    assert state.state == "Dolby Atmos"

    # Test preset sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_preset")
    assert state
    assert state.state == "Movies"

    # Test source sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "Kaleidescape"

    # Test source_format sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_source_format")
    assert state
    assert state.state == "Dolby TrueHD 7.1"

    # Test upmixer sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_upmixer")
    assert state
    assert state.state == "Native"

    # Test volume sensor
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_volume")
    assert state
    assert state.state == "-40.0"

    # Diagnostic sensors
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_connection_status")
    assert state
    assert state.state == "connected"

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_sync_status")
    assert state
    assert state.state == "synced"

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_version")
    assert state
    assert state.state == "4.2.9"

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_device_id")
    assert state
    assert state.state == "ABC123"


async def test_sensor_updates(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test sensor entities update when device state changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Simulate device state change
    mock_device.state.source = "Apple TV"
    mock_device.state.volume = -35.5

    # Trigger coordinator callback
    callback = mock_device.register_adapter_callback.call_args[0][1]
    callback(None, [], [])
    await hass.async_block_till_done()

    # Verify sensor updated
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "Apple TV"

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_volume")
    assert state
    assert state.state == "-35.5"


async def test_sensor_none_values(
    hass: HomeAssistant,
    mock_config_entry,
    mock_trinnov_device_offline,
    mock_setup_entry,
):
    """Test sensors handle None values correctly."""
    # Override mock to return offline device
    mock_setup_entry.return_value = mock_trinnov_device_offline

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Sensors with None values should show as 'unknown'
    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "unknown"

    state = hass.states.get("sensor.trinnov_altitude_192_168_1_100_volume")
    assert state
    assert state.state == "unknown"

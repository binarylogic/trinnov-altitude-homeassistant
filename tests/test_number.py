"""Test the Trinnov Altitude number platform."""

from homeassistant.components.number import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant


async def test_volume_number(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test volume number entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test volume number entity
    state = hass.states.get("number.trinnov_altitude_abc123_volume_number")
    assert state
    assert state.state == "-40.0"
    assert state.attributes.get("min") == -120.0
    assert state.attributes.get("max") == 0.0
    assert state.attributes.get("step") == 0.5


async def test_volume_number_set_value(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test setting volume via number entity."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Set volume to -35.5 dB
    await hass.services.async_call(
        "number",
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: "number.trinnov_altitude_abc123_volume_number",
            ATTR_VALUE: -35.5,
        },
        blocking=True,
    )

    # Verify device method was called
    mock_device.volume_set.assert_called_once_with(-35.5)


async def test_volume_number_updates(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test volume number entity updates when device state changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Verify initial state
    state = hass.states.get("number.trinnov_altitude_abc123_volume_number")
    assert state.state == "-40.0"

    # Simulate volume change
    mock_device.volume = -30.0

    # Trigger callback
    callback = mock_device.register_callback.call_args[0][0]
    callback("volume_changed", None)
    await hass.async_block_till_done()

    # Verify entity updated
    state = hass.states.get("number.trinnov_altitude_abc123_volume_number")
    assert state.state == "-30.0"


async def test_volume_number_none_value(
    hass: HomeAssistant,
    mock_config_entry,
    mock_trinnov_device_offline,
    mock_setup_entry,
):
    """Test volume number handles None value correctly."""
    mock_setup_entry.return_value = mock_trinnov_device_offline

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Volume is None when device is offline
    state = hass.states.get("number.trinnov_altitude_abc123_volume_number")
    assert state
    assert state.state == "unknown"


async def test_volume_number_min_max_bounds(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test volume number respects min/max bounds."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Set to minimum volume (-120 dB)
    await hass.services.async_call(
        "number",
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: "number.trinnov_altitude_abc123_volume_number",
            ATTR_VALUE: -120.0,
        },
        blocking=True,
    )

    mock_device.volume_set.assert_called_with(-120.0)
    mock_device.volume_set.reset_mock()

    # Set to maximum volume (0 dB - capped for safety)
    await hass.services.async_call(
        "number",
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: "number.trinnov_altitude_abc123_volume_number",
            ATTR_VALUE: 0.0,
        },
        blocking=True,
    )

    mock_device.volume_set.assert_called_with(0.0)

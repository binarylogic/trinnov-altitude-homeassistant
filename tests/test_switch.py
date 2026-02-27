"""Test the Trinnov Altitude switch platform."""

from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant


async def test_switches(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test switch entities are created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test mute switch
    state = hass.states.get("switch.trinnov_altitude_abc123_mute")
    assert state
    assert state.state == STATE_OFF

    # Test dim switch
    state = hass.states.get("switch.trinnov_altitude_abc123_dim")
    assert state
    assert state.state == STATE_OFF

    # Test bypass switch
    state = hass.states.get("switch.trinnov_altitude_abc123_bypass")
    assert state
    assert state.state == STATE_OFF


async def test_mute_switch_turn_on(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test turning on mute switch."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "switch",
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.trinnov_altitude_abc123_mute"},
        blocking=True,
    )

    mock_device.mute_on.assert_called_once()


async def test_mute_switch_turn_off(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test turning off mute switch."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "switch",
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.trinnov_altitude_abc123_mute"},
        blocking=True,
    )

    mock_device.mute_off.assert_called_once()


async def test_switch_reflects_device_state(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test switch state reflects device state."""
    mock_device = mock_setup_entry.return_value
    mock_device.state.mute = True

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("switch.trinnov_altitude_abc123_mute")
    assert state
    assert state.state == STATE_ON

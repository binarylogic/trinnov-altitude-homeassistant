"""Test the Trinnov Altitude button platform."""

from homeassistant.components.button import SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant


async def test_buttons(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test button entities are created."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test mute toggle button exists
    state = hass.states.get("button.trinnov_altitude_abc123_mute_toggle")
    assert state

    # Test dim toggle button exists
    state = hass.states.get("button.trinnov_altitude_abc123_dim_toggle")
    assert state


async def test_mute_toggle_button(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test mute toggle button press."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Press mute toggle button
    await hass.services.async_call(
        "button",
        SERVICE_PRESS,
        {
            ATTR_ENTITY_ID: "button.trinnov_altitude_abc123_mute_toggle",
        },
        blocking=True,
    )

    # Verify device method was called
    mock_device.mute_toggle.assert_called_once()


async def test_dim_toggle_button(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test dim toggle button press."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Press dim toggle button
    await hass.services.async_call(
        "button",
        SERVICE_PRESS,
        {
            ATTR_ENTITY_ID: "button.trinnov_altitude_abc123_dim_toggle",
        },
        blocking=True,
    )

    # Verify device method was called
    mock_device.dim_toggle.assert_called_once()


async def test_button_multiple_presses(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test button can be pressed multiple times."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Press mute button twice
    await hass.services.async_call(
        "button",
        SERVICE_PRESS,
        {
            ATTR_ENTITY_ID: "button.trinnov_altitude_abc123_mute_toggle",
        },
        blocking=True,
    )

    await hass.services.async_call(
        "button",
        SERVICE_PRESS,
        {
            ATTR_ENTITY_ID: "button.trinnov_altitude_abc123_mute_toggle",
        },
        blocking=True,
    )

    # Verify device method was called twice
    assert mock_device.mute_toggle.call_count == 2

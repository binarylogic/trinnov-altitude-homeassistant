"""Test the Trinnov Altitude button platform."""

from homeassistant.components.button import SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant


async def test_buttons(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test button entities are created."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test toggle buttons exist
    assert hass.states.get(
        "button.trinnov_altitude_192_168_1_100_toggle_acoustic_correction"
    )
    assert hass.states.get("button.trinnov_altitude_192_168_1_100_toggle_front_display")
    assert hass.states.get(
        "button.trinnov_altitude_192_168_1_100_toggle_level_alignment"
    )
    assert hass.states.get("button.trinnov_altitude_192_168_1_100_toggle_optimization")
    assert hass.states.get(
        "button.trinnov_altitude_192_168_1_100_toggle_time_alignment"
    )


async def test_acoustic_correction_toggle_button(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test acoustic correction toggle button press."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "button",
        SERVICE_PRESS,
        {
            ATTR_ENTITY_ID: "button.trinnov_altitude_192_168_1_100_toggle_acoustic_correction"
        },
        blocking=True,
    )

    mock_device.acoustic_correction_toggle.assert_called_once()

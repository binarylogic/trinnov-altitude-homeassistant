"""Test the Trinnov Altitude select platform."""

import pytest
from homeassistant.components.select import ATTR_OPTION, SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError


async def test_source_select(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test source select entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test source select entity
    state = hass.states.get("select.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "Kaleidescape"
    assert state.attributes.get("options") == ["Kaleidescape", "Apple TV", "Blu-ray"]


async def test_preset_select(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test preset select entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test preset select entity
    state = hass.states.get("select.trinnov_altitude_192_168_1_100_preset")
    assert state
    assert state.state == "Movies"
    assert state.attributes.get("options") == ["Built-in", "Movies", "Music"]


async def test_source_select_option(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test selecting a source via select entity."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Select "Apple TV" source
    await hass.services.async_call(
        "select",
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_source",
            ATTR_OPTION: "Apple TV",
        },
        blocking=True,
    )

    # Verify source set used command ACK flow
    mock_device.command.assert_called_once_with(
        "profile 1", wait_for_ack=True, ack_timeout=2.0
    )


async def test_preset_select_option(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test selecting a preset via select entity."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Select "Music" preset (ID 2)
    await hass.services.async_call(
        "select",
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_preset",
            ATTR_OPTION: "Music",
        },
        blocking=True,
    )

    # Verify preset set used command ACK flow
    mock_device.command.assert_called_once_with(
        "loadp 2", wait_for_ack=True, ack_timeout=2.0
    )


async def test_select_updates(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test select entities update when device state changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Verify initial state
    state = hass.states.get("select.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "Kaleidescape"

    # Simulate source change
    mock_device.state.source = "Blu-ray"

    # Trigger coordinator callback
    callback = mock_device.register_adapter_callback.call_args[0][1]
    callback(None, [], [])
    await hass.async_block_till_done()

    # Verify entity updated
    state = hass.states.get("select.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "Blu-ray"


async def test_select_none_values(
    hass: HomeAssistant,
    mock_config_entry,
    mock_trinnov_device_offline,
    mock_setup_entry,
):
    """Test select entities handle None values correctly."""
    mock_setup_entry.return_value = mock_trinnov_device_offline

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Source is None when device is offline
    state = hass.states.get("select.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "unknown"

    # Preset is None when device is offline
    state = hass.states.get("select.trinnov_altitude_192_168_1_100_preset")
    assert state
    assert state.state == "unknown"


async def test_preset_select_built_in(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test selecting the built-in preset (ID 0)."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Select "Built-in" preset (ID 0)
    await hass.services.async_call(
        "select",
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_preset",
            ATTR_OPTION: "Built-in",
        },
        blocking=True,
    )

    # Verify preset set used command ACK flow
    mock_device.command.assert_called_once_with(
        "loadp 0", wait_for_ack=True, ack_timeout=2.0
    )


async def test_upmixer_select(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test upmixer select entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("select.trinnov_altitude_192_168_1_100_upmixer")
    assert state
    assert state.state == "native"
    options = state.attributes.get("options", [])
    assert "native" in options
    assert "dolby" in options


async def test_source_select_uses_index_fallback_when_label_missing(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test source select degrades gracefully when source labels are unavailable."""
    mock_device = mock_setup_entry.return_value
    mock_device.state.source = None
    mock_device.state.sources = {}
    mock_device.state.current_source_index = 4

    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("select.trinnov_altitude_192_168_1_100_source")
    assert state
    assert state.state == "Source 4"
    assert "Source 4" in state.attributes.get("options", [])

    await hass.services.async_call(
        "select",
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_source",
            ATTR_OPTION: "Source 4",
        },
        blocking=True,
    )

    mock_device.command.assert_called_once_with(
        "profile 4", wait_for_ack=True, ack_timeout=2.0
    )


async def test_preset_select_uses_index_fallback_when_label_missing(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test preset select degrades gracefully when preset labels are unavailable."""
    mock_device = mock_setup_entry.return_value
    mock_device.state.preset = None
    mock_device.state.presets = {}
    mock_device.state.current_preset_index = 2

    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("select.trinnov_altitude_192_168_1_100_preset")
    assert state
    assert state.state == "Preset 2"
    assert "Preset 2" in state.attributes.get("options", [])

    await hass.services.async_call(
        "select",
        SERVICE_SELECT_OPTION,
        {
            ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_preset",
            ATTR_OPTION: "Preset 2",
        },
        blocking=True,
    )

    mock_device.command.assert_called_once_with(
        "loadp 2", wait_for_ack=True, ack_timeout=2.0
    )


async def test_upmixer_select_preserves_unknown_current_value(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test upmixer select keeps unknown current tokens visible."""
    mock_device = mock_setup_entry.return_value
    mock_device.state.upmixer = "neural x"

    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("select.trinnov_altitude_192_168_1_100_upmixer")
    assert state
    assert state.state == "neural x"
    assert "neural x" in state.attributes.get("options", [])


async def test_preset_select_option_invalid(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test selecting unknown preset is rejected by select validation."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "select",
            SERVICE_SELECT_OPTION,
            {
                ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_preset",
                ATTR_OPTION: "Not A Preset",
            },
            blocking=True,
        )


async def test_upmixer_select_option_invalid(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test selecting unknown upmixer is rejected by select validation."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "select",
            SERVICE_SELECT_OPTION,
            {
                ATTR_ENTITY_ID: "select.trinnov_altitude_192_168_1_100_upmixer",
                ATTR_OPTION: "not_real",
            },
            blocking=True,
        )

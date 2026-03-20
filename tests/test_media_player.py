"""Test the Trinnov Altitude media player platform."""

import logging

import pytest
from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_VOLUME_MUTED,
    SERVICE_SELECT_SOURCE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_SET,
    SERVICE_VOLUME_UP,
    MediaPlayerState,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError


async def test_media_player(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test media player entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test media player entity
    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == MediaPlayerState.PLAYING
    assert state.attributes.get(ATTR_MEDIA_VOLUME_MUTED) is False
    assert state.attributes.get(ATTR_MEDIA_VOLUME_LEVEL) == 0.5


async def test_media_player_playing_state(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test media player shows playing state when source format is present."""
    mock_device = mock_setup_entry.return_value
    mock_device.state.source_format = "Dolby TrueHD 7.1"

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == MediaPlayerState.PLAYING


async def test_media_player_off_state(
    hass: HomeAssistant,
    mock_config_entry,
    mock_trinnov_device_offline,
    mock_setup_entry,
):
    """Test media player shows off state when device is disconnected."""
    mock_setup_entry.return_value = mock_trinnov_device_offline

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == MediaPlayerState.OFF


async def test_media_player_booting_state(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test media player shows on state while the device is booting."""
    mock_device = mock_setup_entry.return_value
    mock_device.connected = True
    mock_device.state.synced = False

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == MediaPlayerState.ON


async def test_media_player_idle_state_when_ready_without_source_format(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test media player shows idle when ready without an active source format."""
    mock_device = mock_setup_entry.return_value
    mock_device.state.source_format = None

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == MediaPlayerState.IDLE


async def test_media_player_select_source_invalid_name_raises_ha_error(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Invalid source names should surface as HomeAssistantError."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(HomeAssistantError, match="Unknown source name: Bad Source"):
        await hass.services.async_call(
            "media_player",
            SERVICE_SELECT_SOURCE,
            {
                ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
                ATTR_INPUT_SOURCE: "Bad Source",
            },
            blocking=True,
        )


async def test_media_player_volume_level_none_when_percentage_missing(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Volume level should be None when the device has no percentage reading."""
    mock_device = mock_setup_entry.return_value
    mock_device.volume_percentage = None

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.attributes.get(ATTR_MEDIA_VOLUME_LEVEL) is None


async def test_media_player_unavailable_when_not_connected_and_no_wake_path(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Media player should be unavailable if it is neither connected nor wakeable."""
    mock_device = mock_setup_entry.return_value
    mock_device.connected = False
    mock_device.power_on_available.return_value = False

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == "unavailable"


async def test_media_player_turn_on(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry, caplog
):
    """Test turning on media player."""
    caplog.set_level(
        logging.DEBUG,
        logger="custom_components.trinnov_altitude.media_player",
    )
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "media_player",
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
        },
        blocking=True,
    )

    mock_device.power_on.assert_called_once()
    assert "Wake-on-LAN requested via media_player" in caplog.text
    assert "host=192.168.1.100" in caplog.text
    assert "mac=00:11:22:33:44:55" in caplog.text


async def test_media_player_turn_off(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test turning off media player."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "media_player",
        SERVICE_TURN_OFF,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
        },
        blocking=True,
    )

    mock_device.command.assert_called_once_with(
        "power_off_SECURED_FHZMCH48FE", wait_for_ack=True, ack_timeout=2.0
    )

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    assert state.state == MediaPlayerState.OFF

    power_status = hass.states.get("sensor.trinnov_altitude_192_168_1_100_power_status")
    assert power_status
    assert power_status.state == "off"


async def test_media_player_volume_up(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test volume up."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "media_player",
        SERVICE_VOLUME_UP,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
        },
        blocking=True,
    )

    mock_device.volume_up.assert_called_once()


async def test_media_player_volume_down(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test volume down."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "media_player",
        SERVICE_VOLUME_DOWN,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
        },
        blocking=True,
    )

    mock_device.volume_down.assert_called_once()


async def test_media_player_set_volume(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test setting volume level."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Set volume to 75% (0.75)
    await hass.services.async_call(
        "media_player",
        SERVICE_VOLUME_SET,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
            ATTR_MEDIA_VOLUME_LEVEL: 0.75,
        },
        blocking=True,
    )

    # Should convert to percentage
    mock_device.volume_percentage_set.assert_called_once_with(75.0)


async def test_media_player_mute(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test muting volume."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Mute
    await hass.services.async_call(
        "media_player",
        SERVICE_VOLUME_MUTE,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
            ATTR_MEDIA_VOLUME_MUTED: True,
        },
        blocking=True,
    )

    mock_device.mute_set.assert_called_once_with(True)
    mock_device.mute_set.reset_mock()

    # Unmute
    await hass.services.async_call(
        "media_player",
        SERVICE_VOLUME_MUTE,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
            ATTR_MEDIA_VOLUME_MUTED: False,
        },
        blocking=True,
    )

    mock_device.mute_set.assert_called_once_with(False)


async def test_media_player_select_source(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test selecting source."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    await hass.services.async_call(
        "media_player",
        SERVICE_SELECT_SOURCE,
        {
            ATTR_ENTITY_ID: "media_player.trinnov_altitude_192_168_1_100",
            ATTR_INPUT_SOURCE: "Apple TV",
        },
        blocking=True,
    )

    mock_device.source_set.assert_called_once_with(1)


async def test_media_player_available_when_offline_with_mac(
    hass: HomeAssistant,
    mock_config_entry,
    mock_trinnov_device_offline,
    mock_setup_entry,
):
    """Test media player is available when offline if MAC address is configured."""
    mock_device = mock_trinnov_device_offline
    mock_device.power_on_available = lambda: True
    mock_setup_entry.return_value = mock_device

    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("media_player.trinnov_altitude_192_168_1_100")
    assert state
    # Should be available even when offline because power_on_available returns True
    assert state.state == MediaPlayerState.OFF

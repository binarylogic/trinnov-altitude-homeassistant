"""Test the Trinnov Altitude number platform."""

import asyncio
import contextlib
from unittest.mock import patch

import pytest
from homeassistant.components.number import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry
from trinnov_altitude.client import TrinnovAltitudeClient
from trinnov_altitude.exceptions import CommandConvergenceTimeoutError
from trinnov_altitude.mocks import MockTrinnovAltitudeServer

from custom_components.trinnov_altitude.const import CLIENT_ID, DOMAIN


async def test_volume_number(hass: HomeAssistant, mock_config_entry, mock_setup_entry):
    """Test volume number entity is created with correct state."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Test volume number entity
    state = hass.states.get("number.trinnov_altitude_192_168_1_100_volume")
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
            ATTR_ENTITY_ID: "number.trinnov_altitude_192_168_1_100_volume",
            ATTR_VALUE: -35.5,
        },
        blocking=True,
    )

    # Verify device method was called
    mock_device.volume_set.assert_called_once_with(-35.5)


async def test_volume_number_uses_db_wire_flow(hass: HomeAssistant, socket_enabled):
    """Volume number should send absolute dB once and request volume readback."""
    server = MockTrinnovAltitudeServer(host="127.0.0.1", port=0)
    server.volume = -22.0
    await server.start_server()

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Trinnov Altitude (127.0.0.1)",
        data={
            CONF_HOST: "127.0.0.1",
            CONF_MAC: "00:11:22:33:44:55",
            CLIENT_ID: "test_client",
        },
        unique_id="ABC123",
    )

    def client_factory(host: str, mac: str | None, client_id: str):
        return TrinnovAltitudeClient(
            host=host,
            port=server.port,
            mac=mac,
            client_id=client_id,
            auto_reconnect=False,
            connect_timeout=1.0,
            command_timeout=1.0,
            read_timeout=0.1,
        )

    try:
        with patch(
            "custom_components.trinnov_altitude.TrinnovAltitudeClient",
            side_effect=client_factory,
        ):
            config_entry.add_to_hass(hass)
            assert await hass.config_entries.async_setup(config_entry.entry_id)
            await hass.async_block_till_done()

            await hass.services.async_call(
                "number",
                SERVICE_SET_VALUE,
                {
                    ATTR_ENTITY_ID: "number.trinnov_altitude_127_0_0_1_volume",
                    ATTR_VALUE: -17.5,
                },
                blocking=True,
            )

            await asyncio.wait_for(
                _wait_for(lambda: server.received_messages.count("send volume") == 1),
                timeout=1.0,
            )

            assert server.received_messages.count("volume -17.5") == 1
            assert server.received_messages.count("send volume") == 1
    finally:
        await hass.config_entries.async_unload(config_entry.entry_id)
        await server.stop_server()


async def test_volume_number_set_value_surfaces_command_error(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test volume convergence failures surface as Home Assistant errors."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value
    mock_device.volume_set.side_effect = CommandConvergenceTimeoutError(
        "volume -15.0 dB to be active", 5.0
    )

    with pytest.raises(HomeAssistantError, match="volume -15.0"):
        await hass.services.async_call(
            "number",
            SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: "number.trinnov_altitude_192_168_1_100_volume",
                ATTR_VALUE: -15.0,
            },
            blocking=True,
        )


async def test_volume_number_updates(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test volume number entity updates when device state changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value

    # Verify initial state
    state = hass.states.get("number.trinnov_altitude_192_168_1_100_volume")
    assert state
    assert state.state == "-40.0"

    # Simulate volume change
    mock_device.state.volume = -30.0

    # Trigger coordinator callback
    callback = mock_device.register_adapter_callback.call_args[0][1]
    callback(None, [], [])
    await hass.async_block_till_done()

    # Verify entity updated
    state = hass.states.get("number.trinnov_altitude_192_168_1_100_volume")
    assert state
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
    state = hass.states.get("number.trinnov_altitude_192_168_1_100_volume")
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
            ATTR_ENTITY_ID: "number.trinnov_altitude_192_168_1_100_volume",
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
            ATTR_ENTITY_ID: "number.trinnov_altitude_192_168_1_100_volume",
            ATTR_VALUE: 0.0,
        },
        blocking=True,
    )

    mock_device.volume_set.assert_called_with(0.0)


async def _wait_for(predicate):
    if predicate():
        return

    event = asyncio.Event()
    while not predicate():
        with contextlib.suppress(asyncio.TimeoutError, TimeoutError):
            await asyncio.wait_for(event.wait(), timeout=0.01)

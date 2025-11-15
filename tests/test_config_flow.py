"""Test the Trinnov Altitude config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from trinnov_altitude.exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    MalformedMacAddressError,
)

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.trinnov_altitude.const import DOMAIN


async def test_form_user_success(hass: HomeAssistant):
    """Test successful user setup."""
    mock_device = MagicMock()
    mock_device.id = "ABC123"
    mock_device.connect = AsyncMock()
    mock_device.start_listening = MagicMock()
    mock_device.wait_for_initial_sync = AsyncMock()
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_MAC: "00:11:22:33:44:55",
            },
        )

        await hass.async_block_till_done()

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Trinnov Altitude (ABC123)"
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_MAC: "00:11:22:33:44:55",
        }

        # Verify device was connected and synced
        mock_device.connect.assert_called_once()
        mock_device.start_listening.assert_called_once()
        mock_device.wait_for_initial_sync.assert_called_once()
        mock_device.stop_listening.assert_called_once()
        mock_device.disconnect.assert_called_once()


async def test_form_user_without_mac(hass: HomeAssistant):
    """Test user setup without MAC address."""
    mock_device = MagicMock()
    mock_device.id = "ABC123"
    mock_device.connect = AsyncMock()
    mock_device.start_listening = MagicMock()
    mock_device.wait_for_initial_sync = AsyncMock()
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
            },
        )

        await hass.async_block_till_done()

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_MAC: None,
        }


async def test_form_invalid_mac(hass: HomeAssistant):
    """Test invalid MAC address."""
    mock_device = MagicMock()
    mock_device.connect = AsyncMock(side_effect=MalformedMacAddressError("invalid"))
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_MAC: "invalid",
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {CONF_MAC: "invalid_mac"}


async def test_form_invalid_host(hass: HomeAssistant):
    """Test invalid host address."""
    mock_device = MagicMock()
    mock_device.connect = AsyncMock(side_effect=ConnectionFailedError(Exception("Connection failed")))
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {CONF_HOST: "invalid_host"}


async def test_form_cannot_connect(hass: HomeAssistant):
    """Test connection timeout."""
    mock_device = MagicMock()
    mock_device.connect = AsyncMock(side_effect=ConnectionTimeoutError)
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(hass: HomeAssistant):
    """Test unknown error."""
    mock_device = MagicMock()
    mock_device.connect = AsyncMock(side_effect=Exception("Unknown error"))
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
            },
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "unknown"}


async def test_form_already_configured(hass: HomeAssistant):
    """Test device already configured."""
    mock_device = MagicMock()
    mock_device.id = "ABC123"
    mock_device.connect = AsyncMock()
    mock_device.start_listening = MagicMock()
    mock_device.wait_for_initial_sync = AsyncMock()
    mock_device.stop_listening = AsyncMock()
    mock_device.disconnect = AsyncMock()

    # Create existing entry
    existing_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Trinnov Altitude (ABC123)",
        data={CONF_HOST: "192.168.1.100"},
        source=config_entries.SOURCE_USER,
        entry_id="existing",
        unique_id="ABC123",
        discovery_keys={},
        options={},
    )
    existing_entry.add_to_hass(hass)

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitude",
        return_value=mock_device,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
            },
        )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"

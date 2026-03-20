"""Test the Trinnov Altitude config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from trinnov_altitude.exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
)

from custom_components.trinnov_altitude.const import DOMAIN


async def test_form_user_success(hass: HomeAssistant):
    """Test successful user setup."""
    mock_device = MagicMock()
    mock_device.state.id = "ABC123"
    mock_device.start = AsyncMock()
    mock_device.wait_synced = AsyncMock()
    mock_device.stop = AsyncMock()

    with (
        patch(
            "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
            return_value=mock_device,
        ),
        patch(
            "custom_components.trinnov_altitude.config_flow.async_discover_mac_address",
            AsyncMock(return_value="00:11:22:33:44:55"),
        ),
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
            },
        )

        await hass.async_block_till_done()

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Trinnov Altitude (192.168.1.100)"
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_MAC: "00:11:22:33:44:55",
        }

        # Verify device was connected and synced
        mock_device.start.assert_called_once()
        mock_device.wait_synced.assert_called_once()
        mock_device.stop.assert_called_once()


async def test_form_user_manual_mac_skips_discovery(hass: HomeAssistant):
    """Test explicit setup MAC is normalized and stored without discovery."""
    mock_device = MagicMock()
    mock_device.state.id = "ABC123"
    mock_device.start = AsyncMock()
    mock_device.wait_synced = AsyncMock()
    mock_device.stop = AsyncMock()

    with (
        patch(
            "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
            return_value=mock_device,
        ),
        patch(
            "custom_components.trinnov_altitude.config_flow.async_discover_mac_address",
            AsyncMock(),
        ) as discover_mac,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_MAC: "00-11-22-33-44-55",
            },
        )

        await hass.async_block_till_done()

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == {
            CONF_HOST: "192.168.1.100",
            CONF_MAC: "00:11:22:33:44:55",
        }
        discover_mac.assert_not_awaited()


async def test_form_user_without_mac(hass: HomeAssistant):
    """Test user setup without MAC address."""
    mock_device = MagicMock()
    mock_device.state.id = "ABC123"
    mock_device.start = AsyncMock()
    mock_device.wait_synced = AsyncMock()
    mock_device.stop = AsyncMock()

    with (
        patch(
            "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
            return_value=mock_device,
        ),
        patch(
            "custom_components.trinnov_altitude.config_flow.async_discover_mac_address",
            AsyncMock(return_value=None),
        ),
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


async def test_form_user_rejects_invalid_manual_mac(hass: HomeAssistant):
    """Test manual setup rejects malformed MAC addresses."""
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
    mock_device.start = AsyncMock(
        side_effect=ConnectionFailedError(Exception("Connection failed"))
    )
    mock_device.stop = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
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
    mock_device.start = AsyncMock(side_effect=ConnectionTimeoutError)
    mock_device.stop = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
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
    mock_device.start = AsyncMock(side_effect=Exception("Unknown error"))
    mock_device.stop = AsyncMock()

    with patch(
        "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
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
    mock_device.state.id = "ABC123"
    mock_device.start = AsyncMock()
    mock_device.wait_synced = AsyncMock()
    mock_device.stop = AsyncMock()

    # Create existing entry
    existing_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Trinnov Altitude (192.168.1.100)",
        data={CONF_HOST: "192.168.1.100"},
        unique_id="ABC123",
    )
    existing_entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.trinnov_altitude.config_flow.TrinnovAltitudeClient",
            return_value=mock_device,
        ),
        patch(
            "custom_components.trinnov_altitude.config_flow.async_discover_mac_address",
            AsyncMock(return_value="00:11:22:33:44:55"),
        ),
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


async def test_options_flow_updates_mac(hass: HomeAssistant):
    """Test options flow updates the stored MAC address in entry data and reloads."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Trinnov Altitude (192.168.1.100)",
        data={CONF_HOST: "192.168.1.100", CONF_MAC: None},
        unique_id="ABC123",
    )
    entry.add_to_hass(hass)

    with patch.object(hass.config_entries, "async_schedule_reload") as reload_entry:
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] == FlowResultType.FORM

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_MAC: "00-11-22-33-44-55"},
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert (
        hass.config_entries.async_get_entry(entry.entry_id).data[CONF_MAC]
        == "00:11:22:33:44:55"
    )
    reload_entry.assert_called_once_with(entry.entry_id)


async def test_options_flow_rejects_invalid_mac(hass: HomeAssistant):
    """Test options flow validates manual MAC overrides."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Trinnov Altitude (192.168.1.100)",
        data={CONF_HOST: "192.168.1.100", CONF_MAC: None},
        unique_id="ABC123",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_MAC: "invalid"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_MAC: "invalid_mac"}


async def test_extract_mac_address_normalizes_mac():
    """Test command output MAC parsing normalizes separators and case."""
    from custom_components.trinnov_altitude.config_flow import _extract_mac_address

    assert (
        _extract_mac_address("? (192.168.1.100) at 00-11-22-AA-BB-CC on en0")
        == "00:11:22:aa:bb:cc"
    )

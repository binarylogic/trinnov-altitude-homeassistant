"""Test Trinnov Altitude domain services."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.trinnov_altitude.const import (
    ATTR_ENTRY_ID,
    ATTR_PRESET_ID,
    ATTR_SOURCE,
    ATTR_UPMIXER,
    DOMAIN,
    SERVICE_SET_PRESET,
    SERVICE_SET_SOURCE_BY_NAME,
    SERVICE_SET_UPMIXER,
)


async def test_service_set_source_by_name(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test domain source-by-name service."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_SOURCE_BY_NAME,
        {ATTR_SOURCE: "Apple TV"},
        blocking=True,
    )

    mock_device.command.assert_called_once_with(
        "profile 1", wait_for_ack=True, ack_timeout=2.0
    )


async def test_service_set_preset(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test domain preset service."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    mock_device = mock_setup_entry.return_value
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_PRESET,
        {ATTR_PRESET_ID: 2},
        blocking=True,
    )

    mock_device.command.assert_called_once_with(
        "loadp 2", wait_for_ack=True, ack_timeout=2.0
    )


async def test_service_set_upmixer_invalid(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test domain upmixer service validation."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_UPMIXER,
            {ATTR_UPMIXER: "not_a_mode"},
            blocking=True,
        )


async def test_service_set_source_by_name_unknown_source(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test unknown source is surfaced as service validation error."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError, match="Unknown source name"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_SOURCE_BY_NAME,
            {ATTR_SOURCE: "Does Not Exist"},
            blocking=True,
        )


async def test_service_requires_entry_id_when_multiple_entries(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test entry_id is required when multiple devices are loaded."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Simulate another loaded entry to force entry_id disambiguation.
    hass.data[DOMAIN]["another_entry"] = hass.data[DOMAIN][mock_config_entry.entry_id]

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_SOURCE_BY_NAME,
            {ATTR_SOURCE: "Apple TV"},
            blocking=True,
        )

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_SOURCE_BY_NAME,
        {ATTR_ENTRY_ID: mock_config_entry.entry_id, ATTR_SOURCE: "Apple TV"},
        blocking=True,
    )


async def test_service_invalid_entry_id(
    hass: HomeAssistant, mock_config_entry, mock_setup_entry
):
    """Test unknown entry_id is rejected."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_SOURCE_BY_NAME,
            {ATTR_ENTRY_ID: "missing", ATTR_SOURCE: "Apple TV"},
            blocking=True,
        )

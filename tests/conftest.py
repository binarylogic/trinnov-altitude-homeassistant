"""Fixtures for Trinnov Altitude integration tests."""

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_MAC
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.trinnov_altitude.const import CLIENT_ID, DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_trinnov_device():
    """Create a mock Trinnov Altitude device."""
    device = MagicMock()

    # Device properties
    device.host = "192.168.1.100"
    device.mac = "00:11:22:33:44:55"
    device.connected = True
    device.logger = logging.getLogger("test.trinnov_altitude")
    device.command_timeout = 2.0

    device.state = SimpleNamespace(
        id="ABC123",
        version="4.2.9",
        synced=True,
        volume=-40.0,
        mute=False,
        dim=False,
        bypass=False,
        source="Kaleidescape",
        sources={0: "Kaleidescape", 1: "Apple TV", 2: "Blu-ray"},
        preset="Movies",
        presets={0: "Built-in", 1: "Movies", 2: "Music"},
        audiosync="Master",
        decoder="Dolby Atmos",
        source_format="Dolby TrueHD 7.1",
        upmixer="Native",
    )

    # Async methods
    device.start = AsyncMock()
    device.wait_synced = AsyncMock()
    device.stop = AsyncMock()

    # Commands
    device.power_on = MagicMock()
    device.power_off = AsyncMock()
    device.power_on_available = MagicMock(return_value=True)

    device.volume_set = AsyncMock()
    device.volume_up = AsyncMock()
    device.volume_down = AsyncMock()
    device.volume_adjust = AsyncMock()
    device.volume_percentage_set = AsyncMock()
    device.volume_percentage = 50.0

    device.mute_set = AsyncMock()
    device.mute_on = AsyncMock()
    device.mute_off = AsyncMock()
    device.mute_toggle = AsyncMock()

    device.dim_on = AsyncMock()
    device.dim_off = AsyncMock()
    device.dim_toggle = AsyncMock()

    device.bypass_on = AsyncMock()
    device.bypass_off = AsyncMock()
    device.bypass_toggle = AsyncMock()

    device.acoustic_correction_toggle = AsyncMock()
    device.front_display_toggle = AsyncMock()
    device.level_alignment_toggle = AsyncMock()
    device.quick_optimized_toggle = AsyncMock()
    device.time_alignment_toggle = AsyncMock()

    device.upmixer_set = AsyncMock()
    device.remapping_mode_set = AsyncMock()

    device.source_set = AsyncMock()
    device.source_set_by_name = AsyncMock()
    device.source_get = AsyncMock()

    device.preset_set = AsyncMock()
    device.preset_get = AsyncMock()
    device.command = AsyncMock()

    # Callbacks
    device.register_callback = MagicMock()
    device.deregister_callback = MagicMock()

    return device


@pytest.fixture
def mock_trinnov_device_offline():
    """Create a mock Trinnov Altitude device that is offline."""
    device = MagicMock()
    device.host = "192.168.1.100"
    device.mac = "00:11:22:33:44:55"
    device.connected = False
    device.logger = logging.getLogger("test.trinnov_altitude")
    device.command_timeout = 2.0
    device.state = SimpleNamespace(
        id="ABC123",
        version=None,
        synced=False,
        volume=None,
        source=None,
        preset=None,
        source_format=None,
        sources={},
        presets={},
        audiosync=None,
        decoder=None,
        upmixer=None,
        mute=None,
        dim=None,
        bypass=None,
    )
    device.start = AsyncMock()
    device.wait_synced = AsyncMock()
    device.stop = AsyncMock()
    device.command = AsyncMock()
    device.power_on_available = MagicMock(return_value=True)
    device.volume_percentage = None
    return device


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Trinnov Altitude (ABC123)",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_MAC: "00:11:22:33:44:55",
            CLIENT_ID: "test_client",
        },
        unique_id="ABC123",
    )


@pytest.fixture
def mock_setup_entry(mock_trinnov_device):
    """Mock TrinnovAltitude class for setup."""
    with patch(
        "custom_components.trinnov_altitude.TrinnovAltitudeClient",
        return_value=mock_trinnov_device,
    ) as mock_class:
        yield mock_class

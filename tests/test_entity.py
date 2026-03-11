"""Tests for Trinnov Altitude entity identity behavior."""

from homeassistant.core import HomeAssistant

from custom_components.trinnov_altitude.commands import TrinnovAltitudeCommands
from custom_components.trinnov_altitude.coordinator import TrinnovAltitudeCoordinator
from custom_components.trinnov_altitude.entity import TrinnovAltitudeEntity
from custom_components.trinnov_altitude.sensor import (
    TrinnovAltitudeSensor,
    TrinnovAltitudeSensorEntityDescription,
)


async def test_base_entity_uses_stable_device_id_when_runtime_id_missing(
    hass: HomeAssistant, mock_trinnov_device
) -> None:
    """Entity identity must not drift to unknown when runtime state id disappears."""
    mock_trinnov_device.state.id = None
    coordinator = TrinnovAltitudeCoordinator(
        hass,
        mock_trinnov_device,
        TrinnovAltitudeCommands(mock_trinnov_device),
        stable_device_id="ABC123",
    )

    entity = TrinnovAltitudeEntity(coordinator)

    assert entity.unique_id == "ABC123"
    assert entity.device_info["identifiers"] == {
        ("trinnov_altitude", "ABC123"),
    }


async def test_sensor_uses_stable_device_id_when_runtime_id_missing(
    hass: HomeAssistant, mock_trinnov_device
) -> None:
    """Derived entity unique IDs must stay anchored to the stable device id."""
    mock_trinnov_device.state.id = None
    coordinator = TrinnovAltitudeCoordinator(
        hass,
        mock_trinnov_device,
        TrinnovAltitudeCommands(mock_trinnov_device),
        stable_device_id="ABC123",
    )
    description = TrinnovAltitudeSensorEntityDescription(
        key="device_id",
        translation_key="device_id",
        name="Device ID",
        value_fn=lambda state: state.id,
    )

    entity = TrinnovAltitudeSensor(coordinator, description)

    assert entity.unique_id == "ABC123-device_id"

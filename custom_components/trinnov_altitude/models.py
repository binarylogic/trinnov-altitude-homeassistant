"""Data models for Trinnov Altitude integration."""

from __future__ import annotations

from dataclasses import dataclass

from trinnov_altitude.client import TrinnovAltitudeClient

from .commands import TrinnovAltitudeCommands
from .coordinator import TrinnovAltitudeCoordinator


@dataclass
class TrinnovAltitudeIntegrationData:
    """Runtime data for a config entry."""

    client: TrinnovAltitudeClient
    coordinator: TrinnovAltitudeCoordinator
    commands: TrinnovAltitudeCommands

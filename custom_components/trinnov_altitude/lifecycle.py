"""Lifecycle helpers for Trinnov Altitude entities."""

from __future__ import annotations

from enum import StrEnum


class PowerStatus(StrEnum):
    """Primary lifecycle states exposed to Home Assistant."""

    OFF = "off"
    BOOTING = "booting"
    READY = "ready"

"""Volume projection helpers for Trinnov Altitude."""

VOLUME_MIN_DB = -120.0
VOLUME_MAX_DB = 0.0


def db_to_level(db: float) -> float:
    """Convert Trinnov dB volume to Home Assistant's 0..1 volume level."""
    clamped = min(max(db, VOLUME_MIN_DB), VOLUME_MAX_DB)
    return (clamped - VOLUME_MIN_DB) / (VOLUME_MAX_DB - VOLUME_MIN_DB)


def level_to_db(level: float) -> float:
    """Convert Home Assistant's 0..1 volume level to Trinnov dB volume."""
    if not 0 <= level <= 1:
        raise ValueError("Volume level must be between 0 and 1")
    return round((level * (VOLUME_MAX_DB - VOLUME_MIN_DB)) + VOLUME_MIN_DB, 1)

"""State value resolvers with graceful fallbacks for optional protocol data."""

from __future__ import annotations

from trinnov_altitude.const import UpmixerMode


def resolve_source_name(state: object) -> str | None:
    """Return current source name with index fallback when labels are absent."""
    source = getattr(state, "source", None)
    if source:
        return str(source)

    index = getattr(state, "current_source_index", None)
    if not isinstance(index, int) or index < 0:
        return None

    sources = getattr(state, "sources", {})
    if isinstance(sources, dict) and index in sources:
        value = sources.get(index)
        if value:
            return str(value)

    return f"Source {index}"


def resolve_preset_name(state: object) -> str | None:
    """Return current preset name with index fallback when labels are absent."""
    preset = getattr(state, "preset", None)
    if preset:
        return str(preset)

    index = getattr(state, "current_preset_index", None)
    if not isinstance(index, int) or index < 0:
        return None

    presets = getattr(state, "presets", {})
    if isinstance(presets, dict) and index in presets:
        value = presets.get(index)
        if value:
            return str(value)

    return f"Preset {index}"


def resolve_upmixer_value(state: object) -> str | None:
    """Return normalized upmixer value, preserving unknown tokens."""
    upmixer = getattr(state, "upmixer", None)
    if upmixer is None:
        return None

    normalized = str(upmixer).strip().lower().replace("_", " ")
    known = {mode.value for mode in UpmixerMode}
    if normalized in known:
        return normalized
    return str(upmixer).strip()


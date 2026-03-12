"""Tests for Trinnov Altitude state resolvers."""

from types import SimpleNamespace

from custom_components.trinnov_altitude.resolvers import (
    resolve_preset_name,
    resolve_source_name,
    resolve_upmixer_value,
)


def test_resolve_source_name_returns_none_for_invalid_index() -> None:
    """Source resolver should return None when no valid source information exists."""
    assert (
        resolve_source_name(SimpleNamespace(source=None, current_source_index=-1))
        is None
    )
    assert (
        resolve_source_name(SimpleNamespace(source=None, current_source_index="bad"))
        is None
    )


def test_resolve_source_name_uses_index_fallback_label() -> None:
    """Source resolver should synthesize a stable fallback label from the index."""
    state = SimpleNamespace(source=None, current_source_index=4, sources={})
    assert resolve_source_name(state) == "Source 4"


def test_resolve_source_name_ignores_empty_label_at_known_index() -> None:
    """Empty source labels should still fall back to the numeric index."""
    state = SimpleNamespace(source=None, current_source_index=2, sources={2: ""})
    assert resolve_source_name(state) == "Source 2"


def test_resolve_preset_name_returns_none_for_invalid_index() -> None:
    """Preset resolver should return None when no valid preset information exists."""
    assert (
        resolve_preset_name(SimpleNamespace(preset=None, current_preset_index=-1))
        is None
    )
    assert (
        resolve_preset_name(SimpleNamespace(preset=None, current_preset_index="bad"))
        is None
    )


def test_resolve_preset_name_uses_index_fallback_label() -> None:
    """Preset resolver should synthesize a stable fallback label from the index."""
    state = SimpleNamespace(preset=None, current_preset_index=3, presets={})
    assert resolve_preset_name(state) == "Preset 3"


def test_resolve_preset_name_ignores_empty_label_at_known_index() -> None:
    """Empty preset labels should still fall back to the numeric index."""
    state = SimpleNamespace(preset=None, current_preset_index=1, presets={1: ""})
    assert resolve_preset_name(state) == "Preset 1"


def test_resolve_upmixer_uses_active_fallback_and_none() -> None:
    """Upmixer resolver should fall back to active mode and gracefully return None."""
    assert (
        resolve_upmixer_value(SimpleNamespace(upmixer=None, active_upmixer=None))
        is None
    )
    state = SimpleNamespace(upmixer=None, active_upmixer=" Dolby_Upmixer ")
    assert resolve_upmixer_value(state) == "Dolby_Upmixer"

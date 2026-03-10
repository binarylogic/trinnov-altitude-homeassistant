# AGENTS.md

## Purpose
`trinnov-altitude-homeassistant` is the Home Assistant integration for Trinnov Altitude processors.

## Workflow
- Use `uv` for local commands.
- Run repo-local lint and targeted tests before pushing.
- Keep Home Assistant behavior projection-only where possible; protocol semantics belong in `py-trinnov-altitude`.

## Lifecycle Contract
- Primary lifecycle entities must stay explicit and typed:
  - `media_player`: `off` when powered down if HA can still turn the device on.
  - `sensor.power_status`: explicit lifecycle enum such as `off`, `booting`, `ready`.
- Secondary datapoints that are not meaningful while off should become `unknown`, not `unavailable`.
- Reserve `unavailable` for true communication/control failure.
- Never change entity unique IDs because the device booted in a different state.

## Dependencies
- `custom_components/trinnov_altitude/manifest.json` must track the minimum `py-trinnov-altitude` version required for released fixes.
- Release the library first when HA behavior depends on library changes.

## Commits
- Use conventional commits for releasable changes: `fix: ...` or `feat: ...`.

## Releases
1. Merge normal conventional commits to `master`.
2. Let `release-please` open or update the release PR.
3. Do not manually edit version files or changelogs outside the Release Please PR.
4. Do not manually create tags or GitHub releases.
5. Merge the Release Please PR to publish.

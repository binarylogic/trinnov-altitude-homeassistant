# AGENTS.md

## Purpose
`trinnov-altitude-homeassistant` is the Home Assistant integration built on top of `py-trinnov-altitude`.

## Development Workflow
- Use `uv` for local tasks.
- Key commands:
  - `uv run ruff check custom_components tests`
  - `uv run ruff format custom_components tests`
  - `uv run pytest -q --no-cov tests/test_select.py tests/test_sensor.py tests/test_init.py tests/test_config_flow.py`
- CI is strict about formatting (`ruff format --check` equivalent). Format failures are common if skipped.

## Integration Design Expectations
- HA layer should be projection-only where possible.
- Protocol quirks belong in library (`py-trinnov-altitude`), not in HA entities.
- Entity behavior should degrade gracefully:
  - id-first logic
  - optional labels
  - stable fallback display values

## Dependency Policy
- `custom_components/trinnov_altitude/manifest.json` requirement must track minimum library version needed for fixes.
- For protocol semantic fixes in library, bump minimum requirement promptly.

## Commit Conventions
- Use conventional commits for release-please:
  - `fix: ...` or `feat: ...`

## Release Process
1. Push conventional commits to `master`.
2. `release-please` opens/updates release PR automatically.
3. Review PR contents should usually be only:
  - `.release-please-manifest.json`
  - `CHANGELOG.md`
  - `custom_components/trinnov_altitude/manifest.json` (version/dependency)
4. Wait for `Tests` and `Validate` checks.
5. Merge release PR using allowed repo merge mode (historically `--rebase` works if others are blocked).
6. Confirm new GitHub release tag and attached zip artifact are published.

## Branch Protection / Merge Mechanics
- This repo enforces PR flow; direct push may still happen via bypass but should not be relied on.
- Merge mode restrictions may reject `--merge` or `--squash`; use allowed mode with admin only when necessary.

## Cross-Repo Coordination
- Always release `py-trinnov-altitude` first.
- Then release HA integration with updated minimum dependency.
- When reporting back to users, provide both final version numbers and release links.

## Session Hygiene
- Before merging releases, check:
  - `gh pr list --state open --limit 20`
  - `gh run list --limit 10`
  - `gh release list --limit 10`
- Keep changelog/release PRs small and frequent to avoid large catch-up release PRs.

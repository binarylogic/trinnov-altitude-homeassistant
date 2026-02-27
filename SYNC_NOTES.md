# Trinnov Altitude Sync Notes (Source of Truth Workflow)

This repository is the source of truth.

Upstream Home Assistant repositories are release targets:
- `home-assistant/core` (integration code)
- `home-assistant/home-assistant.io` (docs)
- `home-assistant/brands` (logos/brand metadata)

## Current Upstream PRs

- Core: https://github.com/home-assistant/core/pull/164392
- Docs: https://github.com/home-assistant/home-assistant.io/pull/43819
- Brands (merged): https://github.com/home-assistant/brands/pull/8455

## Sync Policy

1. Build and merge features in this repo first.
2. Port from one exact source commit/tag into upstream sync branches.
3. Keep intentional differences documented (no undocumented drift).
4. Any upstream review-requested logic change must be backported here.

## Required Structural Differences

These are expected and should not be treated as drift:
- Pathing: `custom_components/trinnov_altitude/*` vs `homeassistant/components/trinnov_altitude/*`
- Manifest format differences between custom integration and core integration.
- Core generated files and indexes (`homeassistant/generated/*`, requirements lists, `CODEOWNERS`).
- Test layout differences (`tests/*` vs `tests/components/trinnov_altitude/*`).

## Current Scope Delta (Needs Closing Over Time)

Source repo currently includes more platforms/features than the current core PR snapshot.

Present in source repo:
- `button`, `media_player`, `number`, `remote`, `select`, `sensor`, `switch`
- coordinator-backed state model
- domain services and service descriptions

Present in current core PR branch:
- `remote` only + config flow/setup base

This is temporary scope drift and should be reduced through follow-up upstream work.

## Repeatable Sync Procedure

1. Create/refresh an upstream sync branch from latest `home-assistant/core:dev`.
2. Port changes from one exact source commit from this repo.
3. Run required generation/validation in upstream repo.
4. Open/update upstream PR with links to docs/brands PRs.
5. Record any maintainer-requested logic changes.
6. Backport those logic changes to this repo in a dedicated `sync-backport` commit.

## Backport Checklist Template

For each upstream review round:
- [ ] List each requested change.
- [ ] Mark if logic-affecting or upstream-only formatting/generated change.
- [ ] Backport logic-affecting changes to this repo.
- [ ] Add commit hash links for upstream commit and backport commit.
- [ ] Re-run local tests in this repo.


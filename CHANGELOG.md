# Changelog

## [2.0.5](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v2.0.4...v2.0.5) (2026-02-28)


### Bug Fixes

* cover preset index fallback behavior in entities ([c3be851](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/c3be85198ef57ace962d056122d516140fd43a38))
* format resolver helpers for CI ([f4195a1](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/f4195a156d338ee91f513a0cd94ad05e2d75e6ad))

## [2.0.4](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v2.0.3...v2.0.4) (2026-02-28)


### Bug Fixes

* cover preset index fallback behavior in entities ([c3be851](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/c3be85198ef57ace962d056122d516140fd43a38))
* require trinnov-altitude 3.1.1 for Altitude CI startup ([adad43a](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/adad43ae41e1acf0b43d60e69e7f2ddcff15c983))

## [2.0.4](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v2.0.3...v2.0.4) (2026-02-28)

### Bug Fixes

* bump `trinnov-altitude` minimum version to `3.1.1` for Altitude CI startup source/preset compatibility

## [2.0.3](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v2.0.2...v2.0.3) (2026-02-27)

### Bug Fixes

* stabilize CI formatting checks and metadata alignment
* trigger patch release ([d6d47f5](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/d6d47f52e686f80490b77c451c4dc70641679b9e))

## [2.0.2](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v2.0.1...v2.0.2) (2026-02-27)

### Bug Fixes

* trigger patch release ([d6d47f5](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/d6d47f52e686f80490b77c451c4dc70641679b9e))

## [2.0.1](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v2.0.0...v2.0.1) (2026-02-27)

### Bug Fixes

* require trinnov-altitude v3 API ([fda0f4c](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/fda0f4c2b95d43903d3af93947b27f3598daac57))

## [2.0.0](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v1.6.2...v2.0.0) (2026-02-27)

### ⚠ BREAKING CHANGES

* migrate HA integration to adapter-driven updates and strict command API

### Features

* migrate HA integration to adapter-driven updates and strict command API ([bcbbe31](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/bcbbe31d522320b5cb7bfbb01d5190930383696a))

### Bug Fixes

* deregister adapter callback using registered handle ([8889f33](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/8889f3322de19903aa9ec65a40691e79bc2c2bd3))

## [1.6.2](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v1.6.1...v1.6.2) (2026-02-27)

### Bug Fixes

* keep integration loaded when device is offline at startup ([cee93cd](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/cee93cd8f57a5213837706c39f36afcf251d4c04))
* quote service description to satisfy YAML parser ([a9e824b](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/a9e824b3ab0f2638e03a1d2ea35227ed1f296511))
* satisfy hassfest service metadata and translations ([8a57e88](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/8a57e88125d42e2a3e6c5e429b1a2b6cab2a4dec))

## [1.6.1](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v1.6.0...v1.6.1) (2026-02-27)

### Bug Fixes

* align integration manifest version with latest release ([ccffb4e](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/ccffb4e37af82cee8cb7b5ff7af44f643fb41406))

## [1.6.0](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v1.5.0...v1.6.0) (2026-02-27)

### Features

* migrate integration to trinnov-altitude v2 with coordinator+command architecture ([15c1bfe](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/15c1bfe3ffc0778cb1b0a7aa20db0688f4d554c4))
* **sensor:** add dynamic icons for power_status sensor ([5222344](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/52223446d0200b399abc139f515cf093a3898306))

## [1.5.0](https://github.com/binarylogic/trinnov-altitude-homeassistant/compare/v1.4.0...v1.5.0) (2025-12-15)

### Features

* **sensor:** add power_status sensor with off/booting/ready states ([76993d6](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/76993d6e7435fb2f7bde57606876e86346ab8075))

### Bug Fixes

* **ci:** combine release steps to avoid race condition ([94fc7b3](https://github.com/binarylogic/trinnov-altitude-homeassistant/commit/94fc7b361982266c2ed2fb093dee9f0ddc3f0dbf))

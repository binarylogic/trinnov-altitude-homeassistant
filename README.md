# Trinnov Altitude Home Assistant Integration

A [Home Assistant](https://www.home-assistant.io) integration for the
[Trinnov Altitude](https://www.trinnov.com/en/products/altitude32/) processor. Uses the [`trinnov-altitude`](https://github.com/binarylogic/py-trinnov-altitude) library.

## Prerequisites

1. Home Assistant 2024.4.1 or newer
2. [HACS](https://hacs.xyz) installed
3. Trinnov Altitude accessible on your network

**It's strongly recommended to assign your Trinnov Altitude a static IP address.**

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Search for "Trinnov Altitude"
3. Click "Download"
4. Restart Home Assistant

### Manual

1. Download the latest release
2. Copy `custom_components/trinnov_altitude` to your `config/custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "+ Add Integration"
3. Search for "Trinnov Altitude"
4. Enter your device's IP address
5. Optionally enter the MAC address (required for Wake-on-LAN power on)

## Entities

### Switches

Control toggleable features with state feedback:

| Entity | Description |
|--------|-------------|
| `switch.*_mute` | Mute audio |
| `switch.*_dim` | Dim volume |
| `switch.*_bypass` | Bypass Trinnov optimizer |

### Selects

Dropdown selectors for device settings:

| Entity | Description |
|--------|-------------|
| `select.*_source` | Input source |
| `select.*_preset` | Audio preset |
| `select.*_upmixer` | Upmixer mode (native, dolby, dts, auro3d, etc.) |

### Number

| Entity | Description |
|--------|-------------|
| `number.*_volume` | Volume slider (-120 dB to 0 dB, 0.5 dB steps) |

### Buttons

Toggle buttons for features without state feedback:

| Entity | Description |
|--------|-------------|
| `button.*_toggle_acoustic_correction` | Toggle acoustic correction |
| `button.*_toggle_front_display` | Toggle front display |
| `button.*_toggle_level_alignment` | Toggle level alignment |
| `button.*_toggle_quick_optimized` | Toggle quick optimized |
| `button.*_toggle_time_alignment` | Toggle time alignment |

### Sensors

Read-only state information:

| Entity | Description |
|--------|-------------|
| `sensor.*_volume` | Current volume (dB) |
| `sensor.*_source` | Current source name |
| `sensor.*_preset` | Current preset name |
| `sensor.*_decoder` | Active decoder |
| `sensor.*_upmixer` | Active upmixer |
| `sensor.*_source_format` | Source audio format |
| `sensor.*_audiosync` | Audiosync mode (Master/Slave) |

### Media Player

Full media player entity with volume, mute, source selection, and power control.

### Remote

Send commands via the `remote.send_command` service:

```yaml
service: remote.send_command
target:
  entity_id: remote.trinnov_altitude_*
data:
  command:
    - mute_on
```

#### Available Commands

**Toggle Commands:**
- `acoustic_correction_on/off/toggle`
- `bypass_on/off/toggle`
- `dim_on/off/toggle`
- `front_display_on/off/toggle`
- `level_alignment_on/off/toggle`
- `mute_on/off/toggle`
- `quick_optimized_on/off/toggle`
- `time_alignment_on/off/toggle`

**Navigation:**
- `page_up`, `page_down`
- `volume_up`, `volume_down`

**Commands with Parameters:**
- `preset_set <int>` - Set preset by index
- `source_set <int>` - Set source by index
- `source_set_by_name <string>` - Set source by name
- `volume_set <decimal>` - Set volume in dB
- `volume_percentage_set <decimal>` - Set volume as 0-100%
- `volume_ramp <decimal>` - Ramp volume to target
- `upmixer_set <string>` - Set upmixer (native, dolby, dts, auro3d, etc.)
- `remapping_mode_set <string>` - Set remapping mode (none, 2D, 3D, etc.)

## Example Automations

### Send Commands (Device Already On)

```yaml
service: remote.send_command
target:
  entity_id: remote.trinnov_altitude_*
data:
  command:
    - source_set_by_name Kaleidescape
    - volume_set -40.0
```

### Power On and Configure

The remote entity's state reflects connection status - `on` when connected, `off` when disconnected. Use this to wait for the device to be ready after Wake-on-LAN:

```yaml
automation:
  - alias: "Theater Mode"
    trigger:
      - platform: state
        entity_id: remote.kaleidescape
        to: "on"
    action:
      - service: remote.turn_on
        target:
          entity_id: remote.trinnov_altitude_*
      - wait_for_trigger:
          - platform: state
            entity_id: remote.trinnov_altitude_*
            to: "on"
        timeout: "00:00:30"
      - service: remote.send_command
        target:
          entity_id: remote.trinnov_altitude_*
        data:
          command:
            - source_set_by_name Kaleidescape
            - volume_set -40.0
```

## Development

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
make install

# Development
make test        # Run tests
make test-fast   # Run tests without coverage
make lint        # Check code
make format      # Format code

# Release
make release     # Run checks and create release zip
```

## Support

Issues and feature requests: [GitHub Issues](https://github.com/binarylogic/trinnov-altitude-homeassistant/issues)

# Trinnov Altitude Home Assistant Integration

A [Home Assistant](https://www.home-assistant.io) integration for the
[Trinnov Altitude AVR](https://www.trinnov.com/en/products/altitude32/). Uses
the [`trinnov-altitude` library](https://github.com/binarylogic/py-trinnov-altitude) under the hood.

## Prerequisites

1. Home Assistant instance (at minimum 2024.4.1).
2. [HACS](https://hacs.xyz) (Home Assistant Community Store) installed on your Home Assistant.
3. Trinnov Altitude set up and accessible from the network as your Home Assistant in connected to.

**:warning: It's strongly recommended that the Trinnov Altitude is assigned a
static IP address. If the IP address changes, the Altitude will be incorrectly
shown as powered off in Home Assistant. When this happens, reconfiguration with
the new IP address is necessary.**

## Installation

### Installation via [HACS](https://hacs.xyz)

1. [Open HACS](http://homeassistant.local:8123/hacs/dashboard) in your Home Assistant interface.
2. Search for "Trinnov Altitude" and select it.
3. Click the "Download" in bottom right of the page.
4. Restart Home Assistant to apply the changes.

## Manual Installation

1. Download the latest release from the GitHub repository.
2. Unzip the release and copy the `custom_components/trinnov_altitude` folder to your Home Assistant `config/custom_components` directory.
3. Restart Home Assistant to apply the changes.

## Configuration

After installation, add the Trinnov Altitude integration via the Home Assistant UI:

1. Navigate to Configuration > Integrations.
2. Click on the "+ Add Integration" button.
3. Search for "Trinnov Altitude" and select it.
4. Follow the on-screen instructions to complete the setup.
   1. Note: The MAC Address is optional, but is required to power on the
      Trinnov Altitude via Wake on Lan. The Trinnov Altitude does not have a standby mode that maintains TCP connections. Wake on Lan is the only way
      to power on the Trinnov Altitude over IP.

## Entities

This integration provides multiple entity types for controlling your Trinnov Altitude:

### Controls

#### Volume Slider (Number)
A dedicated volume slider for precise control from -120 dB to 0 dB (capped at 0 dB for safety).
- **Entity:** `number.trinnov_altitude_*_volume`
- **Range:** -120.0 to 0.0 dB
- **Step:** 0.5 dB

#### Source Selector (Select)
Dropdown to select the active input source.
- **Entity:** `select.trinnov_altitude_*_source`
- **Options:** Your configured sources

#### Preset Selector (Select)
Dropdown to select audio presets.
- **Entity:** `select.trinnov_altitude_*_preset`
- **Options:** Your configured presets

#### Toggle Buttons (Button)
One-tap controls for common functions:
- **Mute Toggle:** `button.trinnov_altitude_*_mute_toggle`
- **Dim Toggle:** `button.trinnov_altitude_*_dim_toggle`

### Media Player

A full-featured media player entity with volume control, source selection, and power management.
- **Entity:** `media_player.trinnov_altitude_*`

### Remote

The Trinnov Altitude remote platform will create a [Remote](https://www.home-assistant.io/integrations/remote/) entity for the device. This entity allows you to send the following commands via the [remote.send_command](https://www.home-assistant.io/integrations/remote/) service.

A typical service call might look like the example below, which sends a command to the device to mute the volume.

```yaml
service: remote.send_command
target:
  entity_id: remote.trinnov_altitude
data:
  command:
    - mute_on
```

#### Single Commands

- `acoustic_correction_off`
- `acoustic_correction_on`
- `acoustic_correction_toggle`
- `bypass_off`
- `bypass_on`
- `bypass_toggle`
- `dim_off`
- `dim_on`
- `dim_toggle`
- `front_display_off`
- `front_display_on`
- `front_display_toggle`
- `level_alignment_off`
- `level_alignment_on`
- `level_alignment_toggle`
- `mute_off`
- `mute_on`
- `mute_toggle`
- `page_down`
- `page_up`
- `quick_optimized_off`
- `quick_optimized_on`
- `quick_optimized_toggle`
- `time_alignment_off`
- `time_alignment_on`
- `time_alignment_toggle`
- `volume_down`
- `volume_up`

#### Commands With Paramteres

- `preset_set (int)`
- `remapping_mode_set (string)`
- `source_set (int)`
- `volume_set (decimal)`
- `volume_ramp (decimal)`
- `upmixer_set (string)`

### Binary Sensors

The integration creates multiple [Binary Sensor](https://www.home-assistant.io/integrations/binary_sensor/) entities for the device.

* `Bypass` is On when the device is bypassing the Trinnov optimizer.
* `Dim` is On when the volume is dimmed.
* `Mute` is On when the volume is muted.

### Sensors

The integration creates multiple [Sensor](https://www.home-assistant.io/integrations/sensor/) entities for the device.

#### AUDIOSYNC

How the Altitude is syncing video with audio given upstream equipment.

- `Slave`
- `Master`

#### DECODER

Bypass the Trinnov optimizer.

- `True`
- `False`

#### PRESET

Current Trinnov preset loaded.

#### SOURCE

Current source loaded, will the be source name, not the index.

#### SOURCE_FORMAT

Current source format.

#### UPMIXER

Current upmixer being used, if any.

#### VOLUME

Current volume level in dB, from `-120.0db` to `20.0db`

## Automations

An example automation that turns on the Trinnov Altitude, sets the source,
preset, and volume when a Kaleidescape players turns on.

**Note: Because the Trinnov Altitude can take a variable amount of time to turn
on, I've added a step to wait for it to power on before sending commands.**

```yaml
description: "Turn on Trinnov Altitude for Kaleidescape"
mode: single
trigger:
  - platform: device
    type: turned_on
    entity_id: remote.kaleidescape
    domain: remote
condition: []
action:
  - type: turn_on
    entity_id: remote.trinnov_altitude
    domain: remote
  - if:
      - condition: device
        type: is_off
        entity_id: remote.trinnov_altitude
        domain: remote
    then:
      - wait_for_trigger:
          - platform: device
            type: turned_on
            entity_id: remote.trinnov_altitude
            domain: remote
  - service: remote.send_command
    metadata: {}
    data:
      num_repeats: 1
      delay_secs: 0.7
      hold_secs: 0
      command:
        - source_set 0
        - preset_set 1
        - volume_set -40.0
    target:
      entity_id: remote.media_room_trinnov_altitude
```

## Development

### Setup

This project uses modern Python tooling:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint code
make lint

# Format code
make format
```

### Testing

The integration includes comprehensive tests with 95% coverage requirement:
- Unit tests for all platforms
- Integration tests for config flow
- Mock devices for testing without hardware

Tests run automatically on push/PR via GitHub Actions.

## Support

If you encounter any issues or have questions about this integration, please open an issue on the GitHub repository.

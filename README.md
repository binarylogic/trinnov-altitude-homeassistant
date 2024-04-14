# Trinnov Altitude Home Assistant Integration

A [Home Assistant](https://www.home-assistant.io) integration for the
[Trinnov Altitude AVR](https://www.trinnov.com/en/products/altitude32/).

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

## Usage

### Remote

The Trinnov Altitude remote platform will create a [Remote](https://www.home-assistant.io/integrations/remote/) entity for the device. This entity allows you to send the following commands via the [remote.send_command](https://www.home-assistant.io/integrations/remote/) service.

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
- `preset_set`
- `quick_optimized_off`
- `quick_optimized_on`
- `quick_optimized_toggle`
- `remapping_mode_set`
- `source_set`
- `time_alignment_off`
- `time_alignment_on`
- `time_alignment_toggle`
- `upmixer_set`
- `volume_down`
- `volume_ramp`
- `volume_set`
- `volume_up`

A typical service call might look like the example below, which sends a command to the device to select the currently highlighted item.

```yaml
service: remote.send_command
target:
  entity_id: remote.trinnov_altitude
data:
  command:
    - volume_up
```

Commands can take arguments, like that of the `source_set` command:

```yaml
service: remote.send_command
target:
  entity_id: remote.trinnov_altitude
data:
  command:
    - source_set 1
```

### Sensors

The Kaleidescape sensor platform will create multiple [Sensor](https://www.home-assistant.io/integrations/sensor/) entities for the device. The follow sensors are provided:

#### AUDIOSYNC

How the Altitude is syncing video with audio given upstream equipment.

- `Slave`
- `Master`

#### BYPASS

Bypass the Trinnov optimizer.

- `True`
- `False`

#### DECODER

Bypass the Trinnov optimizer.

- `True`
- `False`

### DIM

Volume dim status.

- `True`
- `False`

### MUTE

Volume mute status.

- `True`
- `False`

### PRESET

Current Trinnov preset loaded.

### SOURCE

Current source loaded, will the be source name, not the index.

### SOURCE_FORMAT

Current source format.

### UPMIXER

Current upmixer being used, if any.

### VOLUME

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

## Support

If you encounter any issues or have questions about this integration, please open an issue on the GitHub repository.

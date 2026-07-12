# MeteoAlarm Custom Integration for Home Assistant

A custom integration for [Home Assistant](https://www.home-assistant.io/) that follows the official [MeteoAlarm](https://meteoalarm.org/) weather warning feeds for the regions you choose - with a friendly setup flow, multiple entities per region, and a bundled Lovelace card.

## Features

- **Guided setup** - pick the country from a dropdown, then pick your region from the list of regions in the country feed (free-text entry is also allowed, e.g. on calm days when the feed lists nothing). Custom country slugs are accepted so future feed additions keep working.
- **All active warnings** - the integration talks to the MeteoAlarm feeds directly (no extra Python dependencies) and returns *every* active warning for the region, not just the first one, in your preferred language.
- **Entities per region** (grouped under one device):
  - `sensor.<region>_warning_level` - enum: `none` / `minor` / `moderate` / `severe` / `extreme` (translated in the UI). The `alerts` attribute holds the full list of active warnings; the most severe one is also exposed as flat attributes (`event`, `headline`, `onset`, `expires`, `description`, ...).
  - `sensor.<region>_active_warnings` - number of active warnings.
  - `sensor.<region>_warnings_start` / `sensor.<region>_warnings_end` - timestamps of the earliest start and latest end of the active warnings.
  - `binary_sensor.<region>_warning_active` - on while any warning is active (safety device class).
  - `event.<region>_new_warning` - fires whenever a previously unseen warning appears; the event data contains the whole alert. Great for notifications.
- **Options flow** - change the language and update interval any time from the integration's *Configure* button (the entry reloads automatically).
- **Diagnostics** - download a JSON snapshot of the entry and current alerts from the integration page.
- **Bundled Lovelace card** - `custom:meteoalarm-card` is served by the integration and registered as a dashboard resource automatically (storage-mode dashboards). No separate HACS frontend install needed.

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. HACS → three dots → *Custom repositories* → add `https://github.com/gatisr/meteoalarm_custom` as an *Integration*.
3. Search for "MeteoAlarm Custom", install it, and restart Home Assistant.

### Manual Installation

1. Copy `custom_components/meteoalarm_custom` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

Settings → Devices & Services → *Add Integration* → **MeteoAlarm Custom**:

1. **Country** - pick from the list, or type a custom feed slug exactly as it appears in the `https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-<slug>` URL (e.g. `latvia`, `united-kingdom`).
2. **Region** - pick from the regions currently present in the feed, or type the region name exactly as MeteoAlarm publishes it (e.g. `Riga`, `Smiltene municipality`). Marine areas with an EMMA geocode (e.g. `LV803`) also work.
3. **Language** - ISO code of the warning texts. Only languages published by that country's weather service are available; anything else falls back to English.
4. **Update interval** - polling interval in minutes.

Repeat for as many regions as you like - each region becomes its own entry and device. Language and interval can be changed later via *Configure*.

## Lovelace card

The card ships with the integration. On storage-mode dashboards the resource is registered automatically - just add a card:

```yaml
type: custom:meteoalarm-card
entity: sensor.meteoalarm_riga_warning_level
# optional:
# title: Rīga
# show_description: true
# show_instruction: false
# compact: false
```

The card shows the region's status with severity colors and one row per active warning (icon by warning type, time range, description). It has a visual editor, so all options can be set from the UI.

On YAML-mode dashboards add the resource manually:

```yaml
resources:
  - url: /meteoalarm_custom/meteoalarm-card.js
    type: module
```

## Automation examples

Notify when a new warning appears:

```yaml
triggers:
  - trigger: state
    entity_id: event.meteoalarm_riga_new_warning
actions:
  - action: notify.mobile_app_phone
    data:
      title: "{{ trigger.to_state.attributes.event }}"
      message: "{{ trigger.to_state.attributes.description }}"
```

Do something while any warning is active:

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.meteoalarm_riga_warning_active
    to: "on"
```

## Development

```bash
# integration tests
python3 -m venv .venv && .venv/bin/pip install -r requirements_test.txt
.venv/bin/pytest

# live smoke test against the real feed
.venv/bin/python tests_manual/test.py latvia "Riga" lv

# Lovelace card (sources in card/, bundle committed to custom_components/.../frontend/)
cd card && npm install && npm run build
```

## Troubleshooting

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.meteoalarm_custom: debug
```

The integration page also offers a *Download diagnostics* button with the raw alert data.

## License

This project is licensed under the [MIT License](LICENSE).

## Credits

Developed by [@gatisr](https://github.com/gatisr/). Data provided by [MeteoAlarm](https://meteoalarm.org/); see their terms for redistribution requirements.

## Disclaimer

This integration is not affiliated with or endorsed by MeteoAlarm or any of its associated organizations. Use of this integration is at your own risk.

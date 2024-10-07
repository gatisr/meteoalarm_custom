# MeteoAlarm Custom Integration for Home Assistant

This is a custom integration for [Home Assistant](https://www.home-assistant.io/) that provides a sensor for retrieving weather alerts from the [MeteoAlarm](https://meteoalarm.org/) service. Developed because default integration didn't work as supposed for me.

## Features

- Configurable sensor for any supported country, province, and language
- Retrieves alert data from the MeteoAlarm API
- Provides alert level and additional alert attributes
- Handles cases when no alerts are available

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. In the HACS panel, select "Integrations".
3. Click on the three dots in the top right corner and choose "Custom repositories".
4. Enter `https://github.com/gatisr/meteoalarm_custom` as the repository URL.
5. Select the category "Integration".
6. Click "Add".
7. Search for "MeteoAlarm" and install it.

### Manual Installation

1. Download the `meteoalarm_custom` directory from this repository.
2. Place the `meteoalarm_custom` directory inside the `custom_components` directory of your Home Assistant configuration folder.
3. Restart your Home Assistant instance.

## Configuration

1. After installation, go to the Home Assistant UI and navigate to "Configuration" -> "Integrations".
2. Click on the "+" button and search for "MeteoAlarm Custom".
3. Enter the required configuration details:
   - **Country**: The country code for the desired location (e.g., "latvia").
     - It is crucial to write the country name exactly as it appears in the URL starting with https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom- including any hyphens used in the name. (e.g. "latvia" for https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-latvia)
     - Feed list you can find here https://feeds.meteoalarm.org/
   - **Province**: The province code for the desired location (e.g., "LV001").
      - The province code can be found from feed link above, in `feed` -> `entry` -> `cap:geocode` -> `value` or `feed` -> `entry` -> `cap:areaDesc` tag value.
      - Alternatively, you can try to find the province code by using the MeteoAlarm warnings API like this https://feeds.meteoalarm.org/api/v1/warnings/feeds-latvia/ (see `areaDesc` and `geocode` -> `value`).
   - **Language**: The language code for the alerts (e.g., "en").
      - The ISO code of your language, please be aware that this is only possible in the current country. So if you are in Latvia, you can't get alerts in Norwegian.
   - **Update Interval**: The interval in minutes for updating the sensor data (default is 30 minutes).
4. Click on "Submit" to complete the configuration.

## Sensor

The integration provides a sensor entity with the following details:

- **Entity ID**: `sensor.meteoalarm_<province>`
- **State**: The current alert level (e.g., "2; yellow; Moderate") or "No Alert" if no alerts are available.
- **Attributes**:
  - `category`: The category of the alert.
  - `urgency`: The urgency of the alert.
  - `severity`: The severity of the alert.
  - `certainty`: The certainty of the alert.
  - `effective`: The effective time of the alert.
  - `onset`: The onset time of the alert.
  - `expires`: The expiration time of the alert.
  - `sender_name`: The name of the sender of the alert.
  - `description`: The description of the alert.
  - `web`: The web URL for more information about the alert.
  - `contact`: Contact information for the alert.
  - `awareness_level`: The awareness level of the alert.
  - `awareness_type`: The awareness type of the alert.

### Automation example

```yaml
alias: "Global telegram periodiskais info un komandas "
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.meteoalarm_riga
    attribute: "'Spēkā stāšanās laiks'"
    id: riga_alarm
    alias: MeteoAlarm Rīga
  - trigger: state
    entity_id:
      - sensor.meteoalarm_salaspils
    attribute: Spēkā stāšanās laiks
    id: salaspils_alarm
    alias: MeteoAlarm Salaspils
  - trigger: state
    entity_id:
      - sensor.meteoalarm_smiltene
    attribute: Spēkā stāšanās laiks
    id: smiltene_alarm
    alias: MeteoAlarm Smiltene
conditions: []
actions:
  - alias: Apstrādāt un sūtīt MeteoAlarm brīdinājumu
    if:
      - condition: trigger
        id:
          - salaspils_alarm
          - smiltene_alarm
          - riga_alarm
      - condition: template
        value_template: "{{ states[trigger.entity_id].attributes['Spēkā stāšanās laiks'] is defined and states[trigger.entity_id].attributes['Spēkā stāšanās laiks'] != '' }}"
    then:
      - target:
          entity_id: script.global_openai_telegram
        data:
          variables:
            message: >
              Brīdinājuma analītiķi, saņemts jauns MeteoAlarm brīdinājums no {{
              states[trigger.entity_id].attributes['contact'] }}. Pārskatiet
              saņemtos stāvokļa atribūtus: Brīdinājuma informācija: {{
              states[trigger.entity_id].attributes }} Īsi izanalizējiet
              brīdinājumu, kas tajā tiek ziņots, kāds risks un seku potenciāls
              pastāv. Ja pieejams, atkarībā no bīstamības, iekļaujiet arī
              ieteikumus kā rīkoties. Pieminiet brīdinājuma avotu. Ja ziņojumā
              nav pietiekami informācijas, pieņemiet ka risks tiek uzskaitīts
              zemākajā līmenī. Būtiskus faktus, datumus un laikus iekļaujiet
              apkopojumā. Izmanto emoji. Obligāti piemini kurā pilsētā tas notiek - izvelc to no koda {{trigger.entity_id}}
        action: script.turn_on
  ```

## Updating

### HACS

If you have installed the integration via HACS, you can easily update it by navigating to the HACS panel, selecting the "Integrations" tab, and clicking on the "Update" button for the MeteoAlarm Custom integration.

### Manual Update

To manually update the integration, simply download the latest version of the `meteoalarm_custom` directory from this repository and replace the existing directory in your Home Assistant `custom_components` folder. Restart your Home Assistant instance to complete the update.

## Troubleshooting

If you encounter any issues with the integration, please check the Home Assistant logs for error messages. You can also enable debug logging by adding the following lines to your Home Assistant `configuration.yaml` file:

```yaml
logger:
  default: info
  logs:
    custom_components.meteoalarm_custom: debug
```

## Contributing

Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/gatisr/meteoalarm_custom)

## License

This project is licensed under the [MIT License](LICENSE).

## Credits

This integration was developed by [@gatisr](https://github.com/gatisr/) and is based on the [meteoalert-api](https://github.com/rolfberkenbosch/meteoalert-api) python wraaper for the MeteoAlarm API.

## Disclaimer

This integration is not affiliated with or endorsed by MeteoAlarm or any of its associated organizations. Use of this integration is at your own risk.

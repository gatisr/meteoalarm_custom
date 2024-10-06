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
   - **Province**: The province code for the desired location (e.g., "LV001").
   - **Language**: The language code for the alerts (e.g., "en").
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
  - `senderName`: The name of the sender of the alert.
  - `description`: The description of the alert.
  - `web`: The web URL for more information about the alert.
  - `contact`: Contact information for the alert.
  - `awareness_level`: The awareness level of the alert.
  - `awareness_type`: The awareness type of the alert.

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
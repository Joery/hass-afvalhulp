# hass-afvalhulp
Home Assistant integration for Afvalhulp, used by various Dutch municipalities for trash pickup.

[![HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Joery&repository=hass-afvalhulp)

## Entities
Each configured address provides:

- Blue Bin sensor
- Green Bin sensor
- Grey Bin sensor
- Afvalhulp calendar

Sensor state examples:

- `Today, Thursday, 01-10-2026`
- `Tomorrow, Friday, 02-10-2026`
- `Monday, 05-10-2026`

Each sensor provides a `days_until` attribute (`0` for today, `1` for tomorrow, etc.), which can be used for automations, dashboard visibility conditions, and other templates.

## Design
During initial setup, the integration uses the postal code and house number to retrieve the address-specific Afvalhulp `.ics` calendar URL.
Home Assistant's built-in `DataUpdateCoordinator` refreshes the `.ics` feed every six hours and updates the entities when the collection schedule changes.

## Installation

### HACS
1. Search for **Afvalhulp** in HACS or use the button above.
2. Install **Afvalhulp**.
3. Restart Home Assistant.
4. Add **Afvalhulp** under **Settings > Devices & services**.
5. Enter your postal code and house number.

### Manual
Copy `custom_components/afvalhulp` into `/config/custom_components/` and restart Home Assistant.

## Contributing
Contributions are welcome. If you find any issues or have improvements, you can create an [issue](https://codeberg.org/Zegers/hass-afvalhulp/issues) or [pull request](https://codeberg.org/Zegers/hass-afvalhulp/pulls) on Codeberg or on [GitHub](https://github.com/Joery/hass-afvalhulp).

## License
This repo is licensed under the [GNU General Public License v3.0](LICENSE).

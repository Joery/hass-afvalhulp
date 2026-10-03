# hass-afvalhulp
Home Assistant integration for Afvalhulp, used by various Dutch municipalities for trash pickup.

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
1. Add `https://github.com/Joery/hass-afvalhulp` to HACS as a custom **Integration** repository.
2. Install **Afvalhulp**.
3. Restart Home Assistant.
4. Add **Afvalhulp** under **Settings > Devices & services**.
5. Enter your postal code and house number.

### Manual
Copy `custom_components/afvalhulp` into `/config/custom_components/` and restart Home Assistant.

## Contributing
Contributions are welcome. If you find any issues or have improvements, you can create an [issue](https://codeberg.org/Zegers/hass-afvalhulp/issues) or [pull request](https://codeberg.org/Zegers/hass-afvalhulp/pulls).

## License
This repo is licensed under the [GNU General Public License v3.0](LICENSE).

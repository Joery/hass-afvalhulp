"""Constants"""

from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "afvalhulp"
PLATFORMS = (Platform.SENSOR, Platform.CALENDAR)
UPDATE_INTERVAL = timedelta(hours=6)
CONF_POSTCODE = "postcode"
CONF_HOUSE_NUMBER = "house_number"
CONF_ADDITION = "addition"
CONF_CALENDAR_URL = "calendar_url"
BASE_URL = "https://mijn.afvalhulp.nl"
POSTCODE_URL = f"{BASE_URL}/postcode"

BINS = {
    "blue": ("Blue Bin", "Papier ophaal"),
    "grey": ("Grey Bin", "PMD+ ophaal"),
    "green": ("Green Bin", "GFT ophaal"),
}

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

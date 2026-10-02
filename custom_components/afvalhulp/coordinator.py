"""Data Coordinator"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import AfvalhulpError, Pickup, fetch_pickups
from .const import CONF_CALENDAR_URL, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class AfvalhulpCoordinator(DataUpdateCoordinator[tuple[Pickup, ...]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self._session = async_get_clientsession(hass)
        self._calendar_url = entry.data[CONF_CALENDAR_URL]
    async def _async_update_data(self) -> tuple[Pickup, ...]:
        try:
            return await fetch_pickups(self._session, self._calendar_url)
        except AfvalhulpError as err:
            raise UpdateFailed(str(err)) from err

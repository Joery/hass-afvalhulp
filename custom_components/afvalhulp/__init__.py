"""Afvalhulp Integration"""

from aiohttp import CookieJar
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .api import AfvalhulpError, discover_calendar_url
from .const import (
    CONF_ADDITION,
    CONF_CALENDAR_URL,
    CONF_HOUSE_NUMBER,
    CONF_POSTCODE,
    PLATFORMS,
)
from .coordinator import AfvalhulpCoordinator

type AfvalhulpConfigEntry = ConfigEntry[AfvalhulpCoordinator]

async def async_setup_entry(hass: HomeAssistant, entry: AfvalhulpConfigEntry) -> bool:
    if CONF_CALENDAR_URL not in entry.data:
        session = async_create_clientsession(
            hass, cookie_jar=CookieJar(), auto_cleanup=False
        )
        try:
            calendar_url = await discover_calendar_url(
                session,
                entry.data[CONF_POSTCODE],
                entry.data[CONF_HOUSE_NUMBER],
                entry.data.get(CONF_ADDITION, entry.data.get("house_number_addition", "")),
            )
        except AfvalhulpError as err:
            raise ConfigEntryNotReady(str(err)) from err
        finally:
            session.detach()
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_CALENDAR_URL: calendar_url}
        )
    coordinator = AfvalhulpCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: AfvalhulpConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

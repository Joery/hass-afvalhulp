"""Config Flow"""

from __future__ import annotations
import re
import voluptuous as vol
from typing import Any
from aiohttp import CookieJar
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .api import AfvalhulpError, discover_calendar_url, normalize_postcode
from .const import (
    CONF_ADDITION,
    CONF_CALENDAR_URL,
    CONF_HOUSE_NUMBER,
    CONF_POSTCODE,
    DOMAIN,
)

_POSTCODE_RE = re.compile(r"^[1-9][0-9]{3}[A-Z]{2}$")

class AfvalhulpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            postcode = normalize_postcode(user_input[CONF_POSTCODE])
            house_number = user_input[CONF_HOUSE_NUMBER]
            addition = user_input.get(CONF_ADDITION, "").strip()
            if not _POSTCODE_RE.fullmatch(postcode):
                errors[CONF_POSTCODE] = "invalid_postcode"
            else:
                await self.async_set_unique_id(f"{postcode}-{house_number}-{addition.lower()}")
                self._abort_if_unique_id_configured()
                session = async_create_clientsession(
                    self.hass, cookie_jar=CookieJar(), auto_cleanup=False
                )
                try:
                    calendar_url = await discover_calendar_url(
                        session, postcode, house_number, addition
                    )
                except AfvalhulpError:
                    errors["base"] = "cannot_connect"
                finally:
                    session.detach()
                if not errors:
                    return self.async_create_entry(
                        title=f"{postcode} {house_number}{addition}",
                        data={
                            CONF_POSTCODE: postcode,
                            CONF_HOUSE_NUMBER: house_number,
                            CONF_ADDITION: addition,
                            CONF_CALENDAR_URL: calendar_url,
                        },
                    )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POSTCODE): str,
                    vol.Required(CONF_HOUSE_NUMBER): vol.All(vol.Coerce(int), vol.Range(min=1)),
                    vol.Optional(CONF_ADDITION, default=""): str,
                }
            ),
            errors=errors,
        )

"""Calendar"""

from datetime import datetime, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
from . import AfvalhulpConfigEntry
from .api import Pickup
from .coordinator import AfvalhulpCoordinator

CALENDAR_NAMES = {
    "blue": "Blue Bin",
    "grey": "Grey Bin",
    "green": "Green Bin",
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: AfvalhulpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([AfvalhulpCalendar(entry.runtime_data, entry)])

class AfvalhulpCalendar(CoordinatorEntity[AfvalhulpCoordinator], CalendarEntity):
    _attr_has_entity_name = True
    _attr_name = "Calendar"
    _attr_icon = "mdi:calendar-trash"
    def __init__(self, coordinator: AfvalhulpCoordinator, entry: AfvalhulpConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_calendar"
    @staticmethod
    def _event(pickup: Pickup) -> CalendarEvent:
        return CalendarEvent(
            summary=CALENDAR_NAMES.get(pickup.bin_type, pickup.summary),
            start=pickup.date,
            end=pickup.date + timedelta(days=1),
        )
    @property
    def event(self) -> CalendarEvent | None:
        today = dt_util.now().date()
        pickup = next((item for item in self.coordinator.data if item.date >= today), None)
        return self._event(pickup) if pickup else None
    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        start = start_date.date()
        end = end_date.date()
        return [
            self._event(item)
            for item in self.coordinator.data
            if start <= item.date < end
        ]

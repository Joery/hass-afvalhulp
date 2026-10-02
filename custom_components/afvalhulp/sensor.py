"""Sensors"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
from . import AfvalhulpConfigEntry
from .api import Pickup
from .const import BINS, WEEKDAYS
from .coordinator import AfvalhulpCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: AfvalhulpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(
        AfvalhulpSensor(entry.runtime_data, entry, bin_type) for bin_type in BINS
    )

class AfvalhulpSensor(CoordinatorEntity[AfvalhulpCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:trash-can"
    def __init__(
        self,
        coordinator: AfvalhulpCoordinator,
        entry: AfvalhulpConfigEntry,
        bin_type: str,
    ) -> None:
        super().__init__(coordinator)
        self._bin_type = bin_type
        self._attr_name = BINS[bin_type][0]
        self._attr_unique_id = f"{entry.unique_id}_{bin_type}"
    @property
    def _pickup(self) -> Pickup | None:
        today = dt_util.now().date()
        return next(
            (item for item in self.coordinator.data if item.bin_type == self._bin_type and item.date >= today),
            None,
        )
    @property
    def native_value(self) -> str | None:
        pickup = self._pickup
        if pickup is None:
            return None
        days = (pickup.date - dt_util.now().date()).days
        weekday = WEEKDAYS[pickup.date.weekday()]
        if days == 0:
            label = f"Today, {weekday}"
        elif days == 1:
            label = f"Tomorrow, {weekday}"
        else:
            label = weekday
        return f"{label}, {pickup.date:%d-%m-%Y}"
    @property
    def extra_state_attributes(self) -> dict[str, int | None]:
        pickup = self._pickup
        return {
            "days_until": None if pickup is None else (pickup.date - dt_util.now().date()).days
        }

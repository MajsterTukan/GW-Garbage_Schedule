"""Sensors for Waste Collection."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import WasteCollectionConfigEntry
from .const import DOMAIN, FRACTION_ICONS, FRACTION_NAMES
from .coordinator import WasteCollectionCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WasteCollectionConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create one sensor for every fraction present in the JSON."""
    coordinator = entry.runtime_data

    async_add_entities(
        WasteCollectionSensor(coordinator, entry.entry_id, fraction)
        for fraction in coordinator.data.dates
    )


class WasteCollectionSensor(
    CoordinatorEntity[WasteCollectionCoordinator],
    SensorEntity,
):
    """Next collection date for one waste fraction."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WasteCollectionCoordinator,
        entry_id: str,
        fraction: str,
    ) -> None:
        """Initialize a waste collection sensor."""
        super().__init__(coordinator)

        self._fraction = fraction
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{fraction}"
        self._attr_name = FRACTION_NAMES.get(
            fraction,
            fraction.replace("_", " ").title(),
        )
        self._attr_icon = FRACTION_ICONS.get(
            fraction,
            "mdi:trash-can-outline",
        )

    @property
    def native_value(self) -> str:
        """Return the nearest collection date or information about its absence."""
        today = dt_util.now().date()

        next_date = next(
            (
                value
                for value in self.coordinator.data.dates[self._fraction]
                if value >= today
            ),
            None,
        )

        if next_date is None:
            return "Brak dodatkowych wywozów"

        return next_date.isoformat()

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return automation and diagnostic attributes."""
        today = dt_util.now().date()

        upcoming = [
            value
            for value in self.coordinator.data.dates[self._fraction]
            if value >= today
        ]

        next_date = upcoming[0] if upcoming else None
        days_remaining = (next_date - today).days if next_date else None

        if days_remaining is None:
            status = "finished"
        elif days_remaining == 0:
            status = "today"
        elif days_remaining == 1:
            status = "tomorrow"
        else:
            status = "scheduled"

        return {
            "days_remaining": days_remaining,
            "status": status,
            "year": self.coordinator.data.year,
            "source": self.coordinator.data.source,
            "collection_day": self.coordinator.data.collection_day,
            "upcoming": [value.isoformat() for value in upcoming],
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Group fraction sensors into one Home Assistant device."""
        schedule = self.coordinator.data

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=f"Wywóz odpadów - {schedule.location}",
            manufacturer="Waste Collection",
            model=f"Harmonogram {schedule.year}",
        )

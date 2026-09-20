"""Coordinator for Waste Collection."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .schedule import Schedule, discover_schedules

_LOGGER = logging.getLogger(__name__)


class WasteCollectionCoordinator(DataUpdateCoordinator[Schedule]):
    """Reload a bundled schedule and expose it to entities."""

    def __init__(self, hass: HomeAssistant, schedule_id: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=6),
        )
        self.schedule_id = schedule_id

    async def _async_update_data(self) -> Schedule:
        schedules, errors = await self.hass.async_add_executor_job(discover_schedules)
        if self.schedule_id not in schedules:
            detail = "; ".join(errors) if errors else "brak pliku"
            raise UpdateFailed(f"Nie znaleziono harmonogramu {self.schedule_id}: {detail}")
        return schedules[self.schedule_id]

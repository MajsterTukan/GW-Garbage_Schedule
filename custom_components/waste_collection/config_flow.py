"""Config flow for Waste Collection."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import SelectOptionDict, SelectSelector, SelectSelectorConfig

from .const import CONF_SCHEDULE, CONF_YEAR, DOMAIN
from .schedule import Schedule, discover_schedules, schedules_for_year


def _select(options: list[SelectOptionDict]) -> SelectSelector:
    return SelectSelector(SelectSelectorConfig(options=options, sort=True))


class _ScheduleFlowMixin:
    """Shared year and schedule selection."""

    _schedules: dict[str, Schedule]
    _selected_year: int

    async def _load_schedules(self) -> bool:
        self._schedules, _errors = await self.hass.async_add_executor_job(discover_schedules)
        return bool(self._schedules)

    async def async_step_year(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Choose a year before showing locations."""
        if not hasattr(self, "_schedules") and not await self._load_schedules():
            return self.async_abort(reason="no_schedules")

        years = sorted({schedule.year for schedule in self._schedules.values()}, reverse=True)
        if user_input is not None:
            self._selected_year = int(user_input[CONF_YEAR])
            return await self.async_step_schedule()

        options = [SelectOptionDict(value=str(year), label=str(year)) for year in years]
        return self.async_show_form(
            step_id="year",
            data_schema=vol.Schema({vol.Required(CONF_YEAR, default=str(years[0])): _select(options)}),
        )

    async def async_step_schedule(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Choose one schedule from the selected year."""
        choices = schedules_for_year(self._schedules, self._selected_year)
        if not choices:
            return self.async_abort(reason="no_schedules_for_year")
        if user_input is not None:
            return self._finish(user_input[CONF_SCHEDULE])

        options = [
            SelectOptionDict(value=schedule_id, label=schedule.location)
            for schedule_id, schedule in sorted(choices.items(), key=lambda item: item[1].location.casefold())
        ]
        return self.async_show_form(
            step_id="schedule",
            data_schema=vol.Schema({vol.Required(CONF_SCHEDULE): _select(options)}),
        )

    def _finish(self, schedule_id: str) -> ConfigFlowResult:
        raise NotImplementedError


class WasteCollectionConfigFlow(_ScheduleFlowMixin, ConfigFlow, domain=DOMAIN):
    """Handle initial setup."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Start with year selection."""
        return await self.async_step_year(user_input)

    def _finish(self, schedule_id: str) -> ConfigFlowResult:
        schedule = self._schedules[schedule_id]
        return self.async_create_entry(
            title=schedule.location,
            data={CONF_YEAR: schedule.year, CONF_SCHEDULE: schedule_id},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return WasteCollectionOptionsFlow()


class WasteCollectionOptionsFlow(_ScheduleFlowMixin, OptionsFlow):
    """Allow switching year and schedule without recreating the entry."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Start options flow."""
        return await self.async_step_year(user_input)

    def _finish(self, schedule_id: str) -> ConfigFlowResult:
        schedule = self._schedules[schedule_id]
        self.hass.config_entries.async_update_entry(self.config_entry, title=schedule.location)
        return self.async_create_entry(
            title="",
            data={CONF_YEAR: schedule.year, CONF_SCHEDULE: schedule_id},
        )

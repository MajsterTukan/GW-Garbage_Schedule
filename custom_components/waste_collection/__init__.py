"""Waste Collection integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_SCHEDULE, DOMAIN, PLATFORMS
from .coordinator import WasteCollectionCoordinator

type WasteCollectionConfigEntry = ConfigEntry[WasteCollectionCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: WasteCollectionConfigEntry) -> bool:
    """Set up Waste Collection from a config entry."""
    schedule_id = entry.options.get(CONF_SCHEDULE, entry.data[CONF_SCHEDULE])
    coordinator = WasteCollectionCoordinator(hass, schedule_id)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: WasteCollectionConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: WasteCollectionConfigEntry) -> None:
    """Reload after changing year or schedule in options."""
    await hass.config_entries.async_reload(entry.entry_id)

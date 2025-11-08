"""Select platform for Furbulous Cat."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .device import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Furbulous Cat select entities from a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    coordinator = coordinators["coordinator"]

    selects = []
    for device in coordinator.data.get("devices", []):
        selects.append(FurbulousCatCleanDelaySelect(coordinator, device))

    async_add_entities(selects)


class FurbulousCatCleanDelaySelect(CoordinatorEntity, SelectEntity):
    """Select entity for auto-clean delay (1-30 minutes)."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_clean_delay"
        self._attr_name = f"{device['name']} - Délai de nettoyage"
        self._attr_icon = "mdi:timer-outline"
        self._attr_device_info = get_device_info(device)
        
        # Options: 1 à 30 minutes
        self._attr_options = [f"{i} min" for i in range(1, 31)]

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("iotid") == self.device_data["iotid"]:
                properties = device.get("properties", {})
                delay = properties.get("catCleanOnOff")
                
                # Handle both dict and direct value
                if isinstance(delay, dict):
                    delay_value = delay.get("value", 0)
                else:
                    delay_value = delay
                
                # Return formatted option (e.g., "5 min")
                if delay_value and 1 <= delay_value <= 30:
                    return f"{delay_value} min"
                
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Extract number from option (e.g., "5 min" -> 5)
        try:
            delay_minutes = int(option.split()[0])
        except (ValueError, IndexError):
            _LOGGER.error("Invalid delay option: %s", option)
            return
        
        if not (1 <= delay_minutes <= 30):
            _LOGGER.error("Delay must be between 1 and 30 minutes, got: %d", delay_minutes)
            return
        
        iotid = self.device_data["iotid"]
        _LOGGER.info("Setting clean delay to %d minutes for device %s", delay_minutes, iotid)
        
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"catCleanOnOff": delay_minutes}
        )
        
        if success:
            _LOGGER.info("✅ Clean delay set to %d minutes for device %s", delay_minutes, iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("❌ Failed to set clean delay for device %s", iotid)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("iotid") == self.device_data["iotid"]:
                properties = device.get("properties", {})
                delay = properties.get("catCleanOnOff")
                
                if isinstance(delay, dict):
                    delay_value = delay.get("value", 0)
                else:
                    delay_value = delay
                
                return {
                    "delay_minutes": delay_value,
                    "min_delay": 1,
                    "max_delay": 30,
                }
        
        return {}

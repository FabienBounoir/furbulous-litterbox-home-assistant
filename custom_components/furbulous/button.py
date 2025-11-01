"""Button platform for Furbulous Cat."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
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
    """Set up Furbulous Cat buttons from a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    coordinator = coordinators["coordinator"]

    buttons = []
    for device in coordinator.data.get("devices", []):
        # Add manual clean button
        buttons.append(FurbulousCatManualCleanButton(coordinator, device))
        # Add dump button
        buttons.append(FurbulousCatDumpButton(coordinator, device))
        # Add auto-pack button
        buttons.append(FurbulousCatAutoPackButton(coordinator, device))
        # Add DND toggle button
        buttons.append(FurbulousCatDNDButton(coordinator, device))

    async_add_entities(buttons)


class FurbulousCatManualCleanButton(ButtonEntity):
    """Representation of a Furbulous Cat manual clean button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_manual_clean"
        self._attr_name = f"{device['name']} Manual Clean"
        self._attr_icon = "mdi:broom"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - start manual cleaning."""
        iotid = self.device_data["iotid"]
        
        # Set handMode to 1 to trigger manual clean
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"handMode": 1}
        )
        
        if success:
            _LOGGER.info("Manual cleaning started for device %s", iotid)
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to start manual cleaning for device %s", iotid)


class FurbulousCatDumpButton(ButtonEntity):
    """Representation of a Furbulous Cat dump/empty button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_dump"
        self._attr_name = f"{device['name']} Vider"
        self._attr_icon = "mdi:delete-empty"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - start dump/empty mode."""
        iotid = self.device_data["iotid"]
        
        # Set handMode to 2 to trigger dump mode
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"handMode": 2}
        )
        
        if success:
            _LOGGER.info("Dump mode started for device %s", iotid)
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to start dump mode for device %s", iotid)


class FurbulousCatAutoPackButton(ButtonEntity):
    """Representation of a Furbulous Cat auto-pack button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_auto_pack"
        self._attr_name = f"{device['name']} Emballage automatique"
        self._attr_icon = "mdi:package-variant-closed"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - start auto-pack mode."""
        iotid = self.device_data["iotid"]
        
        # Set handMode to 3 to trigger auto-pack mode
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"handMode": 3}
        )
        
        if success:
            _LOGGER.info("Auto-pack mode started for device %s", iotid)
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to start auto-pack mode for device %s", iotid)


class FurbulousCatDNDButton(ButtonEntity):
    """Representation of a Furbulous Cat Do Not Disturb toggle button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_dnd_toggle"
        self._attr_name = f"{device['name']} Toggle Do Not Disturb"
        self._attr_icon = "mdi:bell-off"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - toggle DND mode."""
        iotid = self.device_data["iotid"]
        
        # Get current DND state
        current_dnd = self.device_data.get("is_disturb", 0)
        new_dnd = 0 if current_dnd == 1 else 1
        
        # Toggle DND mode
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_disturb,
            iotid,
            bool(new_dnd)
        )
        
        if success:
            _LOGGER.info("DND mode toggled for device %s: %s", iotid, bool(new_dnd))
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to toggle DND mode for device %s", iotid)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "current_dnd_state": "on" if self.device_data.get("is_disturb", 0) == 1 else "off"
        }

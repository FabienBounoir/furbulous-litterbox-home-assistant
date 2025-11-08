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
    # Boutons de contrôle du nettoyage manuel
    for device in coordinator.data.get("devices", []):
        buttons.append(FurbulousCatManualCleanButton(coordinator, device))
        buttons.append(FurbulousCatPauseCleanButton(coordinator, device))
        buttons.append(FurbulousCatResumeCleanButton(coordinator, device))
        buttons.append(FurbulousCatDumpButton(coordinator, device))
        buttons.append(FurbulousCatPackButton(coordinator, device))

    async_add_entities(buttons)


class FurbulousCatManualCleanButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Furbulous Cat manual clean button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_manual_clean"
        self._attr_name = f"{device['name']} Nettoyage Manuel"
        self._attr_icon = "mdi:broom"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - start manual cleaning."""
        iotid = self.device_data["iotid"]
        
        _LOGGER.info("🧹 Manual clean button pressed for device %s", iotid)
        
        try:
            # Utiliser set_device_property avec handMode: 1
            # Le payload sera: {"iotid": "...", "items": {"handMode": 1}}
            success = await self.hass.async_add_executor_job(
                self.coordinator.api.set_device_property,
                iotid,
                {"handMode": 1}
            )
            
            if success:
                _LOGGER.info("✅ Manual cleaning successfully started for device %s", iotid)
                # Refresh coordinator data immediately to see the change
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("❌ Failed to start manual cleaning for device %s", iotid)
        except Exception as err:
            _LOGGER.error("❌ Exception during manual clean for device %s: %s", iotid, err, exc_info=True)


class FurbulousCatPauseCleanButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Furbulous Cat pause cleaning button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_pause_clean"
        self._attr_name = f"{device['name']} Pause Nettoyage"
        self._attr_icon = "mdi:pause"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - pause manual cleaning."""
        iotid = self.device_data["iotid"]
        
        _LOGGER.info("⏸️ Pause clean button pressed for device %s", iotid)
        
        try:
            # handMode: 4 = Pause
            success = await self.hass.async_add_executor_job(
                self.coordinator.api.set_device_property,
                iotid,
                {"handMode": 4}
            )
            
            if success:
                _LOGGER.info("✅ Cleaning paused for device %s", iotid)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("❌ Failed to pause cleaning for device %s", iotid)
        except Exception as err:
            _LOGGER.error("❌ Exception during pause for device %s: %s", iotid, err, exc_info=True)


class FurbulousCatResumeCleanButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Furbulous Cat resume cleaning button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_resume_clean"
        self._attr_name = f"{device['name']} Reprendre Nettoyage"
        self._attr_icon = "mdi:play"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - resume manual cleaning."""
        iotid = self.device_data["iotid"]
        
        _LOGGER.info("▶️ Resume clean button pressed for device %s", iotid)
        
        try:
            # handMode: 5 = Resume
            success = await self.hass.async_add_executor_job(
                self.coordinator.api.set_device_property,
                iotid,
                {"handMode": 5}
            )
            
            if success:
                _LOGGER.info("✅ Cleaning resumed for device %s", iotid)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("❌ Failed to resume cleaning for device %s", iotid)
        except Exception as err:
            _LOGGER.error("❌ Exception during resume for device %s: %s", iotid, err, exc_info=True)


class FurbulousCatDumpButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Furbulous Cat dump/empty button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_dump"
        self._attr_name = f"{device['name']} Vider"
        self._attr_icon = "mdi:delete-empty"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - dump/empty litter box."""
        iotid = self.device_data["iotid"]
        _LOGGER.info("🗑️ Dump button pressed for device %s", iotid)
        
        try:
            # Set handMode to 2 to trigger dump mode
            success = await self.hass.async_add_executor_job(
                self.coordinator.api.set_device_property,
                iotid,
                {"handMode": 2}
            )
            
            if success:
                _LOGGER.info("✅ Dump started for device %s", iotid)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("❌ Failed to dump for device %s", iotid)
        except Exception as err:
            _LOGGER.error("❌ Exception during dump for device %s: %s", iotid, err, exc_info=True)


class FurbulousCatPackButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Furbulous Cat pack bag button."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_pack"
        self._attr_name = f"{device['name']} Emballer"
        self._attr_icon = "mdi:package"
        self._attr_device_info = get_device_info(device)

    async def async_press(self) -> None:
        """Handle the button press - pack the waste bag."""
        iotid = self.device_data["iotid"]
        _LOGGER.info("📦 Pack button pressed for device %s", iotid)
        
        try:
            # Set handMode to 3 to trigger pack mode
            success = await self.hass.async_add_executor_job(
                self.coordinator.api.set_device_property,
                iotid,
                {"handMode": 3}
            )
            
            if success:
                _LOGGER.info("✅ Pack started for device %s", iotid)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("❌ Failed to pack for device %s", iotid)
        except Exception as err:
            _LOGGER.error("❌ Exception during pack for device %s: %s", iotid, err, exc_info=True)

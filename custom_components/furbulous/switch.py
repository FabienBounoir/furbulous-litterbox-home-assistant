"""Switch platform for Furbulous Cat - HomeKit Compatible."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up Furbulous Cat switches from a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    coordinator = coordinators["coordinator"]

    switches = []
    for device in coordinator.data.get("devices", []):
        # Add switches for HomeKit compatibility
        switches.extend([
            FurbulousCatFullAutoModeSwitch(coordinator, device),
            FurbulousCatDNDSwitch(coordinator, device),
            FurbulousCatChildLockSwitch(coordinator, device),
        ])

    async_add_entities(switches)


class FurbulousCatFullAutoModeSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for full auto mode - HomeKit compatible."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_full_auto_mode_switch"
        self._attr_name = f"{device['name']} - Mode auto complet"
        self._attr_icon = "mdi:auto-mode"
        self._attr_device_info = get_device_info(device)

    @property
    def is_on(self) -> bool:
        """Return true if full auto mode is on."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("iotid") == self.device_data["iotid"]:
                properties = device.get("properties", {})
                prop = properties.get("FullAutoModeSwitch")
                if prop:
                    if isinstance(prop, dict):
                        return prop.get("value", 0) == 1
                    return prop == 1
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on full auto mode."""
        iotid = self.device_data["iotid"]
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"FullAutoModeSwitch": 1}
        )
        if success:
            _LOGGER.info("Full auto mode enabled for device %s", iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to enable full auto mode for device %s", iotid)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off full auto mode."""
        iotid = self.device_data["iotid"]
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"FullAutoModeSwitch": 0}
        )
        if success:
            _LOGGER.info("Full auto mode disabled for device %s", iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to disable full auto mode for device %s", iotid)


class FurbulousCatDNDSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for Do Not Disturb mode - HomeKit compatible."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_dnd_switch"
        self._attr_name = f"{device['name']} - Ne pas déranger"
        self._attr_icon = "mdi:moon-waning-crescent"
        self._attr_device_info = get_device_info(device)

    @property
    def is_on(self) -> bool:
        """Return true if DND is on."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("id") == self.device_data["id"]:
                return device.get("is_disturb", 0) == 1
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on DND."""
        iotid = self.device_data["iotid"]
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_disturb,
            iotid,
            True
        )
        if success:
            _LOGGER.info("DND enabled for device %s", iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to enable DND for device %s", iotid)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off DND."""
        iotid = self.device_data["iotid"]
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_disturb,
            iotid,
            False
        )
        if success:
            _LOGGER.info("DND disabled for device %s", iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to disable DND for device %s", iotid)


class FurbulousCatChildLockSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for child lock - HomeKit compatible."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.device_data = device
        self._attr_unique_id = f"{device['iotid']}_child_lock_switch"
        self._attr_name = f"{device['name']} - Verrouillage enfant"
        self._attr_icon = "mdi:lock"
        self._attr_device_info = get_device_info(device)

    @property
    def is_on(self) -> bool:
        """Return true if child lock is on."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("iotid") == self.device_data["iotid"]:
                properties = device.get("properties", {})
                prop = properties.get("childLockOnOff")
                if prop:
                    if isinstance(prop, dict):
                        return prop.get("value", 0) == 1
                    return prop == 1
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on child lock."""
        iotid = self.device_data["iotid"]
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"childLockOnOff": 1}
        )
        if success:
            _LOGGER.info("Child lock enabled for device %s", iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to enable child lock for device %s", iotid)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off child lock."""
        iotid = self.device_data["iotid"]
        success = await self.hass.async_add_executor_job(
            self.coordinator.api.set_device_property,
            iotid,
            {"childLockOnOff": 0}
        )
        if success:
            _LOGGER.info("Child lock disabled for device %s", iotid)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to disable child lock for device %s", iotid)

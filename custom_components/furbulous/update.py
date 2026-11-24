"""Firmware update entity for Furbulous Cat (read-only: install it from the app)."""
from __future__ import annotations

from homeassistant.components.update import UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device import get_device_info


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        FurbulousCatFirmwareUpdate(coordinator, device)
        for device in coordinator.data.get("devices", [])
        if device.get("iotid")
    )


class FurbulousCatFirmwareUpdate(CoordinatorEntity, UpdateEntity):
    """Shows when the app offers a new firmware.

    ponytail: no install() on purpose; a failed OTA bricks the box until someone fixes it in the app.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "firmware"

    def __init__(self, coordinator, device: dict) -> None:
        super().__init__(coordinator)
        self._iotid = device["iotid"]
        self._attr_unique_id = f"{self._iotid}_firmware"
        self._attr_device_info = get_device_info(device)

    @property
    def _ota(self) -> dict:
        for device in self.coordinator.data.get("devices", []):
            if device.get("iotid") == self._iotid:
                return device.get("ota") or {}
        return {}

    # API: {"mcu_version": {"current_version", "version", "release_note"}, "wifi_version": {...}}
    def _versions(self, field: str) -> str | None:
        parts = [f"{name} {mod.get(field)}" for name, mod in (("MCU", self._ota.get("mcu_version")), ("WiFi", self._ota.get("wifi_version"))) if mod and mod.get(field)]
        return " · ".join(parts) or None

    @property
    def installed_version(self) -> str | None:
        return self._versions("current_version")

    @property
    def latest_version(self) -> str | None:
        return self._versions("version") or self.installed_version

    @property
    def release_summary(self) -> str | None:
        notes = " ".join(m.get("release_note") or "" for m in self._ota.values() if isinstance(m, dict)).strip()
        return notes[:255] or None

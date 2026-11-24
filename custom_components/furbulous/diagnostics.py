"""Diagnostics: Settings > Devices > Furbulous > Download diagnostics. Attach it to bug reports."""
from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {"email", "password", "token", "identity_id", "account", "mobile", "phone", "user_id", "uid", "mac", "ssid", "address", "latitude", "longitude"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    return async_redact_data(
        {
            "entry": dict(entry.data),
            "websocket_url": coordinator.api.ws_url,
            "kicked_remaining_s": coordinator.api.kicked_remaining,
            "last_visit": coordinator.last_visit,
            # every raw property + its last-change time: how new codes (like workstatus 5/6) get discovered
            "data": coordinator.data,
        },
        TO_REDACT,
    )

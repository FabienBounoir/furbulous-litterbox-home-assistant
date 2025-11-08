"""The Furbulous Cat integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .furbulous_api import FurbulousCatAPI, FurbulousCatAuthError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SWITCH, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Furbulous Cat from a config entry."""
    # Use email/password authentication with account_type = 1
    api = FurbulousCatAPI(
        email=entry.data.get("email"),
        password=entry.data.get("password"),
        account_type=entry.data.get("account_type", 1)
    )
    
    try:
        await hass.async_add_executor_job(api.authenticate)
    except FurbulousCatAuthError as err:
        raise ConfigEntryAuthFailed from err

    # Coordinateur normal (5 minutes) pour les données générales
    coordinator = FurbulousCatDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    
    # Coordinateur rapide (30 secondes) pour la détection du chat dans la litière
    fast_coordinator = FurbulousCatFastUpdateCoordinator(hass, api)
    await fast_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "fast_coordinator": fast_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class FurbulousCatDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Furbulous Cat data."""

    def __init__(self, hass: HomeAssistant, api: FurbulousCatAPI) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_data)
        except FurbulousCatAuthError as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class FurbulousCatFastUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fast fetching of cat presence data (30 seconds)."""

    def __init__(self, hass: HomeAssistant, api: FurbulousCatAPI) -> None:
        """Initialize fast coordinator for cat detection."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_fast",
            update_interval=timedelta(seconds=30),  # Mise à jour rapide toutes les 30 secondes
        )

    async def _async_update_data(self):
        """Update cat presence data via library."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_data)
        except FurbulousCatAuthError as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

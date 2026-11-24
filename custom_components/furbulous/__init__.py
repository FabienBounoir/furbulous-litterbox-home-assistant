"""The Furbulous Cat integration."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CAT_NEARBY_STATUSES,
    CAT_PRESENT_STATUSES,
    CONF_REGION,
    DEFAULT_REGION,
    DOMAIN,
    EVENT_FURBULOUS,
    EVENT_NOTIFICATION,
)
from .furbulous_api import FurbulousCatAPI, FurbulousCatAuthError, FurbulousCatKicked, extract_properties

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SWITCH, Platform.SELECT, Platform.UPDATE]

# Real-time changes arrive over the WebSocket; polling is only a safety net (daily stats, missed messages).
POLL_INTERVAL = timedelta(minutes=15)
WS_RETRY_DELAY = 30


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Furbulous Cat from a config entry."""
    api = FurbulousCatAPI(
        email=entry.data.get("email"),
        password=entry.data.get("password"),
        account_type=entry.data.get("account_type", 1),
        region=entry.data.get(CONF_REGION, DEFAULT_REGION),  # entries created before 1.2.0 were EU-only
    )

    try:
        await hass.async_add_executor_job(api.authenticate)
    except FurbulousCatAuthError as err:
        raise ConfigEntryAuthFailed from err

    coordinator = FurbulousCatDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_create_background_task(hass, _websocket_loop(hass, api, coordinator), f"{DOMAIN}_websocket")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _websocket_loop(hass: HomeAssistant, api: FurbulousCatAPI, coordinator: FurbulousCatDataUpdateCoordinator) -> None:
    """Stay connected to the app's push channel. Cancelled automatically on unload."""
    session = async_get_clientsession(hass)
    while True:
        try:
            if api.kicked_remaining:
                await asyncio.sleep(api.kicked_remaining)
            if not api.token:
                await hass.async_add_executor_job(api.authenticate)
                _LOGGER.info("Furbulous session restored")
                await coordinator.async_request_refresh()

            connected_at = time.monotonic()
            async with session.ws_connect(api.ws_url, headers={"Authorization": api.token}, heartbeat=30) as ws:
                _LOGGER.debug("Furbulous WebSocket connected")
                async for msg in ws:
                    if msg.type is aiohttp.WSMsgType.TEXT:
                        coordinator.handle_push(msg.data)
            _LOGGER.debug("Furbulous WebSocket closed by server")
            if time.monotonic() - connected_at > WS_RETRY_DELAY:
                continue  # normal recycle (AWS caps connections at 2 h): reconnect now, don't miss events

        except aiohttp.WSServerHandshakeError as err:
            if err.status in (401, 403):
                api.mark_kicked()  # token refused: someone else logged in
                continue
            _LOGGER.debug("Furbulous WebSocket handshake failed: %s", err)
        except FurbulousCatKicked:
            continue  # loop top waits out the cooldown
        except FurbulousCatAuthError as err:
            _LOGGER.warning("Furbulous re-login failed: %s", err)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.debug("Furbulous WebSocket error: %s", err)
        await asyncio.sleep(WS_RETRY_DELAY)


class FurbulousCatDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Furbulous Cat data."""

    def __init__(self, hass: HomeAssistant, api: FurbulousCatAPI) -> None:
        """Initialize."""
        self.api = api
        # Kept outside self.data, which every poll replaces. Lost on restart (last_active then falls back to the API).
        self.visit_start: dict[str, int] = {}  # iotid -> unix time the cat stepped in
        self.last_visit: dict[str, dict] = {}  # iotid -> {"end", "duration", "weight"}
        self._seen_notifications: set | None = None  # None until the first poll: don't replay history
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=POLL_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            data = await self.hass.async_add_executor_job(self.api.get_data)
            self.update_interval = POLL_INTERVAL
            self._fire_new_notifications(data.get("notifications") or [])
            return data
        except FurbulousCatAuthError as err:
            raise ConfigEntryAuthFailed from err
        except FurbulousCatKicked as err:
            # The WebSocket isn't closed on a kick, so this poll is what logs back in: run it right when the cooldown ends
            self.update_interval = timedelta(seconds=self.api.kicked_remaining + 5)
            raise UpdateFailed(f"Session in use by another device: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def handle_push(self, raw: str) -> None:
        """Apply a WebSocket message: {"type": "property", "iotId": ..., "items": {prop: {"value", "time"}}}."""
        try:
            msg = json.loads(raw)
        except ValueError:
            return
        _LOGGER.debug("Furbulous push: %s", msg)
        if not isinstance(msg, dict) or not self.data:
            return

        items = msg.get("items")
        if msg.get("type") != "property" or not isinstance(items, dict):
            # status / event / delete / bind: format varies, just re-read everything
            self.hass.async_create_task(self.async_request_refresh())
            return

        for device in self.data.get("devices", []):
            if device.get("iotid") == msg.get("iotId"):
                props = device.setdefault("properties", {})
                times = device.setdefault("property_times", {})
                old_status = props.get("workstatus")
                new_props = extract_properties(items, times)
                props.update(new_props)
                self._fire_transitions(device, old_status, new_props, times)
                self.async_set_updated_data(self.data)
                return

    def _fire_transitions(self, device: dict, old_status, new_props: dict, times: dict) -> None:
        """Turn raw property changes into furbulous_event events (+ track visits)."""
        iotid = device["iotid"]
        base = {"iotid": iotid, "device_name": device.get("name")}
        fire = lambda kind, **extra: self.hass.bus.async_fire(EVENT_FURBULOUS, {**base, "type": kind, **extra})  # noqa: E731

        if new_props.get("completionStatus") == 1:
            fire("cleaning_done")

        if "workstatus" not in new_props:
            return
        new_status = new_props["workstatus"]
        now = times.get("workstatus") or int(time.time())

        if new_status in CAT_NEARBY_STATUSES and old_status not in CAT_NEARBY_STATUSES:
            fire("cat_nearby")
        if new_status in CAT_PRESENT_STATUSES and old_status not in CAT_PRESENT_STATUSES:
            self.visit_start[iotid] = now
            fire("cat_entered")
        elif old_status in CAT_PRESENT_STATUSES and new_status not in CAT_PRESENT_STATUSES:
            start = self.visit_start.pop(iotid, None)
            visit = {
                "end": now,
                "duration": now - start if start else None,
                "weight": device.get("properties", {}).get("catWeight"),
            }
            self.last_visit[iotid] = visit
            fire("cat_left", **visit)
            # daily counter / average duration live on the REST side: fetch them now, not in 15 min
            self.hass.async_create_task(self.async_request_refresh())

    def _fire_new_notifications(self, notifications: list[dict]) -> None:
        ids = {n.get("record_id") for n in notifications}
        if self._seen_notifications is not None:
            for n in reversed(notifications):  # API lists newest first; fire oldest first
                if n.get("record_id") not in self._seen_notifications:
                    self.hass.bus.async_fire(EVENT_NOTIFICATION, {
                        "title": n.get("title"), "summary": n.get("summary"), "time": n.get("push_time"),
                    })
        self._seen_notifications = (self._seen_notifications or set()) | ids

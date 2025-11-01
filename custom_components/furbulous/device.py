"""Device handling for Furbulous Cat integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


def get_device_info(device_data: dict) -> DeviceInfo:
    """Return device info for a Furbulous device."""
    return DeviceInfo(
        identifiers={(DOMAIN, str(device_data.get("id")))},
        name=device_data.get("name", "Furbulous Device"),
        manufacturer="Furbulous",
        model=device_data.get("product_name", "Furbulous Box"),
        sw_version=device_data.get("version"),
        configuration_url="https://app.furbulouspet.com",
    )

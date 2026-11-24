"""API client for Furbulous Cat."""
from __future__ import annotations

import hashlib
import logging
import time
import requests
from typing import Any

from .const import (
    DEFAULT_REGION,
    KICK_COOLDOWN,
    REGIONS,
    TOKEN_INVALID_CODE,
    API_AUTH_ENDPOINT,
    API_DEVICE_LIST_ENDPOINT,
    API_DEVICE_PROPERTIES_ENDPOINT,
    API_APPID,
    API_VERSION,
    API_PLATFORM,
    API_USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class FurbulousCatAuthError(Exception):
    """Exception raised for authentication errors."""


def extract_properties(raw: dict, times: dict | None = None) -> dict[str, Any]:
    """{prop: {"value", "time"}} -> {prop: value}, with numeric strings ("1") turned into ints
    so every `== 1` / WORK_STATUS.get(value) downstream works whatever type the API sends.
    If `times` is given, it is filled with {prop: unix seconds of last change}."""
    out = {}
    for key, prop in raw.items():
        if times is not None and isinstance(prop, dict) and prop.get("time"):
            t = int(prop["time"])
            times[key] = t // 1000 if t > 10**12 else t  # ponytail: tolerate ms timestamps
        value = prop.get("value") if isinstance(prop, dict) and "value" in prop else prop
        if isinstance(value, str) and value.lstrip("-").isdigit():
            value = int(value)
        out[key] = value
    return out


class FurbulousCatKicked(Exception):
    """Session taken over by another login (e.g. the phone app). Waiting before logging back in."""


class FurbulousCatAPI:
    """API client for Furbulous Cat."""

    def __init__(self, email: str, password: str, account_type: int = 1, token: str = None, region: str = DEFAULT_REGION) -> None:
        """Initialize the API client."""
        self.email = email
        self.password = password
        self.account_type = account_type
        self.token = token  # Allow pre-set token
        self.identity_id = None
        self.session = requests.Session()
        self.devices = []
        self.base_url, self.ws_url = REGIONS[region]
        self.kicked_until = 0.0

    def mark_kicked(self) -> None:
        """Drop the dead token and hold off re-login for KICK_COOLDOWN seconds."""
        if self.token:
            _LOGGER.warning(
                "Furbulous session taken over (phone app login?). Reconnecting in %d min.",
                KICK_COOLDOWN // 60,
            )
            self.kicked_until = time.time() + KICK_COOLDOWN
        self.token = None

    @property
    def kicked_remaining(self) -> float:
        return max(0.0, self.kicked_until - time.time())

    def _generate_sign(self, timestamp: int, path: str) -> str:
        """Generate signature for API requests.
        
        Algorithm found in decompiled app:
        MD5(appid + url_path + timestamp)
        """
        data = f"{API_APPID}{path}{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()

    def authenticate(self) -> bool:
        """Authenticate with the Furbulous Cat API."""
        if self.kicked_remaining:
            raise FurbulousCatKicked(f"Waiting {int(self.kicked_remaining)}s before logging back in")
        url = f"{self.base_url}{API_AUTH_ENDPOINT}"
        
        # Generate timestamp and signature for login request
        timestamp = int(time.time())
        sign = self._generate_sign(timestamp, API_AUTH_ENDPOINT)
        
        payload = {
            "iso": "DE",
            "area": "EU",
            "account_type": self.account_type,
            "clientid": "65l32f6ql1qehx6",  # From decompiled app
            "brand": "HomeAssistant",
            "client_token": "",
            "password": self.password,
            "AppVersion": "HomeAssistant_1.0.0",
            "account": self.email
        }
        
        headers = {
            "Content-Type": "application/json",
            "appid": API_APPID,
            "version": API_VERSION,
            "accept": "*/*",
            "accept-language": "fr",
            "platform": "ios",  # Use ios like in captured request
            "user-agent": API_USER_AGENT,
            "ts": str(timestamp),
            "sign": sign,
        }

        try:
            _LOGGER.debug("Attempting authentication for account: %s", self.email)
            _LOGGER.debug("Timestamp: %s, Sign: %s", timestamp, sign)
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            _LOGGER.debug("Authentication response code: %s, message: %s", 
                         data.get("code"), data.get("message"))
            
            if data.get("code") != 0:
                raise FurbulousCatAuthError(f"Authentication failed: {data.get('message')}")
            
            auth_data = data.get("data", {})
            self.token = auth_data.get("token")  # Field name is 'token' not 'authorization'
            self.identity_id = auth_data.get("identityid")
            
            if not self.token:
                raise FurbulousCatAuthError("No token received from API")
            
            _LOGGER.info("Successfully authenticated with Furbulous Cat API")
            _LOGGER.debug("Token: %s..., Identity ID: %s", self.token[:10] if self.token else None, self.identity_id)
            return True
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error during authentication: %s", err)
            if hasattr(err, 'response') and err.response is not None:
                _LOGGER.error("Response status: %s, body: %s", 
                            err.response.status_code, err.response.text)
            raise FurbulousCatAuthError(f"Authentication request failed: {err}") from err

    def _get_headers(self, endpoint: str) -> dict:
        """Generate headers for authenticated requests."""
        timestamp = int(time.time())
        sign = self._generate_sign(timestamp, endpoint)
        
        return {
            "Content-Type": "application/json",
            "appid": API_APPID,
            "accept": "*/*",
            "version": API_VERSION,
            "authorization": self.token,
            "accept-language": "fr",
            "platform": "ios",  # Use ios instead of android
            "user-agent": API_USER_AGENT,
            "ts": str(timestamp),
            "sign": sign,
        }

    def _make_authenticated_request(self, endpoint: str, method: str = "GET", data: dict = None, retry_count: int = 0) -> dict:
        """Make an authenticated request to the API with improved retry logic.
        
        Args:
            endpoint: Full endpoint URL including query parameters
            method: HTTP method (GET or POST)
            data: JSON data for POST requests
            retry_count: Internal counter for retry attempts
        """
        if not self.token:
            self.authenticate()
        
        url = f"{self.base_url}{endpoint}"
        # Extract path without query parameters for signature
        base_endpoint = endpoint.split('?')[0]
        headers = self._get_headers(base_endpoint)
        
        max_retries = 3
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=15)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data or {}, timeout=15)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=data or {}, timeout=15)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()
            
            # Check if the response indicates success
            if result.get("code") != 0:
                error_message = result.get("message", "")
                error_code = result.get("code")
                _LOGGER.warning("API returned error code %s: %s", error_code, error_message)
                
                # AMÉLIORATION: Détection robuste des erreurs de token
                # Code 10403 = "无效的 Token" (Invalid Token)
                is_token_error = (
                    error_code in [401, 403, 10401, 10402, TOKEN_INVALID_CODE] or  # Auth error codes
                    "token" in error_message.lower() or
                    "无效的" in error_message or  # Invalid in Chinese
                    "expired" in error_message.lower() or
                    "unauthor" in error_message.lower()
                )

                if is_token_error:
                    # Single session per account: re-login now would kick the phone app.
                    # ponytail: a plain token expiry also waits KICK_COOLDOWN (can't tell them apart; rare)
                    self.mark_kicked()
                    raise FurbulousCatKicked(f"Token invalid (code {error_code})")
            
            return result

        except requests.exceptions.Timeout as err:
            _LOGGER.warning("Request timeout for %s (attempt %d/%d): %s", endpoint, retry_count + 1, max_retries, err)
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                _LOGGER.debug("Retrying after %d seconds...", wait_time)
                time.sleep(wait_time)
                return self._make_authenticated_request(endpoint, method, data, retry_count + 1)
            raise
            
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error making authenticated request to %s (attempt %d/%d): %s", endpoint, retry_count + 1, max_retries, err)
            
            if getattr(err, 'response', None) is not None and err.response.status_code == 401:
                self.mark_kicked()
                raise FurbulousCatKicked("HTTP 401") from err
            
            # Retry on network errors
            if retry_count < max_retries and isinstance(err, (requests.exceptions.ConnectionError, requests.exceptions.HTTPError)):
                wait_time = 2 ** retry_count
                _LOGGER.info("Network error, retrying after %d seconds... (attempt %d/%d)", wait_time, retry_count + 1, max_retries)
                time.sleep(wait_time)
                return self._make_authenticated_request(endpoint, method, data, retry_count + 1)
            
            raise

    def get_devices(self) -> list[dict[str, Any]]:
        """Get list of Furbulous devices."""
        try:
            result = self._make_authenticated_request(API_DEVICE_LIST_ENDPOINT)
            
            if result.get("code") == 0:
                # data is already a list, not a dict with "list" key
                devices_data = result.get("data", [])
                self.devices = devices_data if isinstance(devices_data, list) else []
                _LOGGER.info("Retrieved %d Furbulous devices", len(self.devices))
                return self.devices
            else:
                _LOGGER.error("Failed to get devices: %s", result.get("message"))
                return []
                
        except Exception as err:
            _LOGGER.error("Error getting devices: %s", err)
            raise

    def get_device_properties(self, iotid: str, times: dict | None = None) -> dict[str, Any]:
        """Get properties for a specific device.
        
        Uses the properties/get endpoint which returns all device properties.
        Each property has a 'value' and 'time' field.
        """
        try:
            # Use the properties/get endpoint
            endpoint = f"/app/v1/device/properties/get?iotid={iotid}"
            result = self._make_authenticated_request(endpoint)
            
            if result.get("code") == 0:
                extracted_props = extract_properties(result.get("data") or {}, times)

                _LOGGER.debug("Retrieved %d properties for device %s", len(extracted_props), iotid)
                return extracted_props
            else:
                _LOGGER.warning("Failed to get properties for device %s: %s (code: %s)", 
                              iotid, result.get("message"), result.get("code"))
                return {}
                
        except Exception as err:
            _LOGGER.warning("Error getting properties for device %s: %s", iotid, err)
            # Return empty dict instead of raising - properties are optional
            return {}

    def get_device_daily_stats(self, iotid: str) -> dict[str, Any]:
        """Get daily statistics for a specific device.
        
        Returns data from /app/v1/device/data/wcheader endpoint:
        - times: Number of times used today
        - avg_duration: Average duration in seconds
        - times_diff: Difference from previous day
        - avg_diff: Average duration difference from previous day
        """
        try:
            endpoint = f"/app/v1/device/data/wcheader?iotid={iotid}"
            result = self._make_authenticated_request(endpoint)
            
            if result.get("code") == 0:
                stats = result.get("data", {})
                _LOGGER.debug("Retrieved daily stats for device %s: %s", iotid, stats)
                return stats
            else:
                _LOGGER.warning("Failed to get daily stats for device %s: %s (code: %s)", 
                              iotid, result.get("message"), result.get("code"))
                return {}
                
        except Exception as err:
            _LOGGER.warning("Error getting daily stats for device %s: %s", iotid, err)
            return {}

    def set_device_property(self, iotid: str, properties: dict[str, Any]) -> bool:
        """Set device properties.
        
        Args:
            iotid: Device IoT ID
            properties: Dict of property_name: value to set
            
        Returns:
            True if successful
            
        Example:
            api.set_device_property("873Ef2f3f34l", {"childLockOnOff": 1})
        """
        try:
            endpoint = "/app/v1/device/properties/set"
            # CORRECTION: Les propriétés doivent être dans un objet "items"
            payload = {
                "iotid": iotid,
                "items": properties
            }
            
            result = self._make_authenticated_request(endpoint, method="POST", data=payload)
            
            if result.get("code") == 0:
                success_msg = result.get("message", "Success")
                _LOGGER.info("✅ Successfully set properties for %s: %s (API response: %s)", 
                           iotid, properties, success_msg)
                return True
            else:
                _LOGGER.error("❌ Failed to set properties for %s: code=%s, message=%s", 
                            iotid, result.get("code"), result.get("message"))
                return False
                
        except Exception as err:
            _LOGGER.error("Error setting properties for %s: %s", iotid, err)
            return False

    def set_device_disturb(self, iotid: str, is_disturb: bool) -> bool:
        """Set device Do Not Disturb mode.
        
        Args:
            iotid: Device IoT ID
            is_disturb: True to enable DND, False to disable
            
        Returns:
            True if successful
        """
        try:
            endpoint = "/app/v1/device/disturb"
            payload = {
                "iotid": iotid,
                "is_disturb": 1 if is_disturb else 0
            }
            
            result = self._make_authenticated_request(endpoint, method="PUT", data=payload)
            
            if result.get("code") == 0:
                _LOGGER.info("Successfully set DND mode for %s: %s", iotid, is_disturb)
                return True
            else:
                _LOGGER.error("Failed to set DND mode for %s: %s", iotid, result.get("message"))
                return False
                
        except Exception as err:
            _LOGGER.error("Error setting DND mode for %s: %s", iotid, err)
            return False

    def get_pets(self) -> list[dict[str, Any]]:
        """Get list of all pets.
        
        Returns:
            List of pet dictionaries
        """
        try:
            endpoint = "/app/v1/pet/list"
            result = self._make_authenticated_request(endpoint)
            
            if result.get("code") == 0:
                pets_data = result.get("data", {})
                # The API returns {data: {list: [...]}}
                if isinstance(pets_data, dict):
                    pets = pets_data.get("list", [])
                else:
                    pets = []
                _LOGGER.info("Retrieved %d pets", len(pets))
                return pets
            else:
                _LOGGER.error("Failed to get pets: %s", result.get("message"))
                return []
                
        except Exception as err:
            _LOGGER.error("Error getting pets: %s", err)
            return []

    def get_pet_info(self, pet_id: int) -> dict[str, Any]:
        """Get detailed information for a specific pet.
        
        Args:
            pet_id: Pet ID
            
        Returns:
            Dict with pet information
        """
        try:
            endpoint = f"/app/v1/pet/info?petid={pet_id}"
            result = self._make_authenticated_request(endpoint)
            
            if result.get("code") == 0:
                pet_info = result.get("data", {})
                _LOGGER.debug("Retrieved info for pet %s", pet_id)
                return pet_info if isinstance(pet_info, dict) else {}
            else:
                _LOGGER.warning("Failed to get info for pet %s: %s", pet_id, result.get("message"))
                return {}
                
        except Exception as err:
            _LOGGER.warning("Error getting info for pet %s: %s", pet_id, err)
            return {}

    def get_notifications(self) -> list[dict[str, Any]]:
        """Latest device alerts shown in the app's notice tab: [{record_id, title, summary, push_time, icon}]."""
        try:
            result = self._make_authenticated_request("/app/v1/user/devicePushRecord?page_no=1&page_size=20")
            data = result.get("data") or {}
            return (data.get("list") or []) if result.get("code") == 0 else []
        except FurbulousCatKicked:
            raise
        except Exception as err:
            _LOGGER.warning("Error getting notifications: %s", err)
            return []

    def get_ota(self, iotid: str) -> dict[str, Any]:
        """Firmware info: {currentVersion, firmwareVersion, details, status, ...} ({} when none)."""
        try:
            result = self._make_authenticated_request(f"/app/v1/device/ota?iotid={iotid}")
            return (result.get("data") or {}) if result.get("code") == 0 else {}
        except FurbulousCatKicked:
            raise
        except Exception as err:
            _LOGGER.warning("Error getting firmware info for %s: %s", iotid, err)
            return {}

    def get_data(self) -> dict[str, Any]:
        """Get data from the Furbulous Cat API."""
        devices = self.get_devices()
        
        # Get properties and daily stats for each device
        devices_with_properties = []
        for device in devices:
            iotid = device.get("iotid")
            if iotid:
                device["property_times"] = {}
                properties = self.get_device_properties(iotid, device["property_times"])
                device["properties"] = properties
                device["ota"] = self.get_ota(iotid)
                # Get daily stats from wcheader endpoint
                daily_stats = self.get_device_daily_stats(iotid)
                device["daily_stats"] = daily_stats
            devices_with_properties.append(device)
        
        # Get pets information
        pets = self.get_pets()
        
        # The per-device getters swallow errors and return {}: don't publish a half-empty snapshot if we got kicked mid-way
        if self.token is None:
            raise FurbulousCatKicked("Session lost during refresh")

        return {
            "authenticated": True,
            "token": self.token,
            "identity_id": self.identity_id,
            "devices": devices_with_properties,
            "pets": pets,
            "notifications": self.get_notifications(),
        }

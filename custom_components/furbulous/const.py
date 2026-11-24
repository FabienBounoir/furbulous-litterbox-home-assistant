"""Constants for the Furbulous Cat integration."""

DOMAIN = "furbulous"

# Regions: (REST API host, real-time WebSocket) — from app 2.0.4 CountryBean.getHost/getWebsocket
CONF_REGION = "region"
DEFAULT_REGION = "eu"
REGIONS = {
    "eu": ("https://app.api.fr.furbulouspet.com:1443", "wss://ovqwe3lj6k.execute-api.eu-central-1.amazonaws.com/production_eu/"),
    "us": ("https://app.api.us.furbulouspet.com:1443", "wss://8foshorfod.execute-api.us-east-1.amazonaws.com/production_us/"),
    "ap": ("https://app.api.ap.furbulouspet.com:1443", "wss://0c59onhjo9.execute-api.ap-southeast-1.amazonaws.com/production_ap/"),
    "cn": ("https://app.api.cn.furbulouspet.cn:1443", "wss://2hu93rmr11.execute-api.cn-northwest-1.amazonaws.com.cn/production_cn/"),
}

# The account allows a single session: when the phone app logs in, our token dies (code 10403).
# Wait this long before logging back in, so the phone isn't kicked right away.
KICK_COOLDOWN = 300
TOKEN_INVALID_CODE = 10403

API_AUTH_ENDPOINT = "/app/v1/auth/login"
API_DEVICE_LIST_ENDPOINT = "/app/v1/device/list"
API_DEVICE_PROPERTIES_ENDPOINT = "/app/v1/device/properties/get"

# API Headers
API_APPID = "a0baae0630f444b0811ea3c2eb212179"
API_VERSION = "1.0.0"
API_PLATFORM = "ios"
API_USER_AGENT = "Furbulous/2.0.1 (com.furbulous.pet; build:202507031750; iOS 26.0.1) Alamofire/4.9.1"

# Configuration
CONF_ACCOUNT_TYPE = "account_type"
CONF_TOKEN = "token"

# Default values
DEFAULT_ACCOUNT_TYPE = 1

# Device Types
PRODUCT_FURBULOUS_BOX = 1

# Work Status
WORK_STATUS = {
    0: "Idle",
    1: "Cleaning",  # observed 2026-11-24: manual clean cycle
    2: "Cleaning",
    3: "Paused",
    4: "Error",
    5: "Cat nearby",  # observed 2026-11-24: someone in front of the box (comes with errorReportEvent 4096)
    6: "Cat inside",  # observed 2026-11-24: weight sensor occupied
}

# workstatus values meaning "cat inside the box" (5 = only in front of it, 1 = cleaning)
CAT_PRESENT_STATUSES = {6}
CAT_NEARBY_STATUSES = {5}

# Home Assistant bus events (for automations)
EVENT_FURBULOUS = "furbulous_event"  # data.type: cat_nearby | cat_entered | cat_left | cleaning_done
EVENT_NOTIFICATION = "furbulous_notification"  # same alerts as the app's notice tab

# Litter Type
LITTER_TYPE = {
    0: "Bentonite",
    1: "Tofu",
    2: "Mixed",
}

# Error Codes (errorReportEvent values)
# Based on analysis of app code and common IoT error patterns
ERROR_CODES = {
    0: "No error",
    1: "Sensor error - Weight sensor",
    2: "Sensor error - IR sensor", 
    4: "Motor error - Rotation blocked",
    8: "Motor error - Overload",
    16: "Litter full - Need to empty",
    32: "Normal operation",  # Default value when no error
    64: "Drawer not in place",
    128: "Cover open",
    256: "Temperature error",
    512: "Communication error",
    4096: "Cat nearby",  # not an error: presence sensor at the entrance (observed 2026-11-24)
}

# Error severity levels
ERROR_SEVERITY = {
    0: "info",
    1: "warning",
    2: "warning",
    4: "error",
    8: "error",
    16: "warning",
    32: "info",
    64: "warning",
    128: "warning",
    256: "error",
    512: "error",
    4096: "info",
}

# Unit of measurement
UNIT_GRAMS = "g"
UNIT_SECONDS = "s"
UNIT_TIMES = "fois"

"""Constants for the Furbulous Cat integration."""

DOMAIN = "furbulous"

# API Constants
API_BASE_URL = "https://app.api.fr.furbulouspet.com:1443"
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
    1: "Working",
    2: "Cleaning",
    3: "Paused",
    4: "Error",
}

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
}

# Unit of measurement
UNIT_GRAMS = "g"
UNIT_SECONDS = "s"
UNIT_TIMES = "fois"

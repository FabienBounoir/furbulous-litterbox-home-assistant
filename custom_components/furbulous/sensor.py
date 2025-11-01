"""Platform for sensor integration."""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FurbulousCatDataUpdateCoordinator
from .const import (
    DOMAIN,
    WORK_STATUS,
    LITTER_TYPE,
    ERROR_CODES,
    UNIT_GRAMS,
    UNIT_SECONDS,
    UNIT_TIMES,
)
from .device import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Furbulous Cat sensors."""
    coordinators = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = coordinators["coordinator"]

    entities = []
    
    # Add a sensor for each device
    devices = coordinator.data.get("devices", [])
    for device in devices:
        device_id = device.get("id")
        iotid = device.get("iotid")
        
        # Basic sensors
        entities.extend([
            FurbulousCatDeviceSensor(coordinator, device_id, "status"),
            FurbulousCatDeviceSensor(coordinator, device_id, "online"),
            FurbulousCatDeviceSensor(coordinator, device_id, "last_active"),
        ])
        
        # Property-based sensors
        if iotid:
            entities.extend([
                # Weight and usage
                FurbulousCatPropertySensor(coordinator, device_id, "catWeight", "Poids du chat"),
                FurbulousCatPropertySensor(coordinator, device_id, "excreteTimesEveryday", "Utilisations quotidiennes"),
                FurbulousCatPropertySensor(coordinator, device_id, "excreteTimerEveryday", "Durée quotidienne"),
                
                # Status sensors
                FurbulousCatPropertySensor(coordinator, device_id, "workstatus", "État de fonctionnement"),
                FurbulousCatPropertySensor(coordinator, device_id, "errorReportEvent", "Erreur"),
                FurbulousCatPropertySensor(coordinator, device_id, "completionStatus", "Statut de complétude"),
                
                # Settings sensors
                FurbulousCatPropertySensor(coordinator, device_id, "catLitterType", "Type de litière"),
                FurbulousCatPropertySensor(coordinator, device_id, "FullAutoModeSwitch", "Mode auto complet"),
                FurbulousCatPropertySensor(coordinator, device_id, "catCleanOnOff", "Nettoyage auto"),
                FurbulousCatPropertySensor(coordinator, device_id, "childLockOnOff", "Verrouillage enfant"),
                FurbulousCatPropertySensor(coordinator, device_id, "masterSleepOnOff", "Mode sommeil"),
                FurbulousCatPropertySensor(coordinator, device_id, "DisplaySwitch", "Affichage"),
                FurbulousCatPropertySensor(coordinator, device_id, "handMode", "Mode manuel"),
                
                # Version sensors
                FurbulousCatPropertySensor(coordinator, device_id, "mcuversion", "Version MCU"),
                FurbulousCatPropertySensor(coordinator, device_id, "wifivertion", "Version WiFi"),
                FurbulousCatPropertySensor(coordinator, device_id, "trdversion", "Version TRD"),
            ])
    
    # Add pet sensors
    pets = coordinator.data.get("pets", [])
    for pet in pets:
        pet_id = pet.get("pet_id")
        if pet_id:
            entities.append(FurbulousCatPetSensor(coordinator, pet_id))
    
    # Add general status sensor
    entities.append(FurbulousCatStatusSensor(coordinator))
    
    async_add_entities(entities)


class FurbulousCatStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Furbulous Cat status sensor."""

    def __init__(self, coordinator: FurbulousCatDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Furbulous Cat Status"
        self._attr_unique_id = f"{coordinator.api.identity_id}_status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.data.get("authenticated"):
            device_count = len(self.coordinator.data.get("devices", []))
            return f"{device_count} device(s)"
        return "Disconnected"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "identity_id": self.coordinator.data.get("identity_id"),
            "device_count": len(self.coordinator.data.get("devices", [])),
        }


class FurbulousCatDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Furbulous Cat device sensor."""

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._sensor_type = sensor_type
        self._attr_unique_id = f"furbulous_{device_id}_{sensor_type}"
        
        # Set device info
        device = self.device_data
        if device:
            self._attr_device_info = get_device_info(device)

    @property
    def device_data(self) -> dict | None:
        """Get the device data from coordinator."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("id") == self._device_id:
                return device
        return None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        device = self.device_data
        if device:
            device_name = device.get("name", f"Device {self._device_id}")
            sensor_names = {
                "status": "État",
                "online": "Connexion",
                "last_active": "Dernière activité",
            }
            return f"{device_name} - {sensor_names.get(self._sensor_type, self._sensor_type)}"
        return f"Furbulous Device {self._device_id}"

    @property
    def native_value(self) -> str | datetime | None:
        """Return the state of the sensor."""
        device = self.device_data
        if not device:
            return None

        if self._sensor_type == "status":
            return "Active" if device.get("device_online") == 1 else "Inactive"
        elif self._sensor_type == "online":
            return "En ligne" if device.get("device_online") == 1 else "Hors ligne"
        elif self._sensor_type == "last_active":
            timestamp = device.get("active_time")
            if timestamp:
                # Return datetime object with UTC timezone for TIMESTAMP device class
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return None
        
        return None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class."""
        if self._sensor_type == "last_active":
            return SensorDeviceClass.TIMESTAMP
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        device = self.device_data
        if not device:
            return {}

        attrs = {
            "device_id": device.get("id"),
            "device_name": device.get("device_name"),
            "iot_id": device.get("iotid"),
            "product_name": device.get("product_name"),
            "product_id": device.get("product_id"),
            "platform": "AWS" if device.get("platform") == 2 else "Other",
        }

        if self._sensor_type == "status":
            attrs.update({
                "is_shared": device.get("is_share") == 1,
                "is_disturb": device.get("is_disturb") == 1,
                "icon_url": device.get("icon"),
            })

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.device_data is not None


class FurbulousCatPropertySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Furbulous Cat property sensor."""

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
        property_key: str,
        friendly_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._property_key = property_key
        self._friendly_name = friendly_name
        self._attr_unique_id = f"furbulous_{device_id}_{property_key}"
        
        # Set device info
        device = self.device_data
        if device:
            self._attr_device_info = get_device_info(device)

    @property
    def device_data(self) -> dict | None:
        """Get the device data from coordinator."""
        devices = self.coordinator.data.get("devices", [])
        for device in devices:
            if device.get("id") == self._device_id:
                return device
        return None

    @property
    def property_data(self) -> dict | None:
        """Get the property data."""
        device = self.device_data
        if device:
            properties = device.get("properties", {})
            return properties.get(self._property_key)
        return None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        device = self.device_data
        if device:
            device_name = device.get("name", f"Device {self._device_id}")
            return f"{device_name} - {self._friendly_name}"
        return f"Furbulous Device {self._device_id} - {self._friendly_name}"

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        prop = self.property_data
        if not prop:
            return None

        # Handle both dict {"value": x} and direct value cases
        if isinstance(prop, dict):
            value = prop.get("value")
        else:
            value = prop
        
        # Handle specific properties with transformations
        if self._property_key == "catWeight":
            # Weight in grams
            return int(value) if value is not None else None
        
        elif self._property_key == "workstatus":
            # Work status mapping
            return WORK_STATUS.get(value, f"Inconnu ({value})")
        
        elif self._property_key == "catLitterType":
            # Litter type mapping
            return LITTER_TYPE.get(value, f"Inconnu ({value})")
        
        elif self._property_key == "errorReportEvent":
            # Error code mapping
            return ERROR_CODES.get(value, f"Erreur {value}")
        
        elif self._property_key in ["FullAutoModeSwitch", "catCleanOnOff", "childLockOnOff", 
                                     "masterSleepOnOff", "DisplaySwitch", "handMode", 
                                     "completionStatus"]:
            # Boolean switches
            return "Activé" if value == 1 else "Désactivé"
        
        elif self._property_key == "mcuversion":
            # MCU version (might be hex encoded)
            return str(value)
        
        elif self._property_key == "wifivertion":
            # WiFi version
            return str(value)
        
        elif self._property_key in ["excreteTimesEveryday", "excreteTimerEveryday"]:
            # Usage statistics
            return int(value) if value is not None else None
        
        return value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        if self._property_key == "catWeight":
            return UNIT_GRAMS
        elif self._property_key == "excreteTimerEveryday":
            return UNIT_SECONDS
        elif self._property_key == "excreteTimesEveryday":
            return UNIT_TIMES
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        icons = {
            "catWeight": "mdi:weight",
            "excreteTimesEveryday": "mdi:counter",
            "excreteTimerEveryday": "mdi:timer-outline",
            "workstatus": "mdi:state-machine",
            "errorReportEvent": "mdi:alert-circle",
            "completionStatus": "mdi:check-circle",
            "catLitterType": "mdi:grid",
            "FullAutoModeSwitch": "mdi:robot",
            "catCleanOnOff": "mdi:broom",
            "childLockOnOff": "mdi:lock",
            "masterSleepOnOff": "mdi:sleep",
            "DisplaySwitch": "mdi:monitor",
            "handMode": "mdi:hand-back-right",
            "mcuversion": "mdi:chip",
            "wifivertion": "mdi:wifi",
            "trdversion": "mdi:information",
        }
        return icons.get(self._property_key, "mdi:information-outline")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        prop = self.property_data
        if not prop:
            return {}

        # Handle both dict {"value": x} and direct value cases
        if isinstance(prop, dict):
            value = prop.get("value")
            time_ms = prop.get("time")
        else:
            value = prop
            time_ms = None

        attrs = {
            "property_key": self._property_key,
            "raw_value": value,
        }
        
        # Add timestamp if available
        if time_ms:
            attrs["last_updated"] = datetime.fromtimestamp(time_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
        
        # Add error details for errorReportEvent
        if self._property_key == "errorReportEvent":
            error_code = value
            attrs["error_code"] = error_code
            attrs["error_message"] = ERROR_CODES.get(error_code, f"Unknown error {error_code}")
            attrs["error_severity"] = self._get_error_severity(error_code)
        
        return attrs
    
    def _get_error_severity(self, error_code: int) -> str:
        """Get error severity level."""
        from .const import ERROR_SEVERITY
        return ERROR_SEVERITY.get(error_code, "unknown")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.property_data is not None


class FurbulousCatPetSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Furbulous Cat Pet sensor."""

    def __init__(
        self, coordinator: FurbulousCatDataUpdateCoordinator, pet_id: int
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._pet_id = pet_id
        
        # Get pet data
        pet_data = self._get_pet_data()
        pet_name = pet_data.get("nickname", f"Pet {pet_id}")
        
        self._attr_unique_id = f"furbulous_pet_{pet_id}"
        self._attr_name = f"Furbulous Cat - {pet_name}"
        self._attr_icon = "mdi:cat"

    def _get_pet_data(self) -> dict:
        """Get pet data from coordinator."""
        pets = self.coordinator.data.get("pets", [])
        for pet in pets:
            if pet.get("pet_id") == self._pet_id:
                return pet
        return {}

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        pet_data = self._get_pet_data()
        
        # Return pet name as state
        return pet_data.get("nickname", "Unknown")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        pet_data = self._get_pet_data()
        
        if not pet_data:
            return {}
        
        attrs = {
            "pet_id": self._pet_id,
            "name": pet_data.get("nickname"),
            "gender": self._get_gender_label(pet_data.get("gender")),
            "birthday_timestamp": pet_data.get("date"),
            "age": pet_data.get("age"),
            "breed": pet_data.get("variety"),
            "weight": pet_data.get("weight"),
            "avatar": pet_data.get("avatar"),
            "food_brand": pet_data.get("food_brand"),
            "sterilization": "Yes" if pet_data.get("sterilization") == 1 else "No",
            "pet_type": self._get_pet_type_label(pet_data.get("pet_type")),
        }
        
        # Calculate age if birthday timestamp is available
        if pet_data.get("date"):
            try:
                from datetime import datetime
                birthday = datetime.fromtimestamp(pet_data.get("date"))
                age_days = (datetime.now() - birthday).days
                attrs["birthday"] = birthday.strftime("%Y-%m-%d")
                attrs["age_days"] = age_days
            except:
                pass
        
        return attrs
    
    def _get_gender_label(self, gender: int) -> str:
        """Convert gender code to label."""
        gender_map = {
            1: "Male",
            2: "Female",
            0: "Unknown"
        }
        return gender_map.get(gender, "Unknown")
    
    def _get_pet_type_label(self, pet_type: int) -> str:
        """Convert pet type code to label."""
        type_map = {
            1: "Cat",
            2: "Dog",
            0: "Other"
        }
        return type_map.get(pet_type, "Unknown")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return bool(self._get_pet_data())

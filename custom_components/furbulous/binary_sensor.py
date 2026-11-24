"""Binary sensor platform for Furbulous Cat integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FurbulousCatDataUpdateCoordinator
from .const import CAT_NEARBY_STATUSES, CAT_PRESENT_STATUSES, DOMAIN, WORK_STATUS
from .device import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Furbulous Cat binary sensors."""
    coordinators = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = coordinators["coordinator"]

    entities = []
    
    # Add binary sensors for each device
    devices = coordinator.data.get("devices", [])
    for device in devices:
        device_id = device.get("id")
        iotid = device.get("iotid")
        
        if iotid:
            entities.extend([
                # 1. Device online status
                FurbulousCatOnlineBinarySensor(coordinator, device_id),
                
                # 2. Cat in box sensor (real-time via WebSocket)
                FurbulousCatInBoxSensor(coordinator, device_id),
                FurbulousCatNearbySensor(coordinator, device_id),
                
                # 3. Waste bin full sensor
                FurbulousCatWasteBinFullSensor(coordinator, device_id),
                
                # 4. Child lock (seul capteur binaire de sécurité nécessaire)
                FurbulousCatPropertyBinarySensor(
                    coordinator, device_id, "childLockOnOff", "child_lock", "lock"
                ),
                
                # 5. Sleep mode (mode Ne Pas Déranger)
                FurbulousCatPropertyBinarySensor(
                    coordinator, device_id, "masterSleepOnOff", "sleep_mode", "running"
                ),
            ])
    
    async_add_entities(entities)


class FurbulousCatOnlineBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for device online status."""

    _attr_has_entity_name = True
    _attr_translation_key = "connectivity"

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"furbulous_{device_id}_connectivity"
        
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
    def is_on(self) -> bool:
        """Return true if the device is online."""
        device = self.device_data
        if device:
            return device.get("device_online") == 1
        return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.device_data is not None


class FurbulousCatInBoxSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for cat presence in litter box (real-time via WebSocket)."""

    _attr_has_entity_name = True
    _attr_translation_key = "cat_in_box"

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _statuses = CAT_PRESENT_STATUSES
    _unique_suffix = "cat_in_box"

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"furbulous_{device_id}_{self._unique_suffix}"
        
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
    def is_on(self) -> bool:
        """Return true if cat is in the litter box."""
        device = self.device_data
        if device:
            properties = device.get("properties", {})
            workstatus_prop = properties.get("workstatus")
            
            if workstatus_prop is not None:
                # Handle both dict {"value": x} and direct value cases
                if isinstance(workstatus_prop, dict):
                    workstatus = workstatus_prop.get("value", 0)
                else:
                    workstatus = workstatus_prop
                
                return workstatus in self._statuses
        
        return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        device = self.device_data
        if not device:
            return {}
        
        properties = device.get("properties", {})
        workstatus_prop = properties.get("workstatus")
        
        attrs = {}
        
        if workstatus_prop is not None:
            if isinstance(workstatus_prop, dict):
                workstatus = workstatus_prop.get("value", 0)
                attrs["last_update"] = workstatus_prop.get("time")
            else:
                workstatus = workstatus_prop
            
            attrs["work_status"] = WORK_STATUS.get(workstatus, f"Unknown ({workstatus})")
            attrs["work_status_code"] = workstatus
        
        # Ajouter le poids du chat si disponible
        cat_weight_prop = properties.get("catWeight")
        if cat_weight_prop:
            if isinstance(cat_weight_prop, dict):
                attrs["cat_weight_grams"] = cat_weight_prop.get("value")
            else:
                attrs["cat_weight_grams"] = cat_weight_prop
        
        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.device_data is not None


class FurbulousCatNearbySensor(FurbulousCatInBoxSensor):
    """Cat in front of the box (entrance presence sensor, workstatus 5), not inside it."""

    _attr_translation_key = "cat_nearby"
    _attr_device_class = BinarySensorDeviceClass.MOTION
    _statuses = CAT_NEARBY_STATUSES
    _unique_suffix = "cat_nearby"


class FurbulousCatWasteBinFullSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for waste bin full status."""

    _attr_has_entity_name = True
    _attr_translation_key = "waste_bin_full"

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_waste_bin_full"
        from .device import get_device_info
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
    def is_on(self) -> bool:
        """Return true if waste bin is full."""
        device = self.device_data
        if device:
            properties = device.get("properties", {})
            
            # Méthode 1: Vérifier le code d'erreur 16
            error_prop = properties.get("errorReportEvent")
            if error_prop is not None:
                if isinstance(error_prop, dict):
                    error_code = error_prop.get("value", 0)
                else:
                    error_code = error_prop
                
                if error_code == 16:  # Litter full code
                    return True
            
            # Méthode 2: Logique basée sur completionStatus
            # completionStatus == 1 pourrait indiquer "terminé/plein"
            completion_prop = properties.get("completionStatus")
            if completion_prop is not None:
                if isinstance(completion_prop, dict):
                    completion = completion_prop.get("value", 0)
                else:
                    completion = completion_prop
                
                # Si completionStatus == 0, cela pourrait indiquer "plein"
                # (à ajuster selon le comportement réel)
                # Pour l'instant, on ne l'utilise que si errorCode == 16
                pass
            
            # Méthode 3: Vérifier handMode == 2 (dump mode actif)
            # Si le mode "dump" est actif, c'est peut-être parce que c'est plein
            hand_mode_prop = properties.get("handMode")
            if hand_mode_prop is not None:
                if isinstance(hand_mode_prop, dict):
                    hand_mode = hand_mode_prop.get("value", 0)
                else:
                    hand_mode = hand_mode_prop
                
                # handMode == 2 pourrait indiquer "nécessite vidage"
                # (à ajuster selon comportement)
                pass
        
        return False

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:delete-alert" if self.is_on else "mdi:delete-empty"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        device = self.device_data
        if device:
            properties = device.get("properties", {})
            
            # Extraire les propriétés utiles
            attrs = {}
            
            # Error code
            error_prop = properties.get("errorReportEvent")
            if error_prop is not None:
                if isinstance(error_prop, dict):
                    error_code = error_prop.get("value", 0)
                else:
                    error_code = error_prop
                attrs["error_code"] = error_code
            
            # Completion status
            completion_prop = properties.get("completionStatus")
            if completion_prop is not None:
                if isinstance(completion_prop, dict):
                    completion = completion_prop.get("value", 0)
                else:
                    completion = completion_prop
                attrs["completion_status"] = completion
            
            # Hand mode
            hand_mode_prop = properties.get("handMode")
            if hand_mode_prop is not None:
                if isinstance(hand_mode_prop, dict):
                    hand_mode = hand_mode_prop.get("value", 0)
                else:
                    hand_mode = hand_mode_prop
                attrs["hand_mode"] = hand_mode
            
            # Usage today
            usage_prop = properties.get("excreteTimesEveryday")
            if usage_prop:
                if isinstance(usage_prop, dict):
                    usage = usage_prop.get("value", 0)
                else:
                    usage = usage_prop
                attrs["usage_today"] = usage
            
            return attrs
        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.device_data is not None


class FurbulousCatPropertyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor based on device properties."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
        property_key: str,
        friendly_name: str,
        device_class: str | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_translation_key = friendly_name
        self._device_id = device_id
        self._property_key = property_key
        self._friendly_name = friendly_name
        self._attr_unique_id = f"furbulous_{device_id}_{property_key}_binary"
        
        if device_class:
            self._attr_device_class = device_class
        
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
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        prop = self.property_data
        if prop is not None:
            # Handle both dict {"value": x} and direct value cases
            if isinstance(prop, dict):
                value = prop.get("value")
            else:
                value = prop
            return value == 1
        return False

    @property
    def icon(self) -> str:
        """Return the icon."""
        icons = {
            "FullAutoModeSwitch": "mdi:robot",
            "catCleanOnOff": "mdi:broom",
            "childLockOnOff": "mdi:lock" if self.is_on else "mdi:lock-open",
            "masterSleepOnOff": "mdi:sleep",
            "DisplaySwitch": "mdi:monitor" if self.is_on else "mdi:monitor-off",
            "handMode": "mdi:hand-back-right",
        }
        return icons.get(self._property_key, "mdi:toggle-switch")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.property_data is not None


class FurbulousCatErrorBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for error status."""

    _attr_has_entity_name = True
    _attr_translation_key = "error"

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: FurbulousCatDataUpdateCoordinator,
        device_id: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"furbulous_{device_id}_error"
        
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
    def is_on(self) -> bool:
        """Return true if there is an error."""
        device = self.device_data
        if device:
            properties = device.get("properties", {})
            error_prop = properties.get("errorReportEvent")
            if error_prop is not None:
                # Handle both dict {"value": x} and direct value cases
                if isinstance(error_prop, dict):
                    error_code = error_prop.get("value", 0)
                else:
                    error_code = error_prop
                return error_code != 0
        return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        device = self.device_data
        if device:
            properties = device.get("properties", {})
            error_prop = properties.get("errorReportEvent")
            if error_prop is not None:
                # Handle both dict {"value": x} and direct value cases
                if isinstance(error_prop, dict):
                    error_code = error_prop.get("value", 0)
                else:
                    error_code = error_prop
                return {
                    "error_code": error_code,
                }
        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.device_data is not None

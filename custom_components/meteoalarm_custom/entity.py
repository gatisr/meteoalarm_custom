"""Base entity for the MeteoAlarm integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import MeteoAlarmAlert
from .const import ATTRIBUTION, CONFIGURATION_URL, COUNTRIES, DOMAIN, MANUFACTURER
from .coordinator import MeteoAlarmCoordinator


class MeteoAlarmEntity(CoordinatorEntity[MeteoAlarmCoordinator]):
    """Common base for all MeteoAlarm entities of one region."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: MeteoAlarmCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"MeteoAlarm {coordinator.province}",
            manufacturer=MANUFACTURER,
            model=COUNTRIES.get(coordinator.country, coordinator.country),
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=CONFIGURATION_URL,
        )

    @property
    def alerts(self) -> list[MeteoAlarmAlert]:
        """Return the currently active alerts."""
        return self.coordinator.data or []

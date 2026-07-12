"""Binary sensor platform for the MeteoAlarm integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MeteoAlarmConfigEntry, MeteoAlarmCoordinator
from .entity import MeteoAlarmEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MeteoAlarm binary sensor."""
    async_add_entities([MeteoAlarmActiveSensor(entry.runtime_data)])


class MeteoAlarmActiveSensor(MeteoAlarmEntity, BinarySensorEntity):
    """On when at least one alert is active for the region."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(self, coordinator: MeteoAlarmCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, "warning")

    @property
    def is_on(self) -> bool:
        """Return True when any alert is active."""
        return bool(self.alerts)

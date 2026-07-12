"""Sensor platform for the MeteoAlarm integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MeteoAlarmAlert, severity_rank
from .const import (
    ATTR_ALERTS,
    ATTR_AREA,
    ATTR_AWARENESS_LEVEL,
    ATTR_AWARENESS_TYPE,
    ATTR_CATEGORY,
    ATTR_CERTAINTY,
    ATTR_DESCRIPTION,
    ATTR_EVENT,
    ATTR_EXPIRES,
    ATTR_HEADLINE,
    ATTR_INSTRUCTION,
    ATTR_ONSET,
    ATTR_SENDER_NAME,
    ATTR_SEVERITY,
    ATTR_URGENCY,
    SEVERITY_NONE,
    SEVERITY_ORDER,
)
from .coordinator import MeteoAlarmConfigEntry, MeteoAlarmCoordinator
from .entity import MeteoAlarmEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MeteoAlarm sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            MeteoAlarmAlertSensor(coordinator),
            MeteoAlarmCountSensor(coordinator),
            MeteoAlarmOnsetSensor(coordinator),
            MeteoAlarmExpiresSensor(coordinator),
        ]
    )


def _most_severe(alerts: list[MeteoAlarmAlert]) -> MeteoAlarmAlert | None:
    if not alerts:
        return None
    return max(alerts, key=lambda alert: severity_rank(alert.severity))


class MeteoAlarmAlertSensor(MeteoAlarmEntity, SensorEntity):
    """Highest severity of the currently active alerts."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = SEVERITY_ORDER

    def __init__(self, coordinator: MeteoAlarmCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "alert")

    @property
    def native_value(self) -> str:
        """Return the highest severity among active alerts."""
        alert = _most_severe(self.alerts)
        return alert.severity if alert else SEVERITY_NONE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the full alert list plus flat details of the worst alert."""
        attributes: dict[str, Any] = {
            ATTR_ALERTS: [alert.as_dict() for alert in self.alerts],
            ATTR_AREA: self.coordinator.api.resolved_area,
        }
        if alert := _most_severe(self.alerts):
            attributes.update(
                {
                    ATTR_EVENT: alert.event,
                    ATTR_HEADLINE: alert.headline,
                    ATTR_SEVERITY: alert.severity,
                    ATTR_AWARENESS_LEVEL: alert.awareness_level,
                    ATTR_AWARENESS_TYPE: alert.awareness_type,
                    ATTR_CATEGORY: alert.category,
                    ATTR_URGENCY: alert.urgency,
                    ATTR_CERTAINTY: alert.certainty,
                    ATTR_ONSET: alert.onset.isoformat() if alert.onset else None,
                    ATTR_EXPIRES: alert.expires.isoformat() if alert.expires else None,
                    ATTR_SENDER_NAME: alert.sender_name,
                    ATTR_DESCRIPTION: alert.description,
                    ATTR_INSTRUCTION: alert.instruction,
                }
            )
        return attributes


class MeteoAlarmCountSensor(MeteoAlarmEntity, SensorEntity):
    """Number of currently active alerts."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MeteoAlarmCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "active_alerts")

    @property
    def native_value(self) -> int:
        """Return the number of active alerts."""
        return len(self.alerts)


class MeteoAlarmOnsetSensor(MeteoAlarmEntity, SensorEntity):
    """Earliest start time of the currently active alerts."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: MeteoAlarmCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "onset")

    @property
    def native_value(self) -> datetime | None:
        """Return the earliest onset."""
        onsets = [alert.onset for alert in self.alerts if alert.onset]
        return min(onsets) if onsets else None


class MeteoAlarmExpiresSensor(MeteoAlarmEntity, SensorEntity):
    """Latest end time of the currently active alerts."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: MeteoAlarmCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "expires")

    @property
    def native_value(self) -> datetime | None:
        """Return the latest expiry."""
        expires = [alert.expires for alert in self.alerts if alert.expires]
        return max(expires) if expires else None

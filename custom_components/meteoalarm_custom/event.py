"""Event platform for the MeteoAlarm integration."""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MeteoAlarmAlert
from .const import EVENT_TYPE_ALERT
from .coordinator import MeteoAlarmConfigEntry, MeteoAlarmCoordinator
from .entity import MeteoAlarmEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MeteoAlarm event entity."""
    async_add_entities([MeteoAlarmAlertEvent(entry.runtime_data)])


def _alert_key(alert: MeteoAlarmAlert) -> str:
    """Return a stable key identifying an alert across updates.

    Falls back to event/onset/area for senders that omit the CAP identifier,
    so those alerts still fire an event instead of being ignored.
    """
    if alert.identifier:
        return alert.identifier
    onset = alert.onset.isoformat() if alert.onset else ""
    return f"{alert.event}|{onset}|{alert.area}"


class MeteoAlarmAlertEvent(MeteoAlarmEntity, EventEntity):
    """Fires whenever a new alert appears for the region."""

    _attr_event_types = [EVENT_TYPE_ALERT]
    _unrecorded_attributes = frozenset({"description", "instruction"})

    def __init__(self, coordinator: MeteoAlarmCoordinator) -> None:
        """Initialize the event entity."""
        super().__init__(coordinator, "alert_event")
        self._seen: set[str] = {_alert_key(alert) for alert in coordinator.data or []}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fire an event for every alert not seen before."""
        current: set[str] = set()
        for alert in self.alerts:
            key = _alert_key(alert)
            current.add(key)
            if key not in self._seen:
                self._trigger_event(EVENT_TYPE_ALERT, alert.as_dict())
        self._seen = current
        super()._handle_coordinator_update()

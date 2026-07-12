"""Diagnostics support for the MeteoAlarm integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import MeteoAlarmConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MeteoAlarmConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": {
            "version": entry.version,
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
            "unique_id": entry.unique_id,
        },
        "resolved_area": coordinator.api.resolved_area,
        "last_update_success": coordinator.last_update_success,
        "alerts": [alert.as_dict() for alert in coordinator.data or []],
    }

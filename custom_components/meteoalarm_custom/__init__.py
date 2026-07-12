"""The MeteoAlarm Custom integration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration
from homeassistant.util import slugify

from .const import (
    CONF_COUNTRY,
    CONF_LANGUAGE,
    CONF_PROVINCE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_LANGUAGE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import MeteoAlarmConfigEntry, MeteoAlarmCoordinator
from .frontend import async_register_frontend, async_remove_frontend

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: MeteoAlarmConfigEntry) -> bool:
    """Set up MeteoAlarm from a config entry."""
    coordinator = MeteoAlarmCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    integration = await async_get_integration(hass, DOMAIN)
    await async_register_frontend(hass, str(integration.version))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MeteoAlarmConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: MeteoAlarmConfigEntry) -> None:
    """Clean up after the last config entry is removed."""
    if not hass.config_entries.async_entries(DOMAIN):
        await async_remove_frontend(hass)


async def async_migrate_entry(hass: HomeAssistant, entry: MeteoAlarmConfigEntry) -> bool:
    """Migrate old config entries to the current version.

    Version history:
    1: original schema, everything in ``data``.
    2: same schema; the version was bumped at runtime by an old release
       without raising ``ConfigFlow.VERSION`` (which broke loading entirely).
    3: ``language``/``update_interval`` moved to options, per-entry
       ``unique_id`` added, entity unique_ids based on ``entry_id``.
    """
    if entry.version > 3:
        # Downgrade from a future version is not supported.
        return False

    if entry.version < 3:
        data = dict(entry.data)
        options = dict(entry.options)

        country = str(data.get(CONF_COUNTRY, "")).strip().lower()
        province = str(data.get(CONF_PROVINCE, "")).strip()
        language = data.pop(CONF_LANGUAGE, None) or DEFAULT_LANGUAGE
        update_interval = data.pop(CONF_UPDATE_INTERVAL, None) or DEFAULT_UPDATE_INTERVAL

        data[CONF_COUNTRY] = country
        data[CONF_PROVINCE] = province
        options.setdefault(CONF_LANGUAGE, language)
        options.setdefault(CONF_UPDATE_INTERVAL, update_interval)

        # Versions 1/2 created exactly one sensor per entry; rename its
        # unique_id so the entity (with history and customizations) survives.
        new_unique_id = f"{entry.entry_id}_alert"
        ent_reg = er.async_get(hass)
        for entity_entry in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
            if entity_entry.unique_id == new_unique_id:
                continue
            try:
                ent_reg.async_update_entity(
                    entity_entry.entity_id, new_unique_id=new_unique_id
                )
            except ValueError:
                _LOGGER.warning(
                    "Could not migrate unique_id of %s", entity_entry.entity_id
                )

        hass.config_entries.async_update_entry(
            entry,
            data=data,
            options=options,
            unique_id=f"{country}_{slugify(province)}",
            version=3,
        )
        _LOGGER.info(
            "Migrated config entry %s (%s) to version 3", entry.title, entry.entry_id
        )

    return True

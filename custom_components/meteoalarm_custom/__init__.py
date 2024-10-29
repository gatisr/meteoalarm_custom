from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MeteoAlarm from a config entry."""
    # Run migration if needed
    if entry.version < 2:  # Increment this when making breaking changes
        await async_migrate_entry(hass, entry)
        entry.version = 2

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception as exc:
        raise ConfigEntryNotReady from exc

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  """Unload a config entry."""
  unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
  if unload_ok:
      # Clean up any existing entities
      ent_reg = entity_registry.async_get(hass)
      entries = entity_registry.async_entries_for_config_entry(ent_reg, entry.entry_id)
      for entity_entry in entries:
          ent_reg.async_remove(entity_entry.entity_id)
  return unload_ok



async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    ent_reg = entity_registry.async_get(hass)

    # Get all entities for this config entry
    entity_entries = entity_registry.async_entries_for_config_entry(
        ent_reg, config_entry.entry_id
    )

    # Clean up old entities that don't match current unique_id pattern
    for entity_entry in entity_entries:
        expected_unique_id = f"{config_entry.data['country']}_{config_entry.data['province']}_{config_entry.data['language']}"
        if entity_entry.unique_id != expected_unique_id:
            ent_reg.async_remove(entity_entry.entity_id)

    return True


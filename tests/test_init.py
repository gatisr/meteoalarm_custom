"""Tests for setup, unload and config entry migration."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteoalarm_custom.const import DOMAIN


def _v3_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        version=3,
        title="Riga",
        unique_id="latvia_riga",
        data={"country": "latvia", "province": "Riga", "geocode": None},
        options={"language": "en", "update_interval": 30},
    )


async def test_setup_and_unload(hass, mock_feed):
    """A v3 entry sets up all platforms and unloads cleanly."""
    entry = _v3_entry()
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    ent_reg = er.async_get(hass)
    entities = er.async_entries_for_config_entry(ent_reg, entry.entry_id)
    unique_ids = {e.unique_id for e in entities}
    assert unique_ids == {
        f"{entry.entry_id}_alert",
        f"{entry.entry_id}_active_alerts",
        f"{entry.entry_id}_onset",
        f"{entry.entry_id}_expires",
        f"{entry.entry_id}_warning",
        f"{entry.entry_id}_alert_event",
    }

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED

    # Unloading (restart/reload) must NOT wipe the entity registry.
    assert er.async_entries_for_config_entry(ent_reg, entry.entry_id)


async def test_migration_from_v2(hass, mock_feed):
    """Old v2 entries (the broken-version ones) migrate to v3 and load."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        title="Smiltene LV045",
        data={
            "country": "latvia",
            "province": "Smiltene LV045",
            "language": "lv",
            "update_interval": 20,
        },
    )
    entry.add_to_hass(hass)

    # The single legacy sensor created by the old release.
    ent_reg = er.async_get(hass)
    legacy = ent_reg.async_get_or_create(
        "sensor",
        DOMAIN,
        "latvia_Smiltene LV045_lv",
        config_entry=entry,
        suggested_object_id="meteoalarm_latvia_smiltene_lv045_lv",
    )

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.version == 3
    assert entry.data == {"country": "latvia", "province": "Smiltene LV045"}
    assert entry.options == {"language": "lv", "update_interval": 20}
    assert entry.unique_id == "latvia_smiltene_lv045"

    # The legacy entity keeps its entity_id (history preserved) but gets the
    # new unique_id.
    migrated = ent_reg.async_get(legacy.entity_id)
    assert migrated is not None
    assert migrated.unique_id == f"{entry.entry_id}_alert"

    # The free-text region still resolves against the feed.
    state = hass.states.get(legacy.entity_id)
    assert state is not None
    assert state.state == "extreme"
    assert len(state.attributes["alerts"]) == 2


async def test_migration_from_v1(hass, mock_feed):
    """v1 entries migrate straight to v3."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        title="Riga",
        data={"country": "latvia", "province": "Riga", "language": "en"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.version == 3
    assert entry.options["language"] == "en"
    assert entry.options["update_interval"] == 30


async def test_future_version_not_supported(hass, mock_feed):
    """Entries from a newer schema refuse to load instead of corrupting."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=4,
        title="Riga",
        data={"country": "latvia", "province": "Riga"},
    )
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.MIGRATION_ERROR

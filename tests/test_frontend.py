"""Tests for serving the card and registering its Lovelace resource."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteoalarm_custom.const import DOMAIN, FRONTEND_URL_PATH
from custom_components.meteoalarm_custom.frontend import (
    async_register_frontend,
    async_remove_frontend,
)


class FakeResources:
    """Storage-mode Lovelace resource collection."""

    def __init__(self, items=None) -> None:
        self.loaded = True
        self.items = list(items or [])
        self.create_calls = 0

    async def async_load(self) -> None:
        self.loaded = True

    def async_items(self):
        return list(self.items)

    async def async_create_item(self, data) -> None:
        self.create_calls += 1
        self.items.append({"id": f"id{len(self.items)}", "url": data["url"]})

    async def async_update_item(self, item_id, data) -> None:
        for item in self.items:
            if item["id"] == item_id:
                item.update(data)

    async def async_delete_item(self, item_id) -> None:
        self.items = [item for item in self.items if item["id"] != item_id]


def _prepare(hass, resources=None, register=None):
    hass.http = MagicMock()
    hass.http.async_register_static_paths = register or AsyncMock()
    hass.data["lovelace"] = SimpleNamespace(resources=resources)
    return hass.http.async_register_static_paths


async def test_registers_static_path_and_resource(hass):
    """The card is served and added to the Lovelace resources once."""
    resources = FakeResources()
    register = _prepare(hass, resources)

    await async_register_frontend(hass, "1.2.3")

    register.assert_awaited_once()
    config = register.await_args.args[0][0]
    assert config.url_path == FRONTEND_URL_PATH
    assert resources.items[0]["url"] == f"{FRONTEND_URL_PATH}?v=1.2.3"





async def test_concurrent_setups_register_once(hass):
    """Entries set up concurrently must not race on the static route."""
    resources = FakeResources()

    async def slow_register(_configs):
        await asyncio.sleep(0.01)

    register = _prepare(hass, resources, AsyncMock(side_effect=slow_register))

    await asyncio.gather(
        async_register_frontend(hass, "1.0.0"),
        async_register_frontend(hass, "1.0.0"),
        async_register_frontend(hass, "1.0.0"),
    )

    register.assert_awaited_once()
    assert resources.create_calls == 1











async def test_outdated_resource_url_is_updated(hass):
    """A new integration version updates the cache-busting query string."""
    resources = FakeResources([{"id": "a", "url": f"{FRONTEND_URL_PATH}?v=0.9.0"}])
    _prepare(hass, resources)

    await async_register_frontend(hass, "1.0.0")

    assert resources.items == [{"id": "a", "url": f"{FRONTEND_URL_PATH}?v=1.0.0"}]
    assert resources.create_calls == 0











async def test_remove_deletes_resource_and_allows_reregistration(hass):
    """After removal a later setup (no restart) registers the card again."""
    resources = FakeResources()
    _prepare(hass, resources)
    await async_register_frontend(hass, "1.0.0")
    assert len(resources.items) == 1

    await async_remove_frontend(hass)
    assert resources.items == []

    await async_register_frontend(hass, "1.0.0")
    assert len(resources.items) == 1


async def test_resource_removed_only_with_last_entry(hass, mock_feed):
    """Removing one of two entries keeps the card; removing the last one drops it."""
    resources = FakeResources()
    _prepare(hass, resources)
    entries = [
        MockConfigEntry(
            domain=DOMAIN,
            version=3,
            title=name,
            unique_id=f"latvia_{name.lower()}",
            data={"country": "latvia", "province": name, "geocode": None},
            options={"language": "en", "update_interval": 30},
        )
        for name in ("Riga", "Smiltene municipality")
    ]
    for entry in entries:
        entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entries[0].entry_id)
    await hass.async_block_till_done()
    assert all(e.state is ConfigEntryState.LOADED for e in entries)
    assert len(resources.items) == 1

    await hass.config_entries.async_remove(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(resources.items) == 1

    await hass.config_entries.async_remove(entries[1].entry_id)
    await hass.async_block_till_done()
    assert resources.items == []

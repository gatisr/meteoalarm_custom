"""Tests for the shared download cache and remembered regions."""

import pytest

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.meteoalarm_custom.api import (
    FeedCache,
    MeteoAlarmConnectionError,
    MeteoAlarmRegion,
)
from custom_components.meteoalarm_custom.shared import KnownRegions

URL = "https://feeds.test/doc"


async def test_cache_reuses_fresh_documents(hass, aioclient_mock):
    """A second request within the TTL does not hit the network."""
    aioclient_mock.get(URL, text="one")
    cache = FeedCache(ttl=60)
    session = async_get_clientsession(hass)

    assert await cache.fetch(session, URL) == b"one"
    assert await cache.fetch(session, URL) == b"one"
    assert aioclient_mock.call_count == 1


async def test_cache_does_not_keep_locks_of_failed_urls(hass, aioclient_mock):
    """Failing URLs must not leave per-URL state behind."""
    aioclient_mock.get(URL, status=503)
    aioclient_mock.get("https://feeds.test/ok", text="ok")
    cache = FeedCache(ttl=60)
    session = async_get_clientsession(hass)

    with pytest.raises(MeteoAlarmConnectionError):
        await cache.fetch(session, URL)
    await cache.fetch(session, "https://feeds.test/ok")

    assert URL not in cache._locks


async def test_known_regions_persist_and_merge(hass):
    """Regions are remembered per country; a later geocode fills a gap."""
    known = KnownRegions(hass)
    await known.async_add("latvia", [MeteoAlarmRegion("Riga")])
    await known.async_add("latvia", [MeteoAlarmRegion("Riga", "LV039")])

    again = KnownRegions(hass)
    assert await again.async_get("latvia") == [MeteoAlarmRegion("Riga", "LV039")]
    assert await again.async_get("estonia") == []

"""Tests for the MeteoAlarm API client."""

import pytest

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.meteoalarm_custom.api import (
    MeteoAlarmApi,
    MeteoAlarmUnsupportedCountryError,
    async_get_regions,
)

from .conftest import FEED_URL


async def test_exact_area_match(hass, mock_feed):
    """An exact areaDesc match returns only that region's alerts."""
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Riga", "en")
    alerts = await api.get_alerts()

    assert api.resolved_area == "Riga"
    assert len(alerts) == 1
    assert alerts[0].event == "Yellow Fog Warning"
    assert alerts[0].severity == "moderate"
    assert alerts[0].awareness_type == "7; Fog"


async def test_multiple_alerts_sorted_by_severity(hass, mock_feed):
    """All active alerts are returned, most severe first."""
    api = MeteoAlarmApi(
        async_get_clientsession(hass), "latvia", "Smiltene municipality", "en"
    )
    alerts = await api.get_alerts()

    assert len(alerts) == 2
    assert [a.severity for a in alerts] == ["extreme", "moderate"]
    assert alerts[0].event == "Red Rain Warning"


async def test_legacy_freetext_province_match(hass, mock_feed):
    """Free-text values stored by old versions still resolve to a region."""
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Smiltene LV045", "en")
    alerts = await api.get_alerts()

    assert api.resolved_area == "Smiltene municipality"
    assert len(alerts) == 2


async def test_loose_match_prefers_shortest_area(hass, mock_feed):
    """'Riga' style tokens must not also match 'Southern Gulf of Riga'."""
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "riga LV039", "en")
    alerts = await api.get_alerts()

    assert api.resolved_area == "Riga"
    assert len(alerts) == 1


async def test_diacritics_are_ignored(hass, mock_feed):
    """Local spellings like 'Rīga' match the feed's ASCII 'Riga'."""
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Rīga", "en")
    alerts = await api.get_alerts()

    assert api.resolved_area == "Riga"
    assert len(alerts) == 1


async def test_geocode_match(hass, mock_feed):
    """A stored geocode matches the feed entry's EMMA_ID."""
    api = MeteoAlarmApi(
        async_get_clientsession(hass), "latvia", "Whatever", "en", geocode="LV806"
    )
    alerts = await api.get_alerts()

    assert api.resolved_area == "Southern Gulf of Riga"
    assert len(alerts) == 1
    assert alerts[0].severity == "severe"


async def test_language_selection_and_fallback(hass, mock_feed):
    """The CAP info block matching the language is used; unknown -> English."""
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Riga", "lv")
    alerts = await api.get_alerts()
    assert alerts[0].event == "Dzeltenais miglas brīdinājums"

    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Riga", "de")
    alerts = await api.get_alerts()
    assert alerts[0].event == "Yellow Fog Warning"


async def test_get_regions(hass, mock_feed):
    """Regions are unique, sorted and carry geocodes when present."""
    regions = await async_get_regions(async_get_clientsession(hass), "latvia")

    assert [r.name for r in regions] == [
        "Riga",
        "Smiltene municipality",
        "Southern Gulf of Riga",
    ]
    assert regions[2].geocode == "LV806"


async def test_unsupported_country(hass, aioclient_mock):
    """A 404 feed raises the dedicated error."""
    aioclient_mock.get(
        "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-nowhere", status=404
    )
    api = MeteoAlarmApi(async_get_clientsession(hass), "nowhere", "Riga", "en")
    with pytest.raises(MeteoAlarmUnsupportedCountryError):
        await api.get_alerts()


async def test_expired_alerts_are_dropped(hass, aioclient_mock):
    """Alerts past their expiry stay in the feed for a while but are ignored."""
    from .conftest import FIXTURES

    aioclient_mock.get(FEED_URL, text=(FIXTURES / "feed.xml").read_text())
    expired = (FIXTURES / "cap_riga_fog.xml").read_text().replace("2126-", "2020-")
    aioclient_mock.get("https://feeds.test/cap/riga-fog", text=expired)

    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Riga", "en")
    alerts = await api.get_alerts()

    assert api.resolved_area == "Riga"
    assert alerts == []


async def test_no_alerts_for_unknown_region(hass, mock_feed):
    """An unknown region yields no alerts instead of a false match."""
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Atlantis", "en")
    alerts = await api.get_alerts()

    assert alerts == []
    assert api.resolved_area is None

"""Tests for the MeteoAlarm API client."""

import pytest

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.meteoalarm_custom.api import (
    MeteoAlarmApi,
    MeteoAlarmConnectionError,
    MeteoAlarmParseError,
    MeteoAlarmUnsupportedCountryError,
    async_get_regions,
)

from .conftest import FEED_URL, load_fixture

RIGA_FOG_URL = "https://feeds.test/cap/riga-fog"


def _riga_api(hass, language="en"):
    return MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Riga", language)


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


# --- error handling ---------------------------------------------------------





async def test_invalid_feed_xml(hass, aioclient_mock):
    """Broken feed XML raises the dedicated parse error."""
    aioclient_mock.get(FEED_URL, text="<feed><entry></feed>")
    with pytest.raises(MeteoAlarmParseError):
        await _riga_api(hass).get_alerts()


async def test_invalid_cap_xml(hass, mock_feed_only):
    """Broken CAP XML must not be mistaken for 'no alert'."""
    mock_feed_only.get(RIGA_FOG_URL, text="<alert>")
    with pytest.raises(MeteoAlarmParseError):
        await _riga_api(hass).get_alerts()


async def test_cap_failure_does_not_look_like_all_clear(hass, mock_feed_only):
    """A failing CAP request fails the update instead of dropping the alert."""
    mock_feed_only.get(RIGA_FOG_URL, status=503)
    with pytest.raises(MeteoAlarmConnectionError):
        await _riga_api(hass).get_alerts()





# --- CAP content ------------------------------------------------------------








# --- matching ---------------------------------------------------------------





def _feed_with_areas(*areas: str) -> str:
    entries = "".join(
        f"""<entry><cap:areaDesc>{area}</cap:areaDesc><cap:severity>Moderate</cap:severity>
        <link type="application/cap+xml" href="https://feeds.test/cap/riga-fog"/></entry>"""
        for area in areas
    )
    return (
        '<feed xmlns="http://www.w3.org/2005/Atom" '
        f'xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2">{entries}</feed>'
    )


async def test_ambiguous_loose_match_is_not_guessed(hass, aioclient_mock):
    """'Riga' on a calm day must not adopt a marine area's warnings."""
    aioclient_mock.get(
        FEED_URL, text=_feed_with_areas("Gulf of Riga East", "Gulf of Riga West")
    )
    api = _riga_api(hass)

    assert await api.get_alerts() == []
    assert api.resolved_area is None


async def test_loose_match_prefers_area_starting_with_the_name(hass, aioclient_mock):
    """'Smiltene' resolves to 'Smiltene municipality' even if other areas contain it."""
    aioclient_mock.get(
        FEED_URL, text=_feed_with_areas("Smiltene municipality", "North of Smiltene Bay")
    )
    aioclient_mock.get(RIGA_FOG_URL, text=load_fixture("cap_riga_fog.xml"))
    api = MeteoAlarmApi(async_get_clientsession(hass), "latvia", "Smiltene", "en")

    await api.get_alerts()

    assert api.resolved_area == "Smiltene municipality"

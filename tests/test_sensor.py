"""Tests for the MeteoAlarm entities."""

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteoalarm_custom.const import DOMAIN

from .conftest import FEED_URL, load_fixture


async def _setup(hass) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        title="Smiltene municipality",
        unique_id="latvia_smiltene_municipality",
        data={"country": "latvia", "province": "Smiltene municipality", "geocode": None},
        options={"language": "en", "update_interval": 30},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


_KEY_DOMAIN = {
    "alert": "sensor",
    "active_alerts": "sensor",
    "onset": "sensor",
    "expires": "sensor",
    "warning": "binary_sensor",
    "alert_event": "event",
}


def _entity_id(hass, entry, key: str) -> str:
    ent_reg = er.async_get(hass)
    entity_id = ent_reg.async_get_entity_id(
        _KEY_DOMAIN[key], DOMAIN, f"{entry.entry_id}_{key}"
    )
    assert entity_id is not None
    return entity_id


async def test_entity_states(hass, mock_feed):
    """All entities reflect the two active Smiltene alerts."""
    entry = await _setup(hass)

    alert = hass.states.get(_entity_id(hass, entry, "alert"))
    assert alert.state == "extreme"
    assert alert.attributes["event"] == "Red Rain Warning"
    assert len(alert.attributes["alerts"]) == 2
    assert alert.attributes["area"] == "Smiltene municipality"
    assert alert.attributes["attribution"] == "Data provided by MeteoAlarm"

    count = hass.states.get(_entity_id(hass, entry, "active_alerts"))
    assert count.state == "2"

    onset = hass.states.get(_entity_id(hass, entry, "onset"))
    assert onset.state == "2026-07-12T03:00:00+00:00"

    expires = hass.states.get(_entity_id(hass, entry, "expires"))
    assert expires.state == "2026-07-13T03:00:00+00:00"

    warning = hass.states.get(_entity_id(hass, entry, "warning"))
    assert warning.state == "on"


async def test_event_fires_for_new_alert(hass, mock_feed):
    """The event entity fires only when a previously unseen alert appears."""
    entry = await _setup(hass)

    event_entity = _entity_id(hass, entry, "alert_event")
    assert hass.states.get(event_entity).state == "unknown"

    # Same alerts again -> still no event.
    coordinator = entry.runtime_data
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(event_entity).state == "unknown"

    # A new alert identifier appears -> the event fires with its data.
    mock_feed.clear_requests()
    mock_feed.get(FEED_URL, text=load_fixture("feed.xml"))
    mock_feed.get(
        "https://feeds.test/cap/smiltene-storm",
        text=load_fixture("cap_smiltene_storm.xml").replace(
            "LV.SMILTENE.STORM.1", "LV.SMILTENE.STORM.2"
        ),
    )
    mock_feed.get(
        "https://feeds.test/cap/smiltene-rain", text=load_fixture("cap_smiltene_rain.xml")
    )

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get(event_entity)
    assert state.state != "unknown"
    assert state.attributes["event_type"] == "alert"
    assert state.attributes["identifier"] == "LV.SMILTENE.STORM.2"


async def test_no_alerts_state(hass, aioclient_mock):
    """With an empty feed everything reports the calm state."""
    aioclient_mock.get(
        FEED_URL,
        text='<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2"></feed>',
    )
    entry = await _setup(hass)

    assert hass.states.get(_entity_id(hass, entry, "alert")).state == "none"
    assert hass.states.get(_entity_id(hass, entry, "active_alerts")).state == "0"
    assert hass.states.get(_entity_id(hass, entry, "onset")).state == "unknown"
    assert hass.states.get(_entity_id(hass, entry, "warning")).state == "off"

"""Tests for the MeteoAlarm entities."""

from datetime import timedelta

from homeassistant.helpers import entity_registry as er, issue_registry as ir
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

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
    assert expires.state == "2126-07-13T03:00:00+00:00"

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


def _swap_feed(mock_feed, storm_text: str | None = None, empty: bool = False):
    """Replace the mocked feed responses."""
    mock_feed.clear_requests()
    if empty:
        mock_feed.get(
            FEED_URL,
            text='<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" '
            'xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2"></feed>',
        )
        return
    mock_feed.get(FEED_URL, text=load_fixture("feed.xml"))
    mock_feed.get(
        "https://feeds.test/cap/smiltene-storm",
        text=storm_text or load_fixture("cap_smiltene_storm.xml"),
    )
    mock_feed.get(
        "https://feeds.test/cap/smiltene-rain", text=load_fixture("cap_smiltene_rain.xml")
    )


async def test_event_refires_after_alert_disappears_and_returns(hass, mock_feed):
    """An alert that ends and later comes back is announced again."""
    entry = await _setup(hass)
    event_entity = _entity_id(hass, entry, "alert_event")
    coordinator = entry.runtime_data

    _swap_feed(mock_feed, empty=True)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(event_entity).state == "unknown"

    _swap_feed(mock_feed)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(event_entity).state != "unknown"


async def test_event_fires_for_alert_without_identifier(hass, mock_feed):
    """Alerts lacking a CAP identifier still produce an event, only once."""
    entry = await _setup(hass)
    event_entity = _entity_id(hass, entry, "alert_event")
    coordinator = entry.runtime_data

    no_id = load_fixture("cap_smiltene_storm.xml").replace(
        "<identifier>LV.SMILTENE.STORM.1</identifier>", "<identifier></identifier>"
    )
    _swap_feed(mock_feed, storm_text=no_id)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    first = hass.states.get(event_entity)
    assert first.state != "unknown"
    assert first.attributes["identifier"] == ""

    # The same identifier-less alert on the next poll is not announced again.
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(event_entity).state == first.state


async def test_feed_outage_keeps_state_and_does_not_refire(hass, mock_feed):
    """A CAP outage marks entities unavailable; recovery does not re-fire events."""
    entry = await _setup(hass)
    alert_entity = _entity_id(hass, entry, "alert")
    event_entity = _entity_id(hass, entry, "alert_event")
    coordinator = entry.runtime_data

    mock_feed.clear_requests()
    mock_feed.get(FEED_URL, text=load_fixture("feed.xml"))
    mock_feed.get("https://feeds.test/cap/smiltene-storm", status=503)
    mock_feed.get(
        "https://feeds.test/cap/smiltene-rain", text=load_fixture("cap_smiltene_rain.xml")
    )
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Not a false all-clear: the sensor is unavailable, not "none".
    assert hass.states.get(alert_entity).state == "unavailable"

    _swap_feed(mock_feed)
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(alert_entity).state == "extreme"
    assert hass.states.get(event_entity).state == "unknown"


async def test_alert_is_dropped_exactly_when_it_expires(hass, mock_feed, freezer):
    """The expiry timer clears an ended alert without waiting for the next poll."""
    soon = (dt_util.utcnow() + timedelta(minutes=10)).isoformat()
    mock_feed.clear_requests()
    mock_feed.get(FEED_URL, text=load_fixture("feed.xml"))
    mock_feed.get(
        "https://feeds.test/cap/smiltene-storm",
        text=load_fixture("cap_smiltene_storm.xml").replace(
            "2126-07-12T23:00:00+03:00", soon
        ),
    )
    mock_feed.get(
        "https://feeds.test/cap/smiltene-rain", text=load_fixture("cap_smiltene_rain.xml")
    )
    entry = await _setup(hass)
    alert = _entity_id(hass, entry, "active_alerts")
    assert hass.states.get(alert).state == "2"
    calls = mock_feed.call_count

    freezer.tick(timedelta(minutes=11))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert hass.states.get(alert).state == "1"
    assert mock_feed.call_count == calls  # no refetch, the timer did it


async def test_missing_feed_raises_and_clears_repairs_issue(hass, aioclient_mock):
    """A 404 country feed raises a Repairs issue that disappears on recovery."""
    aioclient_mock.get(FEED_URL, status=404)
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        title="Riga",
        unique_id="latvia_riga",
        data={"country": "latvia", "province": "Riga", "geocode": None},
        options={"language": "en", "update_interval": 30},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = ir.async_get(hass)
    issue_id = f"feed_unavailable_{entry.entry_id}"
    assert registry.async_get_issue(DOMAIN, issue_id) is not None

    aioclient_mock.clear_requests()
    aioclient_mock.get(FEED_URL, text=load_fixture("feed.xml"))
    aioclient_mock.get("https://feeds.test/cap/riga-fog", text=load_fixture("cap_riga_fog.xml"))
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert registry.async_get_issue(DOMAIN, issue_id) is None


async def test_expiry_timer_does_not_mask_an_outage(hass, mock_feed, freezer):
    """After a failed poll the expiry timer must not make stale data available."""
    soon = (dt_util.utcnow() + timedelta(minutes=10)).isoformat()
    mock_feed.clear_requests()
    mock_feed.get(FEED_URL, text=load_fixture("feed.xml"))
    for name, url in (
        ("cap_smiltene_storm.xml", "smiltene-storm"),
        ("cap_smiltene_rain.xml", "smiltene-rain"),
    ):
        mock_feed.get(
            f"https://feeds.test/cap/{url}",
            text=load_fixture(name).replace(
                "2126-07-12T23:00:00+03:00", soon
            ),
        )
    entry = await _setup(hass)
    alert = _entity_id(hass, entry, "alert")

    mock_feed.clear_requests()
    mock_feed.get(FEED_URL, status=503)
    await entry.runtime_data.async_refresh()
    assert hass.states.get(alert).state == "unavailable"

    freezer.tick(timedelta(minutes=11))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert hass.states.get(alert).state == "unavailable"


async def test_removing_entry_deletes_repairs_issue(hass, aioclient_mock):
    """The feed issue does not outlive its config entry."""
    aioclient_mock.get(FEED_URL, status=404)
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        title="Riga",
        unique_id="latvia_riga",
        data={"country": "latvia", "province": "Riga", "geocode": None},
        options={"language": "en", "update_interval": 30},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    registry = ir.async_get(hass)
    issue_id = f"feed_unavailable_{entry.entry_id}"
    assert registry.async_get_issue(DOMAIN, issue_id) is not None

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert registry.async_get_issue(DOMAIN, issue_id) is None

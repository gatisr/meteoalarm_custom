"""Shared fixtures for the MeteoAlarm tests."""

from pathlib import Path
from unittest.mock import patch

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

FIXTURES = Path(__file__).parent / "fixtures"
FEED_URL = "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-latvia"

CAP_URLS = {
    "https://feeds.test/cap/riga-fog": "cap_riga_fog.xml",
    "https://feeds.test/cap/gulf-wind": "cap_gulf_wind.xml",
    "https://feeds.test/cap/smiltene-storm": "cap_smiltene_storm.xml",
    "https://feeds.test/cap/smiltene-rain": "cap_smiltene_rain.xml",
}


def load_fixture(name: str) -> str:
    """Load a fixture file."""
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations."""
    yield


@pytest.fixture(autouse=True)
def no_feed_cache_ttl():
    """Tests swap mocked responses between polls, so never serve from the cache."""
    with patch("custom_components.meteoalarm_custom.api.CACHE_TTL", 0):
        yield


@pytest.fixture
def mock_feed(aioclient_mock):
    """Mock the meteoalarm feed and CAP documents for Latvia."""
    aioclient_mock.get(FEED_URL, text=load_fixture("feed.xml"))
    for url, fixture in CAP_URLS.items():
        aioclient_mock.get(url, text=load_fixture(fixture))
    return aioclient_mock


@pytest.fixture
def mock_feed_only(aioclient_mock):
    """Mock only the Latvia feed; tests register the CAP documents themselves."""
    aioclient_mock.get(FEED_URL, text=load_fixture("feed.xml"))
    return aioclient_mock

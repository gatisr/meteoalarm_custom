"""Tests for the MeteoAlarm config and options flows."""

from unittest.mock import patch

from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteoalarm_custom.api import (
    MeteoAlarmRegion,
    MeteoAlarmUnsupportedCountryError,
)
from custom_components.meteoalarm_custom.const import DOMAIN

REGIONS = [
    MeteoAlarmRegion(name="Riga"),
    MeteoAlarmRegion(name="Southern Gulf of Riga", geocode="LV806"),
]


def _patch_regions(**kwargs):
    return patch(
        "custom_components.meteoalarm_custom.config_flow.async_get_regions", **kwargs
    )


def _patch_setup():
    return patch(
        "custom_components.meteoalarm_custom.async_setup_entry", return_value=True
    )


async def test_full_flow_creates_entry(hass):
    """The happy path: country dropdown -> region dropdown -> entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with _patch_regions(return_value=REGIONS):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "region"

    with _patch_setup():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"province": "Southern Gulf of Riga", "language": "lv", "update_interval": 15},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Southern Gulf of Riga"
    assert result["data"] == {
        "country": "latvia",
        "province": "Southern Gulf of Riga",
        "geocode": "LV806",
    }
    assert result["options"] == {"language": "lv", "update_interval": 15}
    assert result["result"].unique_id == "latvia_southern_gulf_of_riga"
    assert result["result"].version == 3


async def test_duplicate_region_aborts(hass):
    """Adding the same region twice aborts."""
    MockConfigEntry(
        domain=DOMAIN, unique_id="latvia_riga", data={}, title="Riga"
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(return_value=REGIONS):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"province": "Riga", "language": "en", "update_interval": 30}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_invalid_custom_country_shows_error(hass):
    """A custom slug that has no feed shows an inline error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(side_effect=MeteoAlarmUnsupportedCountryError):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "nowhere-land"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"country": "invalid_country"}


async def test_custom_region_without_active_alerts(hass):
    """A region can be typed manually even when the feed lists none."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(return_value=[]):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )
    with _patch_setup():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"province": "Cesis municipality", "language": "en", "update_interval": 30},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["province"] == "Cesis municipality"
    assert result["data"]["geocode"] is None


async def test_options_flow(hass, mock_feed):
    """Language and update interval can be changed after setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        title="Riga",
        unique_id="latvia_riga",
        data={"country": "latvia", "province": "Riga", "geocode": None},
        options={"language": "en", "update_interval": 30},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"language": "lv", "update_interval": 10}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {"language": "lv", "update_interval": 10}

"""Tests for the MeteoAlarm config and options flows."""

from unittest.mock import patch

import pytest

from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteoalarm_custom.api import (
    MeteoAlarmConnectionError,
    MeteoAlarmParseError,
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


async def test_custom_country_cannot_connect(hass):
    """A custom slug cannot be verified offline -> inline error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(side_effect=MeteoAlarmConnectionError):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "custom-land"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"country": "cannot_connect"}


@pytest.mark.parametrize("error", [MeteoAlarmConnectionError, MeteoAlarmParseError])
async def test_known_country_with_feed_problem_still_continues(hass, error):
    """A known country is accepted even if its feed is temporarily broken."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(side_effect=error):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "region"


async def test_blank_region_is_rejected(hass):
    """Whitespace-only regions show an inline error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(return_value=REGIONS):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"province": "   ", "language": "en", "update_interval": 30}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"province": "invalid_province"}


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


async def _reconfigure(hass, entry, country, province, regions=REGIONS):
    result = await entry.start_reconfigure_flow(hass)
    assert result["step_id"] == "reconfigure"
    with _patch_regions(return_value=regions):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": country}
        )
    assert result["step_id"] == "reconfigure_region"
    with _patch_setup():
        return await hass.config_entries.flow.async_configure(
            result["flow_id"], {"province": province}
        )


def _entry(hass, province="Riga") -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        title=province,
        unique_id=f"latvia_{province.lower()}",
        data={"country": "latvia", "province": province, "geocode": None},
        options={"language": "en", "update_interval": 30},
    )
    entry.add_to_hass(hass)
    return entry


async def test_reconfigure_changes_region(hass):
    """The region of an entry can be changed without recreating it."""
    entry = _entry(hass)

    result = await _reconfigure(hass, entry, "latvia", "Southern Gulf of Riga")

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.title == "Southern Gulf of Riga"
    assert entry.unique_id == "latvia_southern_gulf_of_riga"
    assert entry.data == {
        "country": "latvia",
        "province": "Southern Gulf of Riga",
        "geocode": "LV806",
    }
    assert entry.options == {"language": "en", "update_interval": 30}


async def test_reconfigure_rejects_region_of_another_entry(hass):
    """Switching to a region that already has an entry aborts."""
    entry = _entry(hass)
    _entry(hass, "Cesis")

    result = await _reconfigure(hass, entry, "latvia", "Cesis")

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data["province"] == "Riga"


async def test_reconfigure_invalid_country(hass):
    """A missing feed shows an inline error on the reconfigure form."""
    entry = _entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    with _patch_regions(side_effect=MeteoAlarmUnsupportedCountryError):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "nowhere-land"}
        )

    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {"country": "invalid_country"}


async def test_remembered_regions_fill_the_dropdown(hass):
    """Regions seen earlier stay selectable on days the feed lists none."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(return_value=REGIONS):
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions(return_value=[]):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": "latvia"}
        )

    selector = result["data_schema"].schema["province"]
    assert [o["value"] for o in selector.config["options"]] == [
        "Riga",
        "Southern Gulf of Riga",
    ]


async def test_reconfigure_same_region_succeeds(hass):
    """Re-saving the entry's own region is not a duplicate."""
    entry = _entry(hass)

    result = await _reconfigure(hass, entry, "latvia", "Riga")

    assert result["reason"] == "reconfigure_successful"


@pytest.mark.parametrize("slug", ["../etc", "a/b", "x?y=1", "Lat via"])
async def test_malformed_custom_slug_is_rejected_without_request(hass, slug):
    """Slugs that could alter the feed URL never reach the network."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    with _patch_regions() as regions:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"country": slug}
        )

    assert result["errors"] == {"country": "invalid_country"}
    regions.assert_not_called()

"""Tests for the diagnostics download."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteoalarm_custom.const import DOMAIN
from custom_components.meteoalarm_custom.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics(hass, mock_feed):
    """Diagnostics expose the entry, the matched area and the active alerts."""
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

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["entry"]["data"]["province"] == "Smiltene municipality"
    assert diagnostics["entry"]["options"] == {"language": "en", "update_interval": 30}
    assert diagnostics["resolved_area"] == "Smiltene municipality"
    assert diagnostics["last_update_success"] is True
    assert len(diagnostics["alerts"]) == 2

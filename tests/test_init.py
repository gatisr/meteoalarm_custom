from unittest.mock import patch, MagicMock
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.meteoalarm_custom import async_setup_entry, async_unload_entry
from custom_components.meteoalarm_custom.const import DOMAIN, PLATFORMS

@pytest.fixture
def mock_config_entry():
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Test",
        data={},
        source="test",
        options={},
        unique_id="testid",
        entry_id="testentryid",
        minor_version=1,
        discovery_keys=None
    )

@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, mock_config_entry):
    hass.config_entries._entries[mock_config_entry.entry_id] = mock_config_entry

    with patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", return_value=None) as mock_forward:
        assert await async_setup_entry(hass, mock_config_entry)
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        mock_forward.assert_called_once_with(mock_config_entry, PLATFORMS)

@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry):
    hass.config_entries._entries[mock_config_entry.entry_id] = mock_config_entry

    # Setup the entry first
    with patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", return_value=None):
        await async_setup_entry(hass, mock_config_entry)

    # Now test unloading
    with patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms", return_value=True) as mock_unload:
        assert await async_unload_entry(hass, mock_config_entry)
        mock_unload.assert_called_once_with(mock_config_entry, PLATFORMS)

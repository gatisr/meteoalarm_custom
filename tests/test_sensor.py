import os
import json
import pytest
import threading
from unittest.mock import patch, AsyncMock, MagicMock
from custom_components.meteoalarm_custom.sensor import MeteoAlarmSensor
from homeassistant.core import HomeAssistant
from datetime import timedelta, datetime
from homeassistant.helpers.entity_registry import EntityRegistry
from custom_components.meteoalarm_custom.const import (
    ATTRIBUTION,
    ATTR_CATEGORY,
    ATTR_URGENCY,
    ATTR_SEVERITY,
    ATTR_CERTAINTY,
    ATTR_EFFECTIVE,
    ATTR_ONSET,
    ATTR_EXPIRES,
    ATTR_SENDER_NAME,
    ATTR_DESCRIPTION,
    ATTR_WEB,
    ATTR_CONTACT,
    ATTR_AWARENESS_LEVEL,
    ATTR_AWARENESS_TYPE,
)
from custom_components.meteoalarm_custom.const import CONF_COUNTRY, CONF_PROVINCE, CONF_LANGUAGE, CONF_UPDATE_INTERVAL
from datetime import timedelta
from homeassistant.util import dt as dt_util

@pytest.fixture
def mock_meteoalert():
    with patch("custom_components.meteoalarm_custom.sensor.Meteoalert") as mock:
        yield mock

@pytest.fixture
def mock_async_get_meteoalert_data():
  with patch('custom_components.meteoalarm_custom.sensor.async_get_meteoalert_data') as mock:
      yield mock

@pytest.fixture
def mock_hass():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.states.async_available = AsyncMock(return_value=True)
    hass.data = {}
    entity_registry = MagicMock(spec=EntityRegistry)
    entity_registry.async_get_entity_id = AsyncMock(return_value=None)
    hass.data["entity_registry"] = entity_registry
    hass.loop_thread_id = threading.get_ident()  # Add this line
    return hass

def load_translations(lang):
    lang_file = f"custom_components/meteoalarm_custom/translations/{lang}.json"
    with open(lang_file) as file:
        return json.load(file)

def test_sensor_initialization(mock_hass):
    config = {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "en",
        CONF_UPDATE_INTERVAL: 30,
    }
    sensor = MeteoAlarmSensor(mock_hass, config)
    translations = load_translations("en")
    assert sensor.name == translations["entity"]["sensor"]["name"]["name"].format(country="latvia", province="LV001")
    assert sensor.unique_id == "latvia_LV001_en"
    assert sensor.attribution == ATTRIBUTION

@pytest.mark.asyncio
async def test_sensor_update_with_alert_data(mock_hass, mock_async_get_meteoalert_data):
    alert_data = {
        ATTR_AWARENESS_LEVEL: "2; yellow; Moderate",
        ATTR_CATEGORY: "Met",
        ATTR_URGENCY: "Immediate",
        ATTR_SEVERITY: "Moderate",
        ATTR_CERTAINTY: "Likely",
        ATTR_EFFECTIVE: "2024-10-05T01:00:00+03:00",
        ATTR_ONSET: "2024-10-05T01:00:00+03:00",
        ATTR_EXPIRES: "2024-10-05T09:00:00+03:00",
        ATTR_SENDER_NAME: "Latvijas Vides, ģeoloģijas un meteoroloģijas centrs",
        ATTR_DESCRIPTION: "Description of the alert",
        ATTR_WEB: "https://example.com",
        ATTR_CONTACT: "Contact information",
        ATTR_AWARENESS_TYPE: "6; low-temperature",
    }
    mock_async_get_meteoalert_data.return_value = {}

    config = {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "en",
        CONF_UPDATE_INTERVAL: 30,
    }
    sensor = MeteoAlarmSensor(mock_hass, config)
    translations = load_translations("en")
    with patch.object(sensor, 'async_write_ha_state'):
        await sensor.async_update()
    assert sensor.extra_state_attributes == {}
    assert sensor.state == None

    config = {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "en",
        CONF_UPDATE_INTERVAL: 30,
    }
    mock_async_get_meteoalert_data.return_value = alert_data

    sensor = MeteoAlarmSensor(mock_hass, config)
    translations = load_translations("en")
    with patch.object(sensor, 'async_write_ha_state'):
        await sensor.async_update()

    
    expected_attributes = [
            ATTR_CATEGORY, ATTR_URGENCY, ATTR_SEVERITY, ATTR_CERTAINTY,
            ATTR_EFFECTIVE, ATTR_ONSET, ATTR_EXPIRES, ATTR_SENDER_NAME,
            ATTR_DESCRIPTION, ATTR_WEB, ATTR_CONTACT, ATTR_AWARENESS_LEVEL,
            ATTR_AWARENESS_TYPE
        ]

    for attr in expected_attributes:
      assert attr in sensor.extra_state_attributes, f"Attribute {attr} not found in extra_state_attributes"
      assert sensor.extra_state_attributes[attr] == alert_data[attr], f"Attribute {attr} value does not match"

    assert len(sensor.extra_state_attributes) == len(expected_attributes), "Extra_state_attributes contains extra attributes"

    assert sensor.state == "moderate"


@pytest.fixture
def sensor_config():
    return {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "lv",
        CONF_UPDATE_INTERVAL: 30
    }

def test_sensor_initialization(mock_hass, sensor_config):
    sensor = MeteoAlarmSensor(mock_hass, sensor_config)
    assert sensor.unique_id == "latvia_LV001_lv"
    assert sensor.name == "MeteoAlarm (latvia, LV001)"
    assert sensor._update_interval == timedelta(minutes=30)
    assert sensor.entity_id.startswith("sensor.meteoalarm_")

@pytest.mark.asyncio
async def test_sensor_update(mock_hass, sensor_config, mock_async_get_meteoalert_data):
    with patch('custom_components.meteoalarm_custom.sensor.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0)
        sensor = MeteoAlarmSensor(mock_hass, sensor_config)

        # Mock the Meteoalert.get_alert() method
        mock_async_get_meteoalert_data.return_value = {
            "awareness_level": "2; yellow; Moderate",
            "category": "Met",
            "urgency": "Immediate",
        }

        # First update
        with patch.object(sensor, 'async_write_ha_state'):
            await sensor.async_update()
        assert sensor.state == "moderate"
        assert sensor.extra_state_attributes["category"] == "Met"
        assert sensor.extra_state_attributes["urgency"] == "Immediate"

        # Second update (should be throttled)
        mock_async_get_meteoalert_data.return_value = {
            "awareness_level": "3; orange; Severe",
            "category": "Met",
            "urgency": "Immediate",
        }
        with patch.object(sensor, 'async_write_ha_state'):
            await sensor.async_update()
        assert sensor.state == "moderate"  # Should not change due to throttling

        # Third update (after update interval)
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 31)
        with patch.object(sensor, 'async_write_ha_state'):
            await sensor.async_update()
        assert sensor.state == "severe"  # Should change now

@pytest.mark.asyncio
async def test_sensor_update_error(mock_hass, sensor_config, mock_async_get_meteoalert_data):
    sensor = MeteoAlarmSensor(mock_hass, sensor_config)
    
    # Mock an exception in Meteoalert.get_alert()
    mock_async_get_meteoalert_data.side_effect = Exception("API Error")

    with patch.object(sensor, 'async_write_ha_state'):
        await sensor.async_update()
    assert sensor.state is None
    assert sensor.extra_state_attributes == {}
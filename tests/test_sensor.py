import os
import json
import pytest
from unittest.mock import patch, MagicMock
from custom_components.meteoalarm_custom.sensor import MeteoAlarmSensor
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

@pytest.fixture
def mock_meteoalert():
    with patch("custom_components.meteoalarm_custom.sensor.Meteoalert") as mock:
        yield mock

def load_translations(lang):
    lang_file = f"custom_components/meteoalarm_custom/translations/{lang}.json"
    with open(lang_file) as file:
        return json.load(file)

def test_sensor_initialization():
    config = {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "en",
        CONF_UPDATE_INTERVAL: 30,
    }
    sensor = MeteoAlarmSensor(config)
    translations = load_translations("en")
    assert sensor.name == translations["entity"]["sensor"]["name"]["name"].format(country="latvia", province="LV001")
    assert sensor.unique_id == "latvia_LV001_en"
    assert sensor.attribution == ATTRIBUTION

@pytest.mark.asyncio
async def test_sensor_update_with_alert_data(mock_meteoalert):
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
    mock_meteoalert.return_value.get_alert.return_value = alert_data

    config = {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "en",
        CONF_UPDATE_INTERVAL: 30,
    }
    sensor = MeteoAlarmSensor(config)
    translations = load_translations("en")
    await sensor.async_update()


    assert sensor.state == "moderate"
    expected_attributes = {
        translations["entity"]["sensor"][attr]["name"]: alert_data[attr]
        for attr in [
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
        ]
    }
    assert sensor.extra_state_attributes == {**expected_attributes, **alert_data}

@pytest.mark.asyncio
async def test_sensor_update_without_alert_data(mock_meteoalert):
    mock_meteoalert.return_value.get_alert.return_value = {}

    config = {
        CONF_COUNTRY: "latvia",
        CONF_PROVINCE: "LV001",
        CONF_LANGUAGE: "en",
        CONF_UPDATE_INTERVAL: 30,
    }
    sensor = MeteoAlarmSensor(config)
    translations = load_translations("en")
    await sensor.async_update()

    assert sensor.state == None
    assert sensor.extra_state_attributes == {}
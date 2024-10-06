import logging
import os
import json
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import Throttle

from .const import CONF_COUNTRY, CONF_PROVINCE, CONF_LANGUAGE, CONF_UPDATE_INTERVAL
from .const import ATTR_CATEGORY, ATTR_URGENCY, ATTR_SEVERITY, ATTR_CERTAINTY, ATTR_EFFECTIVE, ATTR_ONSET
from .const import ATTRIBUTION
from .const import ATTR_EXPIRES, ATTR_SENDER_NAME, ATTR_DESCRIPTION, ATTR_WEB, ATTR_CONTACT, ATTR_AWARENESS_LEVEL, ATTR_AWARENESS_TYPE

from meteoalertapi import Meteoalert

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    config = entry.data
    async_add_entities([MeteoAlarmSensor(config)], True)

class MeteoAlarmSensor(SensorEntity):
    def __init__(self, config):
        self._country = config[CONF_COUNTRY]
        self._province = config[CONF_PROVINCE]
        self._language = config[CONF_LANGUAGE]
        self._lang = self._language.split("-")[0]
        self._update_interval = timedelta(minutes=config[CONF_UPDATE_INTERVAL])
        # ToDo: use DEFAULT_UPDATE_INTERVAL if not provided
        self._attr_unique_id = f"{self._country}_{self._province}_{self._language}"
        self._data = None
        self._translations = self.load_translations()

    def load_translations(self):
        lang_file = f"{os.path.dirname(__file__)}/translations/{self._lang}.json"
        with open(lang_file) as file:
            return json.load(file)

    @property
    def name(self):
        return self._translations["entity"]["sensor"]["name"]["name"].format(country=self._country, province=self._province)

    @property
    def state(self) -> str | None:
        if self._data:
            awareness_level_parts = self._data["awareness_level"].lower().split(";")
            awareness_color = awareness_level_parts[1].strip()

            if awareness_color == "yellow":
                return "moderate"
            elif awareness_color == "orange":
                return "severe"
            elif awareness_color == "red":
                return "extreme"

        return None

    @property
    def extra_state_attributes(self):
        if self._data:
            attributes = {}
            for attr_key in [ATTR_CATEGORY, ATTR_URGENCY, ATTR_SEVERITY, ATTR_CERTAINTY, ATTR_AWARENESS_LEVEL, ATTR_AWARENESS_TYPE, ATTR_EXPIRES, ATTR_SENDER_NAME, ATTR_DESCRIPTION, ATTR_WEB, ATTR_CONTACT, ATTR_EFFECTIVE, ATTR_ONSET]:
                original_value = self._data.get(attr_key)
                if original_value:
                    translated_name = self._translations["entity"]["sensor"][attr_key]["name"]
                    attributes[translated_name] = original_value 

            return {**attributes, **self._data}
        return {}

    @property
    def attribution(self):
        return ATTRIBUTION

    @Throttle(lambda self: self._update_interval)
    async def async_update(self):
        try:
            data = Meteoalert(self._country, self._province, self._language)
            self._data = data.get_alert()
        except Exception as err:
            _LOGGER.error("Error updating MeteoAlarm sensor: %s", err)
            self._data = None
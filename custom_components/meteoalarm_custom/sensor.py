import aiofiles
import logging
import os
import json
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import generate_entity_id
import asyncio
from functools import partial
from datetime import datetime, timedelta

from .const import CONF_COUNTRY, CONF_PROVINCE, CONF_LANGUAGE, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
from .const import ATTR_CATEGORY, ATTR_URGENCY, ATTR_SEVERITY, ATTR_CERTAINTY, ATTR_EFFECTIVE, ATTR_ONSET
from .const import ATTRIBUTION, ENTITY_ID_FORMAT
from .const import ATTR_EXPIRES, ATTR_SENDER_NAME, ATTR_DESCRIPTION, ATTR_WEB, ATTR_CONTACT, ATTR_AWARENESS_LEVEL, ATTR_AWARENESS_TYPE

from meteoalertapi import Meteoalert

_LOGGER = logging.getLogger(__name__)

async def async_get_meteoalert_data(country, province, language):
    """Asynchronous wrapper for Meteoalert.get_alert()"""
    def get_alert(country, province, language):
        meteoalert = Meteoalert(country, province, language)
        return meteoalert.get_alert()

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(get_alert, country, province, language))

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    config = entry.data
    async_add_entities([MeteoAlarmSensor(hass, config)], True)

class MeteoAlarmSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, config: dict):
        super().__init__()
        self.hass = hass
        self._country = config[CONF_COUNTRY]
        self._province = config[CONF_PROVINCE]
        self._language = config[CONF_LANGUAGE]
        self._lang = self._language.split("-")[0]
        self._update_interval = timedelta(minutes=config[CONF_UPDATE_INTERVAL])
        self._attr_name = f"MeteoAlarm ({self._country}, {self._province})"  # Default name
        # ToDo: use DEFAULT_UPDATE_INTERVAL if not provided
        self._attr_unique_id = f"{self._country}_{self._province}_{self._language}"
        self._data = None
        if hasattr(hass, 'states') and callable(getattr(hass.states, 'async_available', None)):
            self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self._attr_unique_id, hass=hass)
        else:
            self.entity_id = f"{ENTITY_ID_FORMAT.format(self._attr_unique_id)}"
        self._translations = {}
        self._last_update = None

    async def async_added_to_hass(self):
        """Load translations when added to hass."""
        await self.load_translations()

    async def load_translations(self):
        """Load translations asynchronously."""
        lang_file = f"{os.path.dirname(__file__)}/translations/{self._lang}.json"
        try:
            async with aiofiles.open(lang_file, mode='r') as file:
                content = await file.read()
                self._translations = json.loads(content)
        except Exception as err:
            _LOGGER.error(f"Error loading translations: {err}")
            self._translations = {}

    @property
    def name(self):
        try:
            return self._translations["entity"]["sensor"]["name"]["name"].format(
                country=self._country, province=self._province
            )
        except (KeyError, AttributeError):
            _LOGGER.warning("Translation for name not found, using default")
            return self._attr_name

    @property
    def state(self) -> str | None:
        _LOGGER.debug(f"Entering state property, _data: {self._data}") # Debug statement

        if self._data and "awareness_level" in self._data:
            awareness_level_parts = self._data["awareness_level"].lower().split(";")
            if len(awareness_level_parts) >= 2:
                awareness_color = awareness_level_parts[1].strip()
                _LOGGER.debug(f"awareness_color: {awareness_color}") # Debug statement

                if awareness_color == "yellow":
                    return "moderate"
                elif awareness_color == "orange":
                    return "severe"
                elif awareness_color == "red":
                    return "extreme"

        _LOGGER.debug("State is None") # Debug statement
        return None 

    @property
    def extra_state_attributes(self):
        if self._data:
            attributes = {}
            for attr_key in [ATTR_CATEGORY, ATTR_URGENCY, ATTR_SEVERITY, ATTR_CERTAINTY, ATTR_AWARENESS_LEVEL, ATTR_AWARENESS_TYPE, ATTR_EXPIRES, ATTR_SENDER_NAME, ATTR_DESCRIPTION, ATTR_WEB, ATTR_CONTACT, ATTR_EFFECTIVE, ATTR_ONSET]:
                original_value = self._data.get(attr_key)
                if original_value:
                    try:
                        translated_name = self._translations["entity"]["sensor"][attr_key]["name"]
                    except KeyError:
                        translated_name = attr_key
                    attributes[translated_name] = original_value
            return attributes
        return {}

    @property
    def attribution(self):
        return ATTRIBUTION

    def _get_update_interval(self):
        """Get the update interval, ensuring it's valid and not smaller than 1 minute."""
        if self._update_interval < timedelta(minutes=1):
            _LOGGER.warning("Invalid update interval. Using DEFAULT_UPDATE_INTERVAL.")
            return timedelta(minutes=DEFAULT_UPDATE_INTERVAL)
        return self._update_interval

    async def async_update(self):
        """Update sensor state."""
        now = datetime.now()
        if self._last_update is None or now - self._last_update >= self._get_update_interval():
            try:
                self._data = await async_get_meteoalert_data(self._country, self._province, self._language)
                self._last_update = now
            except Exception as err:
                _LOGGER.error("Error updating MeteoAlarm sensor: %s", err)
                self._data = None

            self.async_write_ha_state()
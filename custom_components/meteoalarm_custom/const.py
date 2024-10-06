"""Constants for the MeteoAlarm integration."""

DOMAIN = "meteoalarm_custom"
PLATFORMS = ["sensor"]

CONF_COUNTRY = "country"
CONF_PROVINCE = "province"
CONF_LANGUAGE = "language"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_NAME = "MeteoAlarm"
DEFAULT_LANGUAGE = "en"
DEFAULT_COUNTRY = "latvia"
DEFAULT_UPDATE_INTERVAL = 30
ATTRIBUTION = "Data provided by MeteoAlarm"

# Sensor attributes
ATTR_NAME = "name"
ATTR_UNIQUE_ID = "unique_id"
ATTR_STATE = "state"
ATTR_CATEGORY = "category"
ATTR_URGENCY = "urgency"
ATTR_SEVERITY = "severity"
ATTR_CERTAINTY = "certainty"
ATTR_EFFECTIVE = "effective"
ATTR_ONSET = "onset"
ATTR_EXPIRES = "expires"
ATTR_SENDER_NAME = "sender_name"
ATTR_DESCRIPTION = "description"
ATTR_WEB = "web"
ATTR_CONTACT = "contact"
ATTR_AWARENESS_LEVEL = "awareness_level"
ATTR_AWARENESS_TYPE = "awareness_type"

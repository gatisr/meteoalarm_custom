"""Constants for the MeteoAlarm integration."""

from homeassistant.const import Platform

DOMAIN = "meteoalarm_custom"
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.EVENT,
    Platform.SENSOR,
]

CONF_COUNTRY = "country"
CONF_PROVINCE = "province"
CONF_GEOCODE = "geocode"
CONF_LANGUAGE = "language"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_NAME = "MeteoAlarm"
DEFAULT_LANGUAGE = "en"
DEFAULT_COUNTRY = "latvia"
DEFAULT_UPDATE_INTERVAL = 30
ATTRIBUTION = "Data provided by MeteoAlarm"

MANUFACTURER = "MeteoAlarm"
CONFIGURATION_URL = "https://meteoalarm.org"

ATTR_ALERTS = "alerts"
ATTR_EVENT = "event"
ATTR_HEADLINE = "headline"
ATTR_SEVERITY = "severity"
ATTR_AWARENESS_LEVEL = "awareness_level"
ATTR_AWARENESS_TYPE = "awareness_type"
ATTR_CATEGORY = "category"
ATTR_URGENCY = "urgency"
ATTR_CERTAINTY = "certainty"
ATTR_ONSET = "onset"
ATTR_EXPIRES = "expires"
ATTR_EFFECTIVE = "effective"
ATTR_SENDER_NAME = "sender_name"
ATTR_DESCRIPTION = "description"
ATTR_INSTRUCTION = "instruction"
ATTR_WEB = "web"
ATTR_CONTACT = "contact"
ATTR_AREA = "area"
ATTR_IDENTIFIER = "identifier"

EVENT_TYPE_ALERT = "alert"

# Severity states, ordered from least to most severe. The state of the main
# sensor is the highest severity among the currently active alerts.
SEVERITY_NONE = "none"
SEVERITY_MINOR = "minor"
SEVERITY_MODERATE = "moderate"
SEVERITY_SEVERE = "severe"
SEVERITY_EXTREME = "extreme"
SEVERITY_ORDER = [
    SEVERITY_NONE,
    SEVERITY_MINOR,
    SEVERITY_MODERATE,
    SEVERITY_SEVERE,
    SEVERITY_EXTREME,
]

# Mapping of meteoalarm awareness colors to severity states.
AWARENESS_COLOR_TO_SEVERITY = {
    "green": SEVERITY_NONE,
    "yellow": SEVERITY_MODERATE,
    "orange": SEVERITY_SEVERE,
    "red": SEVERITY_EXTREME,
}

# Mapping of CAP severity values to severity states (fallback when the
# awareness_level parameter is missing).
CAP_SEVERITY_TO_SEVERITY = {
    "minor": SEVERITY_MINOR,
    "moderate": SEVERITY_MODERATE,
    "severe": SEVERITY_SEVERE,
    "extreme": SEVERITY_EXTREME,
}

FRONTEND_URL_PATH = f"/{DOMAIN}/meteoalarm-card.js"

# Country slugs exactly as used in
# https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-<slug>
# (validated against the live feeds).
COUNTRIES = {
    "andorra": "Andorra",
    "austria": "Austria",
    "belgium": "Belgium",
    "bosnia-herzegovina": "Bosnia and Herzegovina",
    "bulgaria": "Bulgaria",
    "croatia": "Croatia",
    "cyprus": "Cyprus",
    "czechia": "Czechia",
    "denmark": "Denmark",
    "estonia": "Estonia",
    "finland": "Finland",
    "france": "France",
    "germany": "Germany",
    "greece": "Greece",
    "hungary": "Hungary",
    "iceland": "Iceland",
    "ireland": "Ireland",
    "israel": "Israel",
    "italy": "Italy",
    "latvia": "Latvia",
    "lithuania": "Lithuania",
    "luxembourg": "Luxembourg",
    "malta": "Malta",
    "moldova": "Moldova",
    "montenegro": "Montenegro",
    "netherlands": "Netherlands",
    "norway": "Norway",
    "poland": "Poland",
    "portugal": "Portugal",
    "republic-of-north-macedonia": "North Macedonia",
    "romania": "Romania",
    "serbia": "Serbia",
    "slovakia": "Slovakia",
    "slovenia": "Slovenia",
    "spain": "Spain",
    "sweden": "Sweden",
    "switzerland": "Switzerland",
    "ukraine": "Ukraine",
    "united-kingdom": "United Kingdom",
}

"""Data update coordinator for the MeteoAlarm integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MeteoAlarmAlert, MeteoAlarmApi, MeteoAlarmError
from .const import (
    CONF_COUNTRY,
    CONF_GEOCODE,
    CONF_LANGUAGE,
    CONF_PROVINCE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_LANGUAGE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

type MeteoAlarmConfigEntry = ConfigEntry[MeteoAlarmCoordinator]


class MeteoAlarmCoordinator(DataUpdateCoordinator[list[MeteoAlarmAlert]]):
    """Coordinator fetching alerts for one region."""

    config_entry: MeteoAlarmConfigEntry

    def __init__(self, hass: HomeAssistant, entry: MeteoAlarmConfigEntry) -> None:
        """Initialize the coordinator."""
        self.country: str = entry.data[CONF_COUNTRY]
        self.province: str = entry.data[CONF_PROVINCE]
        self.language: str = entry.options.get(
            CONF_LANGUAGE, entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        )
        update_interval = entry.options.get(
            CONF_UPDATE_INTERVAL,
            entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )
        try:
            update_minutes = max(1, int(update_interval))
        except (TypeError, ValueError):
            update_minutes = DEFAULT_UPDATE_INTERVAL

        self.api = MeteoAlarmApi(
            async_get_clientsession(hass),
            self.country,
            self.province,
            self.language,
            geocode=entry.data.get(CONF_GEOCODE),
        )

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {self.province}",
            update_interval=timedelta(minutes=update_minutes),
        )

    async def _async_update_data(self) -> list[MeteoAlarmAlert]:
        """Fetch the currently active alerts."""
        try:
            return await self.api.get_alerts()
        except MeteoAlarmError as err:
            raise UpdateFailed(str(err)) from err

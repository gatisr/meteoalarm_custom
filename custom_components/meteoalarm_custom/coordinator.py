"""Data update coordinator for the MeteoAlarm integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    MeteoAlarmAlert,
    MeteoAlarmApi,
    MeteoAlarmError,
    MeteoAlarmUnsupportedCountryError,
)
from .const import (
    CONFIGURATION_URL,
    COUNTRIES,
    CONF_COUNTRY,
    CONF_GEOCODE,
    CONF_LANGUAGE,
    CONF_PROVINCE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_LANGUAGE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .shared import get_feed_cache, get_known_regions

_LOGGER = logging.getLogger(__name__)

type MeteoAlarmConfigEntry = ConfigEntry[MeteoAlarmCoordinator]


def feed_issue_id(entry_id: str) -> str:
    """Return the Repairs issue id for a missing country feed."""
    return f"feed_unavailable_{entry_id}"


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
            cache=get_feed_cache(hass),
        )
        self._unsub_expiry: CALLBACK_TYPE | None = None

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
            alerts = await self.api.get_alerts()
        except MeteoAlarmUnsupportedCountryError as err:
            self._cancel_expiry()
            self._set_feed_issue(True)
            raise UpdateFailed(str(err)) from err
        except MeteoAlarmError as err:
            self._cancel_expiry()
            raise UpdateFailed(str(err)) from err

        self._set_feed_issue(False)
        await get_known_regions(self.hass).async_add(self.country, self.api.feed_regions)
        self._schedule_expiry(alerts)
        return alerts

    async def async_shutdown(self) -> None:
        """Cancel the pending expiry timer along with the regular refresh."""
        self._cancel_expiry()
        await super().async_shutdown()

    # -- expiry --------------------------------------------------------------

    def _cancel_expiry(self) -> None:
        if self._unsub_expiry is not None:
            self._unsub_expiry()
            self._unsub_expiry = None

    def _schedule_expiry(self, alerts: list[MeteoAlarmAlert]) -> None:
        """Fire once at the earliest expiry so ended alerts vanish before the next poll."""
        self._cancel_expiry()
        now = dt_util.utcnow()
        upcoming = [a.expires for a in alerts if a.expires and a.expires > now]
        if upcoming:
            self._unsub_expiry = async_track_point_in_utc_time(
                self.hass, self._handle_expiry, min(upcoming)
            )

    @callback
    def _handle_expiry(self, _now) -> None:
        self._unsub_expiry = None
        now = dt_util.utcnow()
        self.data = [a for a in self.data or [] if a.expires is None or a.expires > now]
        self._schedule_expiry(self.data)
        # Not async_set_updated_data: it would reset the poll timer.
        self.async_update_listeners()

    # -- repairs -------------------------------------------------------------

    def _set_feed_issue(self, active: bool) -> None:
        """Raise a Repairs issue while the country feed is gone (404)."""
        issue_id = feed_issue_id(self.config_entry.entry_id)
        if active:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.ERROR,
                translation_key="feed_unavailable",
                translation_placeholders={
                    "country": COUNTRIES.get(self.country, self.country),
                    "region": self.province,
                    "url": CONFIGURATION_URL,
                },
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)

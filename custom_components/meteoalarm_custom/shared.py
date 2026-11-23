"""State shared between all config entries of the integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .api import FeedCache, MeteoAlarmRegion
from .const import DOMAIN

_CACHE_KEY = f"{DOMAIN}_feed_cache"
_REGIONS_KEY = f"{DOMAIN}_known_regions"
STORAGE_VERSION = 1


def get_feed_cache(hass: HomeAssistant) -> FeedCache:
    """Return the download cache shared by every entry."""
    if _CACHE_KEY not in hass.data:
        hass.data[_CACHE_KEY] = FeedCache()
    return hass.data[_CACHE_KEY]


class KnownRegions:
    """Regions seen in country feeds, persisted (the live feed lists only active ones)."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, dict[str, str | None]]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.regions"
        )
        self._data: dict[str, dict[str, str | None]] | None = None

    async def _load(self) -> dict[str, dict[str, str | None]]:
        if self._data is None:
            self._data = await self._store.async_load() or {}
        return self._data

    async def async_get(self, country: str) -> list[MeteoAlarmRegion]:
        """Return the remembered regions of a country."""
        data = await self._load()
        return [
            MeteoAlarmRegion(name=name, geocode=geocode)
            for name, geocode in data.get(country, {}).items()
        ]

    async def async_add(self, country: str, regions: list[MeteoAlarmRegion]) -> None:
        """Remember regions; only touches storage when something is new."""
        data = await self._load()
        known = data.setdefault(country, {})
        changed = False
        for region in regions:
            if region.name not in known or (
                region.geocode and known[region.name] != region.geocode
            ):
                known[region.name] = region.geocode
                changed = True
        if changed:
            await self._store.async_save(data)


def get_known_regions(hass: HomeAssistant) -> KnownRegions:
    """Return the persistent region memory."""
    if _REGIONS_KEY not in hass.data:
        hass.data[_REGIONS_KEY] = KnownRegions(hass)
    return hass.data[_REGIONS_KEY]

"""Serve the bundled meteoalarm-card and register it as a Lovelace resource."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN, FRONTEND_URL_PATH

_LOGGER = logging.getLogger(__name__)

_REGISTERED_KEY = f"{DOMAIN}_frontend_registered"
CARD_FILENAME = "meteoalarm-card.js"


def _card_path() -> Path:
    return Path(__file__).parent / "frontend" / CARD_FILENAME


def _card_url(version: str) -> str:
    return f"{FRONTEND_URL_PATH}?v={version}"


async def async_register_frontend(hass: HomeAssistant, version: str) -> None:
    """Serve the card JS and add it to the Lovelace resources (storage mode)."""
    if hass.data.get(_REGISTERED_KEY):
        return

    path = _card_path()
    if not path.exists():
        _LOGGER.debug("Card asset %s not found, skipping frontend setup", path)
        return

    http = getattr(hass, "http", None)
    if http is None:
        return

    await http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL_PATH, str(path), True)]
    )
    hass.data[_REGISTERED_KEY] = True

    resources = _resources(hass)
    if resources is None or not hasattr(resources, "async_create_item"):
        # YAML-mode dashboards manage resources manually; nothing to do.
        return

    url = _card_url(version)
    try:
        if not resources.loaded:
            await resources.async_load()
        for item in resources.async_items():
            item_url = item.get("url", "")
            if item_url.split("?")[0] == FRONTEND_URL_PATH:
                if item_url != url:
                    await resources.async_update_item(item["id"], {"url": url})
                return
        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.info("Registered Lovelace resource %s", url)
    except Exception:  # noqa: BLE001 - never break integration setup over the card
        _LOGGER.exception("Could not register the meteoalarm-card Lovelace resource")


async def async_remove_frontend(hass: HomeAssistant) -> None:
    """Remove the Lovelace resource when the last config entry is removed."""
    resources = _resources(hass)
    if resources is None or not hasattr(resources, "async_delete_item"):
        return
    try:
        if not resources.loaded:
            await resources.async_load()
        for item in list(resources.async_items()):
            if item.get("url", "").split("?")[0] == FRONTEND_URL_PATH:
                await resources.async_delete_item(item["id"])
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Could not remove the meteoalarm-card Lovelace resource")


def _resources(hass: HomeAssistant):
    lovelace = hass.data.get("lovelace")
    if lovelace is None:
        return None
    # LovelaceData dataclass in modern HA; a plain dict on very old versions.
    if isinstance(lovelace, dict):
        return lovelace.get("resources")
    return getattr(lovelace, "resources", None)

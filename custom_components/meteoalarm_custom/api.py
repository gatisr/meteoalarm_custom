"""Async client for the MeteoAlarm feeds.

Replaces the synchronous ``meteoalertapi`` library. Talks directly to the
legacy ATOM feed (one entry per active warning) and the linked CAP documents
(per-language texts), which allows returning every active alert for a region
instead of only the first one, and enumerating the regions that currently
appear in a country feed (used by the config flow dropdown).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
import re
import unicodedata
import xml.etree.ElementTree as ET

import aiohttp

from homeassistant.util import dt as dt_util

from .const import (
    AWARENESS_COLOR_TO_SEVERITY,
    CAP_SEVERITY_TO_SEVERITY,
    SEVERITY_NONE,
    SEVERITY_ORDER,
)

_LOGGER = logging.getLogger(__name__)

FEED_URL = "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-{country}"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "cap": "urn:oasis:names:tc:emergency:cap:1.2",
}


class MeteoAlarmError(Exception):
    """Base error for MeteoAlarm API problems."""


class MeteoAlarmConnectionError(MeteoAlarmError):
    """Raised when the feed cannot be reached."""


class MeteoAlarmUnsupportedCountryError(MeteoAlarmError):
    """Raised when the country feed does not exist (HTTP 404)."""


@dataclass(slots=True)
class MeteoAlarmAlert:
    """A single active weather alert."""

    identifier: str
    event: str | None = None
    headline: str | None = None
    description: str | None = None
    instruction: str | None = None
    severity: str = SEVERITY_NONE
    awareness_level: str | None = None
    awareness_type: str | None = None
    category: str | None = None
    urgency: str | None = None
    certainty: str | None = None
    onset: datetime | None = None
    expires: datetime | None = None
    effective: datetime | None = None
    sender_name: str | None = None
    web: str | None = None
    contact: str | None = None
    language: str | None = None
    area: str | None = None

    def as_dict(self) -> dict:
        """Return a JSON/attribute friendly representation."""
        return {
            "identifier": self.identifier,
            "event": self.event,
            "headline": self.headline,
            "description": self.description,
            "instruction": self.instruction,
            "severity": self.severity,
            "awareness_level": self.awareness_level,
            "awareness_type": self.awareness_type,
            "category": self.category,
            "urgency": self.urgency,
            "certainty": self.certainty,
            "onset": self.onset.isoformat() if self.onset else None,
            "expires": self.expires.isoformat() if self.expires else None,
            "effective": self.effective.isoformat() if self.effective else None,
            "sender_name": self.sender_name,
            "web": self.web,
            "contact": self.contact,
            "language": self.language,
            "area": self.area,
        }


@dataclass(slots=True)
class MeteoAlarmRegion:
    """A region present in a country feed."""

    name: str
    geocode: str | None = None


@dataclass(slots=True)
class _FeedEntry:
    area: str
    geocode: str | None
    cap_url: str | None
    severity: str


def _normalize(value: str) -> str:
    """Lowercase and strip diacritics ("Preiļi" -> "preili").

    The feeds publish region names without diacritics while users (and
    entries created by old versions) often use the local spelling.
    """
    decomposed = unicodedata.normalize("NFKD", value.strip().lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def severity_rank(severity: str) -> int:
    """Return sort rank of a severity state (higher = more severe)."""
    try:
        return SEVERITY_ORDER.index(severity)
    except ValueError:
        return 0


class MeteoAlarmApi:
    """Fetch alerts for one region of one country."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        country: str,
        province: str,
        language: str = "en",
        geocode: str | None = None,
    ) -> None:
        self._session = session
        self._country = country.strip().lower()
        self._province = province.strip()
        self._language = (language or "en").strip()
        self._geocode = (geocode or "").strip() or None
        self.resolved_area: str | None = None

    async def get_alerts(self) -> list[MeteoAlarmAlert]:
        """Return all currently active alerts for the configured region."""
        feed_xml = await _fetch(self._session, FEED_URL.format(country=self._country))
        entries = _parse_feed_entries(feed_xml)
        matched = self._match_entries(entries)
        self.resolved_area = matched[0].area if matched else None

        now = dt_util.utcnow()
        alerts: list[MeteoAlarmAlert] = []
        for entry in matched:
            if not entry.cap_url:
                continue
            try:
                cap_xml = await _fetch(self._session, entry.cap_url)
                alert = _parse_cap(cap_xml, self._language, entry.area)
            except MeteoAlarmError as err:
                _LOGGER.warning("Failed to fetch CAP data from %s: %s", entry.cap_url, err)
                continue
            if alert is None:
                continue
            # The feed keeps entries around for a while after they end;
            # don't report alerts that have already expired.
            if alert.expires is not None and alert.expires <= now:
                continue
            alerts.append(alert)

        alerts.sort(key=lambda a: severity_rank(a.severity), reverse=True)
        return alerts

    def _match_entries(self, entries: list[_FeedEntry]) -> list[_FeedEntry]:
        """Find the feed entries belonging to the configured region.

        Exact areaDesc/geocode matches win. A token-based fallback keeps
        entries created by older versions working (their stored province may
        be a free-text value such as "Smiltene LV045").
        """
        province_norm = _normalize(self._province)

        exact = [
            e
            for e in entries
            if _normalize(e.area) == province_norm
            or (self._geocode and e.geocode and e.geocode.lower() == self._geocode.lower())
            or (e.geocode and e.geocode.lower() == province_norm)
        ]
        if exact:
            return exact

        tokens = [t for t in re.split(r"[\s,;/]+", province_norm) if t]
        if not tokens:
            return []

        candidates: list[_FeedEntry] = []
        for entry in entries:
            area_norm = _normalize(entry.area)
            if entry.geocode and entry.geocode.lower() in tokens:
                candidates.append(entry)
                continue
            alpha_tokens = [t for t in tokens if t.isalpha()]
            if alpha_tokens and all(
                re.search(rf"\b{re.escape(t)}\b", area_norm) for t in alpha_tokens
            ):
                candidates.append(entry)

        if not candidates:
            return []
        # Several distinct areas can match loose tokens ("Riga" also occurs in
        # "Gulf of Riga East"); keep only the shortest matched area name.
        best_area = min((c.area for c in candidates), key=len)
        return [c for c in candidates if c.area == best_area]


async def async_get_regions(
    session: aiohttp.ClientSession, country: str
) -> list[MeteoAlarmRegion]:
    """Return the regions currently present in a country feed.

    The legacy feed only contains regions with active warnings, so on calm
    days this list can be incomplete or empty - callers must allow free-text
    region entry as well.
    """
    feed_xml = await _fetch(session, FEED_URL.format(country=country.strip().lower()))
    regions: dict[str, MeteoAlarmRegion] = {}
    for entry in _parse_feed_entries(feed_xml):
        if entry.area not in regions:
            regions[entry.area] = MeteoAlarmRegion(name=entry.area, geocode=entry.geocode)
    return sorted(regions.values(), key=lambda r: r.name)


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            if response.status == 404:
                raise MeteoAlarmUnsupportedCountryError(
                    f"Feed not found (404) for {url}"
                )
            if response.status != 200:
                raise MeteoAlarmConnectionError(
                    f"Unexpected status {response.status} for {url}"
                )
            return await response.text()
    except (aiohttp.ClientError, TimeoutError) as err:
        raise MeteoAlarmConnectionError(f"Error fetching {url}: {err}") from err


def _parse_feed_entries(feed_xml: str) -> list[_FeedEntry]:
    try:
        root = ET.fromstring(feed_xml)
    except ET.ParseError as err:
        raise MeteoAlarmConnectionError(f"Invalid feed XML: {err}") from err

    entries: list[_FeedEntry] = []
    for entry in root.findall("atom:entry", NS):
        area_el = entry.find("cap:areaDesc", NS)
        if area_el is None or not (area_el.text or "").strip():
            continue

        geocode = None
        geocode_el = entry.find("cap:geocode", NS)
        if geocode_el is not None:
            value_el = geocode_el.find("atom:value", NS)
            if value_el is not None and (value_el.text or "").strip():
                geocode = value_el.text.strip()

        cap_url = None
        for link in entry.findall("atom:link", NS):
            if link.get("type") == "application/cap+xml":
                cap_url = link.get("href")
                break

        severity_el = entry.find("cap:severity", NS)
        severity = CAP_SEVERITY_TO_SEVERITY.get(
            (severity_el.text or "").strip().lower() if severity_el is not None else "",
            SEVERITY_NONE,
        )

        entries.append(
            _FeedEntry(
                area=area_el.text.strip(),
                geocode=geocode,
                cap_url=cap_url,
                severity=severity,
            )
        )
    return entries


def _parse_cap(cap_xml: str, language: str, area: str) -> MeteoAlarmAlert | None:
    try:
        root = ET.fromstring(cap_xml)
    except ET.ParseError as err:
        raise MeteoAlarmConnectionError(f"Invalid CAP XML: {err}") from err

    infos = root.findall("cap:info", NS)
    if not infos:
        return None

    info = _pick_language(infos, language)

    def text(tag: str) -> str | None:
        el = info.find(f"cap:{tag}", NS)
        if el is not None and el.text and el.text.strip():
            return el.text.strip()
        return None

    def when(tag: str) -> datetime | None:
        raw = text(tag)
        return dt_util.parse_datetime(raw) if raw else None

    parameters: dict[str, str] = {}
    for parameter in info.findall("cap:parameter", NS):
        name_el = parameter.find("cap:valueName", NS)
        value_el = parameter.find("cap:value", NS)
        if name_el is not None and value_el is not None and name_el.text:
            parameters[name_el.text.strip()] = (value_el.text or "").strip()

    awareness_level = parameters.get("awareness_level")
    severity = _severity_from(awareness_level, text("severity"))

    identifier_el = root.find("cap:identifier", NS)
    identifier = (
        identifier_el.text.strip()
        if identifier_el is not None and identifier_el.text
        else ""
    )

    sender_el = root.find("cap:sender", NS)
    sender = sender_el.text.strip() if sender_el is not None and sender_el.text else None

    return MeteoAlarmAlert(
        identifier=identifier,
        event=text("event"),
        headline=text("headline"),
        description=text("description"),
        instruction=text("instruction"),
        severity=severity,
        awareness_level=awareness_level,
        awareness_type=parameters.get("awareness_type"),
        category=text("category"),
        urgency=text("urgency"),
        certainty=text("certainty"),
        onset=when("onset") or when("effective"),
        expires=when("expires"),
        effective=when("effective"),
        sender_name=text("senderName") or sender,
        web=text("web"),
        contact=text("contact"),
        language=text("language"),
        area=area,
    )


def _pick_language(infos: list[ET.Element], language: str) -> ET.Element:
    """Pick the info block in the requested language, else English, else first."""
    wanted = language.lower().split("-")[0]

    def info_lang(info: ET.Element) -> str:
        el = info.find("cap:language", NS)
        return (el.text or "").strip().lower() if el is not None and el.text else ""

    for info in infos:
        if info_lang(info).split("-")[0] == wanted:
            return info
    for info in infos:
        if info_lang(info).split("-")[0] == "en":
            return info
    return infos[0]


def _severity_from(awareness_level: str | None, cap_severity: str | None) -> str:
    if awareness_level:
        parts = awareness_level.lower().split(";")
        if len(parts) >= 2:
            color = parts[1].strip()
            if color in AWARENESS_COLOR_TO_SEVERITY:
                return AWARENESS_COLOR_TO_SEVERITY[color]
    if cap_severity:
        return CAP_SEVERITY_TO_SEVERITY.get(cap_severity.lower(), SEVERITY_NONE)
    return SEVERITY_NONE

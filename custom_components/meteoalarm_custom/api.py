"""Async client for the MeteoAlarm legacy ATOM feed and its CAP documents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
import logging
import re
import time
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
MAX_CONCURRENT_CAP_REQUESTS = 5
CACHE_TTL = 60.0  # seconds

# CAP messages that must not be reported as real warnings.
_IGNORED_CAP_STATUSES = {"test", "exercise", "draft"}
_IGNORED_CAP_MSG_TYPES = {"cancel"}

# Letters NFKD decomposition does not fold ("Łódź" -> "lodz").
_TRANSLITERATION = str.maketrans(
    {
        "ł": "l",
        "ø": "o",
        "đ": "d",
        "ð": "d",
        "þ": "th",
        "ß": "ss",
        "æ": "ae",
        "œ": "oe",
        "ı": "i",
    }
)

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


class MeteoAlarmParseError(MeteoAlarmError):
    """Raised when a feed or CAP document is not valid XML."""


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
    """Lowercase and strip diacritics ("Preiļi" -> "preili"); feeds are ASCII."""
    lowered = value.strip().lower().translate(_TRANSLITERATION)
    decomposed = unicodedata.normalize("NFKD", lowered)
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
        cache: FeedCache | None = None,
    ) -> None:
        self._session = session
        self._cache = cache
        self._country = country.strip().lower()
        self._province = province.strip()
        self._language = (language or "en").strip()
        self._geocode = (geocode or "").strip() or None
        self.resolved_area: str | None = None
        # Every region present in the last downloaded feed (matched or not).
        self.feed_regions: list[MeteoAlarmRegion] = []

    async def get_alerts(self) -> list[MeteoAlarmAlert]:
        """Return all currently active alerts for the configured region."""
        feed_xml = await _fetch(
            self._session, FEED_URL.format(country=self._country), self._cache
        )
        entries = _parse_feed_entries(feed_xml)
        self.feed_regions = _regions_of(entries)
        matched = self._match_entries(entries)
        self.resolved_area = matched[0].area if matched else None

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_CAP_REQUESTS)

        async def fetch_alert(entry: _FeedEntry) -> MeteoAlarmAlert | None:
            async with semaphore:
                cap_xml = await _fetch(self._session, entry.cap_url, self._cache)
            return _parse_cap(cap_xml, self._language, entry.area)

        # A failed CAP must fail the update; dropping it would look like an all-clear.
        results = await asyncio.gather(
            *(fetch_alert(entry) for entry in matched if entry.cap_url)
        )

        now = dt_util.utcnow()
        alerts: list[MeteoAlarmAlert] = []
        for alert in results:
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
        """Match by name/geocode; a token fallback serves legacy "Smiltene LV045" values."""
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

        alpha_tokens = [t for t in tokens if t.isalpha()]
        candidates: list[_FeedEntry] = []
        for entry in entries:
            area_norm = _normalize(entry.area)
            if entry.geocode and entry.geocode.lower() in tokens:
                candidates.append(entry)
                continue
            if alpha_tokens and all(
                re.search(rf"\b{re.escape(t)}\b", area_norm) for t in alpha_tokens
            ):
                candidates.append(entry)

        if len({c.area for c in candidates}) <= 1 or not alpha_tokens:
            return candidates

        # Ambiguous: prefer exact name, then prefix; otherwise don't guess.
        wanted = " ".join(alpha_tokens)
        for narrow in (
            lambda area: area == wanted,
            lambda area: area.startswith(wanted),
        ):
            narrowed = [c for c in candidates if narrow(_normalize(c.area))]
            if len({c.area for c in narrowed}) == 1:
                return narrowed
        _LOGGER.debug(
            "Region %r is ambiguous in the %s feed; not guessing", self._province, self._country
        )
        return []


def _regions_of(entries: list[_FeedEntry]) -> list[MeteoAlarmRegion]:
    regions: dict[str, MeteoAlarmRegion] = {}
    for entry in entries:
        if entry.area not in regions:
            regions[entry.area] = MeteoAlarmRegion(name=entry.area, geocode=entry.geocode)
    return sorted(regions.values(), key=lambda r: r.name)


async def async_get_regions(
    session: aiohttp.ClientSession, country: str, cache: FeedCache | None = None
) -> list[MeteoAlarmRegion]:
    """Return the regions in a country feed (only those with active warnings)."""
    feed_xml = await _fetch(
        session, FEED_URL.format(country=country.strip().lower()), cache
    )
    return _regions_of(_parse_feed_entries(feed_xml))


class FeedCache:
    """Share downloads between entries for a short TTL."""

    def __init__(self, ttl: float | None = None) -> None:
        self._ttl = CACHE_TTL if ttl is None else ttl
        self._items: dict[str, tuple[float, bytes]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> bytes:
        """Return the document at ``url``; concurrent callers share one request."""
        async with self._locks.setdefault(url, asyncio.Lock()):
            now = time.monotonic()
            cached = self._items.get(url)
            if cached and now - cached[0] < self._ttl:
                return cached[1]
            body = await _request(session, url)
            self._items[url] = (now, body)
        self._prune(now)
        return body

    def _prune(self, now: float) -> None:
        self._items = {u: i for u, i in self._items.items() if now - i[0] < self._ttl}
        idle = [u for u, lock in self._locks.items() if u not in self._items and not lock.locked()]
        for url in idle:
            del self._locks[url]


async def _fetch(
    session: aiohttp.ClientSession, url: str, cache: FeedCache | None = None
) -> bytes:
    if cache is not None:
        return await cache.fetch(session, url)
    return await _request(session, url)


async def _request(session: aiohttp.ClientSession, url: str) -> bytes:
    if not url.startswith("https://"):
        raise MeteoAlarmConnectionError(f"Refusing non-HTTPS URL {url}")
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            if response.status == 404:
                raise MeteoAlarmUnsupportedCountryError(f"Feed not found (404) for {url}")
            if response.status != 200:
                raise MeteoAlarmConnectionError(
                    f"Unexpected status {response.status} for {url}"
                )
            # Bytes, so the XML declaration decides the encoding.
            return await response.read()
    except (aiohttp.ClientError, TimeoutError) as err:
        raise MeteoAlarmConnectionError(f"Error fetching {url}: {err}") from err


def _parse_feed_entries(feed_xml: bytes | str) -> list[_FeedEntry]:
    try:
        root = ET.fromstring(feed_xml)
    except ET.ParseError as err:
        raise MeteoAlarmParseError(f"Invalid feed XML: {err}") from err

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


def _parse_cap(
    cap_xml: bytes | str, language: str, area: str
) -> MeteoAlarmAlert | None:
    try:
        root = ET.fromstring(cap_xml)
    except ET.ParseError as err:
        raise MeteoAlarmParseError(f"Invalid CAP XML: {err}") from err

    def root_text(tag: str) -> str:
        el = root.find(f"cap:{tag}", NS)
        return (el.text or "").strip().lower() if el is not None else ""

    if (
        root_text("status") in _IGNORED_CAP_STATUSES
        or root_text("msgType") in _IGNORED_CAP_MSG_TYPES
    ):
        return None

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
        parsed = dt_util.parse_datetime(raw) if raw else None
        if parsed is not None and parsed.tzinfo is None:
            # Senders occasionally omit the UTC offset; assume UTC rather than
            # crash on naive/aware comparisons later.
            parsed = parsed.replace(tzinfo=UTC)
        return parsed

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

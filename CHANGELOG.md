# Changelog

## 1.1.0

### Fixed
- A failed or invalid warning document no longer looks like "no warnings"; entities become unavailable instead.
- Ambiguous region names (e.g. `Riga` vs `Gulf of Riga East/West`) are no longer matched to another area.
- Timestamps without a UTC offset no longer break updates.
- Test, exercise, draft and cancel messages are ignored.
- Card: wrong or unavailable entities no longer read as "No active warnings".

### Added
- Reconfigure flow to change country/region of an entry.
- Warnings disappear exactly when they end, not at the next poll.
- Download cache shared between entries; documents load in parallel.
- Region dropdown remembers regions seen in earlier polls.
- Repairs issue when a country's feed disappears (HTTP 404).
- Card: long texts collapse behind "Show details", times follow the user's HA time zone and 12/24h setting, grid options for sections dashboards.
- Brand icon, CI for Python 3.13/3.14, card tests, ruff, dependabot.

### Changed
- Minimum Home Assistant version is 2026.2.0 (tested range).
- Large alert texts are excluded from recorder history.

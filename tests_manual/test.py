"""Manual smoke test against the live meteoalarm feed.

Run with: python tests_manual/test.py [country] [province] [language]
"""

import asyncio
import sys
from pathlib import Path

import aiohttp

sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.meteoalarm_custom.api import MeteoAlarmApi, async_get_regions


async def main() -> None:
    country = sys.argv[1] if len(sys.argv) > 1 else "latvia"
    province = sys.argv[2] if len(sys.argv) > 2 else "Riga"
    language = sys.argv[3] if len(sys.argv) > 3 else "lv"

    async with aiohttp.ClientSession() as session:
        regions = await async_get_regions(session, country)
        print(f"{len(regions)} regions currently in the {country} feed:")
        for region in regions:
            print(f"  {region.name}" + (f" [{region.geocode}]" if region.geocode else ""))

        api = MeteoAlarmApi(session, country, province, language)
        alerts = await api.get_alerts()
        print(f"\n{len(alerts)} active alert(s) for {province!r} (resolved: {api.resolved_area}):")
        for alert in alerts:
            print(f"  [{alert.severity}] {alert.event} ({alert.onset} - {alert.expires})")
            if alert.description:
                print(f"    {alert.description[:120]}")


if __name__ == "__main__":
    asyncio.run(main())

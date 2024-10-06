from meteoalertapi import Meteoalert
import asyncio

country = "latvia"
province = "LV045"
language = "lv"

async def async_get_meteoalert_data(country, province, language):
    """Asynchronous wrapper for Meteoalert.get_alert()"""
    loop = asyncio.get_running_loop()
    meteoalert = Meteoalert(country, province, language)
    return await loop.run_in_executor(None, meteoalert.get_alert)

async def test():
    data = await async_get_meteoalert_data(country, province, language)
    print(data)

def main():
    asyncio.run(test())

if __name__ == "__main__":
    main()
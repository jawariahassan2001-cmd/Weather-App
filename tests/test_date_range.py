
import asyncio
from datetime import date, timedelta

from app.services.geocoding import geocode
from app.services.weather_service import get_weather_for_date_range


async def main():
    location = geocode("Islamabad")[0]

    start_date = date.today() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)

    weather = await get_weather_for_date_range(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=start_date,
        end_date=end_date,
    )

    print("Location:", location["name"])
    print("Weather data:", weather)


if __name__ == "__main__":
    asyncio.run(main())

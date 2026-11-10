import asyncio
from app.services.weather_service import get_weather_by_location
from app.services.geocoding import LocationNotFound, GeocodingError


async def main():
    try:
        result = await get_weather_by_location("Islamabad")

        print("Location:")
        print(result["location"])

        print("\nCurrent Weather:")
        print(result["weather"])

    except (LocationNotFound, GeocodingError, ValueError) as error:
        print("Error:", error)


asyncio.run(main())
import asyncio
from app.services.weather_service import get_current_weather


async def main():
    # Islamabad coordinates
    latitude = 33.7215
    longitude = 73.0433

    try:
        weather = await get_current_weather(latitude, longitude)

        print("Weather API connection successful!")
        print("\nCurrent Weather:")
        print(weather["current"])

    except Exception as error:
        print("Something went wrong:", error)


asyncio.run(main())

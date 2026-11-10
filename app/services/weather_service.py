
import httpx
from datetime import date

from app.services.location_service import resolve_locations


WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


async def get_current_weather(latitude: float, longitude: float):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "wind_speed_10m",
            "weather_code",
        ],
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            WEATHER_API_URL,
            params=params,
        )

        response.raise_for_status()

        return response.json()


async def get_weather_by_location(
    location: str,
    country: str | None = None,
):
    locations = resolve_locations(location, country)
    selected_location = locations[0]

    weather = await get_current_weather(
        latitude=selected_location["latitude"],
        longitude=selected_location["longitude"],
    )

    return {
        "location": selected_location,
        "weather": weather["current"],
    }


async def get_weather_for_date_range(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
):
    today = date.today()

    # Reject date ranges that cross between past and future.
    if start_date < today <= end_date:
        raise ValueError(
            "Date range cannot cross today's date. "
            "Use either historical dates or current/future dates."
        )

    # Select the correct Open-Meteo API.
    if end_date < today:
        api_url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        api_url = WEATHER_API_URL

        if (end_date - today).days > 15:
            raise ValueError(
                "Forecast dates cannot be more than 16 days ahead."
            )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()

        return response.json()

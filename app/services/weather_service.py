
import asyncio
from datetime import date

import httpx

from app.services.location_service import resolve_locations

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


async def get_current_weather(
    latitude: float,
    longitude: float,
) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "is_day,"
            "precipitation,"
            "rain,"
            "showers,"
            "weather_code,"
            "cloud_cover,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        return response.json()


async def get_weather_by_location(
    location: str,
    country: str | None = None,
) -> dict:
    locations = await asyncio.to_thread(
        resolve_locations,
        location,
        country,
    )

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
) -> dict:
    today = date.today()

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    # Reject ranges that cross from historical data into forecast data.
    if start_date < today <= end_date:
        raise ValueError("Date range cannot cross today's date.")

    if end_date < today:
        api_url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        api_url = WEATHER_API_URL

    if end_date >= today and (end_date - today).days > 15:
        raise ValueError(
            "Forecast dates cannot be more than 16 days ahead."
        )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.json()

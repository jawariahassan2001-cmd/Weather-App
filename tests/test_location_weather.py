
from unittest.mock import AsyncMock, patch

import pytest

from app.services.weather_service import get_weather_by_location


@pytest.mark.asyncio
async def test_get_weather_by_location_returns_location_and_weather():
    mock_locations = [
        {
            "name": "Islamabad",
            "country": "Pakistan",
            "latitude": 33.7215,
            "longitude": 73.0433,
        }
    ]

    mock_weather = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 45,
            "wind_speed_10m": 12.5,
        }
    }

    with (
        patch(
            "app.services.weather_service.resolve_locations",
            return_value=mock_locations,
        ) as mock_resolve,
        patch(
            "app.services.weather_service.get_current_weather",
            new_callable=AsyncMock,
            return_value=mock_weather,
        ) as mock_get_weather,
    ):
        result = await get_weather_by_location(
            location="Islamabad",
            country="Pakistan",
        )

        assert result["location"] == mock_locations[0]
        assert result["weather"] == mock_weather["current"]

        mock_resolve.assert_called_once_with("Islamabad", "Pakistan")

        mock_get_weather.assert_awaited_once_with(
            latitude=33.7215,
            longitude=73.0433,
        )


@pytest.mark.asyncio
async def test_get_weather_by_location_uses_first_matching_location():
    mock_locations = [
        {
            "name": "Islamabad",
            "country": "Pakistan",
            "latitude": 33.7215,
            "longitude": 73.0433,
        },
        {
            "name": "Islamabad",
            "country": "India",
            "latitude": 28.6139,
            "longitude": 77.2090,
        },
    ]

    mock_weather = {
        "current": {
            "temperature_2m": 25.0,
        }
    }

    with (
        patch(
            "app.services.weather_service.resolve_locations",
            return_value=mock_locations,
        ),
        patch(
            "app.services.weather_service.get_current_weather",
            new_callable=AsyncMock,
            return_value=mock_weather,
        ) as mock_get_weather,
    ):
        result = await get_weather_by_location("Islamabad")

        assert result["location"] == mock_locations[0]

        mock_get_weather.assert_awaited_once_with(
            latitude=33.7215,
            longitude=73.0433,
        )

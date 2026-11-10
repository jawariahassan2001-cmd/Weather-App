
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.weather_service import (
    WEATHER_API_URL,
    get_current_weather,
)


@pytest.mark.asyncio
async def test_get_current_weather_returns_api_data():
    mock_weather_data = {
        "latitude": 33.7215,
        "longitude": 73.0433,
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 45,
            "apparent_temperature": 26.0,
            "is_day": 1,
            "precipitation": 0.0,
            "wind_speed_10m": 12.5,
            "weather_code": 1,
        },
    }

    mock_response = MagicMock()
    mock_response.json.return_value = mock_weather_data
    mock_response.raise_for_status.return_value = None

    with patch(
        "app.services.weather_service.httpx.AsyncClient"
    ) as mock_client:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await get_current_weather(
            latitude=33.7215,
            longitude=73.0433,
        )

        assert result == mock_weather_data

        mock_get = (
            mock_client.return_value.__aenter__.return_value.get
        )

        mock_get.assert_awaited_once()

        assert mock_get.call_args.args[0] == WEATHER_API_URL

        params = mock_get.call_args.kwargs["params"]

        assert params["latitude"] == 33.7215
        assert params["longitude"] == 73.0433
        assert params["timezone"] == "auto"

        assert "temperature_2m" in params["current"]
        assert "relative_humidity_2m" in params["current"]
        assert "apparent_temperature" in params["current"]
        assert "wind_speed_10m" in params["current"]
        assert "weather_code" in params["current"]


@pytest.mark.asyncio
async def test_get_current_weather_raises_http_error():
    mock_response = MagicMock()

    http_error = httpx.HTTPStatusError(
        "Service unavailable",
        request=httpx.Request("GET", WEATHER_API_URL),
        response=httpx.Response(503),
    )

    mock_response.raise_for_status.side_effect = http_error

    with patch(
        "app.services.weather_service.httpx.AsyncClient"
    ) as mock_client:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        with pytest.raises(httpx.HTTPStatusError):
            await get_current_weather(
                latitude=33.7215,
                longitude=73.0433,
            )


@pytest.mark.asyncio
async def test_get_current_weather_handles_timeout():
    with patch(
        "app.services.weather_service.httpx.AsyncClient"
    ) as mock_client:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        with pytest.raises(httpx.TimeoutException):
            await get_current_weather(
                latitude=33.7215,
                longitude=73.0433,
            )


@pytest.mark.asyncio
async def test_get_current_weather_handles_connection_error():
    with patch(
        "app.services.weather_service.httpx.AsyncClient"
    ) as mock_client:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        with pytest.raises(httpx.ConnectError):
            await get_current_weather(
                latitude=33.7215,
                longitude=73.0433,
            )

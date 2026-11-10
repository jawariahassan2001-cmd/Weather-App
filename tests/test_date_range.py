
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.weather_service import get_weather_for_date_range


@pytest.mark.asyncio
async def test_historical_dates_use_archive_api():
    today = date.today()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "daily": {"temperature_2m_max": [25]}
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "app.services.weather_service.httpx.AsyncClient"
    ) as mock_client:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await get_weather_for_date_range(
            latitude=33.7215,
            longitude=73.0433,
            start_date=today - timedelta(days=3),
            end_date=today - timedelta(days=1),
        )

        assert result == mock_response.json.return_value

        requested_url = (
            mock_client.return_value.__aenter__.return_value.get.call_args.args[0]
        )

        assert requested_url == (
            "https://archive-api.open-meteo.com/v1/archive"
        )


@pytest.mark.asyncio
async def test_future_dates_use_forecast_api():
    today = date.today()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "daily": {"temperature_2m_max": [25]}
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "app.services.weather_service.httpx.AsyncClient"
    ) as mock_client:

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await get_weather_for_date_range(
            latitude=33.7215,
            longitude=73.0433,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=2),
        )

        assert result == mock_response.json.return_value

        requested_url = (
            mock_client.return_value.__aenter__.return_value.get.call_args.args[0]
        )

        assert requested_url == (
            "https://api.open-meteo.com/v1/forecast"
        )


@pytest.mark.asyncio
async def test_date_range_crossing_today_is_rejected():
    today = date.today()

    with pytest.raises(
        ValueError,
        match="cannot cross today's date",
    ):
        await get_weather_for_date_range(
            latitude=33.7215,
            longitude=73.0433,
            start_date=today - timedelta(days=1),
            end_date=today,
        )


@pytest.mark.asyncio
async def test_forecast_beyond_supported_range_is_rejected():
    today = date.today()

    with pytest.raises(
        ValueError,
        match="more than 16 days ahead",
    ):
        await get_weather_for_date_range(
            latitude=33.7215,
            longitude=73.0433,
            start_date=today + timedelta(days=16),
            end_date=today + timedelta(days=16),
        )


from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.geocoding import GeocodingError, LocationNotFound
from app.services.nominatim_service import (
    HEADERS,
    NOMINATIM_URL,
    search_nominatim,
)


@pytest.fixture(autouse=True)
def disable_rate_limit(monkeypatch):
    """Prevent tests from waiting for the real Nominatim rate limiter."""
    monkeypatch.setattr(
        "app.services.nominatim_service.time.sleep",
        lambda seconds: None,
    )
    monkeypatch.setattr(
        "app.services.nominatim_service._last_request_time",
        0.0,
    )


def test_search_nominatim_returns_location():
    mock_data = [
        {
            "name": "Faisal Mosque",
            "display_name": "Faisal Mosque, Islamabad, Pakistan",
            "lat": "33.7294",
            "lon": "73.0372",
            "address": {
                "state": "Islamabad Capital Territory",
                "country": "Pakistan",
            },
        }
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = mock_data

    with patch(
        "app.services.nominatim_service.httpx.get",
        return_value=mock_response,
    ) as mock_get:

        result = search_nominatim("Faisal Mosque")

        assert result == [
            {
                "name": "Faisal Mosque",
                "region": "Islamabad Capital Territory",
                "country": "Pakistan",
                "latitude": 33.7294,
                "longitude": 73.0372,
            }
        ]

        mock_get.assert_called_once()

        assert mock_get.call_args.args[0] == NOMINATIM_URL
        assert mock_get.call_args.kwargs["headers"] == HEADERS


def test_search_nominatim_adds_country_to_query():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "name": "Islamabad",
            "lat": "33.7215",
            "lon": "73.0433",
            "address": {
                "country": "Pakistan",
            },
        }
    ]

    with patch(
        "app.services.nominatim_service.httpx.get",
        return_value=mock_response,
    ) as mock_get:

        search_nominatim("Islamabad", country="Pakistan")

        params = mock_get.call_args.kwargs["params"]

        assert params["q"] == "Islamabad, Pakistan"
        assert params["format"] == "jsonv2"
        assert params["limit"] == 5


def test_search_nominatim_rejects_empty_query():
    with pytest.raises(ValueError, match="Location cannot be empty"):
        search_nominatim("   ")


def test_search_nominatim_raises_location_not_found():
    mock_response = MagicMock()
    mock_response.json.return_value = []

    with patch(
        "app.services.nominatim_service.httpx.get",
        return_value=mock_response,
    ), pytest.raises(LocationNotFound):
        search_nominatim("Unknown Place")


def test_search_nominatim_handles_timeout():
    with patch(
        "app.services.nominatim_service.httpx.get",
        side_effect=httpx.TimeoutException("Request timed out"),
    ), pytest.raises(GeocodingError, match="too long to respond"):
        search_nominatim("Islamabad")


def test_search_nominatim_handles_http_error():
    mock_response = MagicMock()
    mock_response.status_code = 503

    http_error = httpx.HTTPStatusError(
        "Service unavailable",
        request=httpx.Request("GET", NOMINATIM_URL),
        response=httpx.Response(503),
    )

    mock_response.raise_for_status.side_effect = http_error

    with patch(
        "app.services.nominatim_service.httpx.get",
        return_value=mock_response,
    ), pytest.raises(GeocodingError, match="503"):
        search_nominatim("Islamabad")


def test_search_nominatim_handles_connection_error():
    with patch(
        "app.services.nominatim_service.httpx.get",
        side_effect=httpx.ConnectError("Connection failed"),
    ), pytest.raises(GeocodingError, match="Could not connect"):
        search_nominatim("Islamabad")


def test_search_nominatim_skips_incomplete_results():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "name": "Incomplete Location",
            "lat": "invalid",
            "lon": "73.0433",
            "address": {},
        },
        {
            "name": "Islamabad",
            "lat": "33.7215",
            "lon": "73.0433",
            "address": {
                "country": "Pakistan",
            },
        },
    ]

    with patch(
        "app.services.nominatim_service.httpx.get",
        return_value=mock_response,
    ):
        result = search_nominatim("Islamabad")

        assert len(result) == 1
        assert result[0]["name"] == "Islamabad"
        assert result[0]["latitude"] == 33.7215


def test_search_nominatim_raises_error_when_all_results_are_incomplete():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "name": "Incomplete Location",
            "lat": "invalid",
            "lon": "73.0433",
            "address": {},
        }
    ]

    with patch(
        "app.services.nominatim_service.httpx.get",
        return_value=mock_response,
    ), pytest.raises(
        GeocodingError,
        match="incomplete information",
    ):
        search_nominatim("Unknown Location")

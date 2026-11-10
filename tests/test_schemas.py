
import pytest
from pydantic import ValidationError

from app.schemas.weather import WeatherCreate, WeatherUpdate


def test_valid_weather_create():
    data = WeatherCreate(
        location="Islamabad",
        start_date="2026-11-09",
        end_date="2026-11-12",
    )

    assert data.location == "Islamabad"
    assert data.start_date.isoformat() == "2026-11-09"
    assert data.end_date.isoformat() == "2026-11-12"


def test_weather_create_rejects_end_date_before_start_date():
    with pytest.raises(ValidationError):
        WeatherCreate(
            location="Islamabad",
            start_date="2026-11-12",
            end_date="2026-11-09",
        )


def test_weather_create_rejects_location_shorter_than_two_characters():
    with pytest.raises(ValidationError):
        WeatherCreate(
            location="A",
            start_date="2026-11-09",
            end_date="2026-11-12",
        )


def test_valid_weather_update():
    data = WeatherUpdate(
        location="Lahore",
        start_date="2026-11-09",
        end_date="2026-11-12",
    )

    assert data.location == "Lahore"
    assert data.start_date.isoformat() == "2026-11-09"
    assert data.end_date.isoformat() == "2026-11-12"


def test_weather_update_rejects_end_date_before_start_date():
    with pytest.raises(ValidationError):
        WeatherUpdate(
            location="Lahore",
            start_date="2026-11-12",
            end_date="2026-11-09",
        )

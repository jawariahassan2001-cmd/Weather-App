from app.schemas.weather import WeatherCreate
from pydantic import ValidationError

# Test 1: Valid input
try:
    data = WeatherCreate(
        location="Islamabad",
        start_date="2026-11-09",
        end_date="2026-11-12"
    )
    print("Valid input:", data)

except ValidationError as e:
    print("Validation failed:", e)


# Test 2: Invalid date range
try:
    data = WeatherCreate(
        location="Islamabad",
        start_date="2026-11-12",
        end_date="2026-11-09"
    )
    print("Unexpected success:", data)

except ValidationError as e:
    print("\nInvalid date range correctly rejected.")
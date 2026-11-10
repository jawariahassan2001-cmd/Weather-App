
import threading
import time

import httpx

from app.services.geocoding import GeocodingError, LocationNotFound

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "WeatherIntelligencePlatform/1.0"
}

# Control request frequency to respect Nominatim's public usage policy.
_request_lock = threading.Lock()
_last_request_time = 0.0


def search_nominatim(
    query: str,
    country: str | None = None
) -> list[dict]:

    global _last_request_time

    query = (query or "").strip()

    if not query:
        raise ValueError("Location cannot be empty.")

    # Add country information to narrow down the search.
    search_query = query

    if country:
        search_query = f"{query}, {country.strip()}"

    try:
        # Ensure requests are spaced at least one second apart.
        with _request_lock:
            elapsed = time.monotonic() - _last_request_time

            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)

            response = httpx.get(
                NOMINATIM_URL,
                params={
                    "q": search_query,
                    "format": "jsonv2",
                    "addressdetails": 1,
                    "limit": 5,
                    "accept-language": "en",
                },
                headers=HEADERS,
                timeout=10.0,
            )

            _last_request_time = time.monotonic()

        response.raise_for_status()
        data = response.json()

    except httpx.TimeoutException:
        raise GeocodingError(
            "The location service took too long to respond."
        )

    except httpx.HTTPStatusError as error:
        raise GeocodingError(
            f"The location service returned an error: "
            f"{error.response.status_code}"
        )

    except httpx.RequestError:
        raise GeocodingError(
            "Could not connect to the location service."
        )

    except ValueError:
        raise GeocodingError(
            "The location service returned an invalid response."
        )

    # Check whether any results were returned.
    if not data:
        raise LocationNotFound(
            f"No location found for '{query}'."
        )

    locations = []

    # Extract the required location information.
    for place in data:
        try:
            address = place.get("address", {})

            locations.append({
                "name": (
                    place.get("name")
                    or place.get("display_name", "").split(",")[0]
                ),
                "region": (
                    address.get("state")
                    or address.get("county")
                ),
                "country": address.get("country"),
                "latitude": float(place["lat"]),
                "longitude": float(place["lon"]),
            })

        except (KeyError, TypeError, ValueError):
            # Skip incomplete results.
            continue

    if not locations:
        raise GeocodingError(
            "The location service returned incomplete information."
        )

    return locations

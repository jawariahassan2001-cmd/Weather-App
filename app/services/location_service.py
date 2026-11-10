import re

from app.services.geocoding import (
    LocationNotFound,
    geocode,
)
from app.services.nominatim_service import search_nominatim


def resolve_locations(
    query: str,
    country: str | None = None,
) -> list[dict]:

    query = (query or "").strip()

    if not query:
        raise ValueError("Location cannot be empty.")

    # 1. GPS coordinates
    if "," in query:
        return geocode(query)

    # 2. Postal codes
    if re.fullmatch(r"\d{3,10}", query):
        return search_nominatim(query, country)

    # 3. Try Open-Meteo for cities and towns
    try:
        locations = geocode(query)

        # Narrow results by country when the user supplies one.
        if country:
            matching_locations = [
                location
                for location in locations
                if (location.get("country") or "").casefold()
                == country.strip().casefold()
            ]

            if matching_locations:
                return matching_locations

            # No matching country from Open-Meteo:
            # try Nominatim instead.
            return search_nominatim(query, country)

        return locations

    except LocationNotFound:
        # 4. Try Nominatim for landmarks and other places.
        return search_nominatim(query, country)
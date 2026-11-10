
import httpx

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


class LocationNotFound(Exception):
    """Raised when no matching location is found."""


class GeocodingError(Exception):
    """Raised when something goes wrong while contacting the API."""


def geocode(query: str) -> list[dict]:
    # Clean up the location entered by the user.
    query = (query or "").strip()

    if not query:
        raise ValueError("Location cannot be empty.")
    # Check whether the user entered GPS coordinates.
    parts = query.split(",")

    if len(parts) == 2:
        try:
            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())

            if not -90 <= latitude <= 90:
                raise ValueError("Latitude must be between -90 and 90.")

            if not -180 <= longitude <= 180:
                raise ValueError("Longitude must be between -180 and 180.")

            return [{
                "name": f"{latitude}, {longitude}",
                "region": None,
                "country": None,
                "latitude": latitude,
                "longitude": longitude,
            }]

        except ValueError as error:
            if "Latitude must" in str(error) or "Longitude must" in str(error):
                raise
    try:
        # Ask Open-Meteo for matching locations.
        response = httpx.get(
            GEOCODE_URL,
            params={
                "name": query,
                "count": 5,
                "language": "en",
                "format": "json",
            },
            timeout=5.0,
        )

        response.raise_for_status()
        data = response.json()

    except httpx.TimeoutException:
        raise GeocodingError(
            "The geocoding service took too long to respond. Please try again."
        )

    except httpx.HTTPStatusError as e:
        raise GeocodingError(
            f"The geocoding service returned an error: {e.response.status_code}"
        )

    except httpx.RequestError:
        raise GeocodingError(
            "Could not connect to the geocoding service. Check your internet connection."
        )

    except ValueError:
        raise GeocodingError(
            "The geocoding service returned an invalid response."
        )

    # The API may return no results if the location doesn't exist.
    results = data.get("results")

    if not results:
        raise LocationNotFound(f"No location found for '{query}'.")

    # Return only the information our weather service needs.
    locations = []

    for place in results:
        try:
            locations.append({
                "name": place["name"],
                "region": place.get("admin1"),
                "country": place.get("country"),
                "latitude": place["latitude"],
                "longitude": place["longitude"],
            })
        except (KeyError, TypeError):
            # Skip incomplete results instead of crashing the application.
            continue

    if not locations:
        raise GeocodingError(
            "The geocoding service returned incomplete location information."
        )

    return locations


if __name__ == "__main__":
    # A few test cases to check how the function behaves.
    test_locations = [
    "Islamabad",
    "London",
    "asdfghjkl",
    "",
    "33.6844, 73.0479",
    "44000",
    "Faisal Mosque",
]

    for location in test_locations:
        try:
            print(f"\nSearching for: {location}")
            results = geocode(location)

            for place in results:
                print(place)

        except (LocationNotFound, GeocodingError, ValueError) as error:
            print("Error:", error)

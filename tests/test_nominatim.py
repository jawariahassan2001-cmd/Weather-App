import time
import threading

from app.services.nominatim_service import search_nominatim

_request_lock = threading.Lock()
_last_request_time = 0.0

test_locations = [
    ("Faisal Mosque", "Pakistan"),
    ("44000", "Pakistan"),
]

for query, country in test_locations:
    try:
        print(f"\nSearching: {query}, {country}")

        results = search_nominatim(query, country)

        for location in results:
            print(location)

    except Exception as error:
        print("Error:", error)
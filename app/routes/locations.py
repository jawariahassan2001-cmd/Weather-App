from fastapi import APIRouter, HTTPException, Query

from app.services.geocoding import GeocodingError, LocationNotFound
from app.services.location_service import resolve_locations

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"],
)


@router.get("/search")
def search_locations(
    query: str = Query(..., min_length=2, max_length=150),
    country: str | None = Query(None, max_length=100),
):
    try:
        locations = resolve_locations(query, country)

        return {
            "query": query,
            "total_results": len(locations),
            "locations": locations,
        }

    except LocationNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except GeocodingError as error:
        raise HTTPException(status_code=502, detail=str(error))
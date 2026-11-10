
import httpx

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.weather import (
    WeatherCreate,
    WeatherUpdate,
    WeatherResponse,
)

from app.services.geocoding import (
    LocationNotFound,
    GeocodingError,
)

from app.services.location_service import resolve_locations

from app.services.weather_service import (
    get_weather_by_location,
    get_weather_for_date_range,
)

from app.services.weather_repository import (
    create_weather_record,
    get_all_weather_records,
    get_weather_record_by_id,
    update_weather_record,
    delete_weather_record,
)


router = APIRouter(
    prefix="/api/weather",
    tags=["Weather"],
)


# CURRENT WEATHER
@router.get("/current")
async def current_weather(
    location: str = Query(..., min_length=2, max_length=150),
    country: str | None = Query(None, max_length=100),
):
    try:
        return await get_weather_by_location(location, country)

    except LocationNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except GeocodingError as error:
        raise HTTPException(status_code=502, detail=str(error))

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Weather service timed out.",
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Weather service returned an error.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the weather service.",
        )


# CREATE WEATHER RECORD
@router.post("/", response_model=WeatherResponse, status_code=201)
async def create_weather(
    request: WeatherCreate,
    db: Session = Depends(get_db),
):
    try:
        locations = resolve_locations(
            request.location,
            request.country,
        )
        selected_location = locations[0]

        weather_data = await get_weather_for_date_range(
            latitude=selected_location["latitude"],
            longitude=selected_location["longitude"],
            start_date=request.start_date,
            end_date=request.end_date,
        )

        record = create_weather_record(
            db=db,
            location=selected_location,
            start_date=request.start_date,
            end_date=request.end_date,
            weather_data=weather_data,
        )

        return record

    except LocationNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except GeocodingError as error:
        raise HTTPException(status_code=502, detail=str(error))

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Weather service timed out.",
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Weather service returned an error.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the weather service.",
        )


# READ ALL WEATHER RECORDS
@router.get("/", response_model=list[WeatherResponse])
def get_all_weather(
    db: Session = Depends(get_db),
):
    return get_all_weather_records(db)


# READ ONE WEATHER RECORD
@router.get("/{record_id}", response_model=WeatherResponse)
def get_weather_by_id(
    record_id: int,
    db: Session = Depends(get_db),
):
    record = get_weather_record_by_id(db, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Weather record with ID {record_id} not found.",
        )

    return record


# UPDATE WEATHER RECORD
@router.put("/{record_id}", response_model=WeatherResponse)
async def update_weather(
    record_id: int,
    request: WeatherUpdate,
    db: Session = Depends(get_db),
):
    record = get_weather_record_by_id(db, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Weather record with ID {record_id} not found.",
        )

    try:
        locations = resolve_locations(
            request.location,
            request.country,
        )
        selected_location = locations[0]

        weather_data = await get_weather_for_date_range(
            latitude=selected_location["latitude"],
            longitude=selected_location["longitude"],
            start_date=request.start_date,
            end_date=request.end_date,
        )

        updated_record = update_weather_record(
            db=db,
            record=record,
            location=selected_location,
            start_date=request.start_date,
            end_date=request.end_date,
            weather_data=weather_data,
        )

        return updated_record

    except LocationNotFound as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except GeocodingError as error:
        raise HTTPException(status_code=502, detail=str(error))

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Weather service timed out.",
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Weather service returned an error.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the weather service.",
        )


# DELETE WEATHER RECORD
@router.delete("/{record_id}")
def delete_weather(
    record_id: int,
    db: Session = Depends(get_db),
):
    record = get_weather_record_by_id(db, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Weather record with ID {record_id} not found.",
        )

    delete_weather_record(db, record)

    return {
        "message": f"Weather record with ID {record_id} deleted successfully."
    }

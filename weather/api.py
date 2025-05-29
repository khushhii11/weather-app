# weather/api.py

import re
import logging
from typing import Tuple, List, Dict

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from weather.geocode import geocode
from weather.weather_app import fetch_current, fetch_5day
from weather import crud, schemas
from weather.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["weather"],
)


def parse_input(user_input: str) -> Tuple[float, float]:
    """
    If input is "lat,lon", parse and return floats.
    Otherwise, treat it as an address and geocode it.
    """
    coords = re.match(
        r"\s*([-+]?\d+(\.\d+)?)\s*,\s*([-+]?\d+(\.\d+)?)\s*$",
        user_input
    )
    if coords:
        lat = float(coords.group(1))
        lon = float(coords.group(3))
        # Validate ranges
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Coordinates out of range: {lat}, {lon}")
        return lat, lon

    return geocode(user_input)


@router.get("/", summary="Health check")
async def read_root() -> Dict[str, str]:
    return {"message": "Weather API is up. Try /weather?loc=... or /forecast?loc=..."}


@router.get(
    "/weather",
    summary="Current weather",
    description="Get current weather by location (lat,lon) or address.",
)
async def current(
    loc: str = Query(
        ..., 
        min_length=1, 
        description="Location as 'lat,lon' or free-form address for geocoding"
    )
) -> Dict:
    logger.debug("Request for current weather at loc=%s", loc)

    try:
        lat, lon = parse_input(loc)
    except ValueError as e:
        logger.warning("Invalid location input '%s': %s", loc, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    try:
        current_data = fetch_current(lat, lon)
    except ConnectionError as e:
        logger.error("Weather service error for %s: %s", loc, e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error fetching current weather: {e}"
        )

    return {
        "latitude": lat,
        "longitude": lon,
        "current": current_data
    }


@router.get(
    "/forecast",
    summary="5-day forecast",
    description="Get a 5-day weather forecast by location (lat,lon) or address.",
)
async def forecast(
    loc: str = Query(
        ...,
        min_length=1,
        description="Location as 'lat,lon' or free-form address for geocoding"
    )
) -> Dict:
    logger.debug("Request for 5-day forecast at loc=%s", loc)

    try:
        lat, lon = parse_input(loc)
    except ValueError as e:
        logger.warning("Invalid location input '%s': %s", loc, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    try:
        forecast_data = fetch_5day(lat, lon)
    except ConnectionError as e:
        logger.error("Forecast service error for %s: %s", loc, e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error fetching 5-day forecast: {e}"
        )

    return {
        "latitude": lat,
        "longitude": lon,
        "forecast": forecast_data
    }


@router.post(
    "/locations/",
    response_model=schemas.Location,
    status_code=status.HTTP_201_CREATED,
    summary="Create a saved location",
)
def create_loc(
    loc: schemas.LocationCreate,
    db: Session = Depends(get_db)
) -> schemas.Location:
    return crud.create_location(db, loc)


@router.get(
    "/locations/",
    response_model=List[schemas.Location],
    summary="List saved locations",
)
def read_locations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: Session = Depends(get_db)
) -> List[schemas.Location]:
    return crud.get_locations(db, skip, limit)


@router.get(
    "/locations/{loc_id}",
    response_model=schemas.Location,
    summary="Get a saved location by ID",
)
def read_location(
    loc_id: int,
    db: Session = Depends(get_db)
) -> schemas.Location:
    db_loc = crud.get_location(db, loc_id)
    if db_loc is None:
        logger.info("Location id %d not found", loc_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return db_loc


@router.put(
    "/locations/{loc_id}",
    response_model=schemas.Location,
    summary="Update a saved location",
)
def update_loc(
    loc_id: int,
    loc: schemas.LocationUpdate,
    db: Session = Depends(get_db)
) -> schemas.Location:
    updated = crud.update_location(db, loc_id, loc)
    if updated is None:
        logger.info("Failed update; location id %d not found", loc_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return updated


@router.delete(
    "/locations/{loc_id}",
    response_model=schemas.Location,
    summary="Delete a saved location",
)
def delete_loc(
    loc_id: int,
    db: Session = Depends(get_db)
) -> schemas.Location:
    deleted = crud.delete_location(db, loc_id)
    if deleted is None:
        logger.info("Failed delete; location id %d not found", loc_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return deleted

from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from app.core.exceptions import FlightProviderError
from app.schemas.flight import (
    CabinClass,
    FlightSearchResponse,
)
from app.services.flight_service import search_flights


router = APIRouter(
    prefix="/flights",
    tags=["flights"],
)


AirportQuery = Annotated[
    str,
    Query(
        min_length=3,
        max_length=3,
        description="IATA airport code",
        examples=["MAD"],
    ),
]


AdultsQuery = Annotated[
    int,
    Query(
        ge=1,
        le=9,
        description="Number of adult passengers",
    ),
]


@router.get(
    "/search",
    response_model=FlightSearchResponse,
    summary="Search flights",
)
def get_flights(
    origin: AirportQuery,
    destination: AirportQuery,
    departure_date: date,
    return_date: date | None = None,
    adults: AdultsQuery = 1,
    cabin_class: CabinClass = CabinClass.ECONOMY,
) -> FlightSearchResponse:
    if origin.strip().upper() == destination.strip().upper():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Origin and destination "
                "must be different"
            ),
        )

    if departure_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Departure date cannot "
                "be in the past"
            ),
        )

    if (
        return_date is not None
        and return_date < departure_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Return date cannot be "
                "before departure date"
            ),
        )

    try:
        return search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            cabin_class=cabin_class,
        )

    except FlightProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Flight search service is "
                "temporarily unavailable"
            ),
        ) from exc
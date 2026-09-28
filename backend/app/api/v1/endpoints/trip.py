from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    CurrencyProviderError,
    InvalidTripDatesError,
    TripNotCompletedError,
    TripNotFoundError,
    UnsupportedCurrencyError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.trip import (
    TripCreate,
    TripRatingUpdate,
    TripResponse,
    TripUpdate,
)
from app.services.trip_service import (
    create_trip,
    delete_user_trip,
    get_user_trip_by_id,
    get_user_trips,
    update_trip,
    update_trip_rating,
)


router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[TripResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all trips for the current user",
)
def get_all_user_trips(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[TripResponse]:
    return get_user_trips(
        db=db,
        user=current_user,
    )


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific trip by ID for the current user",
)
def get_trip_by_id(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return get_user_trip_by_id(
            db=db,
            user=current_user,
            trip_id=trip_id,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip",
)
def create_new_trip(
    trip_data: TripCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return create_trip(
            db=db,
            user=current_user,
            trip_data=trip_data,
        )

    except UnsupportedCurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported currency code",
        ) from exc

    except CurrencyProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Currency service is temporarily unavailable",
        ) from exc


@router.patch(
    "/{trip_id}",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing trip",
)
def update_existing_trip(
    trip_id: int,
    trip_data: TripUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return update_trip(
            db=db,
            user=current_user,
            trip_id=trip_id,
            trip_data=trip_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except InvalidTripDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The end date cannot be earlier "
                "than the start date"
            ),
        ) from exc

    except UnsupportedCurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported currency code",
        ) from exc

    except CurrencyProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Currency service is temporarily unavailable",
        ) from exc


@router.put(
    "/{trip_id}/rating",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update the rating of a completed trip",
)
def rate_trip(
    trip_id: int,
    rating_data: TripRatingUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return update_trip_rating(
            db=db,
            user=current_user,
            trip_id=trip_id,
            rating=rating_data.rating,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except TripNotCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only completed trips can be rated",
        ) from exc


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trip by ID",
)
def delete_trip(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_user_trip(
            db=db,
            user=current_user,
            trip_id=trip_id,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
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
    AccommodationNotFoundError,
    AccommodationOutsideTripDatesError,
    InvalidAccommodationDatesError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.accommodation import (
    AccommodationCreate,
    AccommodationResponse,
    AccommodationUpdate,
)
from app.services.accommodation_service import (
    add_accommodation_to_trip,
    delete_accommodation_from_trip,
    list_trip_accommodations,
    update_accommodation_in_trip,
)


router = APIRouter(
    prefix="/trips/{trip_id}/accommodations",
    tags=["accommodations"],
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
    response_model=list[AccommodationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all accommodations from a trip",
)
def get_trip_accommodations(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[AccommodationResponse]:
    try:
        return list_trip_accommodations(
            db=db,
            trip_id=trip_id,
            user=current_user,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc


@router.post(
    "",
    response_model=AccommodationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an accommodation to a trip",
)
def add_new_accommodation(
    trip_id: int,
    accommodation_data: AccommodationCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> AccommodationResponse:
    try:
        return add_accommodation_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            accommodation_data=accommodation_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except InvalidAccommodationDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The accommodation dates and times "
                "are not chronologically valid"
            ),
        ) from exc

    except AccommodationOutsideTripDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The accommodation check-in and check-out "
                "must be within the trip dates"
            ),
        ) from exc


@router.patch(
    "/{accommodation_id}",
    response_model=AccommodationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an accommodation from a trip",
)
def update_existing_accommodation(
    trip_id: int,
    accommodation_id: int,
    accommodation_data: AccommodationUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> AccommodationResponse:
    try:
        return update_accommodation_in_trip(
            db=db,
            trip_id=trip_id,
            accommodation_id=accommodation_id,
            user=current_user,
            accommodation_data=accommodation_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except AccommodationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation not found",
        ) from exc

    except InvalidAccommodationDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The accommodation dates and times "
                "are not chronologically valid"
            ),
        ) from exc

    except AccommodationOutsideTripDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The accommodation check-in and check-out "
                "must be within the trip dates"
            ),
        ) from exc


@router.delete(
    "/{accommodation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an accommodation from a trip",
)
def delete_existing_accommodation(
    trip_id: int,
    accommodation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_accommodation_from_trip(
            db=db,
            trip_id=trip_id,
            accommodation_id=accommodation_id,
            user=current_user,
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except AccommodationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation not found",
        ) from exc
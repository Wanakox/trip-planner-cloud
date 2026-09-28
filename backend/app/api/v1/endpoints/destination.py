from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    CurrencyProviderError,
    DestinationLimitExceededError,
    DestinationNotFoundError,
    InvalidDestinationOrderError,
    LastDestinationDeletionError,
    TripNotFoundError,
    UnsupportedCurrencyError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.trip import (
    DestinationCreate,
    DestinationUpdate,
    TripResponse,
    DestinationOrderUpdate,
)
from app.services.destination_service import (
    add_destination_to_trip,
    delete_destination_from_trip,
    update_destination_in_trip,
    reorder_trip_destinations,
)


router = APIRouter(
    prefix="/trips/{trip_id}/destinations",
    tags=["destinations"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new destination to a trip",
)
def add_new_destination(
    trip_id: int,
    destination_data: DestinationCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return add_destination_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            destination_data=destination_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except DestinationLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A trip cannot contain more than 20 destinations",
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


@router.patch(
    "/{destination_id}",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a destination in a trip",
)
def update_existing_destination(
    trip_id: int,
    destination_id: int,
    destination_data: DestinationUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return update_destination_in_trip(
            db=db,
            trip_id=trip_id,
            destination_id=destination_id,
            user=current_user,
            destination_data=destination_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except DestinationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found",
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


@router.delete(
    "/{destination_id}",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a destination from a trip",
)
def delete_existing_destination(
    trip_id: int,
    destination_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return delete_destination_from_trip(
            db=db,
            trip_id=trip_id,
            destination_id=destination_id,
            user=current_user,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except DestinationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found",
        ) from exc

    except LastDestinationDeletionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A trip must contain at least one destination",
        ) from exc


@router.put(
    "/order",
    response_model=TripResponse,
    status_code=status.HTTP_200_OK,
    summary="Reorder the destinations of a trip",
)
def reorder_destinations(
    trip_id: int,
    order_data: DestinationOrderUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TripResponse:
    try:
        return reorder_trip_destinations(
            db=db,
            trip_id=trip_id,
            user=current_user,
            destination_order_data=order_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except InvalidDestinationOrderError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The destination list must contain exactly "
                "all destinations of the trip"
            ),
        ) from exc
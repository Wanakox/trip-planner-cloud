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
    InvalidTransportDatesError,
    TransportNotFoundError,
    TransportOutsideTripDatesError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.transport import (
    TransportCreate,
    TransportResponse,
    TransportUpdate,
)
from app.services.transport_service import (
    add_transport_to_trip,
    delete_transport_from_trip,
    list_trip_transports,
    update_transport_in_trip,
)


router = APIRouter(
    prefix="/trips/{trip_id}/transports",
    tags=["transports"],
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
    response_model=list[TransportResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all transports from a trip",
)
def get_trip_transports(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[TransportResponse]:
    try:
        return list_trip_transports(
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
    response_model=TransportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a transport to a trip",
)
def add_new_transport(
    trip_id: int,
    transport_data: TransportCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TransportResponse:
    try:
        return add_transport_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            transport_data=transport_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except InvalidTransportDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The transport dates and times "
                "are not chronologically valid"
            ),
        ) from exc

    except TransportOutsideTripDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The transport departure and arrival "
                "must be within the trip dates"
            ),
        ) from exc


@router.patch(
    "/{transport_id}",
    response_model=TransportResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a transport from a trip",
)
def update_existing_transport(
    trip_id: int,
    transport_id: int,
    transport_data: TransportUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TransportResponse:
    try:
        return update_transport_in_trip(
            db=db,
            trip_id=trip_id,
            transport_id=transport_id,
            user=current_user,
            transport_data=transport_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except TransportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transport not found",
        ) from exc

    except InvalidTransportDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The transport dates and times "
                "are not chronologically valid"
            ),
        ) from exc

    except TransportOutsideTripDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The transport departure and arrival "
                "must be within the trip dates"
            ),
        ) from exc


@router.delete(
    "/{transport_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transport from a trip",
)
def delete_existing_transport(
    trip_id: int,
    transport_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_transport_from_trip(
            db=db,
            trip_id=trip_id,
            transport_id=transport_id,
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

    except TransportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transport not found",
        ) from exc
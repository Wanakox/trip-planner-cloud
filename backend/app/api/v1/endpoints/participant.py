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
    ParticipantHasExpensesError,
    ParticipantNotFoundError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantResponse,
    ParticipantUpdate,
)
from app.services.participant_service import (
    add_participant_to_trip,
    delete_participant_from_trip,
    list_trip_participants,
    update_participant_in_trip,
)


router = APIRouter(
    prefix="/trips/{trip_id}/participants",
    tags=["participants"],
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
    response_model=list[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all participants from a trip",
)
def get_trip_participants(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[ParticipantResponse]:
    try:
        return list_trip_participants(
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
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a participant to a trip",
)
def add_new_participant(
    trip_id: int,
    participant_data: ParticipantCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ParticipantResponse:
    try:
        return add_participant_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            participant_data=participant_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc


@router.patch(
    "/{participant_id}",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a participant from a trip",
)
def update_existing_participant(
    trip_id: int,
    participant_id: int,
    participant_data: ParticipantUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ParticipantResponse:
    try:
        return update_participant_in_trip(
            db=db,
            trip_id=trip_id,
            participant_id=participant_id,
            user=current_user,
            participant_data=participant_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except ParticipantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        ) from exc


@router.delete(
    "/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a participant from a trip",
)
def delete_existing_participant(
    trip_id: int,
    participant_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_participant_from_trip(
            db=db,
            trip_id=trip_id,
            participant_id=participant_id,
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

    except ParticipantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        ) from exc

    except ParticipantHasExpensesError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The participant cannot be deleted "
                "because they have associated expenses"
            ),
        ) from exc
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
    InvalidNoteDayError,
    NoteDayAlreadyExistsError,
    NoteLimitExceededError,
    NoteNotFoundError,
    NotesUnavailableError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.note import (
    NoteCreate,
    NoteResponse,
    NoteUpdate,
)
from app.services.note_service import (
    add_note_to_trip,
    delete_note_from_trip,
    get_trip_notes,
    update_note_in_trip,
)


router = APIRouter(
    prefix="/trips/{trip_id}/notes",
    tags=["notes"],
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
    response_model=list[NoteResponse],
    status_code=status.HTTP_200_OK,
    summary="Get the notes from a trip",
)
def get_notes(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[NoteResponse]:
    try:
        return get_trip_notes(
            db=db,
            trip_id=trip_id,
            user=current_user,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except NotesUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Notes are only available for "
                "in-progress or completed trips"
            ),
        ) from exc


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a note to a trip",
)
def add_new_note(
    trip_id: int,
    note_data: NoteCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> NoteResponse:
    try:
        return add_note_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            note_data=note_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except NotesUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Notes can only be added to "
                "in-progress or completed trips"
            ),
        ) from exc

    except InvalidNoteDayError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The note day must have been reached "
                "and be within the trip duration"
            ),
        ) from exc

    except NoteLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The trip has reached the maximum "
                "number of notes"
            ),
        ) from exc

    except NoteDayAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A note already exists "
                "for the specified trip day"
            ),
        ) from exc


@router.patch(
    "/{note_id}",
    response_model=NoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a note from a trip",
)
def update_existing_note(
    trip_id: int,
    note_id: int,
    note_data: NoteUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> NoteResponse:
    try:
        return update_note_in_trip(
            db=db,
            trip_id=trip_id,
            note_id=note_id,
            user=current_user,
            note_data=note_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except NotesUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Notes can only be updated for "
                "in-progress or completed trips"
            ),
        ) from exc

    except NoteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        ) from exc

    except InvalidNoteDayError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The note day must have been reached "
                "and be within the trip duration"
            ),
        ) from exc

    except NoteDayAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A note already exists "
                "for the specified trip day"
            ),
        ) from exc


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note from a trip",
)
def delete_existing_note(
    trip_id: int,
    note_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_note_from_trip(
            db=db,
            trip_id=trip_id,
            note_id=note_id,
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

    except NotesUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Notes can only be deleted from "
                "in-progress or completed trips"
            ),
        ) from exc

    except NoteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        ) from exc

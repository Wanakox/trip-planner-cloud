from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvalidNoteDayError,
    NoteDayAlreadyExistsError,
    NoteLimitExceededError,
    NoteNotFoundError,
    NotesUnavailableError,
    TripNotFoundError,
)
from app.models.note import Note
from app.models.trip import (
    Trip,
    TripStatus,
)
from app.models.user import User
from app.repositories.note_repository import (
    count_notes_by_trip_id,
    create_note,
    delete_note,
    get_note_by_id_and_trip_id,
    get_note_by_trip_id_and_day_number,
    get_notes_by_trip_id,
    get_user_trip,
    update_note,
)
from app.schemas.note import (
    NoteCreate,
    NoteUpdate,
)


def get_trip_or_raise(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip:
    """
    Obtiene un viaje perteneciente al usuario autenticado.
    """

    trip = get_user_trip(
        db=db,
        trip_id=trip_id,
        user_id=user_id,
    )

    if trip is None:
        raise TripNotFoundError

    return trip


def get_note_or_raise(
    db: Session,
    trip_id: int,
    note_id: int,
) -> Note:
    """
    Obtiene una nota perteneciente al viaje indicado.
    """

    note = get_note_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        note_id=note_id,
    )

    if note is None:
        raise NoteNotFoundError

    return note


def get_max_available_note_day(
    trip: Trip,
    current_date: date | None = None,
) -> int:
    """
    Devuelve el último día para el que se puede gestionar
    una nota según el estado y la fecha actual del viaje.
    """

    if trip.status == TripStatus.COMPLETED:
        return trip.total_days

    if trip.status == TripStatus.IN_PROGRESS:
        today = current_date or date.today()
        current_day = (today - trip.start_date).days + 1
        return max(0, min(current_day, trip.total_days))

    raise NotesUnavailableError


def validate_note_day(
    trip: Trip,
    day_number: int,
    max_available_day: int,
) -> None:
    """
    Comprueba que el día indicado pertenece al viaje.
    """

    if day_number > trip.total_days or day_number > max_available_day:
        raise InvalidNoteDayError


def validate_available_note_day(
    db: Session,
    trip_id: int,
    day_number: int | None,
    excluded_note_id: int | None = None,
) -> None:
    """
    Comprueba que no existe otra nota asociada
    al mismo día del viaje.
    """

    if day_number is None:
        return

    existing_note = get_note_by_trip_id_and_day_number(
        db=db,
        trip_id=trip_id,
        day_number=day_number,
    )

    if existing_note is None:
        return

    if (
        excluded_note_id is not None
        and existing_note.id == excluded_note_id
    ):
        return

    raise NoteDayAlreadyExistsError


def get_trip_notes(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Note]:
    """
    Obtiene las notas asociadas a un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    get_max_available_note_day(trip)

    return get_notes_by_trip_id(
        db=db,
        trip_id=trip.id,
    )


def add_note_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    note_data: NoteCreate,
) -> Note:
    """
    Añade una nota a un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    max_available_day = get_max_available_note_day(trip)

    current_note_count = count_notes_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    if current_note_count >= trip.total_days:
        raise NoteLimitExceededError

    validate_note_day(
        trip=trip,
        day_number=note_data.day_number,
        max_available_day=max_available_day,
    )

    validate_available_note_day(
        db=db,
        trip_id=trip.id,
        day_number=note_data.day_number,
    )

    note = Note(
        trip_id=trip.id,
        title=note_data.title,
        text=note_data.text,
        day_number=note_data.day_number,
    )

    return create_note(
        db=db,
        note=note,
    )


def update_note_in_trip(
    db: Session,
    trip_id: int,
    note_id: int,
    user: User,
    note_data: NoteUpdate,
) -> Note:
    """
    Actualiza parcialmente una nota de un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    max_available_day = get_max_available_note_day(trip)

    note = get_note_or_raise(
        db=db,
        trip_id=trip.id,
        note_id=note_id,
    )

    update_data = note_data.model_dump(
        exclude_unset=True,
    )

    if "day_number" in update_data:
        new_day_number = update_data["day_number"]

        validate_note_day(
            trip=trip,
            day_number=new_day_number,
            max_available_day=max_available_day,
        )

        validate_available_note_day(
            db=db,
            trip_id=trip.id,
            day_number=new_day_number,
            excluded_note_id=note.id,
        )

    for field, value in update_data.items():
        setattr(
            note,
            field,
            value,
        )

    return update_note(
        db=db,
        note=note,
    )


def delete_note_from_trip(
    db: Session,
    trip_id: int,
    note_id: int,
    user: User,
) -> None:
    """
    Elimina una nota de un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    get_max_available_note_day(trip)

    note = get_note_or_raise(
        db=db,
        trip_id=trip.id,
        note_id=note_id,
    )

    delete_note(
        db=db,
        note=note,
    )

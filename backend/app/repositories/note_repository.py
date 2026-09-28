from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.trip import Trip


def get_user_trip(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip | None:
    """
    Obtiene un viaje perteneciente al usuario indicado.
    """

    statement = select(Trip).where(
        Trip.id == trip_id,
        Trip.user_id == user_id,
    )

    return db.scalar(statement)


def get_note_by_id_and_trip_id(
    db: Session,
    note_id: int,
    trip_id: int,
) -> Note | None:
    """
    Obtiene una nota perteneciente al viaje indicado.
    """

    statement = select(Note).where(
        Note.id == note_id,
        Note.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_notes_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Note]:
    """
    Obtiene las notas de un viaje ordenadas por día.
    """

    statement = (
        select(Note)
        .where(
            Note.trip_id == trip_id,
        )
        .order_by(
            Note.day_number.asc().nulls_last(),
            Note.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_note_by_trip_id_and_day_number(
    db: Session,
    trip_id: int,
    day_number: int,
) -> Note | None:
    """
    Obtiene la nota asociada a un día concreto del viaje.
    """

    statement = select(Note).where(
        Note.trip_id == trip_id,
        Note.day_number == day_number,
    )

    return db.scalar(statement)


def count_notes_by_trip_id(
    db: Session,
    trip_id: int,
) -> int:
    """
    Cuenta las notas asociadas a un viaje.
    """

    statement = select(
        func.count(Note.id)
    ).where(
        Note.trip_id == trip_id,
    )

    return db.scalar(statement) or 0


def create_note(
    db: Session,
    note: Note,
) -> Note:
    """
    Guarda una nota en la base de datos.
    """

    try:
        db.add(note)
        db.commit()
        db.refresh(note)

        return note

    except Exception:
        db.rollback()
        raise


def update_note(
    db: Session,
    note: Note,
) -> Note:
    """
    Guarda los cambios realizados sobre una nota.
    """

    try:
        db.add(note)
        db.commit()
        db.refresh(note)

        return note

    except Exception:
        db.rollback()
        raise


def delete_note(
    db: Session,
    note: Note,
) -> None:
    """
    Elimina una nota de la base de datos.
    """

    try:
        db.delete(note)
        db.commit()

    except Exception:
        db.rollback()
        raise
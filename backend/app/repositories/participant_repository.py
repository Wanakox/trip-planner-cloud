from sqlalchemy import (
    exists,
    select,
)
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.participant import Participant
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


def get_participant_by_id_and_trip_id(
    db: Session,
    participant_id: int,
    trip_id: int,
) -> Participant | None:
    """
    Obtiene un participante perteneciente al viaje indicado.
    """

    statement = select(Participant).where(
        Participant.id == participant_id,
        Participant.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_participants_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Participant]:
    """
    Obtiene los participantes asociados a un viaje.
    """

    statement = (
        select(Participant)
        .where(
            Participant.trip_id == trip_id,
        )
        .order_by(
            Participant.name.asc(),
            Participant.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def participant_has_expenses(
    db: Session,
    participant_id: int,
) -> bool:
    """
    Comprueba si un participante tiene gastos asociados.
    """

    statement = select(
        exists().where(
            Expense.participant_id == participant_id,
        )
    )

    return bool(
        db.scalar(statement)
    )


def create_participant(
    db: Session,
    participant: Participant,
) -> Participant:
    """
    Guarda un participante en la base de datos.
    """

    try:
        db.add(participant)
        db.commit()
        db.refresh(participant)

        return participant

    except Exception:
        db.rollback()
        raise


def update_participant(
    db: Session,
    participant: Participant,
) -> Participant:
    """
    Guarda los cambios realizados sobre un participante.
    """

    try:
        db.add(participant)
        db.commit()
        db.refresh(participant)

        return participant

    except Exception:
        db.rollback()
        raise


def delete_participant(
    db: Session,
    participant: Participant,
) -> None:
    """
    Elimina un participante de la base de datos.
    """

    try:
        db.delete(participant)
        db.commit()

    except Exception:
        db.rollback()
        raise
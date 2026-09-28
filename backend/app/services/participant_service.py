from sqlalchemy.orm import Session

from app.core.exceptions import (
    ParticipantHasExpensesError,
    ParticipantNotFoundError,
    TripNotFoundError,
)
from app.models.participant import Participant
from app.models.trip import Trip
from app.models.user import User
from app.repositories.participant_repository import (
    create_participant,
    delete_participant,
    get_participant_by_id_and_trip_id,
    get_participants_by_trip_id,
    get_user_trip,
    participant_has_expenses,
    update_participant,
)
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantUpdate,
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


def get_participant_or_raise(
    db: Session,
    trip_id: int,
    participant_id: int,
) -> Participant:
    """
    Obtiene un participante perteneciente al viaje indicado.
    """

    participant = get_participant_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        participant_id=participant_id,
    )

    if participant is None:
        raise ParticipantNotFoundError

    return participant


def list_trip_participants(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Participant]:
    """
    Obtiene todos los participantes de un viaje.
    """

    get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    return get_participants_by_trip_id(
        db=db,
        trip_id=trip_id,
    )


def add_participant_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    participant_data: ParticipantCreate,
) -> Participant:
    """
    Añade un participante a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    participant = Participant(
        trip_id=trip.id,
        name=participant_data.name,
    )

    return create_participant(
        db=db,
        participant=participant,
    )


def update_participant_in_trip(
    db: Session,
    trip_id: int,
    participant_id: int,
    user: User,
    participant_data: ParticipantUpdate,
) -> Participant:
    """
    Actualiza parcialmente un participante.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    participant = get_participant_or_raise(
        db=db,
        trip_id=trip.id,
        participant_id=participant_id,
    )

    update_data = participant_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(
            participant,
            field,
            value,
        )

    return update_participant(
        db=db,
        participant=participant,
    )


def delete_participant_from_trip(
    db: Session,
    trip_id: int,
    participant_id: int,
    user: User,
) -> None:
    """
    Elimina un participante que no tenga gastos asociados.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    participant = get_participant_or_raise(
        db=db,
        trip_id=trip.id,
        participant_id=participant_id,
    )

    if participant_has_expenses(
        db=db,
        participant_id=participant.id,
    ):
        raise ParticipantHasExpensesError

    delete_participant(
        db=db,
        participant=participant,
    )
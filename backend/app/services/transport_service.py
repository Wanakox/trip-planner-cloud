from datetime import date, time

from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvalidTransportDatesError,
    TransportNotFoundError,
    TransportOutsideTripDatesError,
    TripNotFoundError,
)
from app.models.transport import Transport
from app.models.trip import Trip
from app.models.user import User
from app.repositories.transport_repository import (
    create_transport,
    delete_transport,
    get_transport_by_id_and_trip_id,
    get_transports_by_trip_id,
    get_user_trip,
    update_transport,
)
from app.schemas.transport import (
    TransportCreate,
    TransportUpdate,
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


def get_transport_or_raise(
    db: Session,
    trip_id: int,
    transport_id: int,
) -> Transport:
    """
    Obtiene un transporte perteneciente al viaje indicado.
    """

    transport = get_transport_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        transport_id=transport_id,
    )

    if transport is None:
        raise TransportNotFoundError

    return transport


def validate_transport_dates(
    departure_date: date,
    arrival_date: date | None,
    departure_time: time | None,
    arrival_time: time | None,
    check_in_date: date | None,
) -> None:
    """
    Comprueba la coherencia cronológica de las fechas
    y horas del transporte.
    """

    if (
        arrival_date is not None
        and arrival_date < departure_date
    ):
        raise InvalidTransportDatesError

    if (
        arrival_date == departure_date
        and departure_time is not None
        and arrival_time is not None
        and arrival_time < departure_time
    ):
        raise InvalidTransportDatesError

    if (
        check_in_date is not None
        and check_in_date > departure_date
    ):
        raise InvalidTransportDatesError


def validate_transport_within_trip(
    trip: Trip,
    departure_date: date,
    arrival_date: date | None,
) -> None:
    """
    Comprueba que la salida y la llegada se encuentran
    dentro del intervalo temporal del viaje.
    """

    if not (
        trip.start_date
        <= departure_date
        <= trip.end_date
    ):
        raise TransportOutsideTripDatesError

    if arrival_date is None:
        return

    if not (
        trip.start_date
        <= arrival_date
        <= trip.end_date
    ):
        raise TransportOutsideTripDatesError


def list_trip_transports(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Transport]:
    """
    Obtiene todos los transportes de un viaje.
    """

    get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    return get_transports_by_trip_id(
        db=db,
        trip_id=trip_id,
    )


def add_transport_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    transport_data: TransportCreate,
) -> Transport:
    """
    Añade un transporte a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_transport_dates(
        departure_date=transport_data.departure_date,
        arrival_date=transport_data.arrival_date,
        departure_time=transport_data.departure_time,
        arrival_time=transport_data.arrival_time,
        check_in_date=transport_data.check_in_date,
    )

    validate_transport_within_trip(
        trip=trip,
        departure_date=transport_data.departure_date,
        arrival_date=transport_data.arrival_date,
    )

    transport = Transport(
        trip_id=trip.id,
        transport_type=transport_data.transport_type,
        price=transport_data.price,
        departure_date=transport_data.departure_date,
        arrival_date=transport_data.arrival_date,
        departure_time=transport_data.departure_time,
        arrival_time=transport_data.arrival_time,
        origin=transport_data.origin,
        destination=transport_data.destination,
        check_in_date=transport_data.check_in_date,
    )

    return create_transport(
        db=db,
        transport=transport,
    )


def update_transport_in_trip(
    db: Session,
    trip_id: int,
    transport_id: int,
    user: User,
    transport_data: TransportUpdate,
) -> Transport:
    """
    Actualiza parcialmente un transporte.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    transport = get_transport_or_raise(
        db=db,
        trip_id=trip.id,
        transport_id=transport_id,
    )

    update_data = transport_data.model_dump(
        exclude_unset=True,
    )

    final_departure_date = update_data.get(
        "departure_date",
        transport.departure_date,
    )

    final_arrival_date = update_data.get(
        "arrival_date",
        transport.arrival_date,
    )

    final_departure_time = update_data.get(
        "departure_time",
        transport.departure_time,
    )

    final_arrival_time = update_data.get(
        "arrival_time",
        transport.arrival_time,
    )

    final_check_in_date = update_data.get(
        "check_in_date",
        transport.check_in_date,
    )

    validate_transport_dates(
        departure_date=final_departure_date,
        arrival_date=final_arrival_date,
        departure_time=final_departure_time,
        arrival_time=final_arrival_time,
        check_in_date=final_check_in_date,
    )

    validate_transport_within_trip(
        trip=trip,
        departure_date=final_departure_date,
        arrival_date=final_arrival_date,
    )

    for field, value in update_data.items():
        setattr(
            transport,
            field,
            value,
        )

    return update_transport(
        db=db,
        transport=transport,
    )


def delete_transport_from_trip(
    db: Session,
    trip_id: int,
    transport_id: int,
    user: User,
) -> None:
    """
    Elimina un transporte perteneciente a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    transport = get_transport_or_raise(
        db=db,
        trip_id=trip.id,
        transport_id=transport_id,
    )

    delete_transport(
        db=db,
        transport=transport,
    )
from datetime import date, time

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AccommodationNotFoundError,
    AccommodationOutsideTripDatesError,
    InvalidAccommodationDatesError,
    TripNotFoundError,
)
from app.models.accommodation import Accommodation
from app.models.trip import Trip
from app.models.user import User
from app.repositories.accommodation_repository import (
    create_accommodation,
    delete_accommodation,
    get_accommodation_by_id_and_trip_id,
    get_accommodations_by_trip_id,
    get_user_trip,
    update_accommodation,
)
from app.schemas.accommodation import (
    AccommodationCreate,
    AccommodationUpdate,
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


def get_accommodation_or_raise(
    db: Session,
    trip_id: int,
    accommodation_id: int,
) -> Accommodation:
    """
    Obtiene un alojamiento perteneciente al viaje indicado.
    """

    accommodation = get_accommodation_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        accommodation_id=accommodation_id,
    )

    if accommodation is None:
        raise AccommodationNotFoundError

    return accommodation


def validate_accommodation_dates(
    check_in_date: date,
    check_out_date: date,
    check_in_time: time | None,
    check_out_time: time | None,
) -> None:
    """
    Comprueba la coherencia cronológica de las fechas
    y horas del alojamiento.
    """

    if check_out_date < check_in_date:
        raise InvalidAccommodationDatesError

    if (
        check_out_date == check_in_date
        and check_in_time is not None
        and check_out_time is not None
        and check_out_time < check_in_time
    ):
        raise InvalidAccommodationDatesError


def validate_accommodation_within_trip(
    trip: Trip,
    check_in_date: date,
    check_out_date: date,
) -> None:
    """
    Comprueba que la entrada y la salida se encuentran
    dentro del intervalo temporal del viaje.
    """

    if not (
        trip.start_date
        <= check_in_date
        <= trip.end_date
    ):
        raise AccommodationOutsideTripDatesError

    if not (
        trip.start_date
        <= check_out_date
        <= trip.end_date
    ):
        raise AccommodationOutsideTripDatesError


def list_trip_accommodations(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Accommodation]:
    """
    Obtiene todos los alojamientos de un viaje.
    """

    get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    return get_accommodations_by_trip_id(
        db=db,
        trip_id=trip_id,
    )


def add_accommodation_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    accommodation_data: AccommodationCreate,
) -> Accommodation:
    """
    Añade un alojamiento a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_accommodation_dates(
        check_in_date=accommodation_data.check_in_date,
        check_out_date=accommodation_data.check_out_date,
        check_in_time=accommodation_data.check_in_time,
        check_out_time=accommodation_data.check_out_time,
    )

    validate_accommodation_within_trip(
        trip=trip,
        check_in_date=accommodation_data.check_in_date,
        check_out_date=accommodation_data.check_out_date,
    )

    accommodation = Accommodation(
        trip_id=trip.id,
        name=accommodation_data.name,
        address=accommodation_data.address,
        price=accommodation_data.price,
        check_in_date=accommodation_data.check_in_date,
        check_out_date=accommodation_data.check_out_date,
        check_in_time=accommodation_data.check_in_time,
        check_out_time=accommodation_data.check_out_time,
    )

    return create_accommodation(
        db=db,
        accommodation=accommodation,
    )


def update_accommodation_in_trip(
    db: Session,
    trip_id: int,
    accommodation_id: int,
    user: User,
    accommodation_data: AccommodationUpdate,
) -> Accommodation:
    """
    Actualiza parcialmente un alojamiento.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    accommodation = get_accommodation_or_raise(
        db=db,
        trip_id=trip.id,
        accommodation_id=accommodation_id,
    )

    update_data = accommodation_data.model_dump(
        exclude_unset=True,
    )

    final_check_in_date = update_data.get(
        "check_in_date",
        accommodation.check_in_date,
    )

    final_check_out_date = update_data.get(
        "check_out_date",
        accommodation.check_out_date,
    )

    final_check_in_time = update_data.get(
        "check_in_time",
        accommodation.check_in_time,
    )

    final_check_out_time = update_data.get(
        "check_out_time",
        accommodation.check_out_time,
    )

    validate_accommodation_dates(
        check_in_date=final_check_in_date,
        check_out_date=final_check_out_date,
        check_in_time=final_check_in_time,
        check_out_time=final_check_out_time,
    )

    validate_accommodation_within_trip(
        trip=trip,
        check_in_date=final_check_in_date,
        check_out_date=final_check_out_date,
    )

    for field, value in update_data.items():
        setattr(
            accommodation,
            field,
            value,
        )

    return update_accommodation(
        db=db,
        accommodation=accommodation,
    )


def delete_accommodation_from_trip(
    db: Session,
    trip_id: int,
    accommodation_id: int,
    user: User,
) -> None:
    """
    Elimina un alojamiento perteneciente a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    accommodation = get_accommodation_or_raise(
        db=db,
        trip_id=trip.id,
        accommodation_id=accommodation_id,
    )

    delete_accommodation(
        db=db,
        accommodation=accommodation,
    )
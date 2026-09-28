from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DestinationLimitExceededError,
    DestinationNotFoundError,
    LastDestinationDeletionError,
    TripNotFoundError,
    InvalidDestinationOrderError,
)
from app.models.destination import Destination
from app.models.trip import Trip
from app.models.user import User
from app.repositories.destination_repository import (
    delete_destination,
    get_destinations_by_trip_id,
    save_destination_order
)
from app.schemas.trip import (
    DestinationCreate,
    DestinationUpdate,
    DestinationOrderUpdate,
)
from app.services.currency_service import (
    validate_currency_code,
)


def get_user_trip(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip:
    """
    Obtiene un viaje perteneciente al usuario autenticado.
    """

    statement = select(Trip).where(
        Trip.id == trip_id,
        Trip.user_id == user_id,
    )

    trip = db.scalar(statement)

    if trip is None:
        raise TripNotFoundError

    return trip


def get_trip_destination(
    trip: Trip,
    destination_id: int,
) -> Destination:
    """
    Obtiene un destino perteneciente al viaje indicado.
    """

    destination = next(
        (
            destination
            for destination in trip.destinations
            if destination.id == destination_id
        ),
        None,
    )

    if destination is None:
        raise DestinationNotFoundError

    return destination


def add_destination_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    destination_data: DestinationCreate,
) -> Trip:
    trip = get_user_trip(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    if len(trip.destinations) >= 20:
        raise DestinationLimitExceededError

    normalized_currency = validate_currency_code(
        destination_data.currency
    )

    next_order = max(
        (
            destination.order
            for destination in trip.destinations
        ),
        default=0,
    ) + 1

    destination = Destination(
        country=destination_data.country,
        city=destination_data.city,
        currency=normalized_currency,
        order=next_order,
    )

    trip.destinations.append(destination)

    try:
        db.commit()
        db.refresh(trip)
    except Exception:
        db.rollback()
        raise

    return trip


def update_destination_in_trip(
    db: Session,
    trip_id: int,
    destination_id: int,
    user: User,
    destination_data: DestinationUpdate,
) -> Trip:
    """
    Actualiza parcialmente un destino de un viaje.
    """

    trip = get_user_trip(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    destination = get_trip_destination(
        trip=trip,
        destination_id=destination_id,
    )

    update_data = destination_data.model_dump(
        exclude_unset=True,
    )

    if "currency" in update_data:
        update_data["currency"] = validate_currency_code(
            update_data["currency"]
        )

    for field, value in update_data.items():
        setattr(
            destination,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(trip)
    except Exception:
        db.rollback()
        raise

    return trip


def delete_destination_from_trip(
    db: Session,
    trip_id: int,
    destination_id: int,
    user: User,
) -> Trip:
    trip = get_user_trip(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    destination = get_trip_destination(
        trip=trip,
        destination_id=destination_id,
    )

    if len(trip.destinations) == 1:
        raise LastDestinationDeletionError

    deleted_order = destination.order

    delete_destination(
        db=db,
        destination=destination,
        commit=False,
    )

    db.flush()

    remaining_destinations = sorted(
        (
            current_destination
            for current_destination in trip.destinations
            if current_destination.id != destination_id
        ),
        key=lambda current_destination: (
            current_destination.order
        ),
    )

    for current_destination in remaining_destinations:
        if current_destination.order > deleted_order:
            current_destination.order -= 1

    try:
        db.commit()
        db.refresh(trip)
    except Exception:
        db.rollback()
        raise

    return trip


def reorder_trip_destinations(
    db: Session,
    trip_id: int,
    user: User,
    destination_order_data: DestinationOrderUpdate,
) -> Trip:
    """
    Modifica el orden de todos los destinos de un viaje.
    """

    trip = get_user_trip(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    destinations = get_destinations_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    current_destination_ids = {
        destination.id
        for destination in destinations
    }

    received_destination_ids = {
        destination_data.id
        for destination_data
        in destination_order_data.destinations
    }

    if current_destination_ids != received_destination_ids:
        raise InvalidDestinationOrderError

    destinations_by_id = {
        destination.id: destination
        for destination in destinations
    }

    temporary_order_start = len(destinations) + 1

    for index, destination in enumerate(
        destinations,
        start=temporary_order_start,
    ):
        destination.order = index

    try:
        db.flush()
    except Exception:
        db.rollback()
        raise

    for destination_data in destination_order_data.destinations:
        destination = destinations_by_id[
            destination_data.id
        ]

        destination.order = destination_data.order

    save_destination_order(
        db=db,
        destinations=destinations,
    )

    db.refresh(trip)

    return trip
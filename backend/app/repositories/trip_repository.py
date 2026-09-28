from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trip import Trip


def get_trips_by_user_id(
    db: Session,
    user_id: int,
) -> list[Trip]:
    """
    Obtiene todos los viajes pertenecientes a un usuario.
    """

    statement = (
        select(Trip)
        .where(Trip.user_id == user_id)
        .order_by(Trip.start_date.asc())
    )

    return list(
        db.scalars(statement).all()
    )


def get_trip_by_id_and_user_id(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip | None:
    """
    Obtiene un viaje si pertenece al usuario indicado.
    """

    statement = select(Trip).where(
        Trip.id == trip_id,
        Trip.user_id == user_id,
    )

    return db.scalar(statement)


def create_trip_with_destinations(
    db: Session,
    trip: Trip,
) -> Trip:
    """
    Guarda un viaje y sus destinos en una única transacción.
    """

    try:
        db.add(trip)
        db.commit()
        db.refresh(trip)

        return trip

    except Exception:
        db.rollback()
        raise


def update_trip(
    db: Session,
    trip: Trip,
) -> Trip:
    """
    Persiste los cambios realizados sobre un viaje.
    """

    try:
        db.add(trip)
        db.commit()
        db.refresh(trip)

        return trip

    except Exception:
        db.rollback()
        raise


def delete_trip(
    db: Session,
    trip: Trip,
) -> None:
    """
    Elimina un viaje de la base de datos.
    """

    try:
        db.delete(trip)
        db.commit()

    except Exception:
        db.rollback()
        raise
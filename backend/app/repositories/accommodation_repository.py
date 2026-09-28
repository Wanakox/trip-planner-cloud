from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.accommodation import Accommodation
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


def get_accommodation_by_id_and_trip_id(
    db: Session,
    accommodation_id: int,
    trip_id: int,
) -> Accommodation | None:
    """
    Obtiene un alojamiento perteneciente al viaje indicado.
    """

    statement = select(Accommodation).where(
        Accommodation.id == accommodation_id,
        Accommodation.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_accommodations_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Accommodation]:
    """
    Obtiene los alojamientos asociados a un viaje,
    ordenados por fecha y hora de entrada.
    """

    statement = (
        select(Accommodation)
        .where(
            Accommodation.trip_id == trip_id,
        )
        .order_by(
            Accommodation.check_in_date.asc(),
            Accommodation.check_in_time.asc().nullsfirst(),
            Accommodation.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def create_accommodation(
    db: Session,
    accommodation: Accommodation,
) -> Accommodation:
    """
    Guarda un alojamiento en la base de datos.
    """

    try:
        db.add(accommodation)
        db.commit()
        db.refresh(accommodation)

        return accommodation

    except Exception:
        db.rollback()
        raise


def update_accommodation(
    db: Session,
    accommodation: Accommodation,
) -> Accommodation:
    """
    Guarda los cambios realizados sobre un alojamiento.
    """

    try:
        db.add(accommodation)
        db.commit()
        db.refresh(accommodation)

        return accommodation

    except Exception:
        db.rollback()
        raise


def delete_accommodation(
    db: Session,
    accommodation: Accommodation,
) -> None:
    """
    Elimina un alojamiento de la base de datos.
    """

    try:
        db.delete(accommodation)
        db.commit()

    except Exception:
        db.rollback()
        raise
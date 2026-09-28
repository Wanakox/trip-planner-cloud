from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transport import Transport
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


def get_transport_by_id_and_trip_id(
    db: Session,
    transport_id: int,
    trip_id: int,
) -> Transport | None:
    """
    Obtiene un transporte perteneciente al viaje indicado.
    """

    statement = select(Transport).where(
        Transport.id == transport_id,
        Transport.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_transports_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Transport]:
    """
    Obtiene los transportes asociados a un viaje,
    ordenados por fecha y hora de salida.
    """

    statement = (
        select(Transport)
        .where(
            Transport.trip_id == trip_id,
        )
        .order_by(
            Transport.departure_date.asc(),
            Transport.departure_time.asc().nullsfirst(),
            Transport.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def create_transport(
    db: Session,
    transport: Transport,
) -> Transport:
    """
    Guarda un transporte en la base de datos.
    """

    try:
        db.add(transport)
        db.commit()
        db.refresh(transport)

        return transport

    except Exception:
        db.rollback()
        raise


def update_transport(
    db: Session,
    transport: Transport,
) -> Transport:
    """
    Guarda los cambios realizados sobre un transporte.
    """

    try:
        db.add(transport)
        db.commit()
        db.refresh(transport)

        return transport

    except Exception:
        db.rollback()
        raise


def delete_transport(
    db: Session,
    transport: Transport,
) -> None:
    """
    Elimina un transporte de la base de datos.
    """

    try:
        db.delete(transport)
        db.commit()

    except Exception:
        db.rollback()
        raise
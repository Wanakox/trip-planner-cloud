from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.destination import Destination


def create_destination(
    db: Session,
    destination: Destination,
) -> Destination:
    """
    Guarda un destino en la base de datos.
    """

    try:
        db.add(destination)
        db.commit()
        db.refresh(destination)

        return destination
    except Exception:
        db.rollback()
        raise


def update_destination(
    db: Session,
    destination: Destination,
) -> Destination:
    """
    Actualiza un destino existente.
    """

    try:
        db.add(destination)
        db.commit()
        db.refresh(destination)

        return destination
    except Exception:
        db.rollback()
        raise


def delete_destination(
    db: Session,
    destination: Destination,
    commit: bool = True,
) -> None:
    """
    Marca un destino para su eliminación.

    El parámetro commit permite que el servicio continúe
    reordenando destinos dentro de la misma transacción.
    """

    try:
        db.delete(destination)

        if commit:
            db.commit()
    except Exception:
        db.rollback()
        raise


def get_destinations_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Destination]:
    """
    Obtiene todos los destinos de un viaje.
    """

    statement = (
        select(Destination)
        .where(
            Destination.trip_id == trip_id,
        )
        .order_by(
            Destination.order.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def save_destination_order(
    db: Session,
    destinations: list[Destination],
) -> list[Destination]:
    """
    Guarda el nuevo orden de los destinos.
    """

    try:
        for destination in destinations:
            db.add(destination)

        db.commit()

        for destination in destinations:
            db.refresh(destination)

        return destinations

    except Exception:
        db.rollback()
        raise
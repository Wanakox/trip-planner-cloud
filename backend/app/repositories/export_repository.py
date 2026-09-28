from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.trip import Trip


def get_trip_for_export(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip | None:
    """
    Obtiene un viaje y carga toda la información
    necesaria para generar su exportación.
    """

    statement = (
        select(Trip)
        .where(
            Trip.id == trip_id,
            Trip.user_id == user_id,
        )
        .options(
            selectinload(Trip.destinations),
            selectinload(Trip.activities),
            selectinload(Trip.transports),
            selectinload(Trip.accommodations),
            selectinload(Trip.participants),
            selectinload(Trip.expenses),
            selectinload(Trip.notes),
            selectinload(Trip.files),
        )
    )

    return db.scalar(statement)
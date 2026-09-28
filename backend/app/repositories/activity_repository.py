from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.activity import Activity
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


def get_activity_by_id_and_trip_id(
    db: Session,
    activity_id: int,
    trip_id: int,
) -> Activity | None:
    """
    Obtiene una actividad perteneciente al viaje indicado.
    """

    statement = select(Activity).where(
        Activity.id == activity_id,
        Activity.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_activities_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Activity]:
    """
    Obtiene todas las actividades de un viaje,
    ordenadas por día y posición.
    """

    statement = (
        select(Activity)
        .where(
            Activity.trip_id == trip_id,
        )
        .order_by(
            Activity.day_number.asc(),
            Activity.order.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_last_activity_order_by_day(
    db: Session,
    trip_id: int,
    day_number: int,
) -> int:
    """
    Obtiene la última posición ocupada en un día del viaje.
    """

    statement = select(
        func.coalesce(
            func.max(Activity.order),
            0,
        )
    ).where(
        Activity.trip_id == trip_id,
        Activity.day_number == day_number,
    )

    return db.scalar(statement) or 0


def create_activity(
    db: Session,
    activity: Activity,
) -> Activity:
    """
    Guarda una actividad en la base de datos.
    """

    try:
        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity

    except Exception:
        db.rollback()
        raise


def update_activity(
    db: Session,
    activity: Activity,
) -> Activity:
    """
    Guarda los cambios realizados sobre una actividad.
    """

    try:
        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity

    except Exception:
        db.rollback()
        raise


def delete_activity(
    db: Session,
    activity: Activity,
    commit: bool = True,
) -> None:
    """
    Marca una actividad para su eliminación.

    El parámetro commit permite continuar modificando
    otras actividades dentro de la misma transacción.
    """

    try:
        db.delete(activity)

        if commit:
            db.commit()

    except Exception:
        db.rollback()
        raise


def save_activities(
    db: Session,
    activities: list[Activity],
) -> list[Activity]:
    """
    Guarda los cambios realizados sobre varias actividades.
    """

    try:
        for activity in activities:
            db.add(activity)

        db.commit()

        for activity in activities:
            db.refresh(activity)

        return activities

    except Exception:
        db.rollback()
        raise
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ActivityNotFoundError,
    InvalidActivityDayError,
    InvalidActivityOrderError,
    TripNotFoundError,
)
from app.models.activity import Activity
from app.models.trip import Trip
from app.models.user import User
from app.repositories.activity_repository import (
    create_activity,
    delete_activity,
    get_activities_by_trip_id,
    get_activity_by_id_and_trip_id,
    get_last_activity_order_by_day,
    get_user_trip,
    save_activities,
    update_activity,
)
from app.schemas.activity import (
    ActivityCompletionUpdate,
    ActivityCreate,
    ActivityOrderUpdate,
    ActivityUpdate,
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


def get_activity_or_raise(
    db: Session,
    trip_id: int,
    activity_id: int,
) -> Activity:
    """
    Obtiene una actividad perteneciente al viaje indicado.
    """

    activity = get_activity_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        activity_id=activity_id,
    )

    if activity is None:
        raise ActivityNotFoundError

    return activity


def calculate_trip_duration(
    trip: Trip,
) -> int:
    """
    Calcula el número de días que comprende un viaje.
    """

    return (
        trip.end_date
        - trip.start_date
    ).days + 1


def validate_activity_day(
    trip: Trip,
    day_number: int,
) -> None:
    """
    Comprueba que el día pertenece a la duración del viaje.
    """

    trip_duration = calculate_trip_duration(
        trip=trip,
    )

    if (
        day_number < 1
        or day_number > trip_duration
    ):
        raise InvalidActivityDayError


def normalize_day_orders(
    activities: list[Activity],
    day_number: int,
) -> None:
    """
    Recalcula las posiciones de las actividades de un día.
    """

    day_activities = sorted(
        (
            activity
            for activity in activities
            if activity.day_number == day_number
        ),
        key=lambda activity: activity.order,
    )

    for index, activity in enumerate(
        day_activities,
        start=1,
    ):
        activity.order = index


def list_trip_activities(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Activity]:
    """
    Obtiene las actividades de un viaje del usuario.
    """

    get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    return get_activities_by_trip_id(
        db=db,
        trip_id=trip_id,
    )


def add_activity_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    activity_data: ActivityCreate,
) -> Activity:
    """
    Añade una actividad a un día concreto del viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_activity_day(
        trip=trip,
        day_number=activity_data.day_number,
    )

    last_order = get_last_activity_order_by_day(
        db=db,
        trip_id=trip.id,
        day_number=activity_data.day_number,
    )

    activity = Activity(
        trip_id=trip.id,
        name=activity_data.name,
        location=activity_data.location,
        start_time=activity_data.start_time,
        day_number=activity_data.day_number,
        completed=False,
        order=last_order + 1,
    )

    return create_activity(
        db=db,
        activity=activity,
    )


def update_activity_in_trip(
    db: Session,
    trip_id: int,
    activity_id: int,
    user: User,
    activity_data: ActivityUpdate,
) -> Activity:
    """
    Actualiza parcialmente una actividad.

    Si cambia de día, se coloca al final del nuevo día
    y se reorganizan las actividades del día anterior.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    activity = get_activity_or_raise(
        db=db,
        trip_id=trip.id,
        activity_id=activity_id,
    )

    update_data = activity_data.model_dump(
        exclude_unset=True,
    )

    new_day_number = update_data.get(
        "day_number"
    )

    if new_day_number is not None:
        validate_activity_day(
            trip=trip,
            day_number=new_day_number,
        )

    original_day_number = activity.day_number

    day_changed = (
        new_day_number is not None
        and new_day_number != original_day_number
    )

    if day_changed:
        activities = get_activities_by_trip_id(
            db=db,
            trip_id=trip.id,
        )

        last_new_day_order = max(
            (
                current_activity.order
                for current_activity in activities
                if (
                    current_activity.day_number
                    == new_day_number
                )
            ),
            default=0,
        )

        activity.day_number = new_day_number
        activity.order = last_new_day_order + 1

        normalize_day_orders(
            activities=activities,
            day_number=original_day_number,
        )

        update_data.pop(
            "day_number",
            None,
        )

        for field, value in update_data.items():
            if field == "name" and value is None:
                continue

            setattr(
                activity,
                field,
                value,
            )

        save_activities(
            db=db,
            activities=activities,
        )

        return activity

    for field, value in update_data.items():
        if field == "name" and value is None:
            continue

        setattr(
            activity,
            field,
            value,
        )

    return update_activity(
        db=db,
        activity=activity,
    )


def delete_activity_from_trip(
    db: Session,
    trip_id: int,
    activity_id: int,
    user: User,
) -> None:
    """
    Elimina una actividad y reorganiza las posiciones
    restantes de su día.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    activity = get_activity_or_raise(
        db=db,
        trip_id=trip.id,
        activity_id=activity_id,
    )

    deleted_day_number = activity.day_number

    activities = get_activities_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    delete_activity(
        db=db,
        activity=activity,
        commit=False,
    )

    db.flush()

    remaining_activities = [
        current_activity
        for current_activity in activities
        if current_activity.id != activity.id
    ]

    normalize_day_orders(
        activities=remaining_activities,
        day_number=deleted_day_number,
    )

    save_activities(
        db=db,
        activities=remaining_activities,
    )


def set_activity_completion(
    db: Session,
    trip_id: int,
    activity_id: int,
    user: User,
    completion_data: ActivityCompletionUpdate,
) -> Activity:
    """
    Establece explícitamente si una actividad está completada.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    activity = get_activity_or_raise(
        db=db,
        trip_id=trip.id,
        activity_id=activity_id,
    )

    activity.completed = completion_data.completed

    return update_activity(
        db=db,
        activity=activity,
    )


def reorder_trip_activities(
    db: Session,
    trip_id: int,
    user: User,
    order_data: ActivityOrderUpdate,
) -> list[Activity]:
    """
    Modifica el día y la posición de las actividades del viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    activities = get_activities_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    current_activity_ids = {
        activity.id
        for activity in activities
    }

    received_activity_ids = {
        activity_data.id
        for activity_data in order_data.activities
    }

    if current_activity_ids != received_activity_ids:
        raise InvalidActivityOrderError

    for activity_data in order_data.activities:
        validate_activity_day(
            trip=trip,
            day_number=activity_data.day_number,
        )

    activities_by_id = {
        activity.id: activity
        for activity in activities
    }

    temporary_order_start = len(activities) + 1

    for index, activity in enumerate(
        activities,
        start=temporary_order_start,
    ):
        activity.order = index

    try:
        db.flush()
    except Exception:
        db.rollback()
        raise

    for activity_data in order_data.activities:
        activity = activities_by_id[
            activity_data.id
        ]

        activity.day_number = activity_data.day_number
        activity.order = activity_data.order

    save_activities(
        db=db,
        activities=activities,
    )

    return get_activities_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import (
    TripNotCompletedError,
    TripNotFoundError,
)
from app.models.activity import Activity
from app.models.trip import (
    Trip,
    TripStatus,
)
from app.models.user import User
from app.repositories.activity_repository import (
    get_activities_by_trip_id,
    get_user_trip,
)
from app.schemas.timeline import (
    TimelineActivityResponse,
    TimelineDayResponse,
    TimelineResponse,
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


def validate_completed_trip(
    trip: Trip,
) -> None:
    """
    Comprueba que el viaje está completado.
    """

    if trip.status != TripStatus.COMPLETED:
        raise TripNotCompletedError


def group_activities_by_day(
    activities: list[Activity],
) -> dict[int, list[Activity]]:
    """
    Agrupa las actividades por número de día.
    """

    activities_by_day: dict[
        int,
        list[Activity],
    ] = {}

    for activity in activities:
        activities_by_day.setdefault(
            activity.day_number,
            [],
        ).append(activity)

    return activities_by_day


def build_timeline_days(
    trip: Trip,
    activities_by_day: dict[int, list[Activity]],
) -> list[TimelineDayResponse]:
    """
    Construye todos los días de la línea temporal.
    """

    days: list[TimelineDayResponse] = []

    for day_number in range(
        1,
        trip.total_days + 1,
    ):
        current_date = (
            trip.start_date
            + timedelta(days=day_number - 1)
        )

        day_activities = activities_by_day.get(
            day_number,
            [],
        )

        days.append(
            TimelineDayResponse(
                day_number=day_number,
                date=current_date,
                activities=[
                    TimelineActivityResponse(
                        id=activity.id,
                        name=activity.name,
                        location=activity.location,
                        start_time=activity.start_time,
                        completed=activity.completed,
                        order=activity.order,
                    )
                    for activity in day_activities
                ],
            )
        )

    return days


def build_trip_timeline(
    trip: Trip,
    activities: list[Activity],
) -> TimelineResponse:
    """
    Construye la línea temporal a partir de un viaje
    y sus actividades ya cargadas.
    """

    activities_by_day = group_activities_by_day(
        activities=activities,
    )

    days = build_timeline_days(
        trip=trip,
        activities_by_day=activities_by_day,
    )

    return TimelineResponse(
        trip_id=trip.id,
        start_date=trip.start_date,
        end_date=trip.end_date,
        days=days,
    )


def get_trip_timeline(
    db: Session,
    trip_id: int,
    user: User,
) -> TimelineResponse:
    """
    Genera la línea temporal de un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_completed_trip(
        trip=trip,
    )

    activities = get_activities_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    return build_trip_timeline(
        trip=trip,
        activities=activities,
    )
from datetime import date
from types import SimpleNamespace

import pytest

from app.core.exceptions import NotesUnavailableError
from app.models.trip import TripStatus
from app.services.note_service import get_max_available_note_day


def make_trip(status: TripStatus) -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        start_date=date(2026, 8, 10),
        total_days=7,
    )


def test_in_progress_trip_allows_reached_days() -> None:
    trip = make_trip(TripStatus.IN_PROGRESS)

    assert (
        get_max_available_note_day(
            trip,
            current_date=date(2026, 8, 12),
        )
        == 3
    )


def test_in_progress_trip_never_exceeds_duration() -> None:
    trip = make_trip(TripStatus.IN_PROGRESS)

    assert (
        get_max_available_note_day(
            trip,
            current_date=date(2026, 8, 30),
        )
        == 7
    )


def test_completed_trip_allows_every_day() -> None:
    trip = make_trip(TripStatus.COMPLETED)

    assert get_max_available_note_day(trip) == 7


@pytest.mark.parametrize(
    "status",
    [TripStatus.PLANNING, TripStatus.CANCELLED],
)
def test_notes_are_unavailable_for_other_statuses(
    status: TripStatus,
) -> None:
    trip = make_trip(status)

    with pytest.raises(NotesUnavailableError):
        get_max_available_note_day(trip)

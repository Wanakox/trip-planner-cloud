"""Unit tests for trip ownership and core trip business rules."""

from datetime import date
from types import SimpleNamespace

import pytest

from app.core.exceptions import InvalidTripDatesError, TripNotCompletedError, TripNotFoundError
from app.models.trip import TripStatus
from app.schemas.trip import TripUpdate
from app.services import trip_service

USER = SimpleNamespace(id=7, name="Juan", surname="García", default_currency="EUR")


def test_get_user_trip_filters_by_authenticated_owner(monkeypatch) -> None:
    expected = SimpleNamespace(id=2, user_id=7)
    captured = {}

    def fake_get(**kwargs):
        captured.update(kwargs)
        return expected

    monkeypatch.setattr(trip_service, "get_trip_by_id_and_user_id", fake_get)
    assert trip_service.get_user_trip_by_id(object(), USER, 2) is expected
    assert captured["trip_id"] == 2
    assert captured["user_id"] == USER.id


def test_other_users_trip_is_indistinguishable_from_missing(monkeypatch) -> None:
    monkeypatch.setattr(trip_service, "get_trip_by_id_and_user_id", lambda **_: None)
    with pytest.raises(TripNotFoundError):
        trip_service.get_user_trip_by_id(object(), USER, 999)


def test_update_rejects_dates_invalid_after_partial_update(monkeypatch) -> None:
    trip = SimpleNamespace(start_date=date(2026, 9, 10), end_date=date(2026, 9, 20))
    monkeypatch.setattr(trip_service, "get_user_trip_by_id", lambda **_: trip)
    with pytest.raises(InvalidTripDatesError):
        trip_service.update_trip(object(), USER, 1, TripUpdate(end_date=date(2026, 9, 9)))


def test_only_completed_trip_can_be_rated(monkeypatch) -> None:
    trip = SimpleNamespace(status=TripStatus.PLANNING, rating=None)
    monkeypatch.setattr(trip_service, "get_user_trip_by_id", lambda **_: trip)
    with pytest.raises(TripNotCompletedError):
        trip_service.update_trip_rating(object(), USER, 1, 5)


def test_completed_trip_rating_is_persisted(monkeypatch) -> None:
    trip = SimpleNamespace(status=TripStatus.COMPLETED, rating=None)
    monkeypatch.setattr(trip_service, "get_user_trip_by_id", lambda **_: trip)
    monkeypatch.setattr(trip_service, "update_trip_repository", lambda **kwargs: kwargs["trip"])
    result = trip_service.update_trip_rating(object(), USER, 1, 5)
    assert result.rating == 5


def test_delete_checks_ownership_before_repository_delete(monkeypatch) -> None:
    trip = SimpleNamespace(id=1, user_id=7)
    deleted = []
    monkeypatch.setattr(trip_service, "get_user_trip_by_id", lambda **_: trip)
    monkeypatch.setattr(
        trip_service, "delete_trip_repository", lambda **kwargs: deleted.append(kwargs["trip"])
    )
    trip_service.delete_user_trip(object(), USER, 1)
    assert deleted == [trip]

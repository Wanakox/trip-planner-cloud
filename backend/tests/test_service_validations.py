"""Unit tests for pure domain rules and external-response mapping."""

from datetime import date, time
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import (
    AccommodationOutsideTripDatesError,
    InvalidAccommodationDatesError,
    InvalidActivityDayError,
    InvalidTransportDatesError,
    TransportOutsideTripDatesError,
    TripNotCompletedError,
    UnsupportedCurrencyError,
)
from app.models.trip import TripStatus
from app.schemas.flight import CabinClass
from app.services import (
    accommodation_service,
    activity_service,
    currency_service,
    export_service,
    flight_service,
    timeline_service,
    transport_service,
)


def trip(**changes):
    values = {
        "id": 1,
        "start_date": date(2026, 9, 1),
        "end_date": date(2026, 9, 7),
        "total_days": 7,
        "status": TripStatus.COMPLETED,
    }
    values.update(changes)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("arrival_date", "departure_time", "arrival_time", "check_in_date"),
    [
        (date(2026, 8, 31), None, None, None),
        (date(2026, 9, 1), time(12), time(11), None),
        (date(2026, 9, 2), None, None, date(2026, 9, 2)),
    ],
)
def test_transport_rejects_incoherent_dates(
    arrival_date, departure_time, arrival_time, check_in_date
):
    with pytest.raises(InvalidTransportDatesError):
        transport_service.validate_transport_dates(
            date(2026, 9, 1), arrival_date, departure_time, arrival_time, check_in_date
        )


def test_transport_accepts_valid_dates_and_optional_arrival():
    transport_service.validate_transport_dates(
        date(2026, 9, 1), None, time(10), None, date(2026, 8, 31)
    )
    transport_service.validate_transport_within_trip(trip(), date(2026, 9, 1), None)


@pytest.mark.parametrize(
    ("departure", "arrival"),
    [(date(2026, 8, 31), None), (date(2026, 9, 1), date(2026, 9, 8))],
)
def test_transport_must_be_inside_trip(departure, arrival):
    with pytest.raises(TransportOutsideTripDatesError):
        transport_service.validate_transport_within_trip(trip(), departure, arrival)


@pytest.mark.parametrize(
    ("check_in", "check_out", "in_time", "out_time"),
    [
        (date(2026, 9, 2), date(2026, 9, 1), None, None),
        (date(2026, 9, 2), date(2026, 9, 2), time(15), time(10)),
    ],
)
def test_accommodation_rejects_incoherent_dates(check_in, check_out, in_time, out_time):
    with pytest.raises(InvalidAccommodationDatesError):
        accommodation_service.validate_accommodation_dates(check_in, check_out, in_time, out_time)


def test_accommodation_accepts_valid_dates():
    accommodation_service.validate_accommodation_dates(
        date(2026, 9, 1), date(2026, 9, 2), time(15), time(10)
    )


@pytest.mark.parametrize(
    ("check_in", "check_out"),
    [(date(2026, 8, 31), date(2026, 9, 2)), (date(2026, 9, 2), date(2026, 9, 8))],
)
def test_accommodation_must_be_inside_trip(check_in, check_out):
    with pytest.raises(AccommodationOutsideTripDatesError):
        accommodation_service.validate_accommodation_within_trip(trip(), check_in, check_out)


def test_activity_duration_day_and_order_normalization():
    current_trip = trip()
    assert activity_service.calculate_trip_duration(current_trip) == 7
    activity_service.validate_activity_day(current_trip, 1)
    activity_service.validate_activity_day(current_trip, 7)
    with pytest.raises(InvalidActivityDayError):
        activity_service.validate_activity_day(current_trip, 0)
    with pytest.raises(InvalidActivityDayError):
        activity_service.validate_activity_day(current_trip, 8)

    activities = [
        SimpleNamespace(day_number=1, order=5),
        SimpleNamespace(day_number=2, order=1),
        SimpleNamespace(day_number=1, order=2),
    ]
    activity_service.normalize_day_orders(activities, 1)
    assert sorted(a.order for a in activities if a.day_number == 1) == [1, 2]


def test_currency_list_is_sorted_and_code_is_normalized(monkeypatch):
    monkeypatch.setattr(
        currency_service, "get_available_currencies", lambda: {"USD": "Dollar", "EUR": "Euro"}
    )
    assert [currency.code for currency in currency_service.list_currencies()] == ["EUR", "USD"]
    assert currency_service.validate_currency_code(" eur ") == "EUR"
    with pytest.raises(UnsupportedCurrencyError):
        currency_service.validate_currency_code("ZZZ")


def test_same_currency_does_not_call_provider(monkeypatch):
    def provider(**kwargs):
        pytest.fail("provider should not be called")

    monkeypatch.setattr(currency_service, "get_latest_rate", provider)
    result = currency_service.convert_currency(Decimal("12.34"), "eur", " EUR ")
    assert result.rate == Decimal("1")
    assert result.result == Decimal("12.34")


def test_currency_conversion_rounds_half_up(monkeypatch):
    monkeypatch.setattr(
        currency_service,
        "get_latest_rate",
        lambda **kwargs: {"rates": {"USD": 1.005}, "date": "2026-08-30"},
    )
    result = currency_service.convert_currency(Decimal("1"), "EUR", "USD")
    assert result.result == Decimal("1.01")


def test_flight_mapping_and_price_order(monkeypatch):
    offers = [
        {
            "id": offer_id,
            "owner": {"name": "Duffel Airways", "iata_code": "ZZ"},
            "total_amount": price,
            "total_currency": "EUR",
            "slices": [
                {
                    "origin": {"iata_code": "MAD"},
                    "destination": {"iata_code": "HER"},
                    "duration": "PT4H",
                    "segments": [
                        {
                            "origin": {"iata_code": "MAD"},
                            "destination": {"iata_code": "HER"},
                            "departing_at": "2026-09-01T10:00:00Z",
                            "arriving_at": "2026-09-01T14:00:00Z",
                            "marketing_carrier": {"name": "Duffel Airways", "iata_code": "ZZ"},
                            "marketing_carrier_flight_number": "101",
                        }
                    ],
                }
            ],
        }
        for offer_id, price in [("expensive", "200.00"), ("cheap", "100.00")]
    ]
    monkeypatch.setattr(flight_service, "create_offer_request", lambda **kwargs: {"offers": offers})
    result = flight_service.search_flights(
        " mad ", "her", date(2026, 9, 1), None, 1, CabinClass.ECONOMY
    )
    assert [offer.id for offer in result.offers] == ["cheap", "expensive"]
    assert result.offers[0].slices[0].segments[0].origin == "MAD"
    assert result.origin == "MAD"


@pytest.mark.parametrize(
    ("value", "expected"),
    [(" Viaje por Creta ", "viaje-por-creta"), ("***", "viaje"), ("A/B", "a-b")],
)
def test_export_filename_is_safe(value, expected):
    assert export_service.sanitize_filename(value) == expected


def test_export_duplicate_names_are_numbered():
    used = set()
    assert export_service.get_unique_archive_name("../billete.pdf", used) == "billete.pdf"
    assert export_service.get_unique_archive_name("billete.pdf", used) == "billete-2.pdf"


def test_timeline_groups_every_day_and_preserves_empty_days():
    activity = SimpleNamespace(
        id=3,
        day_number=2,
        name="Museo",
        location="Centro",
        start_time=time(10),
        completed=True,
        order=1,
    )
    current_trip = trip(total_days=3, end_date=date(2026, 9, 3))
    timeline = timeline_service.build_trip_timeline(current_trip, [activity])
    assert len(timeline.days) == 3
    assert timeline.days[0].activities == []
    assert timeline.days[1].activities[0].name == "Museo"


def test_timeline_requires_completed_trip():
    with pytest.raises(TripNotCompletedError):
        timeline_service.validate_completed_trip(trip(status=TripStatus.IN_PROGRESS))

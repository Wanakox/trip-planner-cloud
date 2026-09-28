"""Validation tests for every mutable API resource schema."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.accommodation import AccommodationCreate
from app.schemas.activity import ActivityCreate, ActivityOrderUpdate
from app.schemas.expense import ExpenseCreate
from app.schemas.note import NoteCreate
from app.schemas.participant import ParticipantCreate
from app.schemas.task import TaskCreate, TaskOrderUpdate
from app.schemas.transport import TransportCreate
from app.schemas.trip import DestinationCreate, DestinationOrderUpdate, TripCreate
from app.schemas.user import UserCreate

VALID_CASES = [
    (
        UserCreate,
        {
            "name": " Juan ",
            "surname": " García ",
            "username": " juan.g ",
            "email": "juan@example.com",
            "password": "password123",
            "default_currency": "eur",
        },
        {"name": "Juan", "username": "juan.g", "default_currency": "EUR"},
    ),
    (
        DestinationCreate,
        {"country": " España ", "city": " Madrid ", "currency": "eur"},
        {"country": "España", "city": "Madrid", "currency": "EUR"},
    ),
    (
        ActivityCreate,
        {"name": " Museo ", "location": " Centro ", "day_number": 1},
        {"name": "Museo", "location": "Centro"},
    ),
    (ParticipantCreate, {"name": " Ana "}, {"name": "Ana"}),
    (TaskCreate, {"name": " Pasaporte ", "priority": "high"}, {"name": "Pasaporte"}),
    (
        NoteCreate,
        {"title": " Día 1 ", "text": " Genial ", "day_number": 1},
        {"title": "Día 1", "text": "Genial"},
    ),
    (
        ExpenseCreate,
        {
            "participant_id": 1,
            "name": " Cena ",
            "amount": "12.50",
            "category": "food",
            "currency": "eur",
            "expense_date": "2026-09-01",
        },
        {"name": "Cena", "currency": "EUR"},
    ),
]


@pytest.mark.parametrize(("schema", "payload", "expected"), VALID_CASES)
def test_schemas_normalize_valid_input(schema, payload: dict, expected: dict) -> None:
    instance = schema.model_validate(payload)
    for field, value in expected.items():
        assert getattr(instance, field) == value


INVALID_CASES = [
    (
        UserCreate,
        {
            "name": " ",
            "surname": "G",
            "username": "juan",
            "email": "juan@example.com",
            "password": "password123",
        },
    ),
    (DestinationCreate, {"country": "Spain", "city": " ", "currency": "EUR"}),
    (ActivityCreate, {"name": " ", "day_number": 1}),
    (ActivityCreate, {"name": "Museum", "day_number": 0}),
    (ParticipantCreate, {"name": " "}),
    (TaskCreate, {"name": " "}),
    (NoteCreate, {"title": "Title", "text": " "}),
    (
        ExpenseCreate,
        {
            "participant_id": 0,
            "name": "Dinner",
            "amount": 1,
            "category": "food",
            "currency": "EUR",
            "expense_date": "2026-09-01",
        },
    ),
    (
        ExpenseCreate,
        {
            "participant_id": 1,
            "name": "Dinner",
            "amount": 0,
            "category": "food",
            "currency": "EUR",
            "expense_date": "2026-09-01",
        },
    ),
    (
        AccommodationCreate,
        {
            "name": "Hotel",
            "address": "Street",
            "check_in_date": "2026-09-02",
            "check_out_date": "2026-09-01",
        },
    ),
    (
        TransportCreate,
        {
            "transport_type": "plane",
            "departure_date": "2026-09-02",
            "arrival_date": "2026-09-01",
            "origin": "MAD",
            "destination": "ATH",
        },
    ),
    (
        TripCreate,
        {
            "name": "Trip",
            "origin": "Madrid",
            "start_date": "2026-09-02",
            "end_date": "2026-09-01",
            "budget": 100,
            "destinations": [{"country": "Greece", "city": "Athens", "currency": "EUR"}],
        },
    ),
]


@pytest.mark.parametrize(("schema", "payload"), INVALID_CASES)
def test_schemas_reject_invalid_input(schema, payload: dict) -> None:
    with pytest.raises(ValidationError):
        schema.model_validate(payload)


@pytest.mark.parametrize(
    ("schema", "payload"),
    [
        (TaskOrderUpdate, {"tasks": [{"id": 1, "order": 1}, {"id": 1, "order": 2}]}),
        (TaskOrderUpdate, {"tasks": [{"id": 1, "order": 1}, {"id": 2, "order": 3}]}),
        (
            ActivityOrderUpdate,
            {
                "activities": [
                    {"id": 1, "day_number": 1, "order": 1},
                    {"id": 2, "day_number": 1, "order": 1},
                ]
            },
        ),
        (DestinationOrderUpdate, {"destinations": [{"id": 1, "order": 1}, {"id": 1, "order": 2}]}),
    ],
)
def test_order_schemas_reject_duplicates_and_gaps(schema, payload: dict) -> None:
    with pytest.raises(ValidationError):
        schema.model_validate(payload)


def test_trip_create_accepts_valid_dates_and_destination() -> None:
    trip = TripCreate.model_validate(
        {
            "name": "Greece",
            "origin": "Madrid",
            "start_date": date(2026, 9, 1),
            "end_date": date(2026, 9, 7),
            "budget": "1000.00",
            "destinations": [{"country": "Greece", "city": "Athens", "currency": "EUR"}],
        }
    )
    assert trip.end_date >= trip.start_date
    assert len(trip.destinations) == 1

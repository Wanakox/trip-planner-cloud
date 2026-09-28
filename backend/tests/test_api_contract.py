"""Cross-cutting API contract, authentication, and request validation tests."""

from datetime import date, timedelta

import pytest

from app.main import app

EXPECTED_OPERATIONS = {
    ("GET", "/api/v1/health"),
    ("POST", "/api/v1/auth/register"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/refresh"),
    ("GET", "/api/v1/users/me"),
    ("PATCH", "/api/v1/users/me"),
    ("DELETE", "/api/v1/users/me"),
    ("GET", "/api/v1/users/me/profile-photo"),
    ("POST", "/api/v1/users/me/profile-photo"),
    ("DELETE", "/api/v1/users/me/profile-photo"),
    ("GET", "/api/v1/trips"),
    ("POST", "/api/v1/trips"),
    ("GET", "/api/v1/trips/{trip_id}"),
    ("PATCH", "/api/v1/trips/{trip_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}"),
    ("PUT", "/api/v1/trips/{trip_id}/rating"),
    ("POST", "/api/v1/trips/{trip_id}/destinations"),
    ("PATCH", "/api/v1/trips/{trip_id}/destinations/{destination_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/destinations/{destination_id}"),
    ("PUT", "/api/v1/trips/{trip_id}/destinations/order"),
    ("GET", "/api/v1/trips/{trip_id}/activities"),
    ("POST", "/api/v1/trips/{trip_id}/activities"),
    ("PATCH", "/api/v1/trips/{trip_id}/activities/{activity_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/activities/{activity_id}"),
    ("PUT", "/api/v1/trips/{trip_id}/activities/{activity_id}/completed"),
    ("PUT", "/api/v1/trips/{trip_id}/activities/order"),
    ("GET", "/api/v1/trips/{trip_id}/transports"),
    ("POST", "/api/v1/trips/{trip_id}/transports"),
    ("PATCH", "/api/v1/trips/{trip_id}/transports/{transport_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/transports/{transport_id}"),
    ("GET", "/api/v1/trips/{trip_id}/accommodations"),
    ("POST", "/api/v1/trips/{trip_id}/accommodations"),
    ("PATCH", "/api/v1/trips/{trip_id}/accommodations/{accommodation_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/accommodations/{accommodation_id}"),
    ("GET", "/api/v1/trips/{trip_id}/participants"),
    ("POST", "/api/v1/trips/{trip_id}/participants"),
    ("PATCH", "/api/v1/trips/{trip_id}/participants/{participant_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/participants/{participant_id}"),
    ("GET", "/api/v1/trips/{trip_id}/expenses"),
    ("GET", "/api/v1/trips/{trip_id}/expenses/summary"),
    ("POST", "/api/v1/trips/{trip_id}/expenses"),
    ("PATCH", "/api/v1/trips/{trip_id}/expenses/{expense_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/expenses/{expense_id}"),
    ("GET", "/api/v1/trips/{trip_id}/checklist"),
    ("POST", "/api/v1/trips/{trip_id}/tasks"),
    ("PATCH", "/api/v1/trips/{trip_id}/tasks/{task_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/tasks/{task_id}"),
    ("PUT", "/api/v1/trips/{trip_id}/tasks/{task_id}/completed"),
    ("PUT", "/api/v1/trips/{trip_id}/tasks/order"),
    ("GET", "/api/v1/trips/{trip_id}/notes"),
    ("POST", "/api/v1/trips/{trip_id}/notes"),
    ("PATCH", "/api/v1/trips/{trip_id}/notes/{note_id}"),
    ("DELETE", "/api/v1/trips/{trip_id}/notes/{note_id}"),
    ("GET", "/api/v1/trips/{trip_id}/files"),
    ("POST", "/api/v1/trips/{trip_id}/files"),
    ("GET", "/api/v1/trips/{trip_id}/files/{file_id}/content"),
    ("DELETE", "/api/v1/trips/{trip_id}/files/{file_id}"),
    ("GET", "/api/v1/trips/{trip_id}/timeline"),
    ("GET", "/api/v1/trips/{trip_id}/export"),
    ("GET", "/api/v1/currencies"),
    ("GET", "/api/v1/currencies/convert"),
    ("GET", "/api/v1/flights/search"),
}


def _operations_from_openapi() -> set[tuple[str, str]]:
    methods = {"get", "post", "put", "patch", "delete"}
    return {
        (method.upper(), path)
        for path, definition in app.openapi()["paths"].items()
        for method in definition
        if method in methods
    }


def test_openapi_exposes_every_expected_operation() -> None:
    assert _operations_from_openapi() == EXPECTED_OPERATIONS


def test_operation_ids_are_unique() -> None:
    ids = [
        operation["operationId"]
        for definition in app.openapi()["paths"].values()
        for method, operation in definition.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert len(ids) == len(set(ids))


PROTECTED_REQUESTS = [
    ("get", "/api/v1/users/me"),
    ("delete", "/api/v1/users/me"),
    ("get", "/api/v1/users/me/profile-photo"),
    ("get", "/api/v1/trips"),
    ("get", "/api/v1/trips/1"),
    ("get", "/api/v1/trips/1/activities"),
    ("get", "/api/v1/trips/1/transports"),
    ("get", "/api/v1/trips/1/accommodations"),
    ("get", "/api/v1/trips/1/participants"),
    ("get", "/api/v1/trips/1/expenses"),
    ("get", "/api/v1/trips/1/checklist"),
    ("get", "/api/v1/trips/1/notes"),
    ("get", "/api/v1/trips/1/files"),
    ("get", "/api/v1/trips/1/files/1/content"),
    ("get", "/api/v1/trips/1/timeline"),
    ("get", "/api/v1/trips/1/export"),
]


@pytest.mark.parametrize(("method", "path"), PROTECTED_REQUESTS)
def test_protected_api_groups_reject_missing_token(client, method: str, path: str) -> None:
    response = getattr(client, method)(path)
    assert response.status_code in {401, 403}


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/api/v1/currencies/convert", {}),
        ("/api/v1/currencies/convert", {"amount": 0, "from_currency": "EUR", "to_currency": "USD"}),
        ("/api/v1/currencies/convert", {"amount": 1, "from_currency": "EU", "to_currency": "USD"}),
        ("/api/v1/flights/search", {}),
        (
            "/api/v1/flights/search",
            {"origin": "MA", "destination": "ATH", "departure_date": date.today()},
        ),
        (
            "/api/v1/flights/search",
            {"origin": "MAD", "destination": "ATH", "departure_date": date.today(), "adults": 10},
        ),
    ],
)
def test_public_query_validation_returns_422(client, path: str, params: dict) -> None:
    assert client.get(path, params=params).status_code == 422


@pytest.mark.parametrize(
    ("params", "detail"),
    [
        (
            {"origin": "MAD", "destination": "mad", "departure_date": date.today()},
            "Origin and destination must be different",
        ),
        (
            {
                "origin": "MAD",
                "destination": "ATH",
                "departure_date": date.today() - timedelta(days=1),
            },
            "Departure date cannot be in the past",
        ),
        (
            {
                "origin": "MAD",
                "destination": "ATH",
                "departure_date": date.today() + timedelta(days=2),
                "return_date": date.today() + timedelta(days=1),
            },
            "Return date cannot be before departure date",
        ),
    ],
)
def test_flight_business_validation_returns_400(client, params: dict, detail: str) -> None:
    response = client.get("/api/v1/flights/search", params=params)
    assert response.status_code == 400
    assert response.json()["detail"] == detail


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/v1/auth/register", {}),
        (
            "/api/v1/auth/register",
            {"name": "A", "surname": "B", "username": "ab", "email": "bad", "password": "short"},
        ),
        ("/api/v1/auth/login", {}),
        ("/api/v1/auth/login", {"identifier": "ab", "password": "short"}),
        ("/api/v1/auth/refresh", {}),
    ],
)
def test_auth_body_validation_returns_422(client, path: str, payload: dict) -> None:
    assert client.post(path, json=payload).status_code == 422

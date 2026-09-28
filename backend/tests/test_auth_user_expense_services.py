from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyRegisteredError,
)
from app.schemas.currency import CurrencyConversionResponse
from app.services import auth_service, expense_service, user_service


def test_authenticate_rejects_unknown_user_and_bad_password(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_identifier", lambda **kwargs: None)
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate_user(object(), "nadie", "clave")

    user = SimpleNamespace(hashed_password="hash")
    monkeypatch.setattr(auth_service, "get_user_by_identifier", lambda **kwargs: user)
    monkeypatch.setattr(auth_service, "verify_password", lambda **kwargs: False)
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate_user(object(), "ana", "incorrecta")


def test_authenticate_and_login_return_user_tokens(monkeypatch):
    user = SimpleNamespace(id=7, hashed_password="hash")
    monkeypatch.setattr(auth_service, "get_user_by_identifier", lambda **kwargs: user)
    monkeypatch.setattr(auth_service, "verify_password", lambda **kwargs: True)
    assert auth_service.authenticate_user(object(), "ana", "correcta") is user
    monkeypatch.setattr(auth_service, "create_access_token", lambda subject: f"access-{subject}")
    monkeypatch.setattr(auth_service, "create_refresh_token", lambda subject: f"refresh-{subject}")
    assert auth_service.login_user(object(), "ana", "correcta") == ("access-7", "refresh-7")


def test_refresh_uses_subject_from_refresh_token(monkeypatch):
    monkeypatch.setattr(auth_service, "decode_refresh_token", lambda token: {"sub": "9"})
    monkeypatch.setattr(auth_service, "create_access_token", lambda subject: f"new-{subject}")
    assert auth_service.refresh_access_token("refresh") == "new-9"


def test_profile_rejects_email_and_username_owned_by_another_user(monkeypatch):
    user = SimpleNamespace(id=1, email="a@test.es", username="ana", default_currency="EUR")
    data = SimpleNamespace(model_dump=lambda **kwargs: {"email": "used@test.es"})
    monkeypatch.setattr(user_service, "get_user_by_email", lambda **kwargs: SimpleNamespace(id=2))
    with pytest.raises(EmailAlreadyRegisteredError):
        user_service.update_current_user(object(), user, data)

    data = SimpleNamespace(model_dump=lambda **kwargs: {"username": "used"})
    monkeypatch.setattr(
        user_service, "get_user_by_username", lambda **kwargs: SimpleNamespace(id=2)
    )
    with pytest.raises(UsernameAlreadyRegisteredError):
        user_service.update_current_user(object(), user, data)


def test_currency_change_converts_every_trip_once_per_source_currency(monkeypatch):
    user = SimpleNamespace(id=1, default_currency="EUR")
    trips = [
        SimpleNamespace(currency="EUR", budget=Decimal("100.00")),
        SimpleNamespace(currency="EUR", budget=Decimal("50.00")),
        SimpleNamespace(currency="GBP", budget=Decimal("10.00")),
    ]
    data = SimpleNamespace(model_dump=lambda **kwargs: {"default_currency": "USD"})
    calls = []
    monkeypatch.setattr(user_service, "validate_currency_code", lambda value: value.upper())
    monkeypatch.setattr(user_service, "get_trips_by_user_id", lambda **kwargs: trips)

    def convert(**kwargs):
        calls.append(kwargs["from_currency"])
        rate = Decimal("2") if kwargs["from_currency"] == "EUR" else Decimal("3")
        return SimpleNamespace(rate=rate)

    monkeypatch.setattr(user_service, "convert_currency", convert)
    monkeypatch.setattr(user_service, "update_user", lambda **kwargs: kwargs["user"])
    updated = user_service.update_current_user(object(), user, data)
    assert sorted(calls) == ["EUR", "GBP"]
    assert [item.budget for item in trips] == [
        Decimal("200.00"),
        Decimal("100.00"),
        Decimal("30.00"),
    ]
    assert all(item.currency == "USD" for item in trips)
    assert updated.default_currency == "USD"


def test_expense_summary_converts_and_groups_by_participant(monkeypatch):
    trip = SimpleNamespace(id=1, currency="EUR", budget=Decimal("100.00"))
    expenses = [
        SimpleNamespace(
            currency="EUR",
            amount=Decimal("20"),
            participant_id=2,
            participant=SimpleNamespace(name="Zoe"),
        ),
        SimpleNamespace(
            currency="USD",
            amount=Decimal("10"),
            participant_id=1,
            participant=SimpleNamespace(name="Ana"),
        ),
        SimpleNamespace(
            currency="USD",
            amount=Decimal("5"),
            participant_id=1,
            participant=SimpleNamespace(name="Ana"),
        ),
    ]
    monkeypatch.setattr(expense_service, "get_trip_or_raise", lambda **kwargs: trip)
    monkeypatch.setattr(expense_service, "get_expenses_by_trip_id", lambda **kwargs: expenses)
    calls = []

    def convert(**kwargs):
        calls.append(kwargs["from_currency"])
        return CurrencyConversionResponse(
            amount=Decimal("1"),
            from_currency="USD",
            to_currency="EUR",
            rate=Decimal("0.5"),
            result=Decimal("0.5"),
            rate_date="2026-08-30",
        )

    monkeypatch.setattr(expense_service, "convert_currency", convert)
    summary = expense_service.get_trip_expense_summary(object(), 1, SimpleNamespace(id=3))
    assert calls == ["USD"]
    assert summary.total_expenses == Decimal("27.50")
    assert summary.remaining_budget == Decimal("72.50")
    assert [item.participant_name for item in summary.participants] == ["Ana", "Zoe"]

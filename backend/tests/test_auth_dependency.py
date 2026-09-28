"""Authentication dependency error and success paths."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api import dependencies


def credentials(token: str = "token") -> SimpleNamespace:
    return SimpleNamespace(credentials=token)


@pytest.mark.parametrize(
    "payload",
    [{}, {"sub": None}, {"sub": "not-an-int"}],
)
def test_current_user_rejects_invalid_subject(monkeypatch, payload: dict) -> None:
    monkeypatch.setattr(dependencies, "decode_access_token", lambda _: payload)
    with pytest.raises(HTTPException) as raised:
        dependencies.get_current_user(credentials(), object())
    assert raised.value.status_code == 401
    assert raised.value.headers == {"WWW-Authenticate": "Bearer"}


def test_current_user_rejects_deleted_user(monkeypatch) -> None:
    monkeypatch.setattr(dependencies, "decode_access_token", lambda _: {"sub": "7"})
    monkeypatch.setattr(dependencies, "get_user_by_id", lambda **_: None)
    with pytest.raises(HTTPException) as raised:
        dependencies.get_current_user(credentials(), object())
    assert raised.value.status_code == 401


def test_current_user_returns_repository_user(monkeypatch) -> None:
    user = SimpleNamespace(id=7)
    monkeypatch.setattr(dependencies, "decode_access_token", lambda _: {"sub": "7"})
    monkeypatch.setattr(dependencies, "get_user_by_id", lambda **_: user)
    assert dependencies.get_current_user(credentials(), object()) is user

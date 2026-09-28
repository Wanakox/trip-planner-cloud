"""Password and JWT security tests."""

from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


def test_password_hash_is_salted_and_verifiable() -> None:
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")
    assert first != second
    assert verify_password("correct horse battery staple", first)
    assert not verify_password("wrong password", first)


@pytest.mark.parametrize(
    ("factory", "decoder"),
    [(create_access_token, decode_access_token), (create_refresh_token, decode_refresh_token)],
)
def test_token_round_trip(factory, decoder) -> None:
    assert decoder(factory("42"))["sub"] == "42"


def test_access_and_refresh_tokens_cannot_be_interchanged() -> None:
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(create_refresh_token("42"))
    with pytest.raises(jwt.InvalidTokenError):
        decode_refresh_token(create_access_token("42"))


@pytest.mark.parametrize("decoder", [decode_access_token, decode_refresh_token])
def test_expired_tokens_are_rejected(decoder) -> None:
    factory = create_access_token if decoder is decode_access_token else create_refresh_token
    with pytest.raises(jwt.ExpiredSignatureError):
        decoder(factory("42", expires_delta=timedelta(seconds=-1)))


@pytest.mark.parametrize("decoder", [decode_access_token, decode_refresh_token])
def test_tampered_tokens_are_rejected(decoder) -> None:
    token = create_access_token("42")
    head, payload, signature = token.split(".")
    replacement = "A" if signature[-1] != "A" else "B"
    with pytest.raises(jwt.InvalidTokenError):
        decoder(".".join((head, payload, signature[:-1] + replacement)))

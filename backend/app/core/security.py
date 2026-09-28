from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Genera un hash seguro a partir de una contraseña."""

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Comprueba si una contraseña coincide con un hash."""

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.access_token_expire_minutes,
        )

    expires_at = datetime.now(UTC) + expires_delta

    payload = {
        "sub": subject,
        "type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(
            days=settings.refresh_token_expire_days,
        )

    expires_at = datetime.now(UTC) + expires_delta

    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """Valida y decodifica un access token."""

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": [
                "sub",
                "type",
                "exp",
            ],
        },
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError

    return payload


def decode_refresh_token(
    token: str,
) -> dict[str, Any]:
    """Valida y decodifica un refresh token."""

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": [
                "sub",
                "type",
                "exp",
            ],
        },
    )

    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError

    return payload
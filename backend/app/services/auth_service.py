from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyRegisteredError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_username,
)
from app.schemas.user import UserCreate


def register_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    normalized_email = str(
        user_data.email
    ).strip().lower()

    existing_email_user = get_user_by_email(
        db=db,
        email=normalized_email,
    )

    if existing_email_user is not None:
        raise EmailAlreadyRegisteredError

    existing_username_user = get_user_by_username(
        db=db,
        username=user_data.username,
    )

    if existing_username_user is not None:
        raise UsernameAlreadyRegisteredError

    user = User(
        name=user_data.name,
        surname=user_data.surname,
        profile_photo=user_data.profile_photo,
        username=user_data.username,
        email=normalized_email,
        default_currency=user_data.default_currency,
        hashed_password=hash_password(
            user_data.password
        ),
    )

    return create_user(
        db=db,
        user=user,
    )


def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
) -> User:
    user = get_user_by_identifier(
        db=db,
        identifier=identifier,
    )

    if user is None:
        raise InvalidCredentialsError

    password_is_valid = verify_password(
        plain_password=password,
        hashed_password=user.hashed_password,
    )

    if not password_is_valid:
        raise InvalidCredentialsError

    return user


def login_user(
    db: Session,
    identifier: str,
    password: str,
) -> tuple[str, str]:
    user = authenticate_user(
        db=db,
        identifier=identifier,
        password=password,
    )

    subject = str(user.id)

    access_token = create_access_token(
        subject=subject,
    )

    refresh_token = create_refresh_token(
        subject=subject,
    )

    return access_token, refresh_token


def refresh_access_token(
    refresh_token: str,
) -> str:
    payload = decode_refresh_token(
        refresh_token
    )

    subject = payload["sub"]

    return create_access_token(
        subject=subject,
    )
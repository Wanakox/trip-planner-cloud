from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    statement = select(User).where(
        User.email == email
    )

    return db.scalar(statement)


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    statement = select(User).where(
        User.username == username
    )

    return db.scalar(statement)


def get_user_by_identifier(
    db: Session,
    identifier: str,
) -> User | None:
    normalized_identifier = (
        identifier.strip()
    )

    statement = select(User).where(
        or_(
            User.email == normalized_identifier.lower(),
            User.username == normalized_identifier,
        )
    )

    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return db.get(
        User,
        user_id,
    )


def create_user(
    db: Session,
    user: User,
) -> User:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


def update_user(
    db: Session,
    user: User,
) -> User:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


def delete_user(
    db: Session,
    user: User,
) -> None:
    try:
        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise
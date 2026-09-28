from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    UsernameAlreadyRegisteredError,
)
from app.models.user import User
from app.repositories.trip_repository import get_trips_by_user_id
from app.repositories.user_repository import (
    delete_user,
    get_user_by_email,
    get_user_by_username,
    update_user,
)
from app.schemas.user import UserUpdate
from app.services.currency_service import (
    convert_currency,
    validate_currency_code,
)
from app.core.storage import delete_profile_image, save_profile_image


def update_current_user(
    db: Session,
    user: User,
    user_data: UserUpdate,
) -> User:
    update_data = user_data.model_dump(
        exclude_unset=True,
    )

    # La foto solo puede cambiarse mediante el endpoint de subida validada.
    update_data.pop("profile_photo", None)

    if "email" in update_data:
        normalized_email = str(
            update_data["email"]
        ).strip().lower()

        existing_user = get_user_by_email(
            db=db,
            email=normalized_email,
        )

        if (
            existing_user is not None
            and existing_user.id != user.id
        ):
            raise EmailAlreadyRegisteredError

        update_data["email"] = normalized_email

    if "username" in update_data:
        existing_user = get_user_by_username(
            db=db,
            username=update_data["username"],
        )

        if (
            existing_user is not None
            and existing_user.id != user.id
        ):
            raise UsernameAlreadyRegisteredError

    if "default_currency" in update_data:
        target_currency = (
            validate_currency_code(
                update_data["default_currency"]
            )
        )
        update_data["default_currency"] = target_currency

        trips = get_trips_by_user_id(db=db, user_id=user.id)
        conversion_rates: dict[str, Decimal] = {}

        # Calculamos todas las conversiones antes de modificar entidades para
        # que un fallo del proveedor no deje datos parcialmente actualizados.
        for source_currency in {
            trip.currency.upper()
            for trip in trips
            if trip.currency.upper() != target_currency
        }:
            conversion_rates[source_currency] = convert_currency(
                amount=Decimal("1"),
                from_currency=source_currency,
                to_currency=target_currency,
            ).rate

        for trip in trips:
            source_currency = trip.currency.upper()
            if source_currency != target_currency:
                trip.budget = (
                    trip.budget * conversion_rates[source_currency]
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            trip.currency = target_currency

    for field, value in update_data.items():
        setattr(
            user,
            field,
            value,
        )

    return update_user(
        db=db,
        user=user,
    )


async def upload_current_user_photo(
    db: Session,
    user: User,
    photo: UploadFile,
) -> User:
    previous_photo = user.profile_photo
    new_photo = await save_profile_image(photo, user.id)
    user.profile_photo = new_photo

    try:
        updated_user = update_user(db=db, user=user)
    except Exception:
        delete_profile_image(new_photo)
        raise

    if previous_photo:
        try:
            delete_profile_image(previous_photo)
        except (OSError, ValueError):
            pass
    return updated_user


def get_current_user_photo_path(user: User) -> Path | None:
    if not user.profile_photo:
        return None
    photo_path = Path(user.profile_photo).resolve()
    if not photo_path.is_file():
        return None
    return photo_path


def remove_current_user_photo(db: Session, user: User) -> None:
    photo_path = user.profile_photo
    user.profile_photo = None
    update_user(db=db, user=user)
    if photo_path:
        try:
            delete_profile_image(photo_path)
        except (OSError, ValueError):
            pass


def delete_current_user(
    db: Session,
    user: User,
) -> None:
    photo_path = user.profile_photo
    delete_user(
        db=db,
        user=user,
    )
    if photo_path:
        try:
            delete_profile_image(photo_path)
        except (OSError, ValueError):
            pass

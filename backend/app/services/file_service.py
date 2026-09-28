from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import (
    TripFileLimitExceededError,
    TripFileNotFoundError,
    TripFileStorageError,
    TripNotCompletedError,
    TripNotFoundError,
)
from app.core.storage import (
    delete_stored_file,
    save_upload_file,
)
from app.models.file import TripFile
from app.models.trip import (
    Trip,
    TripStatus,
)
from app.models.user import User
from app.repositories.file_repository import (
    count_trip_files_by_trip_id,
    create_trip_files,
    delete_trip_file,
    get_trip_file_by_id_and_trip_id,
    get_trip_files_by_trip_id,
    get_user_trip,
)


MAX_TRIP_FILES = 10


def get_trip_or_raise(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip:
    """
    Obtiene un viaje perteneciente al usuario autenticado.
    """

    trip = get_user_trip(
        db=db,
        trip_id=trip_id,
        user_id=user_id,
    )

    if trip is None:
        raise TripNotFoundError

    return trip


def get_trip_file_or_raise(
    db: Session,
    trip_id: int,
    file_id: int,
) -> TripFile:
    """
    Obtiene un archivo perteneciente al viaje indicado.
    """

    trip_file = get_trip_file_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        file_id=file_id,
    )

    if trip_file is None:
        raise TripFileNotFoundError

    return trip_file


def validate_completed_trip(
    trip: Trip,
) -> None:
    """
    Comprueba que el viaje está completado.
    """

    if trip.status != TripStatus.COMPLETED:
        raise TripNotCompletedError


def validate_trip_file_limit(
    current_file_count: int,
    new_file_count: int,
) -> None:
    """
    Comprueba que la subida no supera el límite
    máximo de archivos del viaje.
    """

    if (
        current_file_count
        + new_file_count
        > MAX_TRIP_FILES
    ):
        raise TripFileLimitExceededError


def remove_saved_files(
    file_paths: list[str],
) -> None:
    """
    Elimina los archivos físicos creados durante
    una operación de subida fallida.
    """

    for file_path in file_paths:
        try:
            delete_stored_file(
                file_path=file_path,
            )

        except Exception:
            # La limpieza es de mejor esfuerzo.
            # No debe ocultar la excepción original.
            pass


def get_files_from_trip(
    db: Session,
    trip_id: int,
    user: User,
) -> list[TripFile]:
    """
    Obtiene los archivos asociados a un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_completed_trip(
        trip=trip,
    )

    return get_trip_files_by_trip_id(
        db=db,
        trip_id=trip.id,
    )


async def add_files_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    files: list[UploadFile],
) -> list[TripFile]:
    """
    Guarda uno o varios archivos en un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_completed_trip(
        trip=trip,
    )

    current_file_count = count_trip_files_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    validate_trip_file_limit(
        current_file_count=current_file_count,
        new_file_count=len(files),
    )

    saved_file_paths: list[str] = []
    trip_files: list[TripFile] = []

    try:
        for uploaded_file in files:
            (
                original_name,
                stored_path,
                extension,
                size,
            ) = await save_upload_file(
                upload_file=uploaded_file,
                trip_id=trip.id,
            )

            saved_file_paths.append(
                stored_path
            )

            trip_files.append(
                TripFile(
                    trip_id=trip.id,
                    name=original_name,
                    path=stored_path,
                    extension=extension,
                    size=size,
                )
            )

    except Exception as exc:
        remove_saved_files(
            file_paths=saved_file_paths,
        )

        raise TripFileStorageError from exc

    try:
        return create_trip_files(
            db=db,
            trip_files=trip_files,
        )

    except Exception:
        remove_saved_files(
            file_paths=saved_file_paths,
        )
        raise


def delete_file_from_trip(
    db: Session,
    trip_id: int,
    file_id: int,
    user: User,
) -> None:
    """
    Elimina un archivo perteneciente a un viaje completado.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_completed_trip(
        trip=trip,
    )

    trip_file = get_trip_file_or_raise(
        db=db,
        trip_id=trip.id,
        file_id=file_id,
    )

    file_path = trip_file.path

    try:
        delete_stored_file(
            file_path=file_path,
        )

    except Exception as exc:
        raise TripFileStorageError from exc

    delete_trip_file(
        db=db,
        trip_file=trip_file,
    )

def get_trip_file_path(
    db: Session,
    trip_id: int,
    file_id: int,
    user: User,
) -> tuple[Path, TripFile]:
    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_completed_trip(
        trip=trip,
    )

    trip_file = get_trip_file_or_raise(
        db=db,
        trip_id=trip.id,
        file_id=file_id,
    )

    file_path = Path(trip_file.path)

    if not file_path.is_file():
        raise TripFileNotFoundError

    return file_path, trip_file
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.file import TripFile
from app.models.trip import Trip


def get_user_trip(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip | None:
    """
    Obtiene un viaje perteneciente al usuario indicado.
    """

    statement = select(Trip).where(
        Trip.id == trip_id,
        Trip.user_id == user_id,
    )

    return db.scalar(statement)


def get_trip_file_by_id_and_trip_id(
    db: Session,
    file_id: int,
    trip_id: int,
) -> TripFile | None:
    """
    Obtiene un archivo perteneciente al viaje indicado.
    """

    statement = select(TripFile).where(
        TripFile.id == file_id,
        TripFile.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_trip_files_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[TripFile]:
    """
    Obtiene todos los archivos asociados a un viaje.
    """

    statement = (
        select(TripFile)
        .where(
            TripFile.trip_id == trip_id,
        )
        .order_by(
            TripFile.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def count_trip_files_by_trip_id(
    db: Session,
    trip_id: int,
) -> int:
    """
    Cuenta los archivos asociados a un viaje.
    """

    statement = select(
        func.count(TripFile.id)
    ).where(
        TripFile.trip_id == trip_id,
    )

    return db.scalar(statement) or 0


def create_trip_files(
    db: Session,
    trip_files: list[TripFile],
) -> list[TripFile]:
    """
    Guarda varios archivos en una única transacción.
    """

    try:
        db.add_all(trip_files)
        db.commit()

        for trip_file in trip_files:
            db.refresh(trip_file)

        return trip_files

    except Exception:
        db.rollback()
        raise


def delete_trip_file(
    db: Session,
    trip_file: TripFile,
    commit: bool = True,
) -> None:
    """
    Marca un archivo para su eliminación.

    El parámetro commit permite coordinar la eliminación
    del registro con la eliminación física del archivo.
    """

    try:
        db.delete(trip_file)

        if commit:
            db.commit()

    except Exception:
        db.rollback()
        raise
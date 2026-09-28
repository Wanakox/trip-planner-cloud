import re
import shutil
import tempfile
from pathlib import Path
from zipfile import (
    ZIP_DEFLATED,
    ZipFile,
)

from sqlalchemy.orm import Session

from app.core.exceptions import (
    TripExportError,
    TripNotCompletedError,
    TripNotFoundError,
)
from app.models.trip import (
    Trip,
    TripStatus,
)
from app.models.user import User
from app.repositories.export_repository import get_trip_for_export
from app.services.pdf_generator import generate_trip_pdf
from app.services.timeline_service import build_trip_timeline


def get_trip_or_raise(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip:
    trip = get_trip_for_export(
        db=db,
        trip_id=trip_id,
        user_id=user_id,
    )

    if trip is None:
        raise TripNotFoundError

    return trip


def validate_completed_trip(
    trip: Trip,
) -> None:
    if trip.status != TripStatus.COMPLETED:
        raise TripNotCompletedError


def sanitize_filename(
    value: str,
) -> str:
    """
    Convierte un nombre de viaje en un nombre
    seguro para el archivo descargable.
    """

    normalized = value.strip().lower()

    normalized = re.sub(
        r"[^a-z0-9áéíóúüñ]+",
        "-",
        normalized,
    )

    normalized = normalized.strip("-")

    return normalized or "viaje"


def get_unique_archive_name(
    original_name: str,
    used_names: set[str],
) -> str:
    """
    Evita colisiones cuando existen varios archivos
    con el mismo nombre original.
    """

    safe_name = Path(original_name).name

    if safe_name not in used_names:
        used_names.add(safe_name)
        return safe_name

    path = Path(safe_name)
    stem = path.stem
    suffix = path.suffix

    counter = 2

    while True:
        candidate = (
            f"{stem}-{counter}{suffix}"
        )

        if candidate not in used_names:
            used_names.add(candidate)
            return candidate

        counter += 1


def add_trip_files_to_zip(
    zip_file: ZipFile,
    trip: Trip,
) -> None:
    """
    Añade al ZIP los archivos físicos que todavía
    existen en el almacenamiento.
    """

    used_names: set[str] = set()

    for trip_file in trip.files:
        source_path = Path(
            trip_file.path
        )

        if not source_path.is_file():
            continue

        archive_name = get_unique_archive_name(
            original_name=trip_file.name,
            used_names=used_names,
        )

        zip_file.write(
            filename=source_path,
            arcname=f"archivos/{archive_name}",
        )


def build_trip_export(
    db: Session,
    trip_id: int,
    user: User,
) -> tuple[Path, str, Path]:
    """
    Genera un PDF y lo empaqueta junto a los archivos
    adjuntos del viaje.

    Devuelve:
        zip_path:
            Ruta del ZIP generado.

        download_filename:
            Nombre que recibirá el usuario.

        temporary_directory:
            Directorio que debe eliminarse después
            de enviar la respuesta.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    validate_completed_trip(
        trip=trip,
    )

    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix=f"trip-export-{trip.id}-",
        )
    )

    safe_trip_name = sanitize_filename(
        trip.name
    )

    pdf_path = (
        temporary_directory
        / "resumen-viaje.pdf"
    )

    zip_path = (
        temporary_directory
        / f"{safe_trip_name}.zip"
    )

    try:
        timeline = build_trip_timeline(
            trip=trip,
            activities=list(trip.activities),
        )

        generate_trip_pdf(
            trip=trip,
            timeline=timeline,
            output_path=pdf_path,
        )

        with ZipFile(
            zip_path,
            mode="w",
            compression=ZIP_DEFLATED,
        ) as zip_file:
            zip_file.write(
                filename=pdf_path,
                arcname="resumen-viaje.pdf",
            )

            add_trip_files_to_zip(
                zip_file=zip_file,
                trip=trip,
            )

        download_filename = (
            f"{safe_trip_name}.zip"
        )

        return (
            zip_path,
            download_filename,
            temporary_directory,
        )

    except Exception as exc:
        shutil.rmtree(
            temporary_directory,
            ignore_errors=True,
        )

        raise TripExportError from exc


def delete_temporary_export(
    temporary_directory: Path,
) -> None:
    """
    Elimina el PDF y el ZIP temporales después
    de terminar la respuesta HTTP.
    """

    shutil.rmtree(
        temporary_directory,
        ignore_errors=True,
    )
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


CHUNK_SIZE = 1024 * 1024
PROFILE_IMAGE_MAX_SIZE = 5 * 1024 * 1024
PROFILE_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
}


def get_storage_root() -> Path:
    """
    Obtiene el directorio raíz donde se almacenan
    los archivos de los viajes.
    """

    return Path(
        settings.trip_files_storage_path
    ).resolve()


def get_profile_storage_root() -> Path:
    storage_root = Path(
        settings.profile_images_storage_path
    ).resolve()
    storage_root.mkdir(parents=True, exist_ok=True)
    return storage_root


def get_trip_storage_directory(
    trip_id: int,
) -> Path:
    """
    Obtiene y crea el directorio de almacenamiento
    correspondiente a un viaje.
    """

    trip_directory = (
        get_storage_root()
        / str(trip_id)
    )

    trip_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return trip_directory


def normalize_original_filename(
    filename: str | None,
) -> str:
    """
    Elimina cualquier componente de ruta del nombre
    recibido por el cliente.
    """

    if filename is None:
        return "file"

    normalized_filename = Path(
        filename
    ).name.strip()

    return normalized_filename or "file"


def get_file_extension(
    filename: str,
) -> str:
    """
    Obtiene la extensión del archivo sin el punto.
    """

    return Path(
        filename
    ).suffix.lower().lstrip(".")


async def save_upload_file(
    upload_file: UploadFile,
    trip_id: int,
) -> tuple[
    str,
    str,
    str,
    int,
]:
    """
    Guarda un UploadFile en el almacenamiento local.

    Devuelve:
    - nombre original
    - ruta física
    - extensión
    - tamaño en bytes
    """

    original_name = normalize_original_filename(
        upload_file.filename
    )

    extension = get_file_extension(
        original_name
    )

    stored_filename = str(
        uuid4()
    )

    if extension:
        stored_filename = (
            f"{stored_filename}.{extension}"
        )

    trip_directory = get_trip_storage_directory(
        trip_id=trip_id,
    )

    destination = (
        trip_directory
        / stored_filename
    )

    size = 0

    try:
        with destination.open("wb") as stored_file:
            while chunk := await upload_file.read(
                CHUNK_SIZE
            ):
                stored_file.write(chunk)
                size += len(chunk)

    except Exception:
        destination.unlink(
            missing_ok=True,
        )
        raise

    finally:
        await upload_file.close()

    return (
        original_name,
        str(destination),
        extension,
        size,
    )


def _has_valid_image_signature(content_type: str, header: bytes) -> bool:
    if content_type == "image/jpeg":
        return header.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    return False


async def save_profile_image(upload_file: UploadFile, user_id: int) -> str:
    """Valida y guarda la imagen de perfil del usuario."""

    content_type = (upload_file.content_type or "").lower()
    extension = PROFILE_IMAGE_TYPES.get(content_type)
    if extension is None:
        await upload_file.close()
        raise ValueError("Unsupported profile image type")

    destination = get_profile_storage_root() / f"{user_id}-{uuid4()}.{extension}"
    size = 0
    header = b""
    try:
        with destination.open("wb") as stored_file:
            while chunk := await upload_file.read(CHUNK_SIZE):
                if not header:
                    header = chunk[:12]
                size += len(chunk)
                if size > PROFILE_IMAGE_MAX_SIZE:
                    raise ValueError("Profile image is too large")
                stored_file.write(chunk)

        if not header or not _has_valid_image_signature(content_type, header):
            raise ValueError("Invalid profile image content")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload_file.close()

    return str(destination)


def delete_profile_image(file_path: str) -> None:
    storage_root = get_profile_storage_root()
    target_path = Path(file_path).resolve()
    if not target_path.is_relative_to(storage_root):
        raise ValueError("The profile image is outside the configured directory")
    target_path.unlink(missing_ok=True)


def delete_stored_file(
    file_path: str,
) -> None:
    """
    Elimina un archivo físico únicamente cuando
    pertenece al directorio configurado.
    """

    storage_root = get_storage_root()
    target_path = Path(
        file_path
    ).resolve()

    if not target_path.is_relative_to(
        storage_root
    ):
        raise ValueError(
            "The file path is outside "
            "the configured storage directory"
        )

    target_path.unlink(
        missing_ok=True,
    )

    remove_empty_parent_directory(
        directory=target_path.parent,
        storage_root=storage_root,
    )


def remove_empty_parent_directory(
    directory: Path,
    storage_root: Path,
) -> None:
    """
    Elimina el directorio del viaje cuando queda vacío.
    """

    if directory == storage_root:
        return

    try:
        directory.rmdir()

    except OSError:
        pass

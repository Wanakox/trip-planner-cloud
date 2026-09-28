from functools import lru_cache
from pathlib import Path, PurePosixPath
from uuid import uuid4

from fastapi import UploadFile
from supabase import create_client

from app.core.config import settings

BUCKET = "tripplanner-files"
CHUNK_SIZE = 1024 * 1024
MAX_TRIP_FILE_SIZE = 20 * 1024 * 1024
PROFILE_IMAGE_MAX_SIZE = 5 * 1024 * 1024
PROFILE_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
}


@lru_cache
def storage_bucket():
    client = create_client(
        settings.supabase_url,
        settings.supabase_secret_key,
    )
    return client.storage.from_(BUCKET)


def normalize_original_filename(filename: str | None) -> str:
    if filename is None:
        return "file"
    return Path(filename).name.strip() or "file"


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def _check_key(key: str, prefix: str) -> None:
    path = PurePosixPath(key)
    if (
        not key.startswith(prefix)
        or path.is_absolute()
        or ".." in path.parts
    ):
        raise ValueError("Invalid storage key")


async def _read_upload(upload_file: UploadFile, limit: int) -> bytes:
    data = bytearray()
    try:
        while chunk := await upload_file.read(CHUNK_SIZE):
            data.extend(chunk)
            if len(data) > limit:
                raise ValueError("File is too large")
        return bytes(data)
    finally:
        await upload_file.close()


def download_stored_file(key: str) -> bytes:
    _check_key(key, "trips/")
    return storage_bucket().download(key)


def download_profile_image(key: str) -> bytes:
    _check_key(key, "profiles/")
    return storage_bucket().download(key)


def delete_stored_file(file_path: str) -> None:
    _check_key(file_path, "trips/")
    storage_bucket().remove([file_path])


def delete_profile_image(file_path: str) -> None:
    _check_key(file_path, "profiles/")
    storage_bucket().remove([file_path])


async def save_upload_file(
    upload_file: UploadFile,
    trip_id: int,
) -> tuple[str, str, str, int]:
    original_name = normalize_original_filename(upload_file.filename)
    extension = get_file_extension(original_name)
    stored_name = str(uuid4())
    if extension:
        stored_name += f".{extension}"

    key = f"trips/{trip_id}/{stored_name}"
    content_type = upload_file.content_type or "application/octet-stream"
    data = await _read_upload(upload_file, MAX_TRIP_FILE_SIZE)

    storage_bucket().upload(
        path=key,
        file=data,
        file_options={"content-type": content_type},
    )
    return original_name, key, extension, len(data)


def _has_valid_image_signature(content_type: str, header: bytes) -> bool:
    if content_type == "image/jpeg":
        return header.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    return False


async def save_profile_image(
    upload_file: UploadFile,
    user_id: int,
) -> str:
    content_type = (upload_file.content_type or "").lower()
    extension = PROFILE_IMAGE_TYPES.get(content_type)
    if extension is None:
        await upload_file.close()
        raise ValueError("Unsupported profile image type")

    data = await _read_upload(upload_file, PROFILE_IMAGE_MAX_SIZE)
    if not data or not _has_valid_image_signature(
        content_type, data[:12]
    ):
        raise ValueError("Invalid profile image content")

    key = f"profiles/{user_id}-{uuid4()}.{extension}"
    storage_bucket().upload(
        path=key,
        file=data,
        file_options={"content-type": content_type},
    )
    return key
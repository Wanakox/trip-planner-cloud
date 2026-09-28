from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    TripExportError,
    TripNotCompletedError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.services.export_service import (
    build_trip_export,
    delete_temporary_export,
)


router = APIRouter(
    prefix="/trips/{trip_id}/export",
    tags=["exports"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Export a completed trip",
)
def export_trip(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> FileResponse:
    try:
        (
            zip_path,
            download_filename,
            temporary_directory,
        ) = build_trip_export(
            db=db,
            trip_id=trip_id,
            user=current_user,
        )

        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=download_filename,
            background=BackgroundTask(
                delete_temporary_export,
                temporary_directory,
            ),
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except TripNotCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only completed trips "
                "can be exported"
            ),
        ) from exc

    except TripExportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The trip export could not "
                "be generated"
            ),
        ) from exc
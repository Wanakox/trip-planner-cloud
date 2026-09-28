from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    TripNotCompletedError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.timeline import TimelineResponse
from app.services.timeline_service import get_trip_timeline


router = APIRouter(
    prefix="/trips/{trip_id}/timeline",
    tags=["timeline"],
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
    response_model=TimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the timeline of a trip",
)
def get_timeline(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TimelineResponse:
    try:
        return get_trip_timeline(
            db=db,
            trip_id=trip_id,
            user=current_user,
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
                "The timeline can only be accessed "
                "for completed trips"
            ),
        ) from exc
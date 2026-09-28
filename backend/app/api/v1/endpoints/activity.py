from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    ActivityNotFoundError,
    InvalidActivityDayError,
    InvalidActivityOrderError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.activity import (
    ActivityCompletionUpdate,
    ActivityCreate,
    ActivityOrderUpdate,
    ActivityResponse,
    ActivityUpdate,
)
from app.services.activity_service import (
    add_activity_to_trip,
    delete_activity_from_trip,
    list_trip_activities,
    reorder_trip_activities,
    set_activity_completion,
    update_activity_in_trip,
)


router = APIRouter(
    prefix="/trips/{trip_id}/activities",
    tags=["activities"],
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
    response_model=list[ActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all activities from a trip",
)
def get_trip_activities(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[ActivityResponse]:
    try:
        return list_trip_activities(
            db=db,
            trip_id=trip_id,
            user=current_user,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new activity to a trip",
)
def add_new_activity(
    trip_id: int,
    activity_data: ActivityCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ActivityResponse:
    try:
        return add_activity_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            activity_data=activity_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except InvalidActivityDayError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The activity day must be within "
                "the trip duration"
            ),
        ) from exc


@router.patch(
    "/{activity_id}",
    response_model=ActivityResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an activity from a trip",
)
def update_existing_activity(
    trip_id: int,
    activity_id: int,
    activity_data: ActivityUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ActivityResponse:
    try:
        return update_activity_in_trip(
            db=db,
            trip_id=trip_id,
            activity_id=activity_id,
            user=current_user,
            activity_data=activity_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        ) from exc

    except InvalidActivityDayError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The activity day must be within "
                "the trip duration"
            ),
        ) from exc


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an activity from a trip",
)
def delete_existing_activity(
    trip_id: int,
    activity_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_activity_from_trip(
            db=db,
            trip_id=trip_id,
            activity_id=activity_id,
            user=current_user,
        )

        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        ) from exc


@router.put(
    "/{activity_id}/completed",
    response_model=ActivityResponse,
    status_code=status.HTTP_200_OK,
    summary="Set the completion status of an activity",
)
def update_activity_completion(
    trip_id: int,
    activity_id: int,
    completion_data: ActivityCompletionUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ActivityResponse:
    try:
        return set_activity_completion(
            db=db,
            trip_id=trip_id,
            activity_id=activity_id,
            user=current_user,
            completion_data=completion_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except ActivityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        ) from exc


@router.put(
    "/order",
    response_model=list[ActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Reorder the activities of a trip",
)
def reorder_activities(
    trip_id: int,
    order_data: ActivityOrderUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[ActivityResponse]:
    try:
        return reorder_trip_activities(
            db=db,
            trip_id=trip_id,
            user=current_user,
            order_data=order_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except InvalidActivityDayError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "One or more activity days are outside "
                "the trip duration"
            ),
        ) from exc

    except InvalidActivityOrderError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The activity list must contain exactly "
                "all activities of the trip"
            ),
        ) from exc
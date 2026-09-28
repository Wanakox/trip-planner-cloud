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
    InvalidTaskOrderError,
    TaskNotFoundError,
    TripNotFoundError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.task import (
    TaskCompletionUpdate,
    TaskCreate,
    TaskOrderUpdate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import (
    add_task_to_trip,
    delete_task_from_trip,
    get_trip_checklist,
    reorder_trip_tasks,
    set_task_completion,
    update_task_in_trip,
)


router = APIRouter(
    prefix="/trips/{trip_id}",
    tags=["tasks"],
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
    "/checklist",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get the checklist from a trip",
)
def get_checklist(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[TaskResponse]:
    try:
        return get_trip_checklist(
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
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a task to a trip",
)
def add_new_task(
    trip_id: int,
    task_data: TaskCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TaskResponse:
    try:
        return add_task_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            task_data=task_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task from a trip",
)
def update_existing_task(
    trip_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TaskResponse:
    try:
        return update_task_in_trip(
            db=db,
            trip_id=trip_id,
            task_id=task_id,
            user=current_user,
            task_data=task_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        ) from exc


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task from a trip",
)
def delete_existing_task(
    trip_id: int,
    task_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_task_from_trip(
            db=db,
            trip_id=trip_id,
            task_id=task_id,
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

    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        ) from exc


@router.put(
    "/tasks/{task_id}/completed",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Set the completion status of a task",
)
def update_task_completion(
    trip_id: int,
    task_id: int,
    completion_data: TaskCompletionUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> TaskResponse:
    try:
        return set_task_completion(
            db=db,
            trip_id=trip_id,
            task_id=task_id,
            user=current_user,
            completion_data=completion_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        ) from exc


@router.put(
    "/tasks/order",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Reorder the tasks from a trip",
)
def reorder_tasks(
    trip_id: int,
    order_data: TaskOrderUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[TaskResponse]:
    try:
        return reorder_trip_tasks(
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

    except InvalidTaskOrderError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The task list must contain exactly "
                "all tasks from the trip with "
                "consecutive orders"
            ),
        ) from exc
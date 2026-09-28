from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvalidTaskOrderError,
    TaskNotFoundError,
    TripNotFoundError,
)
from app.models.task import Task
from app.models.trip import Trip
from app.models.user import User
from app.repositories.task_repository import (
    create_task,
    delete_task,
    flush_tasks,
    get_last_task_order,
    get_task_by_id_and_trip_id,
    get_tasks_by_trip_id,
    get_user_trip,
    save_tasks,
    update_task,
)
from app.schemas.task import (
    TaskCompletionUpdate,
    TaskCreate,
    TaskOrderUpdate,
    TaskUpdate,
)


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


def get_task_or_raise(
    db: Session,
    trip_id: int,
    task_id: int,
) -> Task:
    """
    Obtiene una tarea perteneciente al viaje indicado.
    """

    task = get_task_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        task_id=task_id,
    )

    if task is None:
        raise TaskNotFoundError

    return task


def get_trip_checklist(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Task]:
    """
    Obtiene la checklist completa de un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    return get_tasks_by_trip_id(
        db=db,
        trip_id=trip.id,
    )


def add_task_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    task_data: TaskCreate,
) -> Task:
    """
    Añade una tarea al final de la checklist.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    last_order = get_last_task_order(
        db=db,
        trip_id=trip.id,
    )

    task = Task(
        trip_id=trip.id,
        name=task_data.name,
        priority=task_data.priority,
        completed=False,
        order=last_order + 1,
    )

    return create_task(
        db=db,
        task=task,
    )


def update_task_in_trip(
    db: Session,
    trip_id: int,
    task_id: int,
    user: User,
    task_data: TaskUpdate,
) -> Task:
    """
    Actualiza parcialmente el nombre o la prioridad
    de una tarea.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    task = get_task_or_raise(
        db=db,
        trip_id=trip.id,
        task_id=task_id,
    )

    update_data = task_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        if value is None:
            continue

        setattr(
            task,
            field,
            value,
        )

    return update_task(
        db=db,
        task=task,
    )


def delete_task_from_trip(
    db: Session,
    trip_id: int,
    task_id: int,
    user: User,
) -> None:
    """
    Elimina una tarea y reajusta las posiciones
    de las tareas posteriores.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    task = get_task_or_raise(
        db=db,
        trip_id=trip.id,
        task_id=task_id,
    )

    deleted_order = task.order

    tasks = get_tasks_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    remaining_tasks = [
        current_task
        for current_task in tasks
        if current_task.id != task.id
    ]

    try:
        delete_task(
            db=db,
            task=task,
            commit=False,
        )

        db.flush()

        for current_task in remaining_tasks:
            if current_task.order > deleted_order:
                current_task.order -= 1

        db.commit()

    except Exception:
        db.rollback()
        raise


def set_task_completion(
    db: Session,
    trip_id: int,
    task_id: int,
    user: User,
    completion_data: TaskCompletionUpdate,
) -> Task:
    """
    Establece explícitamente el estado completado
    de una tarea.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    task = get_task_or_raise(
        db=db,
        trip_id=trip.id,
        task_id=task_id,
    )

    task.completed = completion_data.completed

    return update_task(
        db=db,
        task=task,
    )


def reorder_trip_tasks(
    db: Session,
    trip_id: int,
    user: User,
    order_data: TaskOrderUpdate,
) -> list[Task]:
    """
    Reemplaza el orden completo de las tareas del viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    tasks = get_tasks_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    current_task_ids = {
        task.id
        for task in tasks
    }

    received_task_ids = {
        task_data.id
        for task_data in order_data.tasks
    }

    if current_task_ids != received_task_ids:
        raise InvalidTaskOrderError

    tasks_by_id = {
        task.id: task
        for task in tasks
    }

    max_current_order = max(
        (
            task.order
            for task in tasks
        ),
        default=0,
    )

    temporary_offset = (
        max_current_order
        + len(tasks)
    )

    try:
        for index, task in enumerate(
            tasks,
            start=1,
        ):
            task.order = (
                temporary_offset
                + index
            )

        flush_tasks(
            db=db,
            tasks=tasks,
        )

        for task_data in order_data.tasks:
            task = tasks_by_id[
                task_data.id
            ]

            task.order = task_data.order

        save_tasks(
            db=db,
            tasks=tasks,
        )

    except Exception:
        db.rollback()
        raise

    return get_tasks_by_trip_id(
        db=db,
        trip_id=trip.id,
    )
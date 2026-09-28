from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session

from app.models.task import Task
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


def get_task_by_id_and_trip_id(
    db: Session,
    task_id: int,
    trip_id: int,
) -> Task | None:
    """
    Obtiene una tarea perteneciente al viaje indicado.
    """

    statement = select(Task).where(
        Task.id == task_id,
        Task.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_tasks_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Task]:
    """
    Obtiene la checklist de un viaje ordenada
    por la posición de las tareas.
    """

    statement = (
        select(Task)
        .where(
            Task.trip_id == trip_id,
        )
        .order_by(
            Task.order.asc(),
            Task.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_last_task_order(
    db: Session,
    trip_id: int,
) -> int:
    """
    Obtiene la última posición ocupada en la checklist.
    """

    statement = select(
        func.coalesce(
            func.max(Task.order),
            0,
        )
    ).where(
        Task.trip_id == trip_id,
    )

    return db.scalar(statement) or 0


def create_task(
    db: Session,
    task: Task,
) -> Task:
    """
    Guarda una tarea en la base de datos.
    """

    try:
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    except Exception:
        db.rollback()
        raise


def update_task(
    db: Session,
    task: Task,
) -> Task:
    """
    Guarda los cambios realizados sobre una tarea.
    """

    try:
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    except Exception:
        db.rollback()
        raise


def delete_task(
    db: Session,
    task: Task,
    commit: bool = True,
) -> None:
    """
    Marca una tarea para su eliminación.

    El parámetro commit permite continuar modificando
    otras tareas dentro de la misma transacción.
    """

    try:
        db.delete(task)

        if commit:
            db.commit()

    except Exception:
        db.rollback()
        raise


def save_tasks(
    db: Session,
    tasks: list[Task],
) -> list[Task]:
    """
    Guarda los cambios realizados sobre varias tareas.
    """

    try:
        for task in tasks:
            db.add(task)

        db.commit()

        for task in tasks:
            db.refresh(task)

        return tasks

    except Exception:
        db.rollback()
        raise


def flush_tasks(
    db: Session,
    tasks: list[Task],
) -> None:
    """
    Envía modificaciones temporales a la base de datos
    sin confirmar la transacción.
    """

    try:
        for task in tasks:
            db.add(task)

        db.flush()

    except Exception:
        db.rollback()
        raise
from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.expense import Expense
from app.models.participant import Participant
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


def get_participant_by_id_and_trip_id(
    db: Session,
    participant_id: int,
    trip_id: int,
) -> Participant | None:
    """
    Obtiene un participante perteneciente al viaje indicado.
    """

    statement = select(Participant).where(
        Participant.id == participant_id,
        Participant.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_expense_by_id_and_trip_id(
    db: Session,
    expense_id: int,
    trip_id: int,
) -> Expense | None:
    """
    Obtiene un gasto perteneciente al viaje indicado.
    """

    statement = select(Expense).where(
        Expense.id == expense_id,
        Expense.trip_id == trip_id,
    )

    return db.scalar(statement)


def get_expenses_by_trip_id(
    db: Session,
    trip_id: int,
) -> list[Expense]:
    """
    Obtiene los gastos asociados a un viaje,
    incluyendo el participante que realizó cada gasto.
    """

    statement = (
        select(Expense)
        .options(
            joinedload(Expense.participant),
        )
        .where(
            Expense.trip_id == trip_id,
        )
        .order_by(
            Expense.expense_date.asc(),
            Expense.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def create_expense(
    db: Session,
    expense: Expense,
) -> Expense:
    """
    Guarda un gasto en la base de datos.
    """

    try:
        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    except Exception:
        db.rollback()
        raise


def update_expense(
    db: Session,
    expense: Expense,
) -> Expense:
    """
    Guarda los cambios realizados sobre un gasto.
    """

    try:
        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    except Exception:
        db.rollback()
        raise


def delete_expense(
    db: Session,
    expense: Expense,
) -> None:
    """
    Elimina un gasto de la base de datos.
    """

    try:
        db.delete(expense)
        db.commit()

    except Exception:
        db.rollback()
        raise
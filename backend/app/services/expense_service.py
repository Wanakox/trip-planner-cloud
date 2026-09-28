from sqlalchemy.orm import Session

from app.core.exceptions import (
    ExpenseNotFoundError,
    ParticipantNotFoundError,
    TripNotFoundError,
)
from app.models.expense import Expense
from app.models.participant import Participant
from app.models.trip import Trip
from app.models.user import User
from app.repositories.expense_repository import (
    create_expense,
    delete_expense,
    get_expense_by_id_and_trip_id,
    get_expenses_by_trip_id,
    get_participant_by_id_and_trip_id,
    get_user_trip,
    update_expense,
)
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseSummaryResponse,
    ParticipantExpenseSummary,
)
from app.services.currency_service import convert_currency
from collections import defaultdict
from decimal import (
    ROUND_HALF_UP,
    Decimal,
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


def get_participant_or_raise(
    db: Session,
    trip_id: int,
    participant_id: int,
) -> Participant:
    """
    Obtiene un participante perteneciente al viaje indicado.
    """

    participant = get_participant_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        participant_id=participant_id,
    )

    if participant is None:
        raise ParticipantNotFoundError

    return participant


def get_expense_or_raise(
    db: Session,
    trip_id: int,
    expense_id: int,
) -> Expense:
    """
    Obtiene un gasto perteneciente al viaje indicado.
    """

    expense = get_expense_by_id_and_trip_id(
        db=db,
        trip_id=trip_id,
        expense_id=expense_id,
    )

    if expense is None:
        raise ExpenseNotFoundError

    return expense


def list_trip_expenses(
    db: Session,
    trip_id: int,
    user: User,
) -> list[Expense]:
    """
    Obtiene todos los gastos de un viaje.
    """

    get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    return get_expenses_by_trip_id(
        db=db,
        trip_id=trip_id,
    )


def add_expense_to_trip(
    db: Session,
    trip_id: int,
    user: User,
    expense_data: ExpenseCreate,
) -> Expense:
    """
    Añade un gasto a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    participant = get_participant_or_raise(
        db=db,
        trip_id=trip.id,
        participant_id=expense_data.participant_id,
    )

    expense = Expense(
        trip_id=trip.id,
        participant_id=participant.id,
        name=expense_data.name,
        amount=expense_data.amount,
        category=expense_data.category,
        currency=expense_data.currency,
        expense_date=expense_data.expense_date,
    )

    return create_expense(
        db=db,
        expense=expense,
    )


def update_expense_in_trip(
    db: Session,
    trip_id: int,
    expense_id: int,
    user: User,
    expense_data: ExpenseUpdate,
) -> Expense:
    """
    Actualiza parcialmente un gasto.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    expense = get_expense_or_raise(
        db=db,
        trip_id=trip.id,
        expense_id=expense_id,
    )

    update_data = expense_data.model_dump(
        exclude_unset=True,
    )

    final_participant_id = update_data.get(
        "participant_id",
        expense.participant_id,
    )

    final_expense_date = update_data.get(
        "expense_date",
        expense.expense_date,
    )

    get_participant_or_raise(
        db=db,
        trip_id=trip.id,
        participant_id=final_participant_id,
    )

    for field, value in update_data.items():
        setattr(
            expense,
            field,
            value,
        )

    return update_expense(
        db=db,
        expense=expense,
    )


def delete_expense_from_trip(
    db: Session,
    trip_id: int,
    expense_id: int,
    user: User,
) -> None:
    """
    Elimina un gasto perteneciente a un viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    expense = get_expense_or_raise(
        db=db,
        trip_id=trip.id,
        expense_id=expense_id,
    )

    delete_expense(
        db=db,
        expense=expense,
    )


def get_trip_expense_summary(
    db: Session,
    trip_id: int,
    user: User,
) -> ExpenseSummaryResponse:
    """
    Calcula el resumen económico del viaje convirtiendo
    todos los gastos a la moneda principal del viaje.
    """

    trip = get_trip_or_raise(
        db=db,
        trip_id=trip_id,
        user_id=user.id,
    )

    expenses = get_expenses_by_trip_id(
        db=db,
        trip_id=trip.id,
    )

    total_expenses = Decimal("0.00")

    totals_by_participant: dict[int, Decimal] = defaultdict(
        lambda: Decimal("0.00")
    )

    participant_names: dict[int, str] = {}

    conversion_rates: dict[str, Decimal] = {}
    rate_dates_by_currency: dict[str, str] = {}

    target_currency = trip.currency.upper()

    for expense in expenses:
        source_currency = expense.currency.upper()

        if source_currency == target_currency:
            converted_amount = expense.amount

        else:
            if source_currency not in conversion_rates:
                conversion = convert_currency(
                    amount=Decimal("1"),
                    from_currency=source_currency,
                    to_currency=target_currency,
                )

                conversion_rates[source_currency] = (
                    conversion.rate
                )

                rate_dates_by_currency[source_currency] = (
                    conversion.rate_date
                )

            converted_amount = (
                expense.amount
                * conversion_rates[source_currency]
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

        total_expenses += converted_amount

        totals_by_participant[
            expense.participant_id
        ] += converted_amount

        participant_names[
            expense.participant_id
        ] = expense.participant.name

    total_expenses = total_expenses.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    participant_summaries = [
        ParticipantExpenseSummary(
            participant_id=participant_id,
            participant_name=participant_names[participant_id],
            total_expenses=participant_total.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            ),
        )
        for participant_id, participant_total in sorted(
            totals_by_participant.items(),
            key=lambda item: participant_names[item[0]].lower(),
        )
    ]

    remaining_budget: Decimal | None = None
    budget_exceeded: bool | None = None

    if trip.budget is not None:
        remaining_budget = (
            trip.budget - total_expenses
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        budget_exceeded = total_expenses > trip.budget

    return ExpenseSummaryResponse(
        currency=target_currency,
        budget=trip.budget,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget,
        budget_exceeded=budget_exceeded,
        participants=participant_summaries,
    )
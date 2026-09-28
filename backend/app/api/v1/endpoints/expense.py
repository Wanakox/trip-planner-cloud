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
    ExpenseNotFoundError,
    ParticipantNotFoundError,
    TripNotFoundError,
    CurrencyProviderError,
    UnsupportedCurrencyError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    ExpenseSummaryResponse,
)
from app.services.expense_service import (
    add_expense_to_trip,
    delete_expense_from_trip,
    list_trip_expenses,
    update_expense_in_trip,
    get_trip_expense_summary,
)


router = APIRouter(
    prefix="/trips/{trip_id}/expenses",
    tags=["expenses"],
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
    response_model=list[ExpenseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all expenses from a trip",
)
def get_trip_expenses(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> list[ExpenseResponse]:
    try:
        return list_trip_expenses(
            db=db,
            trip_id=trip_id,
            user=current_user,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc


@router.get(
    "/summary",
    response_model=ExpenseSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the expense summary from a trip",
)
def get_expense_summary(
    trip_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ExpenseSummaryResponse:
    try:
        return get_trip_expense_summary(
            db=db,
            trip_id=trip_id,
            user=current_user,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except UnsupportedCurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="One of the expense currencies is not supported",
        ) from exc

    except CurrencyProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The currency conversion service "
                "is currently unavailable"
            ),
        ) from exc
    

@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an expense to a trip",
)
def add_new_expense(
    trip_id: int,
    expense_data: ExpenseCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ExpenseResponse:
    try:
        return add_expense_to_trip(
            db=db,
            trip_id=trip_id,
            user=current_user,
            expense_data=expense_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except ParticipantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        ) from exc


@router.patch(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an expense from a trip",
)
def update_existing_expense(
    trip_id: int,
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ExpenseResponse:
    try:
        return update_expense_in_trip(
            db=db,
            trip_id=trip_id,
            expense_id=expense_id,
            user=current_user,
            expense_data=expense_data,
        )

    except TripNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        ) from exc

    except ExpenseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        ) from exc

    except ParticipantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found",
        ) from exc


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense from a trip",
)
def delete_existing_expense(
    trip_id: int,
    expense_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    try:
        delete_expense_from_trip(
            db=db,
            trip_id=trip_id,
            expense_id=expense_id,
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

    except ExpenseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        ) from exc
from datetime import date
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.expense import ExpenseCategory


class ExpenseBase(BaseModel):
    participant_id: int = Field(
        gt=0,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    category: ExpenseCategory

    currency: str = Field(
        min_length=3,
        max_length=3,
    )

    expense_date: date

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The expense name cannot be empty"
            )

        return normalized_value

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip().upper()

        if (
            len(normalized_value) != 3
            or not normalized_value.isalpha()
        ):
            raise ValueError(
                "The currency must be a three-letter code"
            )

        return normalized_value


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    participant_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    category: ExpenseCategory | None = None

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    expense_date: date | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The expense name cannot be empty"
            )

        return normalized_value

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip().upper()

        if (
            len(normalized_value) != 3
            or not normalized_value.isalpha()
        ):
            raise ValueError(
                "The currency must be a three-letter code"
            )

        return normalized_value


class ExpenseResponse(BaseModel):
    id: int
    trip_id: int
    participant_id: int

    name: str
    amount: Decimal
    category: ExpenseCategory
    currency: str
    expense_date: date

    model_config = ConfigDict(
        from_attributes=True,
    )


class ParticipantExpenseSummary(BaseModel):
    participant_id: int
    participant_name: str
    total_expenses: Decimal


class ExpenseSummaryResponse(BaseModel):
    currency: str
    budget: Decimal | None

    total_expenses: Decimal
    remaining_budget: Decimal | None
    budget_exceeded: bool | None

    participants: list[ParticipantExpenseSummary]
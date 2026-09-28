from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.participant import Participant
    from app.models.trip import Trip


class ExpenseCategory(StrEnum):
    ACCOMMODATION = "accommodation"
    TRANSPORT = "transport"
    FOOD = "food"
    LEISURE = "leisure"
    SHOPPING = "shopping"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "gasto"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    trip_id: Mapped[int] = mapped_column(
        "id_viaje",
        BigInteger,
        ForeignKey(
            "viaje.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    participant_id: Mapped[int] = mapped_column(
        "id_participante",
        BigInteger,
        ForeignKey(
            "participante.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        "nombre",
        String(150),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        "cantidad",
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=False,
    )

    category: Mapped[ExpenseCategory] = mapped_column(
        "categoria",
        Enum(
            ExpenseCategory,
            name="expense_category",
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        "moneda",
        String(3),
        nullable=False,
    )

    expense_date: Mapped[date] = mapped_column(
        "fecha",
        Date,
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="expenses",
    )

    participant: Mapped["Participant"] = relationship(
        back_populates="expenses",
    )
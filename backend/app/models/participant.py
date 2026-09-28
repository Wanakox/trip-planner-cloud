from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.trip import Trip


class Participant(Base):
    __tablename__ = "participante"

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

    name: Mapped[str] = mapped_column(
        "nombre",
        String(150),
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="participants",
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="participant",
        passive_deletes=True,
    )
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip


class Note(Base):
    __tablename__ = "nota"

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

    title: Mapped[str] = mapped_column(
        "titulo",
        String(150),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        "texto",
        Text,
        nullable=False,
    )

    day_number: Mapped[int | None] = mapped_column(
        "num_dia",
        Integer,
        nullable=True,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="notes",
    )
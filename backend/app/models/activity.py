from datetime import time
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip


class ActivityStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


class Activity(Base):
    __tablename__ = "actividad"

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

    location: Mapped[str | None] = mapped_column(
        "ubicacion",
        String(250),
        nullable=True,
    )

    start_time: Mapped[time | None] = mapped_column(
        "hora",
        Time,
        nullable=True,
    )

    day_number: Mapped[int] = mapped_column(
        "num_dia",
        Integer,
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
        "completado",
        Boolean,
        nullable=False,
        default=False,
    )

    order: Mapped[int] = mapped_column(
        "orden",
        Integer,
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="activities",
    )
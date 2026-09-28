from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
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
    from app.models.accommodation import Accommodation
    from app.models.activity import Activity
    from app.models.task import Task
    from app.models.destination import Destination
    from app.models.file import TripFile
    from app.models.note import Note
    from app.models.participant import Participant
    from app.models.expense import Expense
    from app.models.transport import Transport
    from app.models.user import User


class TripStatus(StrEnum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Trip(Base):
    __tablename__ = "viaje"

    __table_args__ = (
        CheckConstraint(
            "valoracion IS NULL "
            "OR valoracion BETWEEN 1 AND 5",
            name="ck_viaje_valoracion",
        ),
        CheckConstraint(
            "fecha_fin >= fecha_inicio",
            name="ck_viaje_fechas",
        ),
        CheckConstraint(
            "presupuesto >= 0",
            name="ck_viaje_presupuesto",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        "id_usuario",
        BigInteger,
        ForeignKey(
            "usuario.id",
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

    origin: Mapped[str] = mapped_column(
        "origen",
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        "descripcion",
        Text,
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(
        "fecha_inicio",
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        "fecha_fin",
        Date,
        nullable=False,
    )

    @property
    def total_days(self) -> int:
        return (
            self.end_date - self.start_date
        ).days + 1

    budget: Mapped[Decimal] = mapped_column(
        "presupuesto",
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        "moneda",
        String(3),
        nullable=False,
        default="EUR",
    )

    status: Mapped[TripStatus] = mapped_column(
        "estado",
        Enum(
            TripStatus,
            name="trip_status",
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
        default=TripStatus.PLANNING,
    )

    rating: Mapped[int | None] = mapped_column(
        "valoracion",
        SmallInteger,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="trips",
    )

    destinations: Mapped[list["Destination"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="Destination.order",
        lazy="selectin",
    )

    activities: Mapped[list["Activity"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    transports: Mapped[list["Transport"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    accommodations: Mapped[list["Accommodation"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    participants: Mapped[list["Participant"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="Task.order",
    )

    notes: Mapped[list["Note"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )

    files: Mapped[list["TripFile"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )
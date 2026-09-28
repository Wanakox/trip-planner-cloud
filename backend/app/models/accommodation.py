from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Numeric,
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


class Accommodation(Base):
    __tablename__ = "alojamiento"

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

    address: Mapped[str] = mapped_column(
        "direccion",
        String(250),
        nullable=False,
    )

    price: Mapped[Decimal | None] = mapped_column(
        "precio",
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=True,
    )

    check_in_date: Mapped[date] = mapped_column(
        "fecha_checkin",
        Date,
        nullable=False,
    )

    check_out_date: Mapped[date] = mapped_column(
        "fecha_checkout",
        Date,
        nullable=False,
    )

    check_in_time: Mapped[time | None] = mapped_column(
        "hora_checkin",
        Time,
        nullable=True,
    )
    
    check_out_time: Mapped[time | None] = mapped_column(
        "hora_checkout",
        Time,
        nullable=True,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="accommodations",
    )
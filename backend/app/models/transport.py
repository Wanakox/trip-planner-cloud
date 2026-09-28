from datetime import date, time
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


class TransportType(StrEnum):
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    BOAT = "boat"
    OTHER = "other"


class Transport(Base):
    __tablename__ = "transporte"

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

    transport_type: Mapped[TransportType] = mapped_column(
        "tipo",
        Enum(
            TransportType,
            name="transport_type",
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
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

    departure_date: Mapped[date] = mapped_column(
        "fecha_salida",
        Date,
        nullable=False,
    )

    arrival_date: Mapped[date | None] = mapped_column(
        "fecha_llegada",
        Date,
        nullable=True,
    )

    departure_time: Mapped[time | None] = mapped_column(
        "hora_salida",
        Time,
        nullable=True,
    )

    arrival_time: Mapped[time | None] = mapped_column(
        "hora_llegada",
        Time,
        nullable=True,
    )

    origin: Mapped[str] = mapped_column(
        "origen",
        String(150),
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        "destino",
        String(150),
        nullable=False,
    )

    check_in_date: Mapped[date | None] = mapped_column(
        "fecha_checkin",
        Date,
        nullable=True,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="transports",
    )
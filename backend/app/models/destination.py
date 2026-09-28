from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip


class Destination(Base):
    __tablename__ = "destino"

    __table_args__ = (
        UniqueConstraint(
            "id_viaje",
            "orden",
            name="uq_destino_viaje_orden",
        ),
    )

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

    country: Mapped[str] = mapped_column(
        "pais",
        String(100),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        "ciudad",
        String(100),
        nullable=False,
    )

    order: Mapped[int] = mapped_column(
        "orden",
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        "moneda",
        String(3),
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="destinations",
    )
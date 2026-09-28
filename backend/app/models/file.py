from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.trip import Trip


class TripFile(Base):
    __tablename__ = "archivo"

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
        String(255),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        "ruta",
        String(500),
        nullable=False,
    )

    extension: Mapped[str] = mapped_column(
        "extension",
        String(20),
        nullable=False,
    )

    size: Mapped[int] = mapped_column(
        "tamano",
        BigInteger,
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="files",
    )
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
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


class User(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        "nombre",
        String(100),
        nullable=False,
    )

    surname: Mapped[str] = mapped_column(
        "apellido",
        String(150),
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        "nombre_usuario",
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        "correo_electronico",
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        "contrasena_hash",
        String(255),
        nullable=False,
    )

    profile_photo: Mapped[str | None] = mapped_column(
        "foto_perfil",
        String(500),
        nullable=True,
    )

    default_currency: Mapped[str] = mapped_column(
        "moneda_predeterminada",
        String(3),
        nullable=False,
        default="EUR",
    )

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
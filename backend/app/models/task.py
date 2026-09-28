from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum,
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


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__ = "tarea"

    __table_args__ = (
        UniqueConstraint(
            "id_viaje",
            "orden",
            name="uq_tarea_viaje_orden",
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

    name: Mapped[str] = mapped_column(
        "nombre",
        String(150),
        nullable=False,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        "prioridad",
        Enum(
            TaskPriority,
            name="task_priority",
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
        ),
        nullable=False,
        default=TaskPriority.MEDIUM,
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
        back_populates="tasks",
    )
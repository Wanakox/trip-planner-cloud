from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.task import TaskPriority


class TaskCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    priority: TaskPriority = TaskPriority.MEDIUM

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The task name cannot be empty"
            )

        return normalized_value


class TaskUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    priority: TaskPriority | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The task name cannot be empty"
            )

        return normalized_value


class TaskCompletionUpdate(BaseModel):
    completed: bool


class TaskOrderItem(BaseModel):
    id: int = Field(
        gt=0,
    )

    order: int = Field(
        ge=1,
    )


class TaskOrderUpdate(BaseModel):
    tasks: list[TaskOrderItem] = Field(
        min_length=1,
    )

    @field_validator("tasks")
    @classmethod
    def validate_task_order(
        cls,
        value: list[TaskOrderItem],
    ) -> list[TaskOrderItem]:
        task_ids = [
            task.id
            for task in value
        ]

        orders = [
            task.order
            for task in value
        ]

        if len(task_ids) != len(set(task_ids)):
            raise ValueError(
                "Task IDs cannot be repeated"
            )

        if len(orders) != len(set(orders)):
            raise ValueError(
                "Task orders cannot be repeated"
            )

        expected_orders = list(
            range(
                1,
                len(value) + 1,
            )
        )

        if sorted(orders) != expected_orders:
            raise ValueError(
                "Task orders must be consecutive "
                "and start at 1"
            )

        return value


class TaskResponse(BaseModel):
    id: int
    trip_id: int

    name: str
    priority: TaskPriority
    completed: bool
    order: int

    model_config = ConfigDict(
        from_attributes=True,
    )
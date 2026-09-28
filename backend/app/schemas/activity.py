from datetime import time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ActivityCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    location: str | None = Field(
        default=None,
        max_length=250,
    )

    start_time: time | None = None

    day_number: int = Field(
        ge=1,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The activity name cannot be empty"
            )

        return normalized_value

    @field_validator("location")
    @classmethod
    def normalize_location(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None


class ActivityUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    location: str | None = Field(
        default=None,
        max_length=250,
    )

    start_time: time | None = None

    day_number: int | None = Field(
        default=None,
        ge=1,
    )

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
                "The activity name cannot be empty"
            )

        return normalized_value

    @field_validator("location")
    @classmethod
    def normalize_location(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None


class ActivityCompletionUpdate(BaseModel):
    completed: bool


class ActivityOrderItem(BaseModel):
    id: int = Field(
        gt=0,
    )

    day_number: int = Field(
        ge=1,
    )

    order: int = Field(
        ge=1,
    )


class ActivityOrderUpdate(BaseModel):
    activities: list[ActivityOrderItem] = Field(
        min_length=1,
    )

    @field_validator("activities")
    @classmethod
    def validate_activity_order(
        cls,
        value: list[ActivityOrderItem],
    ) -> list[ActivityOrderItem]:
        activity_ids = [
            activity.id
            for activity in value
        ]

        if len(activity_ids) != len(set(activity_ids)):
            raise ValueError(
                "Activity IDs cannot be repeated"
            )

        positions = [
            (
                activity.day_number,
                activity.order,
            )
            for activity in value
        ]

        if len(positions) != len(set(positions)):
            raise ValueError(
                "Activity positions cannot be repeated "
                "within the same day"
            )

        activities_by_day: dict[
            int,
            list[int],
        ] = {}

        for activity in value:
            activities_by_day.setdefault(
                activity.day_number,
                [],
            ).append(
                activity.order
            )

        for orders in activities_by_day.values():
            expected_orders = list(
                range(
                    1,
                    len(orders) + 1,
                )
            )

            if sorted(orders) != expected_orders:
                raise ValueError(
                    "Activity orders must be consecutive "
                    "and start at 1 for each day"
                )

        return value


class ActivityResponse(BaseModel):
    id: int
    trip_id: int
    name: str
    location: str | None
    start_time: time | None
    day_number: int
    completed: bool
    order: int

    model_config = ConfigDict(
        from_attributes=True,
    )
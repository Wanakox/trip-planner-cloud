from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.trip import TripStatus


class DestinationCreate(BaseModel):
    country: str = Field(
        min_length=1,
        max_length=100,
    )

    city: str = Field(
        min_length=1,
        max_length=100,
    )

    currency: str = Field(
        min_length=3,
        max_length=3,
    )

    @field_validator(
        "country",
        "city",
    )
    @classmethod
    def normalize_text(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The field cannot be empty"
            )

        return normalized_value

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        return value.strip().upper()


class DestinationUpdate(BaseModel):
    country: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    @field_validator(
        "country",
        "city",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The field cannot be empty"
            )

        return normalized_value

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip().upper()


class DestinationOrderItem(BaseModel):
    id: int = Field(
        gt=0,
    )

    order: int = Field(
        ge=1,
    )


class DestinationOrderUpdate(BaseModel):
    destinations: list[DestinationOrderItem] = Field(
        min_length=1,
        max_length=20,
    )

    @field_validator("destinations")
    @classmethod
    def validate_destination_order(
        cls,
        value: list[DestinationOrderItem],
    ) -> list[DestinationOrderItem]:
        destination_ids = [
            destination.id
            for destination in value
        ]

        orders = [
            destination.order
            for destination in value
        ]

        if len(destination_ids) != len(set(destination_ids)):
            raise ValueError(
                "Destination IDs cannot be repeated"
            )

        if len(orders) != len(set(orders)):
            raise ValueError(
                "Destination orders cannot be repeated"
            )

        expected_orders = list(
            range(
                1,
                len(value) + 1,
            )
        )

        if sorted(orders) != expected_orders:
            raise ValueError(
                "Destination orders must be consecutive "
                "and start at 1"
            )

        return value


class DestinationResponse(BaseModel):
    id: int
    country: str
    city: str
    currency: str
    order: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class TripCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    origin: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    start_date: date

    end_date: date

    budget: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    destinations: list[DestinationCreate] = Field(
        min_length=1,
        max_length=20,
    )

    @field_validator(
        "name",
        "origin",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The field cannot be empty"
            )

        return normalized_value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError(
                "The end date cannot be earlier "
                "than the start date"
            )

        return self


class TripUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    origin: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    start_date: date | None = None

    end_date: date | None = None

    budget: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    status: TripStatus | None = None

    @field_validator(
        "name",
        "origin",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The field cannot be empty"
            )

        return normalized_value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None

    @field_validator("currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip().upper()

    @model_validator(mode="after")
    def validate_provided_dates(self) -> Self:
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "The end date cannot be earlier "
                "than the start date"
            )

        return self


class TripRatingUpdate(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
    )
    

class TripResponse(BaseModel):
    id: int
    user_id: int
    name: str
    origin: str
    description: str | None
    start_date: date
    end_date: date
    total_days: int
    budget: Decimal
    currency: str
    status: TripStatus
    rating: int | None
    destinations: list[DestinationResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )
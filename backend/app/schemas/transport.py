from datetime import date, time
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.transport import TransportType


class TransportBase(BaseModel):
    transport_type: TransportType

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    departure_date: date
    arrival_date: date | None = None

    departure_time: time | None = None
    arrival_time: time | None = None

    origin: str = Field(
        min_length=1,
        max_length=150,
    )

    destination: str = Field(
        min_length=1,
        max_length=150,
    )

    check_in_date: date | None = None

    @field_validator(
        "origin",
        "destination",
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

    @model_validator(mode="after")
    def validate_transport_dates(self) -> Self:
        if (
            self.arrival_date is not None
            and self.arrival_date < self.departure_date
        ):
            raise ValueError(
                "The arrival date cannot be earlier "
                "than the departure date"
            )

        if (
            self.arrival_date == self.departure_date
            and self.departure_time is not None
            and self.arrival_time is not None
            and self.arrival_time < self.departure_time
        ):
            raise ValueError(
                "The arrival time cannot be earlier "
                "than the departure time on the same day"
            )

        if (
            self.check_in_date is not None
            and self.check_in_date > self.departure_date
        ):
            raise ValueError(
                "The check-in date cannot be later "
                "than the departure date"
            )

        return self


class TransportCreate(TransportBase):
    pass


class TransportUpdate(BaseModel):
    transport_type: TransportType | None = None

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    departure_date: date | None = None
    arrival_date: date | None = None

    departure_time: time | None = None
    arrival_time: time | None = None

    origin: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    destination: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    check_in_date: date | None = None

    @field_validator(
        "origin",
        "destination",
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


class TransportResponse(BaseModel):
    id: int
    trip_id: int
    transport_type: TransportType

    price: Decimal | None = None

    departure_date: date
    arrival_date: date | None = None

    departure_time: time | None = None
    arrival_time: time | None = None

    origin: str
    destination: str

    check_in_date: date | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )
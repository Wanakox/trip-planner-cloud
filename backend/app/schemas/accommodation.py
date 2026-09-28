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


class AccommodationBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    address: str = Field(
        min_length=1,
        max_length=250,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    check_in_date: date
    check_out_date: date

    check_in_time: time | None = None
    check_out_time: time | None = None

    @field_validator(
        "name",
        "address",
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
    def validate_accommodation_dates(self) -> Self:
        if self.check_out_date < self.check_in_date:
            raise ValueError(
                "The check-out date cannot be earlier "
                "than the check-in date"
            )

        if (
            self.check_out_date == self.check_in_date
            and self.check_in_time is not None
            and self.check_out_time is not None
            and self.check_out_time < self.check_in_time
        ):
            raise ValueError(
                "The check-out time cannot be earlier "
                "than the check-in time on the same day"
            )

        return self


class AccommodationCreate(AccommodationBase):
    pass


class AccommodationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    address: str | None = Field(
        default=None,
        min_length=1,
        max_length=250,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    check_in_date: date | None = None
    check_out_date: date | None = None

    check_in_time: time | None = None
    check_out_time: time | None = None

    @field_validator(
        "name",
        "address",
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


class AccommodationResponse(BaseModel):
    id: int
    trip_id: int

    name: str
    address: str

    price: Decimal | None = None

    check_in_date: date
    check_out_date: date

    check_in_time: time | None = None
    check_out_time: time | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class NoteCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=150,
    )

    text: str = Field(
        min_length=1,
    )

    day_number: int = Field(
        ge=1,
    )

    @field_validator("title")
    @classmethod
    def normalize_title(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The note title cannot be empty"
            )

        return normalized_value

    @field_validator("text")
    @classmethod
    def normalize_text(
        cls,
        value: str,
    ) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The note text cannot be empty"
            )

        return normalized_value


class NoteUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    text: str | None = Field(
        default=None,
        min_length=1,
    )

    day_number: int | None = Field(
        default=None,
        ge=1,
    )

    @field_validator("day_number")
    @classmethod
    def require_day_number(
        cls,
        value: int | None,
    ) -> int:
        if value is None:
            raise ValueError(
                "The note day is required"
            )

        return value

    @field_validator("title")
    @classmethod
    def normalize_title(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The note title cannot be empty"
            )

        return normalized_value

    @field_validator("text")
    @classmethod
    def normalize_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "The note text cannot be empty"
            )

        return normalized_value


class NoteResponse(BaseModel):
    id: int
    trip_id: int

    title: str
    text: str
    day_number: int | None

    model_config = ConfigDict(
        from_attributes=True,
    )

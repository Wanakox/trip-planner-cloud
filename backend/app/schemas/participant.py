from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ParticipantBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
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
                "The participant name cannot be empty"
            )

        return normalized_value


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
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
                "The participant name cannot be empty"
            )

        return normalized_value


class ParticipantResponse(BaseModel):
    id: int
    trip_id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )
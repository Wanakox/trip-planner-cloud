from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    surname: str = Field(
        min_length=1,
        max_length=150,
    )

    profile_photo: str | None = Field(
        default=None,
        max_length=500,
    )

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    email: EmailStr

    default_currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=3,
    )

    @field_validator("name", "surname", "username", mode="before")
    @classmethod
    def remove_surrounding_whitespace(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("The field cannot be empty")

        return value

    @field_validator("default_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    identifier: str = Field(
        min_length=3,
        max_length=255,
        description="Username or email address",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("The identifier cannot be empty")

        return value


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserUpdate(UserBase):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    surname: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    profile_photo: str | None = Field(
        default=None,
        max_length=500,
    )

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )

    email: EmailStr | None = None

    default_currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    @field_validator("name", "surname", "username", mode="before")
    @classmethod
    def remove_surrounding_whitespace(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("The field cannot be empty")

        return value

    @field_validator("default_currency")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.upper()

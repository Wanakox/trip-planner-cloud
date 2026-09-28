from typing import Annotated
import jwt

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyRegisteredError,
)
from app.db.dependencies import get_db
from app.schemas.user import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import (
    login_user,
    refresh_access_token,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    user_data: UserCreate,
    db: DatabaseSession,
) -> UserResponse:
    try:
        return register_user(
            db=db,
            user_data=user_data,
        )

    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado",
        ) from exc

    except UsernameAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nombre de usuario ya registrado",
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user and return an access token",
)
def login(
    credentials: LoginRequest,
    db: DatabaseSession,
) -> TokenResponse:
    try:
        access_token, refresh_token = login_user(
            db=db,
            identifier=credentials.identifier,
            password=credentials.password,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador o contraseña incorrectos",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh an access token",
)
def refresh_token(
    token_data: RefreshTokenRequest,
) -> TokenResponse:
    try:
        access_token = refresh_access_token(
            refresh_token=token_data.refresh_token,
        )

    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o expirado",
        ) from exc

    return TokenResponse(
        access_token=access_token,
        refresh_token=token_data.refresh_token,
    )
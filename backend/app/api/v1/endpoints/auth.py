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
    EmailDeliveryError,
    EmailNotVerifiedError,
    InvalidVerificationTokenError,
    InvalidCredentialsError,
    UsernameAlreadyRegisteredError,
)
from app.db.dependencies import get_db
from app.schemas.user import (
    LoginRequest,
    ResendVerificationRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.auth_service import (
    login_user,
    refresh_access_token,
    register_user,
    resend_verification,
    verify_email,
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
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail="Cuenta creada, pero no se pudo enviar el correo. Solicita otro enlace de verificación.") from exc


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
    except EmailNotVerifiedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

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
    db: DatabaseSession,
) -> TokenResponse:
    try:
        access_token = refresh_access_token(
            db=db,
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


@router.post("/verify-email", status_code=204, summary="Verify an email address")
def verify_email_endpoint(data: VerifyEmailRequest, db: DatabaseSession) -> None:
    try:
        verify_email(db, data.token)
    except InvalidVerificationTokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/resend-verification", status_code=202, summary="Resend verification email")
def resend_verification_endpoint(data: ResendVerificationRequest, db: DatabaseSession) -> dict[str, str]:
    try:
        resend_verification(db, str(data.email))
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"message": "Si la cuenta existe y está pendiente, enviaremos un enlace de verificación."}

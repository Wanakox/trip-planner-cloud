from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.dependencies import get_db
from app.models.user import User
from app.repositories.user_repository import get_user_by_id

bearer_scheme = HTTPBearer()

DatabaseSession = Annotated[Session, Depends(get_db)]

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials,
    Depends(bearer_scheme),
]


def get_current_user(
    credentials: BearerCredentials,
    db: DatabaseSession,
) -> User:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (
        InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise unauthorized_exception from exc

    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise unauthorized_exception

    return user
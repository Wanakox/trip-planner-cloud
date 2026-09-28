from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    status,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import (
    CurrencyProviderError,
    EmailAlreadyRegisteredError,
    UnsupportedCurrencyError,
    UsernameAlreadyRegisteredError,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    delete_current_user,
    get_current_user_photo_path,
    remove_current_user_photo,
    update_current_user,
    upload_current_user_photo,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user",
)
def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    return current_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete the authenticated user",
)
def delete_me(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    delete_current_user(
        db=db,
        user=current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the authenticated user",
)
def update_me(
    user_data: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> UserResponse:
    try:
        return update_current_user(
            db=db,
            user=current_user,
            user_data=user_data,
        )

    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc

    except UsernameAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        ) from exc

    except UnsupportedCurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported currency code",
        ) from exc

    except CurrencyProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Currency service is temporarily unavailable",
        ) from exc


@router.post(
    "/me/profile-photo",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload the authenticated user's profile photo",
)
async def upload_profile_photo(
    current_user: CurrentUser,
    db: DatabaseSession,
    photo: UploadFile = File(...),
) -> UserResponse:
    try:
        return await upload_current_user_photo(db, current_user, photo)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.get(
    "/me/profile-photo",
    response_class=FileResponse,
    summary="Get the authenticated user's profile photo",
)
def get_profile_photo(current_user: CurrentUser) -> FileResponse:
    photo_path = get_current_user_photo_path(current_user)
    if photo_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(photo_path)


@router.delete(
    "/me/profile-photo",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete the authenticated user's profile photo",
)
def delete_profile_photo(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Response:
    remove_current_user_photo(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine

router = APIRouter(
    prefix="/health", 
    tags=["health"]
)


@router.get(
    "",
    summary="Check application health",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable",
        ) from exc

    return {
        "status": "ok",
        "database": "connected",
    }

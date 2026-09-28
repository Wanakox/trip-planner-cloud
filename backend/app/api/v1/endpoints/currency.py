from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.core.exceptions import CurrencyProviderError
from app.schemas.currency import (
    CurrencyConversionResponse,
    CurrencyResponse,
)
from app.services.currency_service import (
    convert_currency,
    list_currencies,
)

router = APIRouter(
    prefix="/currencies",
    tags=["currencies"],
)


AmountQuery = Annotated[
    Decimal,
    Query(
        gt=0,
        description="Amount to convert",
    ),
]

CurrencyQuery = Annotated[
    str,
    Query(
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code",
    ),
]


@router.get(
    "",
    response_model=list[CurrencyResponse],
    summary="List supported currencies",
)
def get_currencies() -> list[CurrencyResponse]:
    try:
        return list_currencies()
    except CurrencyProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de divisas no está disponible temporalmente",
        ) from exc


@router.get(
    "/convert",
    response_model=CurrencyConversionResponse,
    summary="Convert an amount between currencies",
)
def convert_amount(
    amount: AmountQuery,
    from_currency: CurrencyQuery,
    to_currency: CurrencyQuery,
) -> CurrencyConversionResponse:
    try:
        return convert_currency(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
        )
    except CurrencyProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de divisas no está disponible temporalmente",
        ) from exc
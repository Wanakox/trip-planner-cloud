from decimal import Decimal

from pydantic import BaseModel


class CurrencyResponse(BaseModel):
    code: str
    name: str


class CurrencyConversionResponse(BaseModel):
    amount: Decimal
    from_currency: str
    to_currency: str
    rate: Decimal
    result: Decimal
    rate_date: str
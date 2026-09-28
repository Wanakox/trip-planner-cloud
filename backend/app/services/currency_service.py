from decimal import ROUND_HALF_UP, Decimal

from app.core.exceptions import UnsupportedCurrencyError
from app.integrations.frankfurter_client import (
    get_available_currencies,
    get_latest_rate,
)
from app.schemas.currency import (
    CurrencyConversionResponse,
    CurrencyResponse,
)


def list_currencies() -> list[CurrencyResponse]:
    currencies = get_available_currencies()

    return [
        CurrencyResponse(
            code=code,
            name=name,
        )
        for code, name in sorted(currencies.items())
    ]


def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
) -> CurrencyConversionResponse:
    normalized_from = from_currency.strip().upper()
    normalized_to = to_currency.strip().upper()

    if normalized_from == normalized_to:
        return CurrencyConversionResponse(
            amount=amount,
            from_currency=normalized_from,
            to_currency=normalized_to,
            rate=Decimal("1"),
            result=amount,
            rate_date="same-currency",
        )

    data = get_latest_rate(
        from_currency=normalized_from,
        to_currency=normalized_to,
    )

    rate = Decimal(str(data["rates"][normalized_to]))

    result = (amount * rate).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return CurrencyConversionResponse(
        amount=amount,
        from_currency=normalized_from,
        to_currency=normalized_to,
        rate=rate,
        result=result,
        rate_date=data["date"],
    )


def validate_currency_code(currency_code: str) -> str:
    normalized_code = currency_code.strip().upper()

    currencies = get_available_currencies()

    if normalized_code not in currencies:
        raise UnsupportedCurrencyError

    return normalized_code
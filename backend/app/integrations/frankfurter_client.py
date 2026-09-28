from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import CurrencyProviderError


def get_available_currencies() -> dict[str, str]:
    url = f"{settings.frankfurter_base_url}/currencies"

    try:
        response = httpx.get(
            url,
            timeout=settings.external_api_timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise CurrencyProviderError from exc

    data = response.json()

    if not isinstance(data, dict):
        raise CurrencyProviderError

    return data


def get_latest_rate(
    from_currency: str,
    to_currency: str,
) -> dict[str, Any]:
    url = f"{settings.frankfurter_base_url}/latest"

    params = {
        "base": from_currency,
        "symbols": to_currency,
    }

    try:
        response = httpx.get(
            url,
            params=params,
            timeout=settings.external_api_timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise CurrencyProviderError from exc

    data = response.json()

    if (
        not isinstance(data, dict)
        or "rates" not in data
        or to_currency not in data["rates"]
    ):
        raise CurrencyProviderError

    return data

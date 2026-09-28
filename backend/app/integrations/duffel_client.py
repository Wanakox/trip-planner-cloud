from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import FlightProviderError


def get_headers() -> dict[str, str]:
    return {
        "Authorization": (
            f"Bearer {settings.duffel_access_token}"
        ),
        "Duffel-Version": settings.duffel_api_version,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }


def create_offer_request(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None,
    adults: int,
    cabin_class: str,
) -> dict[str, Any]:
    """
    Crea una búsqueda de vuelos en Duffel.
    """

    slices = [
        {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
        }
    ]

    if return_date is not None:
        slices.append(
            {
                "origin": destination,
                "destination": origin,
                "departure_date": return_date,
            }
        )

    passengers = [
        {
            "type": "adult",
        }
        for _ in range(adults)
    ]

    payload = {
        "data": {
            "slices": slices,
            "passengers": passengers,
            "cabin_class": cabin_class,
        }
    }

    url = (
        f"{settings.duffel_base_url}"
        "/air/offer_requests"
    )

    try:
        response = httpx.post(
            url,
            headers=get_headers(),
            json=payload,
            timeout=settings.external_api_timeout_seconds,
        )

        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise FlightProviderError from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise FlightProviderError from exc

    if (
        not isinstance(data, dict)
        or "data" not in data
        or not isinstance(data["data"], dict)
    ):
        raise FlightProviderError

    return data["data"]
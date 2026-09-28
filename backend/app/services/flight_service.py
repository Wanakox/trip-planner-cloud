from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.integrations.duffel_client import (
    create_offer_request,
)
from app.schemas.flight import (
    CabinClass,
    FlightOfferResponse,
    FlightSearchResponse,
    FlightSegmentResponse,
    FlightSliceResponse,
)


def normalize_iata_code(
    code: str,
) -> str:
    return code.strip().upper()


def parse_datetime(
    value: str,
) -> datetime:
    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )


def build_segment(
    segment: dict[str, Any],
) -> FlightSegmentResponse:
    origin = segment.get(
        "origin",
        {},
    )

    destination = segment.get(
        "destination",
        {},
    )

    marketing_carrier = segment.get(
        "marketing_carrier",
        {},
    )

    return FlightSegmentResponse(
        origin=origin.get(
            "iata_code",
            "",
        ),
        destination=destination.get(
            "iata_code",
            "",
        ),
        departure=parse_datetime(
            segment["departing_at"]
        ),
        arrival=parse_datetime(
            segment["arriving_at"]
        ),
        airline=marketing_carrier.get(
            "name",
            "Unknown airline",
        ),
        airline_code=marketing_carrier.get(
            "iata_code"
        ),
        flight_number=segment.get(
            "marketing_carrier_flight_number"
        ),
    )


def build_slice(
    slice_data: dict[str, Any],
) -> FlightSliceResponse:
    segments = [
        build_segment(segment)
        for segment in slice_data.get(
            "segments",
            [],
        )
    ]

    origin = slice_data.get(
        "origin",
        {},
    )

    destination = slice_data.get(
        "destination",
        {},
    )

    return FlightSliceResponse(
        origin=origin.get(
            "iata_code",
            "",
        ),
        destination=destination.get(
            "iata_code",
            "",
        ),
        duration=slice_data.get(
            "duration"
        ),
        stops=max(
            len(segments) - 1,
            0,
        ),
        segments=segments,
    )


def build_offer(
    offer: dict[str, Any],
) -> FlightOfferResponse:
    owner = offer.get(
        "owner",
        {},
    )

    slices = [
        build_slice(slice_data)
        for slice_data in offer.get(
            "slices",
            [],
        )
    ]

    expires_at = offer.get(
        "expires_at"
    )

    return FlightOfferResponse(
        id=offer["id"],
        airline=owner.get(
            "name",
            "Unknown airline",
        ),
        airline_code=owner.get(
            "iata_code"
        ),
        price=Decimal(
            str(
                offer["total_amount"]
            )
        ),
        currency=offer[
            "total_currency"
        ],
        expires_at=(
            parse_datetime(expires_at)
            if expires_at
            else None
        ),
        slices=slices,
    )


def search_flights(
    origin: str,
    destination: str,
    departure_date: date,
    return_date: date | None,
    adults: int,
    cabin_class: CabinClass,
) -> FlightSearchResponse:
    normalized_origin = normalize_iata_code(
        origin
    )

    normalized_destination = normalize_iata_code(
        destination
    )

    data = create_offer_request(
        origin=normalized_origin,
        destination=normalized_destination,
        departure_date=departure_date.isoformat(),
        return_date=(
            return_date.isoformat()
            if return_date
            else None
        ),
        adults=adults,
        cabin_class=cabin_class.value,
    )

    offers_data = data.get(
        "offers",
        [],
    )

    offers = [
        build_offer(offer)
        for offer in offers_data
    ]

    offers.sort(
        key=lambda offer: offer.price
    )

    return FlightSearchResponse(
        origin=normalized_origin,
        destination=normalized_destination,
        departure_date=departure_date,
        return_date=return_date,
        adults=adults,
        cabin_class=cabin_class,
        offers=offers,
    )

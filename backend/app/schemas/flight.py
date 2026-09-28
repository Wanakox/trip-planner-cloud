from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class CabinClass(StrEnum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class FlightSegmentResponse(BaseModel):
    origin: str
    destination: str

    departure: datetime
    arrival: datetime

    airline: str
    airline_code: str | None

    flight_number: str | None


class FlightSliceResponse(BaseModel):
    origin: str
    destination: str

    duration: str | None

    stops: int

    segments: list[FlightSegmentResponse]


class FlightOfferResponse(BaseModel):
    id: str

    airline: str
    airline_code: str | None

    price: Decimal
    currency: str

    expires_at: datetime | None

    slices: list[FlightSliceResponse]


class FlightSearchResponse(BaseModel):
    origin: str
    destination: str

    departure_date: date
    return_date: date | None

    adults: int
    cabin_class: CabinClass

    offers: list[FlightOfferResponse]
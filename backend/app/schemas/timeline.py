from datetime import date, time

from pydantic import BaseModel


class TimelineActivityResponse(BaseModel):
    id: int
    name: str
    location: str | None
    start_time: time | None
    completed: bool
    order: int


class TimelineDayResponse(BaseModel):
    day_number: int
    date: date
    activities: list[TimelineActivityResponse]


class TimelineResponse(BaseModel):
    trip_id: int
    start_date: date
    end_date: date
    days: list[TimelineDayResponse]
from pydantic import (
    BaseModel,
    ConfigDict,
)


class TripFileResponse(BaseModel):
    id: int
    trip_id: int

    name: str
    extension: str
    size: int

    model_config = ConfigDict(
        from_attributes=True,
    )
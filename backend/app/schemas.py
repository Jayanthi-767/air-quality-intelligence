
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeasurementCreate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    station_id: str | None = None
    parameter: str = Field(min_length=1, max_length=30)
    value: float = Field(ge=0, allow_inf_nan=False)
    unit: str
    measured_at: datetime
    source: str = "manual"


class MeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city: str
    country: str
    station_id: str | None
    parameter: str
    value: float
    unit: str
    measured_at: datetime
    source: str
    created_at: datetime

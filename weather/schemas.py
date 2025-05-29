# weather/schemas.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class LocationBase(BaseModel):
    name: str = Field(..., example="Dallas, TX")
    latitude: float = Field(..., example=32.7767)
    longitude: float = Field(..., example=-96.7970)

class LocationCreate(LocationBase):
    """Properties to use when creating a new location."""
    pass

class LocationUpdate(BaseModel):
    """Properties to use when updating an existing location."""
    name: Optional[str] = Field(None, example="Dallas, TX")
    latitude: Optional[float] = Field(None, example=32.7767)
    longitude: Optional[float] = Field(None, example=-96.7970)

class Location(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    name: str
    event_type: str
    description: Optional[str] = None
    address: Optional[str] = None
    estimated_attendance: Optional[int] = None
    start_time: datetime
    end_time: datetime

class EventCreate(EventBase):
    location: dict  # {"type": "Point", "coordinates": [lon, lat]}

    @field_validator('location')
    def validate_location(cls, v):
        if not isinstance(v, dict) or v.get('type') != 'Point' or len(v.get('coordinates', [])) != 2:
            raise ValueError('Location must be GeoJSON Point')
        return v

class EventUpdate(BaseModel):
    name: Optional[str] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    location: Optional[dict] = None
    address: Optional[str] = None
    estimated_attendance: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None

class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    impact_score: float
    risk_score: float
    status: str
    created_at: datetime
    updated_at: datetime
    location: dict  # GeoJSON

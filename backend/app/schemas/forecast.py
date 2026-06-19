from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ForecastRequest(BaseModel):
    event_id: str
    horizon_hours: int = 6
    include_roads: bool = False

class ForecastItem(BaseModel):
    road_id: str
    timestamp: datetime
    congestion_score: float
    predicted_speed: float
    delay_minutes: int
    confidence: float

class ForecastResponse(BaseModel):
    event_id: str
    generated_at: datetime
    horizon_hours: int
    forecasts: List[ForecastItem]
    summary: dict  # avg congestion, max congestion, etc.
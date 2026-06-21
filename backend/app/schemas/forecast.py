from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime

class ForecastRequest(BaseModel):
    event_id: str
    horizon_hours: int = 6
    include_roads: bool = False

class RoadForecast(BaseModel):
    road_id: str
    name: Optional[str] = None
    congestion_score: float
    predicted_speed: float
    delay_minutes: float
    vehicle_density: Optional[float] = None   # vehicles per km (estimated)
    coordinates: List[Tuple[float, float]]


class ForecastResponse(BaseModel):
    event_id: str
    generated_at: datetime
    impact_score: float
    impact_level: str
    expected_duration_minutes: float
    closure_probability: float
    risk_score: float
    confidence: Optional[float] = None
    top_factors: List[str]
    roads: Optional[List[RoadForecast]] = None
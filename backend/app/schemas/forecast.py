from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ForecastRequest(BaseModel):
    event_id: str
    horizon_hours: int = 6
    include_roads: bool = False

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
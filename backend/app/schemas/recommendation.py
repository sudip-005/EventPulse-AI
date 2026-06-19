from pydantic import BaseModel
from typing import List, Optional, Tuple

class RecommendationRequest(BaseModel):
    event_id: str
    simulation_id: Optional[str] = None

class RecommendationResponse(BaseModel):
    id: str
    resource_type: str
    count: int
    location: Tuple[float, float]
    reasoning: str
    priority: int
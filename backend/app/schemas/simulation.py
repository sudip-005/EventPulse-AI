from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class SimulationRequest(BaseModel):
    event_id: str
    scenario_params: Dict[str, Any]

class SimulationResponse(BaseModel):
    id: str
    event_id: str
    name: Optional[str]
    scenario_params: Dict[str, Any]
    predicted_congestion: Dict[str, Any]
    predicted_hotspots: List[Dict[str, Any]]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
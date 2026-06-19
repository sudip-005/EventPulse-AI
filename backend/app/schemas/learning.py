from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LearningRecordResponse(BaseModel):
    id: str
    event_id: str
    prediction_id: str
    predicted_impact: float
    actual_impact: float
    error: float
    mae: float
    rmse: float
    resource_effectiveness: float
    created_at: datetime

class RetrainingRequest(BaseModel):
    model_version: Optional[str] = None
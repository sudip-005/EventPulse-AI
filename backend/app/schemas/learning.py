from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class LearningRecordResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

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
    model_config = ConfigDict(protected_namespaces=())

    model_version: Optional[str] = None

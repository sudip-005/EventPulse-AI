from sqlalchemy import Column, Float, Boolean, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class LearningRecord(Base):
    __tablename__ = "learning_records"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), nullable=False)
    prediction_id: Any = Column(UUID(as_uuid=True))
    predicted_congestion: Any = Column(Float)
    actual_congestion: Any = Column(Float)
    error: Any = Column(Float)
    mae: Any = Column(Float)
    rmse: Any = Column(Float)
    resource_effectiveness: Any = Column(Float)
    model_version: Any = Column(String(50))
    retraining_triggered: Any = Column(Boolean, default=False)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
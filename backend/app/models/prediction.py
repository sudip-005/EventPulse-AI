from sqlalchemy import Column, String, DateTime, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Prediction(Base):
    __tablename__ = "predictions"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), nullable=False)
    road_id: Any = Column(String(100), nullable=False)
    prediction_timestamp: Any = Column(DateTime(timezone=True), nullable=False)
    forecast_timestamp: Any = Column(DateTime(timezone=True), nullable=False)
    congestion_score: Any = Column(Float)
    predicted_speed: Any = Column(Float)
    predicted_volume: Any = Column(Integer)
    delay_minutes: Any = Column(Integer)
    confidence: Any = Column(Float)
    model_version: Any = Column(String(50))
    features_used: Any = Column(JSON)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
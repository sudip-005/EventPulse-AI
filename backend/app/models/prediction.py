from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Prediction(Base):
    __tablename__ = "predictions"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    prediction_timestamp: Any = Column(DateTime(timezone=True), nullable=False)
    forecast_timestamp: Any = Column(DateTime(timezone=True), nullable=False)
    impact_score: Any = Column(Float)
    impact_level: Any = Column(String(20))
    expected_duration_minutes: Any = Column(Float)
    closure_probability: Any = Column(Float)
    risk_score: Any = Column(Float)
    confidence: Any = Column(Float)
    top_factor_1: Any = Column(String(100))
    top_factor_2: Any = Column(String(100))
    top_factor_3: Any = Column(String(100))
    model_version: Any = Column(String(50))
    features_used: Any = Column(JSON)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    event = relationship("Event", back_populates="predictions")
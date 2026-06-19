from sqlalchemy import Column, String, DateTime, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    road_id = Column(String(100), nullable=False)
    prediction_timestamp = Column(DateTime(timezone=True), nullable=False)
    forecast_timestamp = Column(DateTime(timezone=True), nullable=False)
    congestion_score = Column(Float)
    predicted_speed = Column(Float)
    predicted_volume = Column(Integer)
    delay_minutes = Column(Integer)
    confidence = Column(Float)
    model_version = Column(String(50))
    features_used = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
from sqlalchemy import Column, Float, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class LearningRecord(Base):
    __tablename__ = "learning_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    prediction_id = Column(UUID(as_uuid=True))
    predicted_congestion = Column(Float)
    actual_congestion = Column(Float)
    error = Column(Float)
    mae = Column(Float)
    rmse = Column(Float)
    resource_effectiveness = Column(Float)
    model_version = Column(String(50))
    retraining_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class RiskAssessment(Base):
    """
    SQLAlchemy model representing the risk assessment and impact details for an event.
    """
    __tablename__ = "risk_assessments"

    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    impact_score: Any = Column(Float, nullable=False)
    impact_level: Any = Column(String(20), nullable=False)
    risk_score: Any = Column(Float, nullable=False)
    expected_duration_minutes: Any = Column(Float, nullable=False)
    closure_probability: Any = Column(Float, nullable=False)
    top_factor_1: Any = Column(String(100))
    top_factor_2: Any = Column(String(100))
    top_factor_3: Any = Column(String(100))
    model_version: Any = Column(String(50))
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    event = relationship("Event", back_populates="risk_assessments")
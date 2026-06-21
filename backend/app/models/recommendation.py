from sqlalchemy import Column, String, Integer, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    simulation_id: Any = Column(UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="SET NULL"))
    resource_type: Any = Column(String(50))
    resource_count: Any = Column(Integer)
    location: Any = Column(JSON)
    reasoning: Any = Column(Text)
    priority: Any = Column(Integer)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

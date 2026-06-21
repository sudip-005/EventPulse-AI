from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Simulation(Base):
    __tablename__ = "simulations"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    name: Any = Column(String(255))
    scenario_params: Any = Column(JSON, nullable=False)
    predicted_congestion: Any = Column(JSON)
    predicted_hotspots: Any = Column(JSON)
    recommendations: Any = Column(JSON)
    status: Any = Column(String(20), default="pending")
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Any = Column(DateTime(timezone=True))

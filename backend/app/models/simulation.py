from sqlalchemy import Column, String, JSON, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255))
    scenario_params = Column(JSON, nullable=False)
    predicted_congestion = Column(JSON)
    predicted_hotspots = Column(JSON)
    recommendations = Column(JSON)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class TrafficData(Base):
    __tablename__ = "traffic_data"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id: Any = Column(String(100), nullable=False)
    timestamp: Any = Column(DateTime(timezone=True), nullable=False)
    speed_kmh: Any = Column(Float)
    volume: Any = Column(Integer)
    occupancy: Any = Column(Float)
    congestion_level: Any = Column(Integer)
    weather_condition: Any = Column(String(50))
    temperature: Any = Column(Float)
    precipitation: Any = Column(Float)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
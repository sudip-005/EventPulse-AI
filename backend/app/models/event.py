from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Event(Base):
    __tablename__ = "events"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Any = Column(String(255), nullable=False)
    event_type: Any = Column(String(50), nullable=False)
    description: Any = Column(Text)
    location: Any = Column(Geography('POINT', srid=4326), nullable=False)
    address: Any = Column(String(255))
    estimated_attendance: Any = Column(Integer)
    start_time: Any = Column(DateTime(timezone=True), nullable=False)
    end_time: Any = Column(DateTime(timezone=True), nullable=False)
    impact_score: Any = Column(Float)
    risk_score: Any = Column(Float)
    status: Any = Column(String(20), default="scheduled")
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
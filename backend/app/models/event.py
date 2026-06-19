from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid
from datetime import datetime

class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(Text)
    location = Column(Geography('POINT', srid=4326), nullable=False)
    address = Column(String(255))
    estimated_attendance = Column(Integer)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    impact_score = Column(Float)
    risk_score = Column(Float)
    status = Column(String(20), default="scheduled")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
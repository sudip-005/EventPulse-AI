from sqlalchemy import Column, String, Integer, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), nullable=False)
    simulation_id: Any = Column(UUID(as_uuid=True))
    resource_type: Any = Column(String(50))
    resource_count: Any = Column(Integer)
    location: Any = Column(Geography('POINT', srid=4326))
    reasoning: Any = Column(Text)
    priority: Any = Column(Integer)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
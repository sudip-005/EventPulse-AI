from sqlalchemy import Column, String, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid
from datetime import datetime

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    simulation_id = Column(UUID(as_uuid=True))
    resource_type = Column(String(50))
    resource_count = Column(Integer)
    location = Column(Geography('POINT', srid=4326))
    reasoning = Column(Text)
    priority = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
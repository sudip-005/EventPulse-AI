from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid
from datetime import datetime

class Hotspot(Base):
    __tablename__ = "hotspots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    cluster_id = Column(String(100))
    center = Column(Geography('POINT', srid=4326), nullable=False)
    severity = Column(Integer)
    affected_roads = Column(JSON)
    radius_meters = Column(Float)
    congestion_score = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Hotspot(Base):
    __tablename__ = "hotspots"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Any = Column(UUID(as_uuid=True), nullable=False)
    cluster_id: Any = Column(String(100))
    center: Any = Column(Geography('POINT', srid=4326), nullable=False)
    severity: Any = Column(Integer)
    affected_roads: Any = Column(JSON)
    radius_meters: Any = Column(Float)
    congestion_score: Any = Column(Float)
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
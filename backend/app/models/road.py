from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any

class Road(Base):
    __tablename__ = "roads"
    
    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id: Any = Column(String(100), unique=True, nullable=False)
    name: Any = Column(String(255))
    geometry: Any = Column(JSON, nullable=False)
    length_meters: Any = Column(Float)
    speed_limit_kmh: Any = Column(Integer)
    capacity: Any = Column(Integer)
    lanes: Any = Column(Integer, default=2)
    road_type: Any = Column(String(50))
    one_way: Any = Column(Boolean, default=False)
    from_node: Any = Column(String(100))
    to_node: Any = Column(String(100))
    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

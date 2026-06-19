from sqlalchemy import Column, String, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.core.database import Base
import uuid

class Road(Base):
    __tablename__ = "roads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255))
    geometry = Column(Geography('LINESTRING', srid=4326), nullable=False)
    length_meters = Column(Float)
    speed_limit_kmh = Column(Integer)
    capacity = Column(Integer)
    lanes = Column(Integer, default=2)
    road_type = Column(String(50))
    one_way = Column(Boolean, default=False)
    from_node = Column(String(100))
    to_node = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
from sqlalchemy import Column, String, DateTime, Float, Integer
from app.core.database import Base
from datetime import datetime

class TrafficData(Base):
    __tablename__ = "traffic_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    speed_kmh = Column(Float)
    volume = Column(Integer)
    occupancy = Column(Float)
    congestion_level = Column(Integer)
    weather_condition = Column(String(50))
    temperature = Column(Float)
    precipitation = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
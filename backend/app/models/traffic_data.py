from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime, timezone
from typing import Any


class TrafficData(Base):
    __tablename__ = "traffic_data"

    id: Any = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id: Any = Column(String(100), nullable=False, index=True)
    event_id: Any = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)

    # Observed measurements
    observed_at: Any = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    congestion_score: Any = Column(Float, nullable=False, default=0.0)   # 0–100
    vehicle_density: Any = Column(Float, nullable=True)                   # vehicles/km
    average_speed_kmh: Any = Column(Float, nullable=True)
    delay_minutes: Any = Column(Float, nullable=True)
    vehicle_count: Any = Column(Integer, nullable=True)

    # Contextual flags
    is_incident: Any = Column(Boolean, default=False)
    is_road_closed: Any = Column(Boolean, default=False)
    source: Any = Column(String(50), default="forecast")  # "forecast" | "simulation" | "sensor"

    created_at: Any = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

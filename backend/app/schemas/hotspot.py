from pydantic import BaseModel
from typing import List, Optional, Tuple

class HotspotDetectionRequest(BaseModel):
    event_id: str
    algorithm: str = "dbscan"  # or "hdbscan"
    eps: float = 200.0  # meters
    min_samples: int = 5

class HotspotResponse(BaseModel):
    id: str
    cluster_id: str
    center: Tuple[float, float]  # (lat, lon)
    severity: int
    point_count: int
    radius_meters: float
    avg_congestion: float
    max_congestion: float
    affected_roads: List[str]
from pydantic import BaseModel
from typing import List, Optional, Tuple

class RouteRequest(BaseModel):
    origin: Tuple[float, float]
    destination: Tuple[float, float]
    num_routes: int = 3
    avoid_hotspots: bool = True
    event_id: Optional[str] = None

class RoutePath(BaseModel):
    coordinates: List[Tuple[float, float]]
    travel_time_seconds: float
    distance_meters: float

class RouteResponse(BaseModel):
    primary: RoutePath
    alternatives: List[RoutePath]
    time_savings: List[float]  # savings compared to primary
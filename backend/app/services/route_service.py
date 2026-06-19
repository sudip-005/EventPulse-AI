from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from app.geospatial.routing import RouteDiversionEngine
from app.models.road import Road

class RouteService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = RouteDiversionEngine()
        self._build_network()

    def _build_network(self):
        roads = self.db.query(Road).all()
        road_dicts = []
        for r in roads:
            road_dicts.append({
                "from_node": r.from_node,
                "to_node": r.to_node,
                "length_meters": r.length_meters,
                "speed_limit_kmh": r.speed_limit_kmh,
                "capacity": r.capacity,
                "road_id": r.road_id,
                "geometry": r.geometry,
                "one_way": r.one_way,
                "congestion": 0  # would get from traffic
            })
        self.engine.build_road_network(road_dicts)

    async def find_routes(self, origin: Tuple[float, float], destination: Tuple[float, float], num_routes: int = 3, avoid_hotspots: bool = True, event_id: Optional[str] = None) -> List:
        # For hackathon, return mock
        # In production, implement with networkx
        return [{
            "primary": {"coordinates": [origin, destination], "travel_time_seconds": 600, "distance_meters": 5000},
            "alternatives": [],
            "time_savings": []
        }]

    async def get_road_network_geojson(self) -> dict:
        roads = self.db.query(Road).all()
        features = []
        for r in roads:
            # Convert geometry to GeoJSON
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": []  # would extract from r.geometry
                },
                "properties": {"road_id": r.road_id, "name": r.name}
            })
        return {"type": "FeatureCollection", "features": features}
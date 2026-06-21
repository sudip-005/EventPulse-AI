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
                "congestion": 0  # Default to 0, updated dynamically during forecasts
            })
        self.engine.build_road_network(road_dicts)

    async def find_routes(self, origin: Tuple[float, float], destination: Tuple[float, float], num_routes: int = 3, avoid_hotspots: bool = True, event_id: Optional[str] = None) -> List:
        hotspots = []
        if event_id:
            from app.models.hotspot import Hotspot
            from app.services.hotspot_service import HotspotService
            hotspot_service = HotspotService(self.db)
            db_hotspots = self.db.query(Hotspot).filter(Hotspot.event_id == event_id).all()
            for h in db_hotspots:
                lat, lon = hotspot_service._get_hotspot_coordinates(h)
                hotspots.append({
                    "center": (lat, lon),
                    "radius_meters": h.radius_meters,
                    "severity": h.severity
                })
        
        # Compute alternate routes
        routes = self.engine.find_alternate_routes(
            origin=origin,
            destination=destination,
            num_routes=num_routes,
            avoid_hotspots=avoid_hotspots,
            hotspots=hotspots
        )
        
        if not routes:
            return [{
                "primary": {"coordinates": [origin, destination], "travel_time_seconds": 9999.0, "distance_meters": 99999.0},
                "alternatives": [],
                "time_savings": []
            }]
            
        primary = routes[0]
        alternatives = routes[1:]
        
        # Time savings compared to primary route (seconds difference)
        time_savings = []
        primary_time = primary["travel_time_seconds"]
        for alt in alternatives:
            alt_time = alt["travel_time_seconds"]
            time_savings.append(alt_time - primary_time)
            
        return [{
            "primary": {
                "coordinates": primary["path"],
                "travel_time_seconds": primary["travel_time_seconds"],
                "distance_meters": primary["distance_meters"]
            },
            "alternatives": [
                {
                    "coordinates": alt["path"],
                    "travel_time_seconds": alt["travel_time_seconds"],
                    "distance_meters": alt["distance_meters"]
                } for alt in alternatives
            ],
            "time_savings": time_savings
        }]

    async def get_road_network_geojson(self) -> dict:
        roads = self.db.query(Road).all()
        
        features = []
        for r in roads:
            geom = r.geometry or {"type": "LineString", "coordinates": []}
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {"road_id": r.road_id, "name": r.name}
            })
        return {"type": "FeatureCollection", "features": features}

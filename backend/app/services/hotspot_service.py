from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Tuple
from app.geospatial.clustering import HotspotDetector
from app.models.hotspot import Hotspot
from app.models.event import Event
from app.schemas.hotspot import HotspotResponse
from app.services.forecast_service import ForecastService
import random

class HotspotService:
    def __init__(self, db: Session):
        self.db = db
        self.detector = HotspotDetector()

    async def detect_hotspots(self, event_id: str, algorithm: str = "dbscan", eps: float = 200.0, min_samples: int = 5) -> List[HotspotResponse]:
        # Fetch target event
        target_event = self.db.query(Event).filter(Event.id == event_id).first()
        if not target_event:
            raise ValueError("Event not found")
            
        # Get all events
        events = self.db.query(Event).all()
        
        points = []
        scores = []
        
        for e in events:
            # Use event's precalculated impact_score or fallback
            impact_score = e.impact_score if e.impact_score is not None else 45.0
            
            if impact_score > 50:
                lat, lon = self._get_event_coordinates(e)
                points.append((lat, lon))
                scores.append(impact_score)
                
        # If we don't have enough points for DBSCAN/HDBSCAN, simulate a cluster around the target event
        if len(points) < min_samples:
            target_lat, target_lon = self._get_event_coordinates(target_event)
            target_impact = target_event.impact_score if target_event.impact_score is not None else 45.0
            if target_impact > 50:
                points = [(target_lat + random.uniform(-0.001, 0.001), target_lon + random.uniform(-0.001, 0.001)) for _ in range(min_samples)]
                scores = [target_impact + random.normalvariate(0, 5) for _ in range(min_samples)]
            else:
                return []
                
        # Run DBSCAN or HDBSCAN
        clusters = self.detector.detect_hotspots(points, scores, eps, min_samples)
        
        # Save to DB and return responses
        results = []
        for c in clusters:
            center_wkt = f"POINT({c['center'][1]} {c['center'][0]})"
            hotspot = Hotspot(
                event_id=event_id,
                cluster_id=c["cluster_id"],
                center=center_wkt,
                severity=c["severity"],
                affected_roads=[],
                radius_meters=c["radius_meters"],
                impact_score=c["avg_congestion"]
            )
            self.db.add(hotspot)
            self.db.commit()
            self.db.refresh(hotspot)
            
            results.append(HotspotResponse(
                id=str(hotspot.id),
                cluster_id=hotspot.cluster_id,
                center=(c["center"][0], c["center"][1]),
                severity=hotspot.severity,
                point_count=c["point_count"],
                radius_meters=hotspot.radius_meters,
                avg_congestion=c["avg_congestion"],
                max_congestion=c["max_congestion"],
                affected_roads=[]
            ))
        return results

    async def get_hotspots_for_event(self, event_id: str) -> List[HotspotResponse]:
        hotspots = self.db.query(Hotspot).filter(Hotspot.event_id == event_id).all()
        results = []
        for h in hotspots:
            lat, lon = self._get_hotspot_coordinates(h)
            results.append(HotspotResponse(
                id=str(h.id),
                cluster_id=h.cluster_id,
                center=(lat, lon),
                severity=h.severity,
                point_count=0,
                radius_meters=h.radius_meters,
                avg_congestion=h.impact_score or 0.0,
                max_congestion=h.impact_score or 0.0,
                affected_roads=[]
            ))
        return results

    def _get_event_coordinates(self, event: Event) -> Tuple[float, float]:
        """Safely extracts latitude and longitude from an Event geometry point."""
        try:
            res = self.db.query(func.ST_Y(event.location), func.ST_X(event.location)).filter(Event.id == event.id).first()
            if res and res[0] is not None and res[1] is not None:
                return float(res[0]), float(res[1])
        except Exception:
            pass
            
        try:
            if hasattr(event.location, 'y') and hasattr(event.location, 'x'):
                return float(event.location.y), float(event.location.x)
        except Exception:
            pass
            
        return 19.0760, 72.8777  # Default coordinates

    def _get_hotspot_coordinates(self, hotspot: Hotspot) -> Tuple[float, float]:
        """Safely extracts latitude and longitude from a Hotspot center point."""
        try:
            res = self.db.query(func.ST_Y(hotspot.center), func.ST_X(hotspot.center)).filter(Hotspot.id == hotspot.id).first()
            if res and res[0] is not None and res[1] is not None:
                return float(res[0]), float(res[1])
        except Exception:
            pass
            
        try:
            if hasattr(hotspot.center, 'y') and hasattr(hotspot.center, 'x'):
                return float(hotspot.center.y), float(hotspot.center.x)
        except Exception:
            pass
            
        return 19.0760, 72.8777  # Default coordinates
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.geospatial.clustering import HotspotDetector
from app.models.hotspot import Hotspot
from app.schemas.hotspot import HotspotResponse
from app.services.forecast_service import ForecastService
import asyncio

class HotspotService:
    def __init__(self, db: Session):
        self.db = db
        self.detector = HotspotDetector()

    async def detect_hotspots(self, event_id: str, algorithm: str = "dbscan", eps: float = 200.0, min_samples: int = 5) -> List[HotspotResponse]:
        # Get forecasts for event
        forecast_service = ForecastService(self.db)
        forecast_resp = await forecast_service.generate_forecast(event_id, horizon_hours=2, include_roads=False)
        # Extract points with congestion > 50
        points = []
        scores = []
        for f in forecast_resp.forecasts:
            if f.congestion_score > 50:
                # Need road location; for demo we randomize
                # In reality, get road geometry
                lat = 19.0760 + random.uniform(-0.05, 0.05)
                lon = 72.8777 + random.uniform(-0.05, 0.05)
                points.append((lat, lon))
                scores.append(f.congestion_score)
        if not points:
            return []
        # Detect
        clusters = self.detector.detect_hotspots(points, scores, eps, min_samples)
        # Save to DB and return responses
        results = []
        for c in clusters:
            hotspot = Hotspot(
                event_id=event_id,
                cluster_id=c["cluster_id"],
                center=f"POINT({c['center'][1]} {c['center'][0]})",
                severity=c["severity"],
                affected_roads=[],
                radius_meters=c["radius_meters"],
                congestion_score=c["avg_congestion"]
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
        return [HotspotResponse(
            id=str(h.id),
            cluster_id=h.cluster_id,
            center=(h.center.x, h.center.y),  # needs conversion
            severity=h.severity,
            point_count=0,
            radius_meters=h.radius_meters,
            avg_congestion=h.congestion_score,
            max_congestion=h.congestion_score,
            affected_roads=[]
        ) for h in hotspots]
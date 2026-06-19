from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from app.recommendations.resource_allocator import ResourceRecommender
from app.models.recommendation import Recommendation
from app.models.event import Event
from app.models.hotspot import Hotspot
from app.schemas.recommendation import RecommendationResponse
import uuid

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.recommender = ResourceRecommender()

    async def generate_recommendations(self, event_id: str, simulation_id: Optional[str] = None) -> List[RecommendationResponse]:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
        hotspots = self.db.query(Hotspot).filter(Hotspot.event_id == event_id).all()
        hotspot_data = []
        for h in hotspots:
            lat, lon = self._get_hotspot_coordinates(h)
            hotspot_data.append({
                "center": (lat, lon),
                "severity": h.severity,
                "radius_meters": h.radius_meters,
                "avg_congestion": h.impact_score or 0.0
            })
        
        event_lat, event_lon = self._get_event_coordinates(event)
        event_dict = {
            "name": event.name,
            "estimated_attendance": event.estimated_attendance or 0,
            "location": (event_lat, event_lon),
            "impact_score": event.impact_score
        }
        recommendations = self.recommender.recommend_resources(event_dict, hotspot_data, [])
        
        # Store in DB
        for res_type, items in recommendations.items():
            if res_type == "reasoning":
                continue
            for item in items:
                rec = Recommendation(
                    id=uuid.uuid4(),
                    event_id=event_id,
                    simulation_id=simulation_id,
                    resource_type=res_type,
                    resource_count=item.get("count", 0),
                    location=f"POINT({item['location'][1]} {item['location'][0]})",
                    reasoning=item.get("reasoning", ""),
                    priority=item.get("priority", 1)
                )
                self.db.add(rec)
        self.db.commit()
        
        # Return as responses
        saved_recs = self.db.query(Recommendation).filter(Recommendation.event_id == event_id).all()
        return [RecommendationResponse(
            id=str(r.id),
            resource_type=r.resource_type,
            count=r.resource_count,
            location=self._get_recommendation_coordinates(r),
            reasoning=r.reasoning,
            priority=r.priority
        ) for r in saved_recs]

    async def get_recommendations_for_event(self, event_id: str) -> List[RecommendationResponse]:
        recs = self.db.query(Recommendation).filter(Recommendation.event_id == event_id).all()
        return [RecommendationResponse(
            id=str(r.id),
            resource_type=r.resource_type,
            count=r.resource_count,
            location=self._get_recommendation_coordinates(r),
            reasoning=r.reasoning,
            priority=r.priority
        ) for r in recs]

    def _get_event_coordinates(self, event: Event) -> Tuple[float, float]:
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
            
        return 19.0760, 72.8777

    def _get_hotspot_coordinates(self, hotspot: Hotspot) -> Tuple[float, float]:
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
            
        return 19.0760, 72.8777

    def _get_recommendation_coordinates(self, rec: Recommendation) -> Tuple[float, float]:
        try:
            res = self.db.query(func.ST_Y(rec.location), func.ST_X(rec.location)).filter(Recommendation.id == rec.id).first()
            if res and res[0] is not None and res[1] is not None:
                return float(res[0]), float(res[1])
        except Exception:
            pass
            
        try:
            if hasattr(rec.location, 'y') and hasattr(rec.location, 'x'):
                return float(rec.location.y), float(rec.location.x)
        except Exception:
            pass
            
        return 19.0760, 72.8777
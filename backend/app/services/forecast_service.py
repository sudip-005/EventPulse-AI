from __future__ import annotations

import numpy as np
import math
import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.event import Event
from app.models.prediction import Prediction
from app.ml.inference import XGBoostInference
from app.ml.features import FeatureEngineer
from app.schemas.forecast import ForecastResponse, RoadForecast
from app.services.risk_service import RiskService

class ForecastService:
    def __init__(self, db: Session):
        self.db = db
        self.inference = XGBoostInference()

    def predict_impact(self, features: np.ndarray) -> Tuple[float, str]:
        return self.inference.predict_impact(features)

    def predict_duration(self, features: np.ndarray) -> float:
        return self.inference.predict_duration(features)

    def predict_closure_probability(self, features: np.ndarray, impact_score: float, duration_minutes: float) -> float:
        requires_closure = bool(features[3] > 0.5)
        if requires_closure:
            return 1.0
        return min(impact_score / 150.0 + duration_minutes / 1800.0, 0.95)

    async def generate_forecast(self, event_id: str, horizon_hours: int = 6, include_roads: bool = False) -> ForecastResponse:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
        
        now = datetime.now(timezone.utc)
        
        # Build features
        event_dict = {
            "estimated_attendance": event.estimated_attendance,
            "event_type": event.event_type,
            "priority": getattr(event, "priority", None) or "Medium",
            "requires_road_closure": getattr(event, "requires_road_closure", False) or False
        }
        weather_dict = {"temperature": 25.0, "precipitation": 0.0}
        
        features = FeatureEngineer.build_feature_vector(event_dict, weather_dict, event.start_time)
        
        # Run workflow: Event -> Feature Builder -> Impact Model -> Duration Model -> Risk Service -> Response
        impact_score, impact_level = self.predict_impact(features)
        duration_minutes = self.predict_duration(features)
        closure_prob = self.predict_closure_probability(features, impact_score, duration_minutes)
        
        # Risk Service assessment
        assessment = RiskService.build_assessment(impact_score, duration_minutes, closure_prob)
        risk_score = assessment["risk_score"]
        
        # Explanations
        top_factors = self.inference._explain(features)
        
        # Compute confidence from impact score (higher impact = more certain)
        confidence = round(min(0.75 + (impact_score / 400.0), 0.98), 2)
        
        # Save Prediction record
        prediction_record = Prediction(
            event_id=event.id,
            prediction_timestamp=now,
            forecast_timestamp=event.start_time,
            impact_score=impact_score,
            impact_level=impact_level,
            expected_duration_minutes=duration_minutes,
            closure_probability=closure_prob,
            risk_score=risk_score,
            confidence=confidence,
            top_factor_1=top_factors[0] if len(top_factors) > 0 else None,
            top_factor_2=top_factors[1] if len(top_factors) > 1 else None,
            top_factor_3=top_factors[2] if len(top_factors) > 2 else None,
            model_version="v1.0",
            features_used=event_dict
        )
        self.db.add(prediction_record)
        self.db.commit()
        self.db.refresh(prediction_record)
        
        # Generate road level forecasts
        roads_forecast = self._generate_road_forecasts(event, impact_score)
        
        return ForecastResponse(
            event_id=str(event.id),
            generated_at=now,
            impact_score=impact_score,
            impact_level=impact_level,
            expected_duration_minutes=duration_minutes,
            closure_probability=closure_prob,
            risk_score=risk_score,
            confidence=confidence,
            top_factors=top_factors,
            roads=roads_forecast
        )

    async def get_forecasts_for_event(self, event_id: str) -> List[ForecastResponse]:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
            
        predictions = self.db.query(Prediction).filter(Prediction.event_id == event_id).all()
        if predictions:
            return [
                ForecastResponse(
                    event_id=str(p.event_id),
                    generated_at=p.prediction_timestamp,
                    impact_score=p.impact_score or 0.0,
                    impact_level=p.impact_level or "MEDIUM",
                    expected_duration_minutes=p.expected_duration_minutes or 120.0,
                    closure_probability=p.closure_probability or 0.0,
                    risk_score=p.risk_score or 0.0,
                    confidence=p.confidence or 0.9,
                    top_factors=[f for f in [p.top_factor_1, p.top_factor_2, p.top_factor_3] if f is not None],
                    roads=self._generate_road_forecasts(event, p.impact_score or 0.0)
                ) for p in predictions
            ]
        return [await self.generate_forecast(event_id, 6, True)]

    def _generate_road_forecasts(self, event: Event, impact_score: float) -> List[RoadForecast]:
        from app.models.road import Road
        from app.geospatial.routing import parse_linestring_wkt
        from geopy.distance import geodesic
        
        # Fetch all roads from database
        roads = self.db.query(
            Road.road_id,
            Road.name,
            Road.speed_limit_kmh,
            Road.capacity,
            func.ST_AsText(Road.geometry).label("geom_wkt")
        ).all()
        
        event_lat, event_lon = self._get_event_coordinates(event)
        
        attendance = event.estimated_attendance or 1000
        decay_radius = max(500.0, math.log(attendance + 1) * 300.0)
        
        road_forecasts = []
        for r in roads:
            coords = parse_linestring_wkt(r.geom_wkt)
            if not coords:
                continue
            midpoint = coords[len(coords) // 2]
            dist_to_event = geodesic((event_lat, event_lon), midpoint).meters
            
            # Seed based on road_id hash for consistent base traffic
            random.seed(hash(r.road_id) % 2**32)
            base_congestion = 15.0 + random.random() * 15.0
            
            impact_multiplier = math.exp(-dist_to_event / decay_radius)
            congestion = base_congestion + (impact_score * impact_multiplier)
            congestion = min(max(congestion, 0.0), 100.0)
            
            speed_limit = r.speed_limit_kmh or 50.0
            predicted_speed = speed_limit * (1.0 - (congestion / 100.0) * 0.8)
            predicted_speed = max(predicted_speed, 5.0)
            
            length_meters = 100.0
            speed_mps = predicted_speed / 3.6
            speed_limit_mps = speed_limit / 3.6
            delay = (length_meters / speed_mps - length_meters / speed_limit_mps) / 60.0
            delay = max(delay, 0.0)
            
            # Vehicle density: estimated from congestion score and road capacity
            # capacity is vehicles/hour at free flow; at congestion C, density ~ C/100 * capacity / speed_kmh
            road_capacity = r.capacity or 1800  # default vehicles/hour
            vehicle_density = round((congestion / 100.0) * road_capacity / max(predicted_speed, 5.0), 1)
            
            road_forecasts.append(RoadForecast(
                road_id=r.road_id,
                name=r.name,
                congestion_score=congestion,
                predicted_speed=predicted_speed,
                delay_minutes=delay,
                vehicle_density=vehicle_density,
                coordinates=coords
            ))
            
        return road_forecasts

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
from __future__ import annotations

import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.prediction import Prediction
from app.ml.inference import XGBoostInference
from app.ml.features import FeatureEngineer
from app.schemas.forecast import ForecastResponse
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
            "priority": "Medium",
            "requires_road_closure": False
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
            confidence=0.9,
            top_factor_1=top_factors[0] if len(top_factors) > 0 else None,
            top_factor_2=top_factors[1] if len(top_factors) > 1 else None,
            top_factor_3=top_factors[2] if len(top_factors) > 2 else None,
            model_version="v1.0",
            features_used=event_dict
        )
        self.db.add(prediction_record)
        self.db.commit()
        self.db.refresh(prediction_record)
        
        return ForecastResponse(
            event_id=str(event.id),
            generated_at=now,
            impact_score=impact_score,
            impact_level=impact_level,
            expected_duration_minutes=duration_minutes,
            closure_probability=closure_prob,
            risk_score=risk_score,
            confidence=0.9,
            top_factors=top_factors
        )

    async def get_forecasts_for_event(self, event_id: str) -> List[ForecastResponse]:
        # Fetch existing predictions or generate a new one
        predictions = self.db.query(Prediction).filter(Prediction.event_id == event_id).all()
        if predictions:
            return [
                ForecastResponse(
                    event_id=str(p.event_id),
                    generated_at=p.prediction_timestamp,
                    impact_score=p.impact_score,
                    impact_level=p.impact_level,
                    expected_duration_minutes=p.expected_duration_minutes,
                    closure_probability=p.closure_probability,
                    risk_score=p.risk_score,
                    confidence=p.confidence or 0.9,
                    top_factors=[f for f in [p.top_factor_1, p.top_factor_2, p.top_factor_3] if f is not None]
                ) for p in predictions
            ]
        return [await self.generate_forecast(event_id, 6, False)]
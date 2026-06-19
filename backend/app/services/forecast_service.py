from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
import random
from app.models.event import Event
from app.models.road import Road
from app.models.traffic import TrafficData
from app.models.prediction import Prediction
from app.ml.inference import XGBoostInference
from app.ml.features import FeatureEngineer
from app.schemas.forecast import ForecastResponse, ForecastItem

class ForecastService:
    def __init__(self, db: Session):
        self.db = db
        self.inference = XGBoostInference()

    async def generate_forecast(self, event_id: str, horizon_hours: int, include_roads: bool = False) -> ForecastResponse:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
        roads = self.db.query(Road).all()
        forecasts = []
        now = datetime.now(timezone.utc)
        for hour in range(1, horizon_hours + 1):
            forecast_time = now + timedelta(hours=hour)
            for road in roads[:10]:  # Limit for demo
                # Build feature vector
                traffic = self.db.query(TrafficData).filter(TrafficData.road_id == road.road_id).order_by(TrafficData.timestamp.desc()).first()
                traffic_dict = {
                    "speed": traffic.speed_kmh if traffic else 40,
                    "volume": traffic.volume if traffic else 500,
                    "occupancy": traffic.occupancy if traffic else 0.3
                }
                event_dict = {
                    "impact_score": event.impact_score,
                    "risk_score": event.risk_score,
                    "estimated_attendance": event.estimated_attendance or 0,
                    "duration_hours": (event.end_time - event.start_time).total_seconds() / 3600
                }
                weather_dict = {"temperature": 25, "precipitation": 0}
                features = FeatureEngineer.build_feature_vector(
                    traffic_dict, forecast_time, event_dict, weather_dict, road.capacity or 1000
                )
                pred = self.inference.predict(features)
                forecast_item = ForecastItem(
                    road_id=road.road_id,
                    timestamp=forecast_time,
                    congestion_score=pred["congestion_score"],
                    predicted_speed=road.speed_limit_kmh * (1 - pred["congestion_score"]/100),
                    delay_minutes=int(pred["congestion_score"] * 0.5),
                    confidence=pred["confidence"]
                )
                forecasts.append(forecast_item)
        # Summarize
        if forecasts:
            avg_cong = sum(f.congestion_score for f in forecasts) / len(forecasts)
            max_cong = max(f.congestion_score for f in forecasts)
        else:
            avg_cong = max_cong = 0
        summary = {"avg_congestion": avg_cong, "max_congestion": max_cong}
        return ForecastResponse(
            event_id=event_id,
            generated_at=now,
            horizon_hours=horizon_hours,
            forecasts=forecasts,
            summary=summary
        )

    async def get_forecasts_for_event(self, event_id: str) -> List[ForecastResponse]:
        # In real scenario, would query predictions table
        # For demo, generate
        return [await self.generate_forecast(event_id, 6, False)]
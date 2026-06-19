import numpy as np
from datetime import datetime
from typing import Dict

class FeatureEngineer:
    @staticmethod
    def extract_temporal_features(timestamp: datetime) -> Dict:
        return {
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "month": timestamp.month,
            "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
            "is_rush_hour": 1 if (7 <= timestamp.hour <= 10) or (17 <= timestamp.hour <= 20) else 0,
            "hour_sin": np.sin(2 * np.pi * timestamp.hour / 24),
            "hour_cos": np.cos(2 * np.pi * timestamp.hour / 24),
        }

    @staticmethod
    def extract_event_features(event: Dict) -> Dict:
        return {
            "event_impact_score": event.get("impact_score", 0),
            "event_risk_score": event.get("risk_score", 0),
            "estimated_attendance": np.log1p(event.get("estimated_attendance", 0)),
            "event_duration_hours": event.get("duration_hours", 0),
        }

    @staticmethod
    def extract_weather_features(weather: Dict) -> Dict:
        return {
            "temperature": weather.get("temperature", 25),
            "precipitation": weather.get("precipitation", 0),
            "visibility_km": weather.get("visibility", 10),
            "is_raining": 1 if weather.get("precipitation", 0) > 0 else 0,
        }

    @staticmethod
    def build_feature_vector(traffic: Dict, temporal: datetime, event: Dict, weather: Dict, road_capacity: float) -> np.ndarray:
        features = {}
        features["historical_speed"] = traffic.get("speed", 40)
        features["historical_volume"] = traffic.get("volume", 500)
        features["occupancy"] = traffic.get("occupancy", 0.3)
        features["road_capacity"] = road_capacity
        features["capacity_utilization"] = traffic.get("volume", 500) / road_capacity if road_capacity > 0 else 0
        features.update(FeatureEngineer.extract_temporal_features(temporal))
        features.update(FeatureEngineer.extract_event_features(event))
        features.update(FeatureEngineer.extract_weather_features(weather))
        return np.array(list(features.values()))
from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

class FeatureEngineer:
    FEATURE_COLUMNS = [
        "estimated_attendance",
        "event_type_encoded",
        "priority_encoded",
        "requires_road_closure",
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "is_rush_hour",
        "temperature",
        "precipitation",
        "is_raining",
    ]

    @staticmethod
    def get_event_type_map() -> Dict[str, int]:
        return {
            "concert": 1,
            "sports": 2,
            "festival": 3,
            "accident": 4,
            "construction": 5,
            "protest": 6,
            "marathon": 7,
            "other": 8,
        }

    @staticmethod
    def get_priority_map() -> Dict[str, int]:
        return {
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "Critical": 4,
        }

    @staticmethod
    def extract_temporal_features(timestamp: datetime) -> Dict[str, Any]:
        return {
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "month": timestamp.month,
            "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
            "is_rush_hour": 1 if (7 <= timestamp.hour <= 10) or (17 <= timestamp.hour <= 20) else 0,
        }

    @staticmethod
    def extract_weather_features(weather: Dict[str, Any]) -> Dict[str, Any]:
        precip = weather.get("precipitation", 0.0)
        return {
            "temperature": weather.get("temperature", 25.0),
            "precipitation": precip,
            "is_raining": 1 if precip > 0.0 else 0,
        }

    @staticmethod
    def build_feature_dict(event: Dict[str, Any], weather: Dict[str, Any], temporal: datetime) -> Dict[str, Any]:
        event_type_str = event.get("event_type", "other").lower()
        event_type_map = FeatureEngineer.get_event_type_map()
        event_type_encoded = event_type_map.get(event_type_str, event_type_map["other"])

        priority_str = event.get("priority", "Medium")
        priority_map = FeatureEngineer.get_priority_map()
        priority_encoded = priority_map.get(priority_str, priority_map["Medium"])

        features = {
            "estimated_attendance": float(event.get("estimated_attendance", 0) or 0),
            "event_type_encoded": float(event_type_encoded),
            "priority_encoded": float(priority_encoded),
            "requires_road_closure": float(1 if event.get("requires_road_closure", False) else 0),
        }
        features.update(FeatureEngineer.extract_temporal_features(temporal))
        features.update(FeatureEngineer.extract_weather_features(weather))
        return features

    @staticmethod
    def build_feature_vector(event: Dict[str, Any], weather: Dict[str, Any], temporal: datetime) -> np.ndarray:
        feature_dict = FeatureEngineer.build_feature_dict(event, weather, temporal)
        vector = [float(feature_dict[col]) for col in FeatureEngineer.FEATURE_COLUMNS]
        return np.array(vector)

    @staticmethod
    def build_feature_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Build features for training from a raw DataFrame.
        """
        event_type_map = FeatureEngineer.get_event_type_map()
        priority_map = FeatureEngineer.get_priority_map()

        processed = pd.DataFrame(index=df.index)
        processed["estimated_attendance"] = df["estimated_attendance"].fillna(0).astype(float)
        processed["event_type_encoded"] = df["event_type"].str.lower().map(event_type_map).fillna(event_type_map["other"]).astype(float)
        processed["priority_encoded"] = df["priority"].map(priority_map).fillna(priority_map["Medium"]).astype(float)
        processed["requires_road_closure"] = df["requires_road_closure"].fillna(False).astype(int).astype(float)

        timestamps = pd.to_datetime(df["start_datetime"])
        processed["hour"] = timestamps.dt.hour.astype(float)
        processed["day_of_week"] = timestamps.dt.dayofweek.astype(float)
        processed["month"] = timestamps.dt.month.astype(float)
        processed["is_weekend"] = (timestamps.dt.dayofweek >= 5).astype(int).astype(float)
        processed["is_rush_hour"] = (((timestamps.dt.hour >= 7) & (timestamps.dt.hour <= 10)) | ((timestamps.dt.hour >= 17) & (timestamps.dt.hour <= 20))).astype(int).astype(float)

        processed["temperature"] = df["temperature"].fillna(25.0).astype(float)
        processed["precipitation"] = df["precipitation"].fillna(0.0).astype(float)
        processed["is_raining"] = (processed["precipitation"] > 0.0).astype(int).astype(float)

        return processed[FeatureEngineer.FEATURE_COLUMNS]
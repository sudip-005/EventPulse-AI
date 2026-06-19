import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from app.ml.features import FeatureEngineer

def test_extract_temporal_features():
    # Test weekend and rush hour
    weekend_rush = datetime(2026, 6, 21, 18, 30)  # Sunday 18:30
    features = FeatureEngineer.extract_temporal_features(weekend_rush)
    assert features["is_weekend"] == 1
    assert features["is_rush_hour"] == 1
    assert features["hour"] == 18
    assert features["day_of_week"] == 6

    # Test weekday non-rush hour
    weekday_night = datetime(2026, 6, 22, 23, 0)  # Monday 23:00
    features = FeatureEngineer.extract_temporal_features(weekday_night)
    assert features["is_weekend"] == 0
    assert features["is_rush_hour"] == 0
    assert features["hour"] == 23

def test_extract_weather_features():
    weather = {"temperature": 32.5, "precipitation": 12.0}
    features = FeatureEngineer.extract_weather_features(weather)
    assert features["temperature"] == 32.5
    assert features["precipitation"] == 12.0
    assert features["is_raining"] == 1

    dry_weather = {"temperature": 20.0, "precipitation": 0.0}
    features = FeatureEngineer.extract_weather_features(dry_weather)
    assert features["is_raining"] == 0

def test_build_feature_vector():
    event = {"event_type": "concert", "priority": "High", "estimated_attendance": 12000, "requires_road_closure": True}
    weather = {"temperature": 28.0, "precipitation": 0.0}
    t = datetime(2026, 6, 19, 9, 0)  # Friday 9:00 (rush hour)

    vector = FeatureEngineer.build_feature_vector(event, weather, t)
    assert isinstance(vector, np.ndarray)
    assert len(vector) == len(FeatureEngineer.FEATURE_COLUMNS)

    # Convert vector back to dict to verify values
    feat_dict = dict(zip(FeatureEngineer.FEATURE_COLUMNS, vector))
    assert feat_dict["estimated_attendance"] == 12000.0
    assert feat_dict["requires_road_closure"] == 1.0
    assert feat_dict["is_rush_hour"] == 1.0
    assert feat_dict["is_weekend"] == 0.0

def test_build_feature_df():
    df = pd.DataFrame([{
        "start_datetime": datetime(2026, 6, 19, 9, 0),
        "estimated_attendance": 5000,
        "event_type": "sports",
        "priority": "Medium",
        "requires_road_closure": False,
        "temperature": 25.0,
        "precipitation": 0.0
    }])
    processed = FeatureEngineer.build_feature_df(df)
    assert processed.shape == (1, len(FeatureEngineer.FEATURE_COLUMNS))
    assert processed.iloc[0]["event_type_encoded"] == FeatureEngineer.get_event_type_map()["sports"]
    assert processed.iloc[0]["priority_encoded"] == FeatureEngineer.get_priority_map()["Medium"]

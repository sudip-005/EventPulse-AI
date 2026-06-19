import pandas as pd
from sqlalchemy.orm import Session
from app.models.traffic import TrafficData
from app.models.road import Road

def load_training_data(db: Session) -> pd.DataFrame:
    # Query historical traffic and join with roads, events
    # For demo, return synthetic data
    import numpy as np
    np.random.seed(42)
    df = pd.DataFrame({
        "historical_speed": np.random.normal(40, 10, 1000),
        "historical_volume": np.random.normal(500, 100, 1000),
        "occupancy": np.random.uniform(0.2, 0.8, 1000),
        "road_capacity": np.random.normal(1000, 200, 1000),
        "hour": np.random.randint(0, 24, 1000),
        "day_of_week": np.random.randint(0, 7, 1000),
        "month": np.random.randint(1, 13, 1000),
        "is_weekend": np.random.randint(0, 2, 1000),
        "is_rush_hour": np.random.randint(0, 2, 1000),
        "event_impact_score": np.random.uniform(0, 100, 1000),
        "event_risk_score": np.random.uniform(0, 100, 1000),
        "estimated_attendance": np.random.normal(5000, 2000, 1000),
        "event_duration_hours": np.random.uniform(2, 8, 1000),
        "temperature": np.random.normal(25, 5, 1000),
        "precipitation": np.random.exponential(0.5, 1000),
        "visibility_km": np.random.uniform(5, 15, 1000),
        "is_raining": np.random.randint(0, 2, 1000),
        "congestion_score": np.random.uniform(0, 100, 1000)
    })
    return df
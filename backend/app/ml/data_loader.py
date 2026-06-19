from __future__ import annotations

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def load_training_data(db: Session) -> pd.DataFrame:
    """
    Loads historical event/incident records for training.
    For demonstration, returns a synthetic dataset aligning with the Astram dataset schema.
    """
    np.random.seed(42)
    size = 1000
    
    # Generate temporal dates
    start_dates = [datetime.now() - timedelta(days=np.random.randint(1, 30), hours=np.random.randint(0, 24)) for _ in range(size)]
    resolved_dates = [start_dates[i] + timedelta(minutes=np.random.normal(120, 60)) for i in range(size)]

    
    df = pd.DataFrame({
        "start_datetime": start_dates,
        "resolved_datetime": resolved_dates,
        "estimated_attendance": np.random.normal(5000, 2000, size),
        "event_type": np.random.choice(["concert", "sports", "festival", "accident", "construction", "protest", "marathon", "other"], size),
        "priority": np.random.choice(["Low", "Medium", "High", "Critical"], size, p=[0.3, 0.4, 0.2, 0.1]),
        "requires_road_closure": np.random.choice([True, False], size, p=[0.2, 0.8]),
        "temperature": np.random.normal(25, 5, size),
        "precipitation": np.random.exponential(0.5, size),
        "visibility_km": np.random.uniform(5, 15, size),
        "is_raining": np.random.choice([0, 1], size)
    })
    
    return df
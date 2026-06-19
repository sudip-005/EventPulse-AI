from datetime import datetime

def is_rush_hour(dt: datetime) -> bool:
    hour = dt.hour
    return (7 <= hour <= 10) or (17 <= hour <= 20)
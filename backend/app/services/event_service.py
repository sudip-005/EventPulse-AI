import math
from datetime import datetime
from typing import Optional
from app.schemas.event import EventCreate

class EventService:
    @staticmethod
    def calculate_impact_score(event: EventCreate) -> float:
        score = 0.0
        if event.estimated_attendance:
            score += min(math.log(event.estimated_attendance + 1) / 10, 0.5)
        type_weights = {
            "concert": 0.3, "sports": 0.35, "festival": 0.4,
            "accident": 0.5, "construction": 0.25, "protest": 0.45,
            "marathon": 0.3, "other": 0.2
        }
        score += type_weights.get(event.event_type, 0.2)
        duration_hours = (event.end_time - event.start_time).total_seconds() / 3600
        score += min(duration_hours / 24 * 0.15, 0.15)
        hour = event.start_time.hour
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            score += 0.2
        return min(score * 100, 100)

    @staticmethod
    def calculate_risk_score(event: EventCreate) -> float:
        risk = 0.0
        if event.estimated_attendance and event.estimated_attendance > 10000:
            risk += 0.3
        elif event.estimated_attendance and event.estimated_attendance > 5000:
            risk += 0.2
        if event.start_time.weekday() in [5, 6]:
            risk += 0.1
        duration_hours = (event.end_time - event.start_time).total_seconds() / 3600
        if duration_hours > 6:
            risk += 0.15
        type_risks = {
            "concert": 0.2, "sports": 0.25, "festival": 0.3,
            "accident": 0.4, "protest": 0.35, "marathon": 0.2
        }
        risk += type_risks.get(event.event_type, 0.1)
        return min(risk * 100, 100)
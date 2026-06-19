import pytest
from unittest.mock import MagicMock
import datetime
from app.services.event_service import EventService

def test_calculate_impact_score():
    event = MagicMock()
    event.estimated_attendance = 5000
    event.event_type = "sports"
    event.start_time = datetime.datetime(2026, 6, 19, 9, 0)
    event.end_time = datetime.datetime(2026, 6, 19, 12, 0)
    
    score = EventService.calculate_impact_score(event)
    assert isinstance(score, (int, float))
    assert 0.0 <= score <= 100.0

def test_calculate_risk_score():
    event = MagicMock()
    event.estimated_attendance = 12000
    event.event_type = "concert"
    event.start_time = datetime.datetime(2026, 6, 20, 19, 0)  # Saturday
    event.end_time = datetime.datetime(2026, 6, 20, 23, 0)
    
    score = EventService.calculate_risk_score(event)
    assert isinstance(score, (int, float))
    assert 0.0 <= score <= 100.0

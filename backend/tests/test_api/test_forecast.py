import pytest
from unittest.mock import MagicMock, patch
import datetime
from app.services.forecast_service import ForecastService
from app.models.event import Event
from app.schemas.forecast import ForecastResponse

@pytest.mark.asyncio
async def test_generate_forecast():
    event_id = "5b5e5db7-2d45-454b-9381-5ff693b9a703"
    event = MagicMock(spec=Event)
    event.id = event_id
    event.name = "Music Festival"
    event.event_type = "festival"
    event.estimated_attendance = 15000
    event.start_time = datetime.datetime(2026, 6, 20, 18, 0)
    event.end_time = datetime.datetime(2026, 6, 20, 23, 0)
    event.impact_score = 75.0
    event.risk_score = 80.0

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = event
    
    with patch("app.services.forecast_service.XGBoostInference") as mock_inf_cls:
        mock_inf = MagicMock()
        mock_inf.predict_impact.return_value = (70.0, "HIGH")
        mock_inf.predict_duration.return_value = 240.0
        mock_inf._explain.return_value = ["estimated_attendance", "priority_encoded"]
        mock_inf_cls.return_value = mock_inf
        
        service = ForecastService(db)
        resp = await service.generate_forecast(event_id)
        
        assert isinstance(resp, ForecastResponse)
        assert resp.event_id == event_id
        assert resp.impact_score == 70.0
        assert resp.impact_level == "HIGH"
        assert resp.expected_duration_minutes == 240.0
        assert resp.risk_score > 0.0
        assert "estimated_attendance" in resp.top_factors

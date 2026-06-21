from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Any, Dict
from app.api.deps import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """High-level system KPIs: total events, predictions, hotspots, average scores."""
    service = AnalyticsService(db)
    return service.get_overview()


@router.get("/events/breakdown")
async def get_event_type_breakdown(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Counts and average scores grouped by event type."""
    service = AnalyticsService(db)
    return service.get_event_type_breakdown()


@router.get("/ml/performance")
async def get_ml_performance(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """ML model accuracy metrics: MAE, RMSE, accuracy, F1, R²."""
    service = AnalyticsService(db)
    return service.get_ml_performance()


@router.get("/hotspots/distribution")
async def get_hotspot_distribution(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Hotspot severity distribution across the system."""
    service = AnalyticsService(db)
    return service.get_hotspot_severity_distribution()


@router.get("/timeline")
async def get_event_timeline(days: int = 7, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Events created per day over the last N days with average scores."""
    service = AnalyticsService(db)
    return service.get_timeline(days=days)


@router.get("/resources/summary")
async def get_resource_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Summary of all recommended resources grouped by type."""
    service = AnalyticsService(db)
    return service.get_resource_summary()

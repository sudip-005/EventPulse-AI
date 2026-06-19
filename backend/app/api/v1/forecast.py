from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.api.deps import get_db
from app.services.forecast_service import ForecastService
from app.schemas.forecast import ForecastRequest, ForecastResponse

router = APIRouter()

@router.post("/", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest, db: Session = Depends(get_db)):
    service = ForecastService(db)
    result = await service.generate_forecast(
        event_id=request.event_id,
        horizon_hours=request.horizon_hours,
        include_roads=request.include_roads
    )
    return result

@router.get("/{event_id}", response_model=List[ForecastResponse])
async def get_forecasts(event_id: str, db: Session = Depends(get_db)):
    service = ForecastService(db)
    forecasts = await service.get_forecasts_for_event(event_id)
    if not forecasts:
        raise HTTPException(status_code=404, detail="No forecasts found for this event")
    return forecasts
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.hotspot_service import HotspotService
from app.schemas.hotspot import HotspotResponse, HotspotDetectionRequest

router = APIRouter()

@router.post("/detect", response_model=List[HotspotResponse])
async def detect_hotspots(request: HotspotDetectionRequest, db: Session = Depends(get_db)):
    service = HotspotService(db)
    hotspots = await service.detect_hotspots(
        event_id=request.event_id,
        algorithm=request.algorithm,
        eps=request.eps,
        min_samples=request.min_samples
    )
    return hotspots

@router.get("/event/{event_id}", response_model=List[HotspotResponse])
async def get_hotspots_by_event(event_id: str, db: Session = Depends(get_db)):
    service = HotspotService(db)
    return await service.get_hotspots_for_event(event_id)
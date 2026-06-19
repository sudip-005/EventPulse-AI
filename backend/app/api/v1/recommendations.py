from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse

router = APIRouter()

@router.post("/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    service = RecommendationService(db)
    recs = await service.generate_recommendations(
        event_id=request.event_id,
        simulation_id=request.simulation_id
    )
    return recs

@router.get("/event/{event_id}", response_model=List[RecommendationResponse])
async def get_recommendations(event_id: str, db: Session = Depends(get_db)):
    service = RecommendationService(db)
    return await service.get_recommendations_for_event(event_id)
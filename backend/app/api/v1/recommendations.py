from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.models.recommendation import Recommendation

router = APIRouter()


@router.get("")
async def list_recommendations(limit: int = 100, db: Session = Depends(get_db)):
    records = db.query(Recommendation).order_by(Recommendation.created_at.desc()).limit(min(limit, 100)).all()
    return [{
        "id": str(record.id), "event_id": str(record.event_id),
        "resource_type": record.resource_type, "count": record.resource_count,
        "location": record.location, "reasoning": record.reasoning, "priority": record.priority,
    } for record in records]

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

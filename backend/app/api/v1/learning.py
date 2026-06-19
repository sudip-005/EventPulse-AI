from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.learning_service import LearningService
from app.schemas.learning import LearningRecordResponse, RetrainingRequest

router = APIRouter()

@router.post("/record")
async def record_actual_outcome(event_id: str, db: Session = Depends(get_db)):
    service = LearningService(db)
    result = await service.record_actual_outcome(event_id)
    return result

@router.get("/event/{event_id}", response_model=List[LearningRecordResponse])
async def get_learning_records(event_id: str, db: Session = Depends(get_db)):
    service = LearningService(db)
    return await service.get_records_for_event(event_id)

@router.post("/retrain")
async def trigger_retraining(request: RetrainingRequest, db: Session = Depends(get_db)):
    service = LearningService(db)
    result = await service.retrain_model(request.model_version)
    return result
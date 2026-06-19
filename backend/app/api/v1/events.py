from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event_service import EventService
from app.models.event import Event

router = APIRouter()

@router.post("/", response_model=EventResponse)
async def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    impact = EventService.calculate_impact_score(event_in)
    risk = EventService.calculate_risk_score(event_in)
    db_event = Event(
        name=event_in.name,
        event_type=event_in.event_type,
        description=event_in.description,
        location=event_in.location,
        address=event_in.address,
        estimated_attendance=event_in.estimated_attendance,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        impact_score=impact,
        risk_score=risk,
        status="scheduled"
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventResponse])
async def list_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Event).offset(skip).limit(limit).all()

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_in: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event_in.dict(exclude_unset=True).items():
        setattr(event, key, value)
    # Recalculate scores if attendance/time changed
    if "estimated_attendance" in event_in.dict(exclude_unset=True) or "start_time" in event_in.dict(exclude_unset=True):
        event.impact_score = EventService.calculate_impact_score(event)
        event.risk_score = EventService.calculate_risk_score(event)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
async def delete_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"detail": "Event deleted"}
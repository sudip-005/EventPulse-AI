from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import json
from app.api.deps import get_db
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event_service import EventService
from app.models.event import Event

router = APIRouter()

def serialize_event(e: Event, db: Session) -> dict:
    geom_json = db.query(func.ST_AsGeoJSON(e.location)).scalar()
    location_dict = json.loads(geom_json) if geom_json else {"type": "Point", "coordinates": [72.8777, 19.0760]}
    return {
        "id": str(e.id),
        "name": e.name,
        "event_type": e.event_type,
        "description": e.description,
        "address": e.address,
        "estimated_attendance": e.estimated_attendance,
        "start_time": e.start_time,
        "end_time": e.end_time,
        "impact_score": e.impact_score or 0.0,
        "risk_score": e.risk_score or 0.0,
        "status": e.status,
        "created_at": e.created_at,
        "updated_at": e.updated_at,
        "location": location_dict
    }

@router.post("/", response_model=EventResponse)
async def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    impact = EventService.calculate_impact_score(event_in)
    risk = EventService.calculate_risk_score(event_in)
    coords = event_in.location.get("coordinates", [72.8777, 19.0760])
    location_wkt = f"POINT({coords[0]} {coords[1]})"
    
    db_event = Event(
        name=event_in.name,
        event_type=event_in.event_type,
        description=event_in.description,
        location=location_wkt,
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
    return serialize_event(db_event, db)

@router.get("/", response_model=List[EventResponse])
async def list_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(Event).offset(skip).limit(limit).all()
    return [serialize_event(e, db) for e in events]

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return serialize_event(event, db)

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_in: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event_in.model_dump(exclude_unset=True).items():
        if key == "location" and value:
            coords = value.get("coordinates", [72.8777, 19.0760])
            setattr(event, key, f"POINT({coords[0]} {coords[1]})")
        else:
            setattr(event, key, value)
            
    # Recalculate scores if attendance/time changed
    if "estimated_attendance" in event_in.model_dump(exclude_unset=True) or "start_time" in event_in.model_dump(exclude_unset=True):
        event.impact_score = EventService.calculate_impact_score(event)
        event.risk_score = EventService.calculate_risk_score(event)
        
    db.add(event)
    db.commit()
    db.refresh(event)
    return serialize_event(event, db)

@router.delete("/{event_id}")
async def delete_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"detail": "Event deleted"}


@router.get("/{event_id}/risk-assessment")
async def get_risk_assessment(event_id: str, db: Session = Depends(get_db)):
    """Dedicated risk assessment for an event with breakdown and recommendations."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    risk_score = event.risk_score or 0.0
    impact_score = event.impact_score or 0.0

    if risk_score >= 75:
        risk_category = "CRITICAL"
        recommendation = "Immediate multi-agency coordination required. Deploy maximum resources."
    elif risk_score >= 55:
        risk_category = "HIGH"
        recommendation = "Deploy additional police and traffic marshals. Pre-position emergency vehicles."
    elif risk_score >= 35:
        risk_category = "MEDIUM"
        recommendation = "Standard resource deployment. Monitor hotspots closely."
    else:
        risk_category = "LOW"
        recommendation = "Routine monitoring. Standard traffic management protocols."

    factors = []
    if event.estimated_attendance and event.estimated_attendance > 10000:
        factors.append({"factor": "Large attendance", "contribution": "HIGH", "value": event.estimated_attendance})
    if impact_score > 60:
        factors.append({"factor": "High predicted impact", "contribution": "HIGH", "value": round(impact_score, 1)})
    if event.event_type in ["concert", "festival", "sports"]:
        factors.append({"factor": "High-density event type", "contribution": "MEDIUM", "value": event.event_type})

    return {
        "event_id": event_id,
        "event_name": event.name,
        "risk_score": round(risk_score, 2),
        "impact_score": round(impact_score, 2),
        "risk_category": risk_category,
        "recommendation": recommendation,
        "contributing_factors": factors,
        "assessment_timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }
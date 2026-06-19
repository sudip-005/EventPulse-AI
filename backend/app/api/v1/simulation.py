from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.simulation_service import SimulationService
from app.schemas.simulation import SimulationRequest, SimulationResponse

router = APIRouter()

@router.post("/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest, db: Session = Depends(get_db)):
    service = SimulationService(db)
    result = await service.run_simulation(
        event_id=request.event_id,
        scenario_params=request.scenario_params
    )
    return result

@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: str, db: Session = Depends(get_db)):
    service = SimulationService(db)
    sim = await service.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim
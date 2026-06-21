from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.simulation_service import SimulationService
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.models.simulation import Simulation

router = APIRouter()


@router.get("", response_model=List[SimulationResponse])
async def list_simulations(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(Simulation).order_by(Simulation.created_at.desc()).limit(min(limit, 100)).all()
    return [serialize_simulation(record) for record in records]

def serialize_simulation(sim: Simulation) -> dict:
    predicted_congestion = sim.predicted_congestion
    if isinstance(predicted_congestion, list):
        predicted_congestion = {"forecasts": predicted_congestion}
    elif not isinstance(predicted_congestion, dict):
        predicted_congestion = {"forecasts": []}

    return {
        "id": str(sim.id),
        "event_id": str(sim.event_id),
        "name": sim.name,
        "scenario_params": sim.scenario_params or {},
        "predicted_congestion": predicted_congestion,
        "predicted_hotspots": sim.predicted_hotspots or [],
        "status": sim.status,
        "created_at": sim.created_at,
        "completed_at": sim.completed_at
    }

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
    return serialize_simulation(sim)

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Tuple
from app.simulation.scenario_engine import ScenarioSimulator
from app.models.simulation import Simulation
from app.models.event import Event
from app.schemas.simulation import SimulationResponse
import uuid
from datetime import datetime

class SimulationService:
    def __init__(self, db: Session):
        self.db = db
        self.simulator = ScenarioSimulator()

    async def run_simulation(self, event_id: str, scenario_params: Dict[str, Any]) -> SimulationResponse:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
            
        event_lat, event_lon = self._get_event_coordinates(event)
        # Build base event dict
        base_event = {
            "id": str(event.id),
            "name": event.name,
            "event_type": event.event_type,
            "estimated_attendance": event.estimated_attendance or 0,
            "impact_score": event.impact_score,
            "risk_score": event.risk_score,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "location": (event_lat, event_lon)
        }
        # Simulate
        result = self.simulator.simulate_scenario(
            base_event, scenario_params, road_network=[], traffic_data=[]
        )
        # Save simulation
        sim = Simulation(
            id=uuid.uuid4(),
            event_id=event_id,
            name=scenario_params.get("name", "Scenario"),
            scenario_params=scenario_params,
            predicted_congestion=result.get("forecasts", []),
            predicted_hotspots=result.get("hotspots", []),
            recommendations=result.get("recommendations", {}),
            status="completed",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        self.db.add(sim)
        self.db.commit()
        self.db.refresh(sim)
        return SimulationResponse(
            id=str(sim.id),
            event_id=event_id,
            name=sim.name,
            scenario_params=sim.scenario_params,
            predicted_congestion=sim.predicted_congestion,
            predicted_hotspots=sim.predicted_hotspots,
            status=sim.status,
            created_at=sim.created_at,
            completed_at=sim.completed_at
        )

    async def get_simulation(self, sim_id: str) -> Simulation:
        return self.db.query(Simulation).filter(Simulation.id == sim_id).first()

    def _get_event_coordinates(self, event: Event) -> Tuple[float, float]:
        try:
            res = self.db.query(func.ST_Y(event.location), func.ST_X(event.location)).filter(Event.id == event.id).first()
            if res and res[0] is not None and res[1] is not None:
                return float(res[0]), float(res[1])
        except Exception:
            pass
            
        try:
            if hasattr(event.location, 'y') and hasattr(event.location, 'x'):
                return float(event.location.y), float(event.location.x)
        except Exception:
            pass
            
        return 19.0760, 72.8777
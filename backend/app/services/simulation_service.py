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
        base_event = {
            "id": str(event.id),
            "name": event.name,
            "event_type": event.event_type,
            "estimated_attendance": event.estimated_attendance or 0,
            "impact_score": event.impact_score or 45.0,
            "risk_score": event.risk_score or 45.0,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "location": (event_lat, event_lon)
        }
        
        # Load roads from DB
        from app.models.road import Road
        from app.geospatial.routing import parse_linestring_wkt
        
        db_roads = self.db.query(Road).all()
        
        road_network = []
        for r in db_roads:
            coords = parse_linestring_wkt(r.geometry)
            road_network.append({
                "road_id": r.road_id,
                "name": r.name,
                "speed_limit_kmh": r.speed_limit_kmh or 50,
                "capacity": r.capacity or 1000,
                "length_meters": r.length_meters or 100.0,
                "coordinates": coords
            })
            
        # Simulate
        result = self.simulator.simulate_scenario(
            base_event, scenario_params, road_network=road_network
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
            predicted_congestion={"forecasts": sim.predicted_congestion}, # wrap in dict to match schema Dict[str, Any]
            predicted_hotspots=sim.predicted_hotspots,
            status=sim.status,
            created_at=sim.created_at,
            completed_at=sim.completed_at
        )

    async def get_simulation(self, sim_id: str) -> Simulation:
        return self.db.query(Simulation).filter(Simulation.id == sim_id).first()

    def _get_event_coordinates(self, event: Event) -> Tuple[float, float]:
        if isinstance(event.location, dict):
            coordinates = event.location.get("coordinates", [])
            if len(coordinates) == 2:
                return float(coordinates[1]), float(coordinates[0])
        return 19.0760, 72.8777

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.services.route_service import RouteService
from app.schemas.route import RouteRequest, RouteResponse

router = APIRouter()

@router.post("/find", response_model=List[RouteResponse])
async def find_alternate_routes(request: RouteRequest, db: Session = Depends(get_db)):
    service = RouteService(db)
    routes = await service.find_routes(
        origin=request.origin,
        destination=request.destination,
        num_routes=request.num_routes,
        avoid_hotspots=request.avoid_hotspots,
        event_id=request.event_id
    )
    return routes

@router.get("/road-network")
async def get_road_network(db: Session = Depends(get_db)):
    service = RouteService(db)
    geojson = await service.get_road_network_geojson()
    return geojson
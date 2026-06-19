from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import events, forecast, hotspots, routes, simulation, recommendations, learning

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix=f"{settings.API_V1_STR}/events", tags=["events"])
app.include_router(forecast.router, prefix=f"{settings.API_V1_STR}/forecast", tags=["forecast"])
app.include_router(hotspots.router, prefix=f"{settings.API_V1_STR}/hotspots", tags=["hotspots"])
app.include_router(routes.router, prefix=f"{settings.API_V1_STR}/routes", tags=["routes"])
app.include_router(simulation.router, prefix=f"{settings.API_V1_STR}/simulation", tags=["simulation"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations"])
app.include_router(learning.router, prefix=f"{settings.API_V1_STR}/learning", tags=["learning"])

@app.get("/")
async def root():
    return {"message": "EventPulse AI API", "version": settings.VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}
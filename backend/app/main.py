from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import events, forecast, hotspots, routes, simulation, recommendations, learning, analytics

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
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "EventPulse AI API", "version": settings.VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/deep")
async def health_deep():
    """Deep health check — verifies database connectivity and model availability."""
    import os
    from app.core.config import settings as cfg

    # Check model files
    duration_model_ok = os.path.exists(os.path.join(cfg.MODEL_PATH, "duration_model.pkl"))
    impact_model_ok = os.path.exists(os.path.join(cfg.MODEL_PATH, "impact_model.pkl"))

    # Check DB connectivity
    db_ok = False
    db_error = ""
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_error = str(e)

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else f"error: {db_error}",
        "duration_model": "loaded" if duration_model_ok else "missing",
        "impact_model": "loaded" if impact_model_ok else "missing",
        "model_path": cfg.MODEL_PATH,
        "version": settings.VERSION,
    }
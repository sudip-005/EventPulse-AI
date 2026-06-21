import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1 import analytics, events, forecast, hotspots, learning, recommendations, routes, simulation
from app.core.config import settings
from app.core.database import Base, engine
from app.services.model_service import model_registry

# Importing models registers every table with SQLAlchemy metadata.
import app.models  # noqa: F401,E402

logging.basicConfig(
    level=logging.INFO if settings.ENV == "production" else logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
schema_ready = False


@asynccontextmanager
async def lifespan(_: FastAPI):
    global schema_ready
    model_registry.load()
    try:
        Base.metadata.create_all(bind=engine)
        schema_ready = True
        logger.info("Database schema verified")
    except Exception:
        logger.exception("Database schema verification failed")
        raise
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


ROUTERS = (
    (events.router, "/events", "events"),
    (forecast.router, "/forecast", "forecast"),
    (hotspots.router, "/hotspots", "hotspots"),
    (routes.router, "/routes", "routes"),
    (simulation.router, "/simulations", "simulations"),
    (recommendations.router, "/recommendations", "recommendations"),
    (learning.router, "/learning", "learning"),
    (analytics.router, "/analytics", "analytics"),
)

for router, path, tag in ROUTERS:
    app.include_router(router, prefix=f"{settings.API_V1_STR}{path}", tags=[tag])
    app.include_router(router, prefix=path, tags=[tag], include_in_schema=False)

# Preserve the frontend's original singular API path.
app.include_router(simulation.router, prefix=f"{settings.API_V1_STR}/simulation", include_in_schema=False)


@app.get("/")
async def root():
    return {"message": "EventPulse AI API", "version": settings.VERSION, "docs": "/docs"}


@app.get("/health")
async def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    if not schema_ready or not model_registry.loaded:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    return {"status": "healthy"}


@app.get("/health/deep")
async def health_deep():
    database_ok = False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        database_ok = True
    except Exception:
        logger.exception("Deep health database check failed")

    model_status = model_registry.status()
    return {
        "status": "healthy" if database_ok and schema_ready and model_status["loaded"] else "degraded",
        "database": "connected" if database_ok else "unavailable",
        "schema": "ready" if schema_ready else "unavailable",
        "models": model_status,
        "version": settings.VERSION,
    }

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "EventPulse AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "eventpulse"
    DATABASE_URL: Optional[str] = None
    
    # Model path: can be overridden via MODEL_PATH env var; default resolves relative to this file
    MODEL_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "models")
    XGBOOST_PARAMS: dict = {
        "n_estimators": 500,
        "learning_rate": 0.3,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42
    }
    
    DEFAULT_CITY: str = "mumbai"
    DEFAULT_RADIUS_KM: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()
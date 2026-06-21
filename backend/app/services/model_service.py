import logging
from pathlib import Path
from typing import Any

import joblib

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Load ML artifacts once per process and share them across requests."""

    def __init__(self) -> None:
        self.duration_model: Any = None
        self.impact_model: Any = None
        self.encoders: Any = None
        self.scaler: Any = None
        self.loaded = False

    def load(self) -> None:
        model_dir = Path(settings.MODEL_PATH)
        duration_path = model_dir / "duration_model.pkl"
        impact_path = model_dir / "impact_model.pkl"
        congestion_path = model_dir / "congestion_xgb.pkl"

        self.duration_model = joblib.load(duration_path) if duration_path.exists() else None
        # congestion_xgb.pkl is supported as a deployment-compatible alias.
        selected_impact_path = congestion_path if congestion_path.exists() else impact_path
        self.impact_model = joblib.load(selected_impact_path) if selected_impact_path.exists() else None

        encoders_path = model_dir / "encoders.pkl"
        scaler_path = model_dir / "scaler.pkl"
        self.encoders = joblib.load(encoders_path) if encoders_path.exists() else None
        self.scaler = joblib.load(scaler_path) if scaler_path.exists() else None
        self.loaded = self.duration_model is not None and self.impact_model is not None

        if self.loaded:
            logger.info("ML artifacts loaded from %s", model_dir)
        else:
            logger.warning("ML artifacts incomplete in %s; deterministic fallbacks are enabled", model_dir)

    def status(self) -> dict[str, Any]:
        return {
            "loaded": self.loaded,
            "duration_model": self.duration_model is not None,
            "impact_model": self.impact_model is not None,
            "encoders": self.encoders is not None,
            "scaler": self.scaler is not None,
            "model_path": settings.MODEL_PATH,
        }


model_registry = ModelRegistry()

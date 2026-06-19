import xgboost as xgb
import numpy as np
import joblib
from app.core.config import settings

class XGBoostInference:
    def __init__(self):
        try:
            self.model = joblib.load(f"{settings.MODEL_PATH}/xgboost_model.pkl")
        except FileNotFoundError:
            # Fallback: create a dummy model for demo
            self.model = None

    def predict(self, feature_vector: np.ndarray) -> dict:
        if self.model is None:
            # Dummy prediction based on features
            score = np.clip(50 + feature_vector[0] * 0.5, 0, 100)
            return {"congestion_score": float(score), "confidence": 0.5}
        dmatrix = xgb.DMatrix(feature_vector.reshape(1, -1))
        score = float(self.model.predict(dmatrix)[0])
        return {
            "congestion_score": min(max(score, 0), 100),
            "confidence": self._calculate_confidence(score)
        }

    def predict_batch(self, feature_vectors: np.ndarray) -> list:
        if self.model is None:
            return [50.0] * len(feature_vectors)
        dmatrix = xgb.DMatrix(feature_vectors)
        preds = self.model.predict(dmatrix)
        return [min(max(p, 0), 100) for p in preds]

    def _calculate_confidence(self, score: float) -> float:
        if score < 10 or score > 90:
            return 0.9
        elif score < 30 or score > 70:
            return 0.7
        return 0.5
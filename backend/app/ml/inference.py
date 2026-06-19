from __future__ import annotations

import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List

from app.core.config import settings
from app.ml.features import FeatureEngineer
from app.services.risk_service import RiskService

class XGBoostInference:
    def __init__(self):
        try:
            self.duration_model = joblib.load(os.path.join(settings.MODEL_PATH, "duration_model.pkl"))
            self.impact_model = joblib.load(os.path.join(settings.MODEL_PATH, "impact_model.pkl"))
        except FileNotFoundError:
            self.duration_model = None
            self.impact_model = None

    def predict_impact(self, feature_vector: np.ndarray) -> Tuple[float, str]:
        if self.impact_model is None:
            # Fallback expected score and level
            return 45.0, "MEDIUM"
        
        # Reshape for single prediction
        X = feature_vector.reshape(1, -1)
        proba = self.impact_model.predict_proba(X)[0]
        
        # Calculate expected score: E[score]
        expected_score = proba[0]*12.5 + proba[1]*37.5 + proba[2]*62.5 + proba[3]*87.5
        predicted_class_idx = int(np.argmax(proba))
        levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        
        return expected_score, levels[predicted_class_idx]

    def predict_duration(self, feature_vector: np.ndarray) -> float:
        if self.duration_model is None:
            # Fallback 2 hours
            return 120.0
        
        X = feature_vector.reshape(1, -1)
        duration = float(self.duration_model.predict(X)[0])
        return max(duration, 0.0)

    def predict_event_risk(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        impact_score, impact_level = self.predict_impact(feature_vector)
        duration_minutes = self.predict_duration(feature_vector)
        
        # Estimate closure probability: 
        # requires_road_closure is at index 3 in FeatureEngineer.FEATURE_COLUMNS
        requires_closure = bool(feature_vector[3] > 0.5)
        if requires_closure:
            closure_prob = 1.0
        else:
            closure_prob = min(impact_score / 150.0 + duration_minutes / 1800.0, 0.95)

            
        # Build assessment using RiskService
        assessment = RiskService.build_assessment(impact_score, duration_minutes, closure_prob)
        assessment["impact_level"] = impact_level
        
        # Compute explainability factors
        top_factors = self._explain(feature_vector)
        assessment["top_factors"] = top_factors
        
        return assessment

    def _explain(self, feature_vector: np.ndarray) -> List[str]:
        if self.impact_model is None:
            return ["estimated_attendance", "priority_encoded", "requires_road_closure"]
        
        try:
            from app.ml.explainability import ExplainabilityService
            explainer = ExplainabilityService(self.impact_model)
            df_feat = pd.DataFrame([feature_vector], columns=FeatureEngineer.FEATURE_COLUMNS)
            explanation = explainer.explain_prediction(df_feat, top_n=3)
            return [factor["feature"] for factor in explanation["top_factors"]]
        except Exception:
            return ["estimated_attendance", "priority_encoded", "requires_road_closure"]
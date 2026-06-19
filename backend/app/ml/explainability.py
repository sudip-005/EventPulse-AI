import shap
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class ExplainabilityService:
    def __init__(self, model):
        self.model = model
        self.explainer: Optional[shap.TreeExplainer] = None
        try:
            self.explainer = shap.TreeExplainer(model)
        except Exception:
            self.explainer = None


    def explain_prediction(self, df_features: pd.DataFrame, top_n: int = 3) -> Dict[str, Any]:
        """
        Explain a single prediction. Returns a list of dicts with 'feature' and 'contribution' keys.
        """
        if self.explainer is None:
            return self._fallback_explain(df_features, top_n)
        
        try:
            shap_values = self.explainer.shap_values(df_features)
            # shap_values could be a list (for multi-class Classifier) or a single array (for Regressor)
            if isinstance(shap_values, list):
                # For classification, take class contributions (summing over classes for feature importance)
                mean_shap = np.abs(np.array(shap_values)).sum(axis=0)[0]
            elif len(shap_values.shape) > 1 and shap_values.shape[0] == 1:
                mean_shap = shap_values[0]
            else:
                mean_shap = shap_values
                if len(mean_shap.shape) > 1:
                    mean_shap = mean_shap[0]
            
            # Match with feature names
            feature_names = df_features.columns.tolist()
            contributions = []
            for i, feat in enumerate(feature_names):
                contributions.append({
                    "feature": feat,
                    "contribution": float(mean_shap[i])
                })
            
            # Sort by absolute contribution
            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            return {
                "top_factors": contributions[:top_n],
                "all_contributions": contributions
            }
        except Exception:
            return self._fallback_explain(df_features, top_n)

    def _fallback_explain(self, df_features: pd.DataFrame, top_n: int = 3) -> Dict[str, Any]:
        feature_names = df_features.columns.tolist()
        try:
            importances = self.model.feature_importances_
            contributions = [{"feature": feat, "contribution": float(importances[i])} for i, feat in enumerate(feature_names)]
        except Exception:
            # Static fallback ranking based on default weights
            heuristic_ranks = {
                "estimated_attendance": 0.4,
                "requires_road_closure": 0.3,
                "priority_encoded": 0.2,
                "is_rush_hour": 0.1
            }
            contributions = [{"feature": feat, "contribution": heuristic_ranks.get(feat, 0.05)} for feat in feature_names]
        
        contributions.sort(key=lambda x: x["contribution"], reverse=True)
        return {
            "top_factors": contributions[:top_n],
            "all_contributions": contributions
        }

    def feature_importance(self) -> Dict[str, float]:
        """
        Returns global feature importances of the model.
        """
        try:
            importances = self.model.feature_importances_
            feature_names = self.model.get_booster().feature_names or [f"f{i}" for i in range(len(importances))]
            return dict(zip(feature_names, [float(v) for v in importances]))
        except Exception:
            return {}

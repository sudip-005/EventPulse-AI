from __future__ import annotations

import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, r2_score

from app.core.config import settings
from app.ml.features import FeatureEngineer
from app.ml.label_generator import LabelGenerator

class XGBoostTrainer:
    def __init__(self):
        self.impact_model = None
        self.duration_model = None
        # Ensure model directory exists
        os.makedirs(settings.MODEL_PATH, exist_ok=True)

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        # Generate features
        X = FeatureEngineer.build_feature_df(df)
        
        # Generate labels
        duration_minutes = LabelGenerator.generate_duration_minutes(df)
        impact_scores = LabelGenerator.generate_impact_score(df)
        impact_levels = LabelGenerator.generate_impact_level(impact_scores)
        
        # Map impact level to integers for XGBClassifier
        mapping = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        impact_levels_encoded = impact_levels.map(mapping).astype(int)
        
        return X, duration_minutes, impact_levels_encoded

    def train(self, df: pd.DataFrame) -> Dict[str, Any]:

        X, y_duration, y_impact = self.prepare_data(df)
        
        # Split data
        X_train_dur, X_test_dur, y_train_dur, y_test_dur = train_test_split(X, y_duration, test_size=0.2, random_state=42)
        X_train_imp, X_test_imp, y_train_imp, y_test_imp = train_test_split(X, y_impact, test_size=0.2, random_state=42)
        
        # Train Duration model (XGBRegressor)
        self.duration_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.duration_model.fit(X_train_dur, y_train_dur)
        
        # Train Impact model (XGBClassifier)
        self.impact_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            num_class=4,
            random_state=42
        )
        self.impact_model.fit(X_train_imp, y_train_imp)
        
        # Evaluate Duration model
        dur_preds = self.duration_model.predict(X_test_dur)
        dur_mae = mean_absolute_error(y_test_dur, dur_preds)
        dur_rmse = np.sqrt(mean_squared_error(y_test_dur, dur_preds))
        
        # Evaluate Impact model
        imp_preds = self.impact_model.predict(X_test_imp)
        imp_acc = accuracy_score(y_test_imp, imp_preds)
        
        # Save models
        joblib.dump(self.duration_model, os.path.join(settings.MODEL_PATH, "duration_model.pkl"))
        joblib.dump(self.impact_model, os.path.join(settings.MODEL_PATH, "impact_model.pkl"))
        
        return {
            "duration_mae": dur_mae,
            "duration_rmse": dur_rmse,
            "impact_accuracy": imp_acc
        }


    def load_models(self):
        self.duration_model = joblib.load(os.path.join(settings.MODEL_PATH, "duration_model.pkl"))
        self.impact_model = joblib.load(os.path.join(settings.MODEL_PATH, "impact_model.pkl"))
        return self.duration_model, self.impact_model
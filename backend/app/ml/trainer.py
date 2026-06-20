from __future__ import annotations

import os
import joblib
import json
import datetime
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, Tuple, Any
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score, 
    mean_absolute_error, 
    mean_squared_error, 
    r2_score,
    mean_absolute_percentage_error
)

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
        
        # Run 5-Fold cross-validation
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        
        cv_dur_scores = cross_val_score(
            xgb.XGBRegressor(
                n_estimators=300,
                max_depth=5,
                learning_rate=0.01,
                subsample=0.75,
                colsample_bytree=0.8,
                reg_alpha=1.0,
                reg_lambda=1.0,
                min_child_weight=4,
                random_state=42
            ),
            X, y_duration, cv=kf, scoring="neg_mean_absolute_error"
        )
        cv_duration_mae_mean = float(-cv_dur_scores.mean())
        cv_duration_mae_std = float(cv_dur_scores.std())
        
        cv_imp_scores = cross_val_score(
            xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, num_class=4, random_state=42),
            X, y_impact, cv=kf, scoring="accuracy"
        )
        cv_impact_acc_mean = float(cv_imp_scores.mean())
        cv_impact_acc_std = float(cv_imp_scores.std())
        
        # Train Duration model (XGBRegressor)
        self.duration_model = xgb.XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.01,
            subsample=0.75,
            colsample_bytree=0.8,
            reg_alpha=1.0,
            reg_lambda=1.0,
            min_child_weight=4,
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
        dur_mape = mean_absolute_percentage_error(y_test_dur, dur_preds)
        dur_r2 = r2_score(y_test_dur, dur_preds)
        
        # Evaluate Impact model
        imp_preds = self.impact_model.predict(X_test_imp)
        imp_acc = accuracy_score(y_test_imp, imp_preds)
        imp_prec = precision_score(y_test_imp, imp_preds, average="weighted")
        imp_rec = recall_score(y_test_imp, imp_preds, average="weighted")
        imp_f1 = f1_score(y_test_imp, imp_preds, average="weighted")
        
        # Save models
        joblib.dump(self.duration_model, os.path.join(settings.MODEL_PATH, "duration_model.pkl"))
        joblib.dump(self.impact_model, os.path.join(settings.MODEL_PATH, "impact_model.pkl"))
        
        # Generate feature importances
        features = FeatureEngineer.FEATURE_COLUMNS
        dur_importances = dict(zip(features, [float(x) for x in self.duration_model.feature_importances_]))
        imp_importances = dict(zip(features, [float(x) for x in self.impact_model.feature_importances_]))
        dur_importances_sorted = dict(sorted(dur_importances.items(), key=lambda x: x[1], reverse=True))
        imp_importances_sorted = dict(sorted(imp_importances.items(), key=lambda x: x[1], reverse=True))
        
        # Determine the results directory robustly based on trainer.py path
        current_file_path = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        results_dir = os.path.join(backend_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save JSON results
        results_dict = {
            "duration_model_metrics": {
                "mean_absolute_error_minutes": dur_mae,
                "root_mean_squared_error_minutes": float(dur_rmse),
                "r2_score": dur_r2,
                "mean_absolute_percentage_error": dur_mape,
                "cv_mae_mean": cv_duration_mae_mean,
                "cv_mae_std": cv_duration_mae_std
            },
            "impact_model_metrics": {
                "accuracy": float(imp_acc),
                "precision_weighted": float(imp_prec),
                "recall_weighted": float(imp_rec),
                "f1_score_weighted": float(imp_f1),
                "cv_accuracy_mean": cv_impact_acc_mean,
                "cv_accuracy_std": cv_impact_acc_std
            },
            "feature_importances": {
                "duration_model": dur_importances_sorted,
                "impact_model": imp_importances_sorted
            }
        }
        
        json_path = os.path.join(results_dir, "ml_results.json")
        with open(json_path, "w") as f:
            json.dump(results_dict, f, indent=4)
            
        # Save Markdown report
        md_path = os.path.join(results_dir, "ml_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# EventPulse AI - Machine Learning Model Results\n\n")
            f.write(f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 1. Event Duration Regressor (XGBRegressor)\n")
            f.write("Predicts the expected resolution time of the incident in minutes.\n\n")
            f.write(f"- **Mean Absolute Error (MAE)**: {dur_mae:.2f} minutes (CV: {cv_duration_mae_mean:.2f} +/- {cv_duration_mae_std:.2f})\n")
            f.write(f"- **Root Mean Squared Error (RMSE)**: {dur_rmse:.2f} minutes\n")
            f.write(f"- **Mean Absolute Percentage Error (MAPE)**: {dur_mape * 100:.2f}%\n")
            f.write(f"- **R^2 Score**: {dur_r2:.4f}\n\n")
            
            f.write("### Duration Feature Importances\n")
            f.write("| Feature | Importance |\n| :--- | :--- |\n")
            for feat, val in dur_importances_sorted.items():
                f.write(f"| `{feat}` | {val:.4f} |\n")
            f.write("\n")
            
            f.write("## 2. Congestion Impact Level Classifier (XGBClassifier)\n")
            f.write("Predicts the categorical severity rating (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).\n\n")
            f.write(f"- **Overall Accuracy**: {imp_acc * 100:.2f}% (CV: {cv_impact_acc_mean * 100:.2f}% +/- {cv_impact_acc_std * 100:.2f}%)\n")
            f.write(f"- **Weighted Precision**: {imp_prec:.4f}\n")
            f.write(f"- **Weighted Recall**: {imp_rec:.4f}\n")
            f.write(f"- **Weighted F1 Score**: {imp_f1:.4f}\n\n")
            
            f.write("### Impact Feature Importances\n")
            f.write("| Feature | Importance |\n| :--- | :--- |\n")
            for feat, val in imp_importances_sorted.items():
                f.write(f"| `{feat}` | {val:.4f} |\n")
            f.write("\n")
        
        return {
            "duration_mae": dur_mae,
            "duration_rmse": float(dur_rmse),
            "duration_mape": dur_mape,
            "duration_r2": dur_r2,
            "cv_duration_mae_mean": cv_duration_mae_mean,
            "cv_duration_mae_std": cv_duration_mae_std,
            "impact_accuracy": float(imp_acc),
            "impact_precision": float(imp_prec),
            "impact_recall": float(imp_rec),
            "impact_f1": float(imp_f1),
            "cv_impact_acc_mean": cv_impact_acc_mean,
            "cv_impact_acc_std": cv_impact_acc_std
        }

    def load_models(self):
        self.duration_model = joblib.load(os.path.join(settings.MODEL_PATH, "duration_model.pkl"))
        self.impact_model = joblib.load(os.path.join(settings.MODEL_PATH, "impact_model.pkl"))
        return self.duration_model, self.impact_model
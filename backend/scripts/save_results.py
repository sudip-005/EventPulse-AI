import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
import joblib

# Load paths
from app.core.config import settings
from app.ml.features import FeatureEngineer
from app.ml.trainer import XGBoostTrainer
from app.ml.data_loader import load_training_data
from app.core.database import SessionLocal

def main():
    # 1. Create results directory
    results_dir = r"c:\Users\SUDIP MANNA\OneDrive\Desktop\EventPulseAI\backend\results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 2. Connect DB and load data
    db = SessionLocal()
    try:
        df = load_training_data(db)
    finally:
        db.close()
        
    trainer = XGBoostTrainer()
    X, y_duration, y_impact = trainer.prepare_data(df)
    
    # Split
    X_train_dur, X_test_dur, y_train_dur, y_test_dur = train_test_split(X, y_duration, test_size=0.2, random_state=42)
    X_train_imp, X_test_imp, y_train_imp, y_test_imp = train_test_split(X, y_impact, test_size=0.2, random_state=42)
    
    # Load model files
    duration_model = joblib.load(os.path.join(settings.MODEL_PATH, "duration_model.pkl"))
    impact_model = joblib.load(os.path.join(settings.MODEL_PATH, "impact_model.pkl"))
    
    # Evaluate Duration Model
    dur_preds = duration_model.predict(X_test_dur)
    dur_mae = mean_absolute_error(y_test_dur, dur_preds)
    dur_rmse = np.sqrt(mean_squared_error(y_test_dur, dur_preds))
    dur_r2 = r2_score(y_test_dur, dur_preds)
    
    # Evaluate Impact Model
    imp_preds = impact_model.predict(X_test_imp)
    imp_acc = accuracy_score(y_test_imp, imp_preds)
    imp_prec = precision_score(y_test_imp, imp_preds, average="weighted")
    imp_rec = recall_score(y_test_imp, imp_preds, average="weighted")
    imp_f1 = f1_score(y_test_imp, imp_preds, average="weighted")
    
    # Get Feature Importances
    features = FeatureEngineer.FEATURE_COLUMNS
    dur_importances = dict(zip(features, [float(x) for x in duration_model.feature_importances_]))
    imp_importances = dict(zip(features, [float(x) for x in impact_model.feature_importances_]))
    
    # Sort importances
    dur_importances_sorted = dict(sorted(dur_importances.items(), key=lambda x: x[1], reverse=True))
    imp_importances_sorted = dict(sorted(imp_importances.items(), key=lambda x: x[1], reverse=True))
    
    # Results dictionary
    results = {
        "duration_model_metrics": {
            "mean_absolute_error_minutes": float(dur_mae),
            "root_mean_squared_error_minutes": float(dur_rmse),
            "r2_score": float(dur_r2)
        },
        "impact_model_metrics": {
            "accuracy": float(imp_acc),
            "precision_weighted": float(imp_prec),
            "recall_weighted": float(imp_rec),
            "f1_score_weighted": float(imp_f1)
        },
        "feature_importances": {
            "duration_model": dur_importances_sorted,
            "impact_model": imp_importances_sorted
        }
    }
    
    # Write json
    json_path = os.path.join(results_dir, "ml_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results JSON saved to {json_path}")
    
    # Write md report
    md_path = os.path.join(results_dir, "ml_report.md")
    with open(md_path, "w") as f:
        f.write("# EventPulse AI — Machine Learning Model Results\n\n")
        f.write(f"Generated at: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. Event Duration Regressor (XGBRegressor)\n")
        f.write("Predicts the expected resolution time of the incident in minutes.\n\n")
        f.write(f"- **Mean Absolute Error (MAE)**: {dur_mae:.2f} minutes\n")
        f.write(f"- **Root Mean Squared Error (RMSE)**: {dur_rmse:.2f} minutes\n")
        f.write(f"- **R² Score**: {dur_r2:.4f}\n\n")
        
        f.write("### Duration Feature Importances\n")
        f.write("| Feature | Importance |\n| :--- | :--- |\n")
        for feat, val in dur_importances_sorted.items():
            f.write(f"| `{feat}` | {val:.4f} |\n")
        f.write("\n")
        
        f.write("## 2. Congestion Impact Level Classifier (XGBClassifier)\n")
        f.write("Predicts the categorical severity rating (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).\n\n")
        f.write(f"- **Overall Accuracy**: {imp_acc * 100:.2f}%\n")
        f.write(f"- **Weighted Precision**: {imp_prec:.4f}\n")
        f.write(f"- **Weighted Recall**: {imp_rec:.4f}\n")
        f.write(f"- **Weighted F1 Score**: {imp_f1:.4f}\n\n")
        
        f.write("### Impact Feature Importances\n")
        f.write("| Feature | Importance |\n| :--- | :--- |\n")
        for feat, val in imp_importances_sorted.items():
            f.write(f"| `{feat}` | {val:.4f} |\n")
        f.write("\n")
        
    print(f"Markdown Report saved to {md_path}")

if __name__ == "__main__":
    main()

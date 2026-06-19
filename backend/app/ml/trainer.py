import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from typing import Tuple, Dict
from app.core.config import settings

class XGBoostTrainer:
    def __init__(self):
        self.model = None
        self.params = settings.XGBOOST_PARAMS

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        target_col = "congestion_score"
        feature_cols = [col for col in df.columns if col != target_col]
        X = df[feature_cols].values
        y = df[target_col].values
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        X_train, X_test, y_train, y_test = self.prepare_data(df)
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        self.model = xgb.train(
            self.params,
            dtrain,
            num_boost_round=500,
            evals=[(dtrain, "train"), (dtest, "test")],
            early_stopping_rounds=50,
            verbose_eval=False
        )
        y_pred = self.model.predict(dtest)
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }
        joblib.dump(self.model, f"{settings.MODEL_PATH}/xgboost_model.pkl")
        return metrics

    def load_model(self):
        self.model = joblib.load(f"{settings.MODEL_PATH}/xgboost_model.pkl")
        return self.model
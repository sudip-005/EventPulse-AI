from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.learning_record import LearningRecord
from app.models.prediction import Prediction
from app.models.event import Event
from app.schemas.learning import LearningRecordResponse
import random

class LearningService:
    def __init__(self, db: Session):
        self.db = db

    async def record_actual_outcome(self, event_id: str) -> dict:
        # In real life, would fetch actual data after event
        # For demo, simulate random actual impact (within +/-20%)
        predictions = self.db.query(Prediction).filter(Prediction.event_id == event_id).all()
        for pred in predictions:
            pred_impact = pred.impact_score if pred.impact_score is not None else 45.0
            actual = pred_impact * (0.8 + 0.4 * random.random())
            error = abs(pred_impact - actual)
            record = LearningRecord(
                event_id=event_id,
                prediction_id=pred.id,
                predicted_impact=pred_impact,
                actual_impact=actual,
                error=error,
                mae=error,
                rmse=error * 1.2,
                resource_effectiveness=0.7 + 0.3 * random.random(),
                model_version=pred.model_version or "v1.0"
            )
            self.db.add(record)
        self.db.commit()
        return {"message": "Recorded actual outcomes"}

    async def get_records_for_event(self, event_id: str) -> List[LearningRecordResponse]:
        records = self.db.query(LearningRecord).filter(LearningRecord.event_id == event_id).all()
        return [LearningRecordResponse(
            id=str(r.id),
            event_id=str(r.event_id),
            prediction_id=str(r.prediction_id),
            predicted_impact=r.predicted_impact,
            actual_impact=r.actual_impact,
            error=r.error,
            mae=r.mae,
            rmse=r.rmse,
            resource_effectiveness=r.resource_effectiveness,
            created_at=r.created_at
        ) for r in records]

    async def retrain_model(self, model_version: Optional[str] = None) -> dict:
        """Trigger retraining pipeline on all available training data."""
        from app.ml.trainer import XGBoostTrainer
        from app.ml.data_loader import load_training_data
        try:
            df = load_training_data(self.db)
            if df.empty:
                return {"error": "No training data available", "model_version": model_version or "v1.0"}
            trainer = XGBoostTrainer()
            metrics = trainer.train(df)
            new_version = model_version or "v1.1"
            return {
                "message": "Retraining completed successfully",
                "model_version": new_version,
                "metrics": metrics
            }
        except Exception as e:
            return {"error": str(e), "model_version": model_version or "v1.0"}

def load_synthetic_and_train(db: Session) -> dict:
    from app.ml.data_loader import load_training_data
    from app.ml.trainer import XGBoostTrainer
    df = load_training_data(db)
    trainer = XGBoostTrainer()
    return trainer.train(df)
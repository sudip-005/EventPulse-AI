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
        # In real life, would fetch actual traffic data after event
        # For demo, simulate random actual congestion
        predictions = self.db.query(Prediction).filter(Prediction.event_id == event_id).all()
        for pred in predictions:
            # Simulate actual congestion (within +/-20%)
            actual = pred.congestion_score * (0.8 + 0.4 * random.random())
            error = abs(pred.congestion_score - actual)
            record = LearningRecord(
                event_id=event_id,
                prediction_id=pred.id,
                predicted_congestion=pred.congestion_score,
                actual_congestion=actual,
                error=error,
                mae=error,
                rmse=error*1.2,
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
            predicted_congestion=r.predicted_congestion,
            actual_congestion=r.actual_congestion,
            error=r.error,
            mae=r.mae,
            rmse=r.rmse,
            resource_effectiveness=r.resource_effectiveness,
            created_at=r.created_at
        ) for r in records]

    async def retrain_model(self, model_version: Optional[str] = None) -> dict:
        # Trigger retraining pipeline
        from app.ml.trainer import XGBoostTrainer
        trainer = XGBoostTrainer()
        # Would need to load historical data
        # For demo, return
        return {"message": "Retraining triggered", "model_version": model_version or "v1.1"}
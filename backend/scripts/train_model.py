#!/usr/bin/env python3
import asyncio
from app.ml.trainer import XGBoostTrainer
from app.ml.data_loader import load_training_data
from app.core.database import SessionLocal

async def train():
    db = SessionLocal()
    try:
        df = load_training_data(db)
        trainer = XGBoostTrainer()
        metrics = trainer.train(df)
        print("Training completed. Metrics:", metrics)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(train())
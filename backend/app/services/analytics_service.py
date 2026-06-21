from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

from app.models.event import Event
from app.models.prediction import Prediction
from app.models.hotspot import Hotspot
from app.models.simulation import Simulation
from app.models.learning_record import LearningRecord
from app.models.recommendation import Recommendation


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> Dict[str, Any]:
        """High-level system KPIs."""
        total_events = self.db.query(Event).count()
        active_events = self.db.query(Event).filter(Event.status.in_(["scheduled", "active"])).count()
        total_predictions = self.db.query(Prediction).count()
        total_hotspots = self.db.query(Hotspot).count()
        total_simulations = self.db.query(Simulation).count()

        # Average scores
        avg_impact = self.db.query(func.avg(Event.impact_score)).scalar() or 0.0
        avg_risk = self.db.query(func.avg(Event.risk_score)).scalar() or 0.0
        high_risk_events = self.db.query(Event).filter(Event.risk_score >= 60).count()

        return {
            "total_events": total_events,
            "active_events": active_events,
            "total_predictions": total_predictions,
            "total_hotspots": total_hotspots,
            "total_simulations": total_simulations,
            "avg_impact_score": round(float(avg_impact), 2),
            "avg_risk_score": round(float(avg_risk), 2),
            "high_risk_events": high_risk_events,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_event_type_breakdown(self) -> List[Dict[str, Any]]:
        """Count events by type with average risk/impact scores."""
        rows = (
            self.db.query(
                Event.event_type,
                func.count(Event.id).label("count"),
                func.avg(Event.risk_score).label("avg_risk"),
                func.avg(Event.impact_score).label("avg_impact"),
            )
            .group_by(Event.event_type)
            .all()
        )
        return [
            {
                "event_type": r.event_type,
                "count": r.count,
                "avg_risk_score": round(float(r.avg_risk or 0), 2),
                "avg_impact_score": round(float(r.avg_impact or 0), 2),
            }
            for r in rows
        ]

    def get_ml_performance(self) -> Dict[str, Any]:
        """ML model accuracy metrics from learning records."""
        records = self.db.query(LearningRecord).all()
        if not records:
            return {
                "total_learning_records": 0,
                "avg_mae": None,
                "avg_rmse": None,
                "avg_resource_effectiveness": None,
                "message": "No learning records yet — run post-event learning to populate."
            }

        avg_mae = sum(r.mae for r in records if r.mae) / len(records)
        avg_rmse = sum(r.rmse for r in records if r.rmse) / len(records)
        avg_eff = sum(r.resource_effectiveness for r in records if r.resource_effectiveness) / len(records)

        return {
            "total_learning_records": len(records),
            "avg_mae": round(avg_mae, 4),
            "avg_rmse": round(avg_rmse, 4),
            "avg_resource_effectiveness": round(avg_eff, 4),
            "impact_model_accuracy": 0.94,    # From ml_results.json training run
            "impact_model_f1": 0.9401,
            "duration_model_r2": 0.6903,
            "duration_model_mae_minutes": 71.55,
        }

    def get_hotspot_severity_distribution(self) -> List[Dict[str, Any]]:
        """Distribution of hotspot severities."""
        rows = (
            self.db.query(
                Hotspot.severity,
                func.count(Hotspot.id).label("count"),
                func.avg(Hotspot.impact_score).label("avg_congestion"),
            )
            .group_by(Hotspot.severity)
            .order_by(Hotspot.severity)
            .all()
        )
        return [
            {
                "severity": r.severity,
                "count": r.count,
                "avg_congestion": round(float(r.avg_congestion or 0), 2),
            }
            for r in rows
        ]

    def get_timeline(self, days: int = 7) -> List[Dict[str, Any]]:
        """Events created per day over the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        events = self.db.query(Event).filter(Event.created_at >= cutoff).all()
        by_day: Dict[str, Dict] = {}
        for e in events:
            day = e.created_at.strftime("%Y-%m-%d") if e.created_at else "Unknown"
            if day not in by_day:
                by_day[day] = {"date": day, "event_count": 0, "avg_risk": [], "avg_impact": []}
            by_day[day]["event_count"] += 1
            if e.risk_score:
                by_day[day]["avg_risk"].append(e.risk_score)
            if e.impact_score:
                by_day[day]["avg_impact"].append(e.impact_score)

        result = []
        for day_data in sorted(by_day.values(), key=lambda x: x["date"]):
            result.append({
                "date": day_data["date"],
                "event_count": day_data["event_count"],
                "avg_risk_score": round(sum(day_data["avg_risk"]) / len(day_data["avg_risk"]), 2) if day_data["avg_risk"] else 0.0,
                "avg_impact_score": round(sum(day_data["avg_impact"]) / len(day_data["avg_impact"]), 2) if day_data["avg_impact"] else 0.0,
            })
        return result

    def get_resource_summary(self) -> Dict[str, Any]:
        """Summary of all recommended resources."""
        recs = self.db.query(Recommendation).all()
        by_type: Dict[str, int] = {}
        for r in recs:
            by_type[r.resource_type] = by_type.get(r.resource_type, 0) + (r.resource_count or 1)
        return {
            "total_recommendations": len(recs),
            "by_resource_type": [{"resource_type": k, "total_count": v} for k, v in sorted(by_type.items())],
        }

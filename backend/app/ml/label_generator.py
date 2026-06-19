from __future__ import annotations
import pandas as pd
import numpy as np

class LabelGenerator:
    @staticmethod
    def generate_duration_minutes(df: pd.DataFrame) -> pd.Series:
        """
        Calculates duration in minutes: resolved_datetime - start_datetime.
        """
        start = pd.to_datetime(df["start_datetime"])
        resolved = pd.to_datetime(df["resolved_datetime"])
        duration = (resolved - start).dt.total_seconds() / 60.0
        # Ensure duration is non-negative
        return duration.clip(lower=0.0)

    @staticmethod
    def generate_impact_score(df: pd.DataFrame) -> pd.Series:
        """
        Generates impact score derived from:
        - duration (longer events have higher impact)
        - priority (critical events have higher impact)
        - requires_road_closure (road closure adds massive impact)
        Returns a value clipped between 0 and 100.
        """
        # Base score from priority
        priority_weights = {"low": 15.0, "medium": 35.0, "high": 60.0, "critical": 80.0}
        base_priority_score = df["priority"].str.lower().map(priority_weights).fillna(35.0)

        # Duration component: up to 20 points
        durations = LabelGenerator.generate_duration_minutes(df)
        duration_score = (durations / 12.0).clip(upper=20.0)  # 4 hours is max duration score (240 mins)

        # Road closure component: 20 points if requires_road_closure is true
        closure_score = df["requires_road_closure"].astype(int) * 20.0

        # Attendance component (if available in df)
        attendance_score = 0.0
        if "estimated_attendance" in df.columns:
            attendance_score = (df["estimated_attendance"] / 1000.0).clip(upper=15.0)

        total_score = base_priority_score + duration_score + closure_score + attendance_score
        return total_score.clip(lower=0.0, upper=100.0)

    @staticmethod
    def generate_impact_level(scores: pd.Series) -> pd.Series:
        """
        Maps impact score to: LOW, MEDIUM, HIGH, CRITICAL.
        """
        bins = [-float('inf'), 30.0, 60.0, 85.0, float('inf')]
        labels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        cut_series = pd.cut(scores, bins=bins, labels=labels, right=False)
        return pd.Series(cut_series.astype(str), index=scores.index)
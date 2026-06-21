from __future__ import annotations

import os
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def load_training_data(db: Session) -> pd.DataFrame:
    """
    Loads and cleans the real Astram event dataset from the downloads directory.
    Implements date fallback logic, cause-to-type category mapping, outlier clipping,
    weather/attendance imputation, and upsampling/downsampling to resolve class imbalance.
    """
    # Use environment variable first; fallback to dataset placed next to data_loader.py
    default_path = os.path.join(os.path.dirname(__file__), "astram_event_data.csv")
    csv_path = os.getenv("TRAINING_DATA_PATH", default_path)
    
    # 1. Load the raw dataset
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        # DB Fallback Query for container safety
        from app.models.event import Event
        events = db.query(Event).all()
        if not events:
            return pd.DataFrame(columns=[
                "start_datetime", "resolved_datetime", "estimated_attendance", 
                "event_type", "priority", "requires_road_closure", 
                "temperature", "precipitation", "is_raining", "latitude", "longitude",
                "zone", "junction", "corridor"
            ])
        data = []
        for e in events:
            coordinates = e.location.get("coordinates", []) if isinstance(e.location, dict) else []
            lon, lat = coordinates if len(coordinates) == 2 else (72.8777, 19.0760)
            # Dynamic priority based on risk_score or event_type
            p_val = "Medium"
            if getattr(e, "risk_score", None) is not None:
                if e.risk_score >= 85:
                    p_val = "Critical"
                elif e.risk_score >= 60:
                    p_val = "High"
                elif e.risk_score >= 30:
                    p_val = "Medium"
                else:
                    p_val = "Low"
            else:
                e_type = str(e.event_type).lower()
                if "political" in e_type or "rally" in e_type or "strike" in e_type:
                    p_val = "High"
                elif "concert" in e_type or "sports" in e_type or "marathon" in e_type:
                    p_val = "Medium"
                else:
                    p_val = "Low"

            # Dynamic road closure requirements
            e_type = str(e.event_type).lower()
            requires_closure = False
            if "marathon" in e_type or "rally" in e_type or "strike" in e_type:
                requires_closure = True
            elif e.estimated_attendance and e.estimated_attendance > 5000:
                requires_closure = True

            data.append({
                "start_datetime": e.start_time,
                "resolved_datetime": e.end_time,
                "estimated_attendance": e.estimated_attendance or 1000,
                "event_type": e.event_type,
                "priority": p_val,
                "requires_road_closure": requires_closure,
                "temperature": 25.0,
                "precipitation": 0.0,
                "is_raining": 0.0,
                "latitude": lat,
                "longitude": lon,
                "event_cause": "others",
                "zone": "Unknown",
                "junction": "Unknown",
                "corridor": "Unknown"
            })
        df = pd.DataFrame(data)

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce").fillna(19.0760)
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce").fillna(72.8777)
    df["zone"] = df["zone"].fillna("Unknown") if "zone" in df.columns else "Unknown"
    df["junction"] = df["junction"].fillna("Unknown") if "junction" in df.columns else "Unknown"
    df["corridor"] = df["corridor"].fillna("Unknown") if "corridor" in df.columns else "Unknown"
    
    # 2. Parse start_datetime (fallback to created_date)
    df["start_datetime"] = pd.to_datetime(df["start_datetime"].fillna(df["created_date"]), errors="coerce")
    df = df.dropna(subset=["start_datetime"])
    
    # 3. Parse resolved_datetime (fallback to closed_datetime)
    df["resolved_datetime"] = pd.to_datetime(df["resolved_datetime"].fillna(df["closed_datetime"]), errors="coerce")
    
    # 4. Compute event duration in minutes and clip outliers (10 mins to 8 hours)
    # pyrefly: ignore [unsupported-operation]
    durations = (df["resolved_datetime"] - df["start_datetime"]) / pd.Timedelta(minutes=1)
    durations_clipped = durations.clip(lower=10.0, upper=480.0)
    df["duration"] = durations_clipped
    
    # Impute missing durations using the median duration of each specific event cause
    median_durations = df.groupby("event_cause")["duration"].median().fillna(60.0)
    df["duration"] = df.apply(
        lambda row: row["duration"] if pd.notnull(row["duration"]) else median_durations.get(row["event_cause"], 60.0),
        axis=1
    )
    
    # Re-calculate resolved_datetime for ALL records to strip outliers completely
    df["resolved_datetime"] = df["start_datetime"] + pd.to_timedelta(df["duration"], unit="m")
    
    # 5. Map event causes to the ML engine event categories
    cause_map = {
        "vehicle_breakdown": "accident",
        "construction": "construction",
        "accident": "accident",
        "public_event": "festival",
        "pot_holes": "construction",
        "water_logging": "other",
        "tree_fall": "other",
        "road_conditions": "construction",
        "congestion": "other",
        "others": "other"
    }
    df["event_type_mapped"] = df["event_cause"].str.lower().map(cause_map).fillna("other")
    
    # 6. Map priority categories
    priority_map = {
        "high": "High",
        "low": "Low",
        "critical": "Critical",
        "medium": "Medium"
    }
    df["priority_mapped"] = df["priority"].str.lower().map(priority_map).fillna("Medium")
    
    # 7. Map requires_road_closure
    df["requires_road_closure_mapped"] = df["requires_road_closure"].fillna(False).astype(bool)
    
    # 8. Impute estimated attendance
    np.random.seed(42)
    def estimate_attendance(row):
        if row["event_type"] == "planned" or row["event_type_mapped"] in ["festival", "concert", "sports"]:
            return float(np.random.randint(5000, 25000))
        return 0.0
    df["estimated_attendance"] = df.apply(estimate_attendance, axis=1)
    
    # 9. Impute weather features
    df["temperature"] = 25.0
    df["precipitation"] = df.apply(lambda r: 8.0 if r["event_cause"] == "water_logging" else 0.0, axis=1)
    df["is_raining"] = df["precipitation"].apply(lambda x: 1.0 if x > 0.0 else 0.0)
    
    # 10. Resample to resolve severe class imbalance (target 500 rows per mapped event category)
    target_size = 500
    balanced_dfs = []
    for name, group in df.groupby("event_type_mapped"):
        if len(group) >= target_size:
            resampled_group = group.sample(n=target_size, random_state=42)
        else:
            resampled_group = group.sample(n=target_size, replace=True, random_state=42)
        balanced_dfs.append(resampled_group)
        
    df_balanced = pd.concat(balanced_dfs, ignore_index=True)
    
    # 11. Format final training DataFrame columns
    df_final = pd.DataFrame({
        "start_datetime": df_balanced["start_datetime"],
        "resolved_datetime": df_balanced["resolved_datetime"],
        "estimated_attendance": df_balanced["estimated_attendance"],
        "event_type": df_balanced["event_type_mapped"],
        "priority": df_balanced["priority_mapped"],
        "requires_road_closure": df_balanced["requires_road_closure_mapped"],
        "temperature": df_balanced["temperature"],
        "precipitation": df_balanced["precipitation"],
        "is_raining": df_balanced["is_raining"],
        "latitude": df_balanced["latitude"],
        "longitude": df_balanced["longitude"],
        "zone": df_balanced.get("zone", "Unknown").fillna("Unknown"),
        "junction": df_balanced.get("junction", "Unknown").fillna("Unknown"),
        "corridor": df_balanced.get("corridor", "Unknown").fillna("Unknown")
    })
    
    return df_final

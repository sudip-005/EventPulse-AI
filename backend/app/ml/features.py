from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

class FeatureEngineer:
    FEATURE_COLUMNS = [
        "estimated_attendance",
        "event_type_encoded",
        "priority_encoded",
        "requires_road_closure",
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "is_rush_hour",
        "temperature",
        "precipitation",
        "is_raining",
        "latitude",
        "longitude",
        "geohash",
        "zone_encoded",
        "junction_encoded",
        "corridor_encoded",
        "historical_event_frequency",
        "average_resolution_time",
        "zone_incident_density",
        "junction_incident_density",
    ]

    @staticmethod
    def get_event_type_map() -> Dict[str, int]:
        return {
            "concert": 1,
            "sports": 2,
            "festival": 3,
            "accident": 4,
            "construction": 5,
            "protest": 6,
            "marathon": 7,
            "other": 8,
        }

    @staticmethod
    def get_priority_map() -> Dict[str, int]:
        return {
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "Critical": 4,
        }

    @staticmethod
    def get_historical_stats() -> Dict[str, Dict[str, float]]:
        return {
            "concert": {"frequency": 0.05, "avg_duration": 240.0},
            "sports": {"frequency": 0.08, "avg_duration": 180.0},
            "festival": {"frequency": 0.12, "avg_duration": 300.0},
            "accident": {"frequency": 0.35, "avg_duration": 90.0},
            "construction": {"frequency": 0.20, "avg_duration": 360.0},
            "protest": {"frequency": 0.05, "avg_duration": 150.0},
            "marathon": {"frequency": 0.03, "avg_duration": 240.0},
            "other": {"frequency": 0.12, "avg_duration": 120.0},
        }

    @staticmethod
    def stable_hash(text: str, buckets: int = 100) -> float:
        if not text:
            return 0.0
        import hashlib
        return float(int(hashlib.md5(text.lower().strip().encode('utf-8')).hexdigest(), 16) % buckets + 1)

    @staticmethod
    def latlon_to_geohash(lat: float, lon: float, precision: int = 5) -> float:
        lat_range = [-90.0, 90.0]
        lon_range = [-180.0, 180.0]
        bits = []
        for i in range(precision * 5):
            if i % 2 == 0:
                mid = (lon_range[0] + lon_range[1]) / 2.0
                if lon > mid:
                    bits.append(1)
                    lon_range[0] = mid
                else:
                    bits.append(0)
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2.0
                if lat > mid:
                    bits.append(1)
                    lat_range[0] = mid
                else:
                    bits.append(0)
                    lat_range[1] = mid
        val = 0
        for b in bits:
            val = (val << 1) | b
        return float(val) / (2**(precision * 5))

    @staticmethod
    def extract_temporal_features(timestamp: datetime) -> Dict[str, Any]:
        return {
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "month": timestamp.month,
            "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
            "is_rush_hour": 1 if (7 <= timestamp.hour <= 10) or (17 <= timestamp.hour <= 20) else 0,
        }

    @staticmethod
    def extract_weather_features(weather: Dict[str, Any]) -> Dict[str, Any]:
        precip = weather.get("precipitation", 0.0)
        return {
            "temperature": weather.get("temperature", 25.0),
            "precipitation": precip,
            "is_raining": 1 if precip > 0.0 else 0,
        }

    @staticmethod
    def build_feature_dict(event: Dict[str, Any], weather: Dict[str, Any], temporal: datetime) -> Dict[str, Any]:
        event_type_str = event.get("event_type", "other").lower()
        event_type_map = FeatureEngineer.get_event_type_map()
        event_type_encoded = event_type_map.get(event_type_str, event_type_map["other"])

        priority_str = event.get("priority", "Medium")
        priority_map = FeatureEngineer.get_priority_map()
        priority_encoded = priority_map.get(priority_str, priority_map["Medium"])

        loc = event.get("location")
        lat = 19.0760
        lon = 72.8777
        if isinstance(loc, dict):
            coords = loc.get("coordinates", [72.8777, 19.0760])
            if len(coords) >= 2:
                lon = coords[0]
                lat = coords[1]
        elif isinstance(loc, (tuple, list)):
            if len(loc) >= 2:
                lat = loc[0]
                lon = loc[1]
        elif loc is not None:
            if hasattr(loc, 'y') and hasattr(loc, 'x'):
                lat = loc.y
                lon = loc.x

        geohash_val = FeatureEngineer.latlon_to_geohash(lat, lon)

        zone_str = event.get("zone", "Unknown") or "Unknown"
        junction_str = event.get("junction", "Unknown") or "Unknown"
        corridor_str = event.get("corridor", "Unknown") or "Unknown"

        zone_encoded = FeatureEngineer.stable_hash(zone_str, buckets=20)
        junction_encoded = FeatureEngineer.stable_hash(junction_str, buckets=200)
        corridor_encoded = FeatureEngineer.stable_hash(corridor_str, buckets=100)

        hist_stats = FeatureEngineer.get_historical_stats()
        stats = hist_stats.get(event_type_str, hist_stats["other"])
        freq = stats["frequency"]
        avg_dur = stats["avg_duration"]

        features = {
            "estimated_attendance": float(event.get("estimated_attendance", 0) or 0),
            "event_type_encoded": float(event_type_encoded),
            "priority_encoded": float(priority_encoded),
            "requires_road_closure": float(1 if event.get("requires_road_closure", False) else 0),
            "latitude": float(lat),
            "longitude": float(lon),
            "geohash": geohash_val,
            "zone_encoded": zone_encoded,
            "junction_encoded": junction_encoded,
            "corridor_encoded": corridor_encoded,
            "historical_event_frequency": freq,
            "average_resolution_time": avg_dur,
            # Incident density: estimated from event frequency in zone/junction
            "zone_incident_density": round(freq * zone_encoded / 10.0, 4),
            "junction_incident_density": round(freq * junction_encoded / 100.0, 4),
        }
        features.update(FeatureEngineer.extract_temporal_features(temporal))
        features.update(FeatureEngineer.extract_weather_features(weather))
        return features

    @staticmethod
    def build_feature_vector(event: Dict[str, Any], weather: Dict[str, Any], temporal: datetime) -> np.ndarray:
        feature_dict = FeatureEngineer.build_feature_dict(event, weather, temporal)
        vector = [float(feature_dict[col]) for col in FeatureEngineer.FEATURE_COLUMNS]
        return np.array(vector)

    @staticmethod
    def build_feature_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Build features for training from a raw DataFrame.
        """
        event_type_map = FeatureEngineer.get_event_type_map()
        priority_map = FeatureEngineer.get_priority_map()

        processed = pd.DataFrame(index=df.index)
        processed["estimated_attendance"] = df["estimated_attendance"].fillna(0).astype(float)
        processed["event_type_encoded"] = df["event_type"].str.lower().map(event_type_map).fillna(event_type_map["other"]).astype(float)
        processed["priority_encoded"] = df["priority"].map(priority_map).fillna(priority_map["Medium"]).astype(float)
        processed["requires_road_closure"] = df["requires_road_closure"].fillna(False).astype(int).astype(float)

        timestamps = pd.to_datetime(df["start_datetime"])
        processed["hour"] = timestamps.dt.hour.astype(float)
        processed["day_of_week"] = timestamps.dt.dayofweek.astype(float)
        processed["month"] = timestamps.dt.month.astype(float)
        processed["is_weekend"] = (timestamps.dt.dayofweek >= 5).astype(int).astype(float)
        processed["is_rush_hour"] = (((timestamps.dt.hour >= 7) & (timestamps.dt.hour <= 10)) | ((timestamps.dt.hour >= 17) & (timestamps.dt.hour <= 20))).astype(int).astype(float)

        processed["temperature"] = df["temperature"].fillna(25.0).astype(float)
        processed["precipitation"] = df["precipitation"].fillna(0.0).astype(float)
        processed["is_raining"] = (processed["precipitation"] > 0.0).astype(int).astype(float)

        if "latitude" in df.columns:
            processed["latitude"] = df["latitude"].fillna(19.0760).astype(float)
        else:
            processed["latitude"] = 19.0760

        if "longitude" in df.columns:
            processed["longitude"] = df["longitude"].fillna(72.8777).astype(float)
        else:
            processed["longitude"] = 72.8777

        # geohash
        def compute_row_geohash(row):
            lat = pd.to_numeric(row.get("latitude"), errors="coerce")
            lon = pd.to_numeric(row.get("longitude"), errors="coerce")
            if pd.isna(lat) or pd.isna(lon):
                return FeatureEngineer.latlon_to_geohash(19.0760, 72.8777)
            return FeatureEngineer.latlon_to_geohash(float(lat), float(lon))
        processed["geohash"] = df.apply(compute_row_geohash, axis=1)

        # zone, junction, corridor
        if "zone" in df.columns:
            processed["zone_encoded"] = df["zone"].fillna("Unknown").apply(lambda x: FeatureEngineer.stable_hash(str(x), buckets=20))
        else:
            processed["zone_encoded"] = 0.0

        if "junction" in df.columns:
            processed["junction_encoded"] = df["junction"].fillna("Unknown").apply(lambda x: FeatureEngineer.stable_hash(str(x), buckets=200))
        else:
            processed["junction_encoded"] = 0.0

        if "corridor" in df.columns:
            processed["corridor_encoded"] = df["corridor"].fillna("Unknown").apply(lambda x: FeatureEngineer.stable_hash(str(x), buckets=100))
        else:
            processed["corridor_encoded"] = 0.0

        # historical stats
        if "event_type" in df.columns:
            type_counts = df["event_type"].str.lower().value_counts(normalize=True)
            if "start_datetime" in df.columns and "resolved_datetime" in df.columns:
                start_t = pd.to_datetime(df["start_datetime"])
                resolved_t = pd.to_datetime(df["resolved_datetime"])
                durations = (resolved_t - start_t) / pd.Timedelta(minutes=1)
                df_temp = df.copy()
                df_temp["duration_temp"] = durations
                type_durations = df_temp.groupby(df_temp["event_type"].str.lower())["duration_temp"].mean()
            else:
                type_durations = pd.Series()

            processed["historical_event_frequency"] = df["event_type"].str.lower().map(type_counts).fillna(0.05).astype(float)
            processed["average_resolution_time"] = df["event_type"].str.lower().map(type_durations).fillna(120.0).astype(float)
        else:
            processed["historical_event_frequency"] = 0.05
            processed["average_resolution_time"] = 120.0

        # Zone and junction incident density (computed from frequency × encoded location)
        processed["zone_incident_density"] = (
            processed["historical_event_frequency"] * processed["zone_encoded"] / 10.0
        ).round(4)
        processed["junction_incident_density"] = (
            processed["historical_event_frequency"] * processed["junction_encoded"] / 100.0
        ).round(4)

        return processed[FeatureEngineer.FEATURE_COLUMNS]
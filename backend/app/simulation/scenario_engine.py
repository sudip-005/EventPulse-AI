import copy
from typing import Dict, List, Any
from app.services.forecast_service import ForecastService
from app.geospatial.clustering import HotspotDetector
from app.recommendations.resource_allocator import ResourceRecommender
import numpy as np

class ScenarioSimulator:
    def __init__(self):
        self.hotspot_detector = HotspotDetector()

    def simulate_scenario(self, base_event: Dict, scenario_params: Dict, road_network: List[Dict], traffic_data: List[Dict]) -> Dict:
        modified_event = copy.deepcopy(base_event)
        if "attendance_multiplier" in scenario_params:
            modified_event["estimated_attendance"] *= scenario_params["attendance_multiplier"]
            modified_event["impact_score"] = min(modified_event.get("impact_score", 50) * scenario_params["attendance_multiplier"], 100)
        if "weather" in scenario_params and scenario_params["weather"].get("condition") == "rain":
            modified_event["impact_score"] = min(modified_event.get("impact_score", 50) * 1.3, 100)
        if "road_closure" in scenario_params:
            # would update road_network
            pass
        # Generate synthetic forecasts
        forecasts = []
        for i in range(10):
            cong = 50 + modified_event.get("impact_score", 50) * 0.5 + np.random.normal(0, 10)
            forecasts.append({
                "road_id": f"road_{i}",
                "congestion_score": min(max(cong, 0), 100),
                "location": (19.0 + i*0.001, 72.8 + i*0.001)
            })
        # Detect hotspots
        points = [(f["location"][0], f["location"][1]) for f in forecasts if f["congestion_score"] > 50]
        scores = [f["congestion_score"] for f in forecasts if f["congestion_score"] > 50]
        hotspots = self.hotspot_detector.detect_hotspots(points, scores)
        return {
            "scenario_params": scenario_params,
            "modified_event": modified_event,
            "forecasts": forecasts,
            "hotspots": hotspots,
            "status": "completed"
        }
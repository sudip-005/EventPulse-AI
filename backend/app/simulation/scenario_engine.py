import copy
import math
import random
from typing import Dict, List, Any, Tuple
from app.geospatial.clustering import HotspotDetector
from app.recommendations.resource_allocator import ResourceRecommender
from geopy.distance import geodesic
from app.ml.inference import XGBoostInference
from app.ml.features import FeatureEngineer
from datetime import datetime

class ScenarioSimulator:
    def __init__(self):
        self.hotspot_detector = HotspotDetector()
        self.recommender = ResourceRecommender()
        self.inference = XGBoostInference()

    def simulate_scenario(self, base_event: Dict, scenario_params: Dict, road_network: List[Dict]) -> Dict:
        modified_event = copy.deepcopy(base_event)
        
        # 1. Apply attendance multiplier
        attendance_mult = scenario_params.get("attendance_multiplier", 1.0)
        attendance = modified_event.get("estimated_attendance", 1000) * attendance_mult
        modified_event["estimated_attendance"] = int(attendance)
        
        # 2. Apply weather effects
        weather = scenario_params.get("weather", {})
        is_raining = weather.get("condition") == "rain" or weather.get("is_raining", False)
        
        # Extract coordinates
        event_lat, event_lon = base_event["location"]
        
        # Build modified features
        event_dict = {
            "estimated_attendance": int(attendance),
            "event_type": modified_event.get("event_type", "other"),
            "priority": modified_event.get("priority", "Medium"),
            "requires_road_closure": modified_event.get("requires_road_closure", False),
            "location": (event_lat, event_lon)
        }
        
        weather_dict = {
            "temperature": weather.get("temperature", 25.0),
            "precipitation": 8.0 if is_raining else 0.0
        }
        
        start_time = modified_event.get("start_time")
        if not isinstance(start_time, datetime):
            start_time = datetime.now()
            
        features = FeatureEngineer.build_feature_vector(event_dict, weather_dict, start_time)
        
        # Run ML model inference dynamically
        simulated_impact, impact_level = self.inference.predict_impact(features)
        
        simulated_impact = min(max(simulated_impact, 0.0), 100.0)
        modified_event["impact_score"] = simulated_impact
        
        # 3. Road closures & incidents
        closed_road_ids = set(scenario_params.get("road_closures", []))
        incident = scenario_params.get("incident", {})
        
        # Generate simulated road forecasts
        event_lat, event_lon = base_event["location"]
        decay_radius = max(500.0, math.log(attendance + 1) * 300.0)
        
        forecasts = []
        for r in road_network:
            road_id = r["road_id"]
            coords = r["coordinates"]
            if not coords:
                continue
            midpoint = coords[len(coords) // 2]
            
            # Base congestion
            random.seed(hash(road_id) % 2**32)
            base_congestion = 15.0 + random.random() * 15.0
            
            # Apply rain to baseline congestion
            if is_raining:
                base_congestion += 15.0
                
            dist_to_event = geodesic((event_lat, event_lon), midpoint).meters
            impact_multiplier = math.exp(-dist_to_event / decay_radius)
            congestion = base_congestion + (simulated_impact * impact_multiplier)
            
            # Apply road closures
            if road_id in closed_road_ids:
                congestion = 100.0
                
            # Apply incident impact (decays with distance from incident)
            if incident and "location" in incident and incident["location"]:
                inc_lat, inc_lon = incident["location"]
                dist_to_incident = geodesic((inc_lat, inc_lon), midpoint).meters
                if dist_to_incident < 800.0:  # 800m impact radius from incident epicenter
                    inc_mult = math.exp(-dist_to_incident / 250.0)
                    congestion += 60.0 * inc_mult
                    
            congestion = min(max(congestion, 0.0), 100.0)
            
            speed_limit = r["speed_limit_kmh"]
            if is_raining:
                speed_limit *= 0.8  # Speed limits drop by 20% in rain
            
            predicted_speed = speed_limit * (1.0 - (congestion / 100.0) * 0.8)
            predicted_speed = max(predicted_speed, 2.0 if road_id in closed_road_ids else 5.0)
            
            length_meters = r["length_meters"]
            speed_mps = predicted_speed / 3.6
            speed_limit_mps = speed_limit / 3.6
            delay = (length_meters / speed_mps - length_meters / speed_limit_mps) / 60.0
            delay = max(delay, 0.0)
            
            forecasts.append({
                "road_id": road_id,
                "name": r["name"],
                "congestion_score": congestion,
                "predicted_speed": predicted_speed,
                "delay_minutes": delay,
                "location": midpoint
            })
            
        # 4. Detect hotspots on simulated congestion
        points = [f["location"] for f in forecasts if f["congestion_score"] > 50.0]
        scores = [f["congestion_score"] for f in forecasts if f["congestion_score"] > 50.0]
        
        hotspots = []
        if len(points) >= 3:
            hotspots = self.hotspot_detector.detect_hotspots(points, scores, eps=250.0, min_samples=3)
        else:
            # Fake/Simulate a hotspot if we have at least one high congestion road
            high_cong_roads = [f for f in forecasts if f["congestion_score"] > 60.0]
            for idx, f in enumerate(high_cong_roads[:2]):
                hotspots.append({
                    "cluster_id": f"sim_hotspot_{idx}",
                    "center": f["location"],
                    "severity": min(int(f["congestion_score"] / 20.0), 5),
                    "point_count": 1,
                    "radius_meters": 100.0,
                    "avg_congestion": f["congestion_score"],
                    "max_congestion": f["congestion_score"]
                })
                
        # 5. Generate resource recommendations
        recs = self.recommender.recommend_resources(modified_event, hotspots, forecasts)
        
        return {
            "scenario_params": scenario_params,
            "modified_event": modified_event,
            "forecasts": forecasts,
            "hotspots": hotspots,
            "recommendations": recs,
            "status": "completed"
        }
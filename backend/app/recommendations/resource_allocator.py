from typing import List, Dict, Tuple, Any

class ResourceRecommender:
    def __init__(self):
        self.police_per_1000_attendees = 2
        self.barricades_per_1000_attendees = 5
        self.marshals_per_500_attendees = 1
        
        # Max capacity constraints
        self.max_police_capacity = 50
        self.max_barricades_capacity = 100
        self.max_marshals_capacity = 30

    def recommend_resources(self, event: Dict, hotspots: List[Dict], forecasts: List[Dict]) -> Dict:
        # Calculate raw allocations
        police_recs = self._recommend_police(event, hotspots)
        barricade_recs = self._recommend_barricades(event, hotspots)
        marshal_recs = self._recommend_marshals(event, hotspots)
        
        warnings = []
        
        # Enforce capacity constraints on Police
        total_police = sum(r["count"] for r in police_recs)
        if total_police > self.max_police_capacity:
            warnings.append(f"Police request ({total_police}) exceeded max capacity ({self.max_police_capacity}). Scaling allocation proportionally, prioritizing high-severity hotspots.")
            scale = self.max_police_capacity / total_police
            for r in police_recs:
                original_count = r["count"]
                r["count"] = max(1 if original_count > 0 else 0, int(original_count * scale))
                r["reasoning"] += f" (Scaled from {original_count} due to capacity limit)"
        
        # Enforce capacity constraints on Barricades
        total_barricades = sum(r["count"] for r in barricade_recs)
        if total_barricades > self.max_barricades_capacity:
            warnings.append(f"Barricades request ({total_barricades}) exceeded max capacity ({self.max_barricades_capacity}). Scaling allocation proportionally.")
            scale = self.max_barricades_capacity / total_barricades
            for r in barricade_recs:
                original_count = r["count"]
                r["count"] = max(1 if original_count > 0 else 0, int(original_count * scale))
                r["reasoning"] += f" (Scaled from {original_count} due to capacity limit)"
                
        # Enforce capacity constraints on Marshals
        total_marshals = sum(r["count"] for r in marshal_recs)
        if total_marshals > self.max_marshals_capacity:
            warnings.append(f"Marshals request ({total_marshals}) exceeded max capacity ({self.max_marshals_capacity}). Scaling allocation proportionally.")
            scale = self.max_marshals_capacity / total_marshals
            for r in marshal_recs:
                original_count = r["count"]
                r["count"] = max(1 if original_count > 0 else 0, int(original_count * scale))
                r["reasoning"] += f" (Scaled from {original_count} due to capacity limit)"

        recommendations: Dict[str, Any] = {
            "police": police_recs,
            "barricades": barricade_recs,
            "marshals": marshal_recs,
            "emergency_routes": self._recommend_emergency_routes(hotspots, forecasts),
            "warnings": warnings
        }
        recommendations["reasoning"] = self._generate_reasoning(event, hotspots, recommendations)
        return recommendations

    def _recommend_police(self, event: Dict, hotspots: List[Dict]) -> List[Dict]:
        attendance = event.get("estimated_attendance", 0)
        base_count = max(2, int(attendance / 1000 * self.police_per_1000_attendees))
        if not hotspots:
            return [{"location": event.get("location", (0,0)), "count": base_count, "priority": 1, "reasoning": "Base deployment"}]
        recs = []
        for i, h in enumerate(hotspots[:3]):
            recs.append({
                "location": h["center"],
                "count": base_count + h["severity"],
                "priority": h["severity"],
                "reasoning": f"Hotspot {i+1} severity {h['severity']}"
            })
        return recs

    def _recommend_barricades(self, event: Dict, hotspots: List[Dict]) -> List[Dict]:
        attendance = event.get("estimated_attendance", 0)
        base = int(attendance / 1000 * self.barricades_per_1000_attendees)
        return [{"location": h["center"], "count": base + h["severity"]*2, "radius_meters": h["radius_meters"], "reasoning": f"Barricade for hotspot"} for h in hotspots[:3]]

    def _recommend_marshals(self, event: Dict, hotspots: List[Dict]) -> List[Dict]:
        attendance = event.get("estimated_attendance", 0)
        base = max(1, int(attendance / 500 * self.marshals_per_500_attendees))
        return [{"location": h["center"], "count": base + h["severity"], "reasoning": f"Marshal at hotspot"} for h in hotspots[:2]]

    def _recommend_emergency_routes(self, hotspots: List[Dict], forecasts: List[Dict]) -> List[Dict]:
        avoid = [(h["center"], h["radius_meters"]*1.5) for h in hotspots if h["severity"] >= 3]
        return [{"route_id": "emergency_1", "avoid_areas": avoid, "reasoning": "Avoid severe hotspots"}]

    def _generate_reasoning(self, event: Dict, hotspots: List[Dict], recs: Dict) -> str:
        parts = [f"Event '{event.get('name', 'Unknown')}' with {event.get('estimated_attendance', 0)} attendees"]
        if hotspots:
            parts.append(f"Detected {len(hotspots)} congestion hotspots")
        total_police = sum(r["count"] for r in recs.get("police", []))
        total_barricades = sum(r["count"] for r in recs.get("barricades", []))
        parts.append(f"Recommended: {total_police} officers, {total_barricades} barricades")
        if recs.get("warnings"):
            parts.append("RESOURCE CONSTRAINTS ACTIVE")
        return " | ".join(parts)
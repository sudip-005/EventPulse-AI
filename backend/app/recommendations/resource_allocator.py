from typing import List, Dict, Tuple, Any

class ResourceRecommender:
    def __init__(self):
        self.police_per_1000_attendees = 2
        self.barricades_per_1000_attendees = 5
        self.marshals_per_500_attendees = 1

    def recommend_resources(self, event: Dict, hotspots: List[Dict], forecasts: List[Dict]) -> Dict:
        recommendations: Dict[str, Any] = {
            "police": self._recommend_police(event, hotspots),
            "barricades": self._recommend_barricades(event, hotspots),
            "marshals": self._recommend_marshals(event, hotspots),
            "emergency_routes": self._recommend_emergency_routes(hotspots, forecasts)
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
        return " | ".join(parts)
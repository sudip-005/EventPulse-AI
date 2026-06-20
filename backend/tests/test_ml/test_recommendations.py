import pytest
from app.recommendations.resource_allocator import ResourceRecommender

def test_resource_recommender_capacity_constraints():
    recommender = ResourceRecommender()
    
    # Create an event with massive attendance to exceed capacity limits
    event = {
        "name": "Mega Sports Event",
        "estimated_attendance": 100000,
        "event_type": "sports",
        "priority": "Critical",
        "requires_road_closure": True,
        "location": (19.0760, 72.8777)
    }
    
    hotspots = [
        {
            "cluster_id": "hotspot_1",
            "center": (19.0760, 72.8777),
            "severity": 4,
            "point_count": 10,
            "radius_meters": 300.0,
            "avg_congestion": 85.0
        }
    ]
    
    forecasts = []
    
    recs = recommender.recommend_resources(event, hotspots, forecasts)
    
    # Assert fields exist
    assert "police" in recs
    assert "barricades" in recs
    assert "marshals" in recs
    assert "warnings" in recs
    
    # Assert that warnings were generated
    assert len(recs["warnings"]) > 0
    
    # Assert that total recommended resources respect max capacity limits
    total_police = sum(r["count"] for r in recs["police"])
    total_barricades = sum(r["count"] for r in recs["barricades"])
    total_marshals = sum(r["count"] for r in recs["marshals"])
    
    assert total_police <= recommender.max_police_capacity
    assert total_barricades <= recommender.max_barricades_capacity
    assert total_marshals <= recommender.max_marshals_capacity
    
    # Assert scaling was applied (counts are smaller than raw formula results)
    assert total_police < 204

import pytest
from app.geospatial.clustering import HotspotDetector

def test_detect_hotspots():
    detector = HotspotDetector(algorithm="dbscan")
    
    # 5 points clustered together, 1 outlier
    points = [
        (19.0760, 72.8777),
        (19.0761, 72.8778),
        (19.0759, 72.8776),
        (19.0762, 72.8779),
        (19.0758, 72.8775),
        (19.2000, 73.0000)  # Outlier
    ]
    scores = [60.0, 70.0, 65.0, 80.0, 55.0, 90.0]
    
    hotspots = detector.detect_hotspots(points, scores, eps=200.0, min_samples=4)
    assert len(hotspots) > 0
    
    # The first cluster should have specific details
    cluster = hotspots[0]
    assert "cluster_id" in cluster
    assert "center" in cluster
    assert cluster["point_count"] >= 4
    assert "severity" in cluster
    assert "radius_meters" in cluster
    assert "avg_congestion" in cluster

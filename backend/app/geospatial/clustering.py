import numpy as np
from sklearn.cluster import DBSCAN
import hdbscan
from typing import List, Dict, Tuple, Any
from geopy.distance import geodesic

class HotspotDetector:
    def __init__(self, algorithm: str = "dbscan"):
        self.algorithm = algorithm

    def _compute_distance_matrix(self, points: List[Tuple[float, float]]) -> np.ndarray:
        n = len(points)
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                dist = geodesic(points[i], points[j]).meters
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist
        return dist_matrix

    def detect_hotspots(self, points: List[Tuple[float, float]], congestion_scores: List[float],
                        eps: float = 200.0, min_samples: int = 5) -> List[Dict]:
        if len(points) < min_samples:
            return []
        if self.algorithm == "dbscan":
            dist_matrix: Any = self._compute_distance_matrix(points)
            clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
            labels = clusterer.fit_predict(dist_matrix)
        else:
            coords_rad: Any = np.radians(points)
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_samples, metric='haversine', alpha=0.5)
            labels = clusterer.fit_predict(coords_rad)
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:
                continue
            if label not in clusters:
                clusters[label] = {"points": [], "scores": []}
            clusters[label]["points"].append(points[idx])
            clusters[label]["scores"].append(congestion_scores[idx])
        result = []
        for cluster_id, data in clusters.items():
            lat_avg = sum(p[0] for p in data["points"]) / len(data["points"])
            lon_avg = sum(p[1] for p in data["points"]) / len(data["points"])
            severity = int(np.mean(data["scores"]) / 20) + 1
            max_dist = max(geodesic((lat_avg, lon_avg), p).meters for p in data["points"])
            result.append({
                "cluster_id": f"hotspot_{cluster_id}",
                "center": (lat_avg, lon_avg),
                "severity": min(severity, 5),
                "point_count": len(data["points"]),
                "radius_meters": max_dist,
                "avg_congestion": np.mean(data["scores"]),
                "max_congestion": max(data["scores"])
            })
        result.sort(key=lambda x: x["severity"], reverse=True)
        return result
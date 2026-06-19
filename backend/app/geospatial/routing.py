import networkx as nx
from typing import List, Dict, Tuple, Optional

class RouteDiversionEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_road_network(self, roads: List[Dict]):
        for road in roads:
            self.graph.add_edge(
                road["from_node"],
                road["to_node"],
                length=road["length_meters"],
                speed_limit=road["speed_limit_kmh"],
                capacity=road["capacity"],
                road_id=road["road_id"],
                geometry=road["geometry"],
                one_way=road.get("one_way", False),
                congestion=road.get("congestion", 0)
            )
            if not road.get("one_way", False):
                self.graph.add_edge(
                    road["to_node"],
                    road["from_node"],
                    length=road["length_meters"],
                    speed_limit=road["speed_limit_kmh"],
                    capacity=road["capacity"],
                    road_id=road["road_id"],
                    geometry=road["geometry"],
                    one_way=False,
                    congestion=road.get("congestion", 0)
                )

    def _calculate_weight(self, u: str, v: str, edge_data: Dict, congestion_weight: float = 0.5) -> float:
        base_weight = edge_data["length"] / (edge_data["speed_limit"] / 3.6)
        congestion = edge_data.get("congestion", 0)
        penalty = 1 + (congestion / 100) * congestion_weight
        return base_weight * penalty

    def find_alternate_routes(self, origin: Tuple[float, float], destination: Tuple[float, float],
                              num_routes: int = 3, avoid_hotspots: bool = True) -> List[Dict]:
        # Placeholder - real implementation uses NetworkX A* with geometry
        return [{"path": [origin, destination], "travel_time": 600, "is_primary": True}]

    def _heuristic(self, u: str, v: str) -> float:
        return 0

    def _find_nearest_node(self, point: Tuple[float, float]) -> str:
        return "node0"

    def _calculate_path_time(self, path: List[str]) -> float:
        total = 0
        for i in range(len(path)-1):
            edge_data = self.graph.get_edge_data(path[i], path[i+1])
            if edge_data:
                total += self._calculate_weight(path[i], path[i+1], edge_data, 0.3)
        return total
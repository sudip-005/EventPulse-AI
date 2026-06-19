import networkx as nx
from typing import Dict, List, Tuple

class RoadNetworkBuilder:
    @staticmethod
    def build_graph(roads: List[Dict]) -> nx.DiGraph:
        G = nx.DiGraph()
        for r in roads:
            G.add_edge(
                r["from_node"],
                r["to_node"],
                length=r["length_meters"],
                speed_limit=r["speed_limit_kmh"],
                capacity=r["capacity"],
                road_id=r["road_id"],
                geometry=r["geometry"],
                one_way=r.get("one_way", False),
                congestion=r.get("congestion", 0)
            )
            if not r.get("one_way", False):
                G.add_edge(
                    r["to_node"],
                    r["from_node"],
                    length=r["length_meters"],
                    speed_limit=r["speed_limit_kmh"],
                    capacity=r["capacity"],
                    road_id=r["road_id"],
                    geometry=r["geometry"],
                    one_way=False,
                    congestion=r.get("congestion", 0)
                )
        return G
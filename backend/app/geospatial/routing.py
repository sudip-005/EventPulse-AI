import networkx as nx
import re
from typing import Any, List, Dict, Tuple, Optional
from geopy.distance import geodesic

def parse_linestring_wkt(geometry: Any) -> List[Tuple[float, float]]:
    """Return (lat, lon) pairs from either GeoJSON or legacy WKT."""
    if not geometry:
        return []
    if isinstance(geometry, dict):
        return [(float(lat), float(lon)) for lon, lat in geometry.get("coordinates", [])]
    # Support both LINESTRING and geometry representation
    match = re.search(r'LINESTRING\s*\((.*)\)', str(geometry), re.IGNORECASE)
    if not match:
        return []
    points_str = match.group(1).split(',')
    coords = []
    for p in points_str:
        parts = p.strip().split()
        if len(parts) >= 2:
            coords.append((float(parts[1]), float(parts[0])))  # (lat, lon)
    return coords

class RouteDiversionEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_coords = {}

    def build_road_network(self, roads: List[Dict]):
        self.graph.clear()
        self.node_coords.clear()
        
        for road in roads:
            coords = parse_linestring_wkt(road["geometry"])
            if not coords:
                continue
                
            from_node = road["from_node"]
            to_node = road["to_node"]
            
            # Store node coordinates (approximate from edge endpoints)
            self.node_coords[from_node] = coords[0]
            self.node_coords[to_node] = coords[-1]
            
            length = road["length_meters"]
            speed_limit = road["speed_limit_kmh"]
            capacity = road["capacity"]
            road_id = road["road_id"]
            one_way = road.get("one_way", False)
            congestion = road.get("congestion", 0)
            
            self.graph.add_edge(
                from_node,
                to_node,
                length=length,
                speed_limit=speed_limit,
                capacity=capacity,
                road_id=road_id,
                geometry=coords,
                one_way=one_way,
                congestion=congestion
            )
            
            if not one_way:
                self.graph.add_edge(
                    to_node,
                    from_node,
                    length=length,
                    speed_limit=speed_limit,
                    capacity=capacity,
                    road_id=road_id,
                    geometry=list(reversed(coords)),
                    one_way=False,
                    congestion=congestion
                )

    def find_nearest_node(self, point: Tuple[float, float]) -> str:
        if not self.node_coords:
            raise ValueError("Road network graph is empty")
        nearest_node = None
        min_dist = float('inf')
        for node, coords in self.node_coords.items():
            dist = geodesic(point, coords).meters
            if dist < min_dist:
                min_dist = dist
                nearest_node = node
        if nearest_node is None:
            raise ValueError("No nearest node found")
        return nearest_node

    def find_alternate_routes(self, origin: Tuple[float, float], destination: Tuple[float, float],
                              num_routes: int = 3, avoid_hotspots: bool = True, hotspots: Optional[List[Dict]] = None) -> List[Dict]:
        if not self.graph.nodes:
            return []
            
        try:
            source = self.find_nearest_node(origin)
            target = self.find_nearest_node(destination)
        except Exception:
            return []
            
        if source == target:
            return [{"path": [origin, destination], "travel_time_seconds": 0.0, "distance_meters": 0.0, "is_primary": True}]
            
        hotspots = hotspots or []
        
        # Dynamic edge weight calculation
        def get_weight(u, v, d):
            length = d["length"]
            speed_limit = d["speed_limit"]
            congestion = d.get("congestion", 0)
            
            # Base travel time in seconds
            speed_mps = max(speed_limit / 3.6, 1.0)
            travel_time = length / speed_mps
            
            # Congestion penalty: 100% congestion multiplies travel time by 3
            penalty = 1.0 + (congestion / 100.0) * 2.0
            
            # Hotspot avoidance penalty
            if avoid_hotspots:
                edge_coords = d.get("geometry", [])
                if edge_coords:
                    midpoint = edge_coords[len(edge_coords) // 2]
                    for h in hotspots:
                        h_center = h.get("center")
                        h_radius = h.get("radius_meters", 100.0)
                        if h_center:
                            dist = geodesic(midpoint, h_center).meters
                            if dist <= h_radius * 1.5:
                                severity = h.get("severity", 3)
                                # Add severe time penalty
                                penalty += 20.0 * severity
                                
            return travel_time * penalty

        def heuristic(node, target_node):
            node_coord = self.node_coords.get(node)
            target_coord = self.node_coords.get(target_node)
            if node_coord and target_coord:
                # Travel time estimate in seconds (distance / max speed of 120 km/h)
                dist_meters = geodesic(node_coord, target_coord).meters
                return dist_meters / 33.3
            return 0.0

        routes = []
        working_graph = self.graph.copy()
        
        for r_idx in range(num_routes):
            try:
                # Find shortest path using A* Search Algorithm
                path = nx.astar_path(working_graph, source=source, target=target, heuristic=heuristic, weight=get_weight)
                
                path_coords = []
                total_distance = 0.0
                total_time = 0.0
                
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    edge_data = working_graph.get_edge_data(u, v)
                    if edge_data:
                        total_distance += edge_data["length"]
                        speed = max(edge_data["speed_limit"] / 3.6, 1.0)
                        total_time += (edge_data["length"] / speed) * (1.0 + edge_data.get("congestion", 0)/100.0)
                        geom = edge_data["geometry"]
                        if i == 0:
                            path_coords.extend(geom)
                        else:
                            path_coords.extend(geom[1:])
                
                if not path_coords:
                    path_coords = [self.node_coords[n] for n in path]
                    
                routes.append({
                    "path": path_coords,
                    "travel_time_seconds": total_time,
                    "distance_meters": total_distance,
                    "is_primary": (r_idx == 0)
                })
                
                # Penalize edges in this path for subsequent route searches
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    if working_graph.has_edge(u, v):
                        working_graph[u][v]["length"] *= 5.0  # Discourage reuse
                        
            except nx.NetworkXNoPath:
                break
                
        return routes

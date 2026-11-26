import json, math, heapq
from pathlib import Path
from pyvis.network import Network
# JSON is a way to store a dictionary into a file
# Pyvis is a Python library dedicated to visualizing data structures such as graphs  |  https://pyvis.readthedocs.io/en/latest/tutorial.html#getting-started


# -----------------------
# HELPER FUNCTIONS: GRAPH
# -----------------------

# Helper functions validate user input before passing it to Pyvis
def add_location(node_id:int, place:str, x_loc:float = None, y_loc:float = None):
    """Adds a new location on the map as a node on the graph. def add_location(id:int, place:str, x_loc:float = None, y_loc:float = None):"""
    graph.add_node(
        node_id,
        label = place,
        x = x_loc / 1000,
        y = y_loc / -1000,
    )

def add_road(node_a, node_b, distance):
    """Denotes the distance between two locations as an edge"""    
    graph.add_edge(node_a, node_b, label=str(distance))

def remove_location():
    pass

def remove_road():
    pass



# HELPER FUNCTIONS: DIJKSTRA
# Adjacency list stored in memory: {node_id: [(neighbor_id, distance), ...]}
adj_list = {}
locations_meta = {}

def register_undirected_edge(node_a: int, node_b: int, distance: float):
    """Stores both directions in adj_list for shortest-path search."""
    adj_list.setdefault(node_a, []).append((node_b, distance))
    adj_list.setdefault(node_b, []).append((node_a, distance))

def dijkstra(start_id: int, end_id: int):
    """
    Finds the shortest path from start_id to end_id.
    Returns: (total_distance, path_list)
      - total_distance: float('inf') if unreachable
      - path_list: list of node IDs from start_id to end_id (empty if unreachable)
    """
    if start_id not in adj_list or end_id not in adj_list:
        return float("inf"), []

    if start_id == end_id:
        return 0.0, [start_id]

    # Min-heap entries: (cumulative_distance, current_node_id)
    pq = [(0.0, start_id)]
    min_dist = {node_id: float("inf") for node_id in adj_list}
    min_dist[start_id] = 0.0
    parent = {node_id: None for node_id in adj_list}
    visited = set()

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue
        visited.add(current_node)

        # Early exit once we pop the destination with its shortest distance
        if current_node == end_id:
            break

        for neighbor_id, weight in adj_list.get(current_node, []):
            if neighbor_id in visited:
                continue

            new_dist = current_dist + weight
            if new_dist < min_dist[neighbor_id]:
                min_dist[neighbor_id] = new_dist
                parent[neighbor_id] = current_node
                heapq.heappush(pq, (new_dist, neighbor_id))

    if min_dist[end_id] == float("inf"):
        return float("inf"), []

    # Reconstruct path from end_id back to start_id
    path = []
    curr = end_id
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()

    return min_dist[end_id], path


# =========
# INITIALIZATION & DATA LOADING
# =========

# Initialize the graph
graph = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
graph.barnes_hut()

# Find test_data.json robustly relative to this file or current working directory
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_FILE = _DATA_DIR / "test_data.json"
if not _DATA_FILE.exists():
    _DATA_FILE = Path("./data/test_data.json")

def load_graph_data(file_path=None):
    """Loads graph nodes and undirected edges from test_data.json into memory."""
    target_path = Path(file_path) if file_path else _DATA_FILE
    with open(target_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    adj_list.clear()
    locations_meta.clear()

    # Step 1: Add all locations
    for key, value in raw_data.items():
        node_id = int(key)
        place_name = value['place'][0]
        x_coord = value['place'][1]
        y_coord = value['place'][2]
        locations_meta[node_id] = {
            "id": node_id,
            "place": place_name,
            "x": x_coord,
            "y": y_coord,
            "neighbors": value.get("neighbors", [])
        }
        add_location(node_id, place_name, x_coord, y_coord)

    # Step 2: Register roads and undirected edges
    added_edges = set()
    for key, value in raw_data.items():
        node_a = int(key)
        for neighbor in value.get("neighbors", []):
            node_b = int(neighbor[0])
            dist = float(neighbor[1])
            edge_key = tuple(sorted((node_a, node_b)))
            if edge_key not in added_edges:
                add_road(node_a, node_b, dist)
                added_edges.add(edge_key)
            register_undirected_edge(node_a, node_b, dist)

    return raw_data

# Populate data when module is loaded
data = load_graph_data()

def get_graph_dict():
    """Returns nodes and edges formatted for frontend consumption."""
    nodes = []
    for node_id, info in locations_meta.items():
        nodes.append({
            "id": node_id,
            "label": f"Stop {info['place']}",
            "place": info["place"],
            "x": info["x"] * 100,
            "y": info["y"] * -100,
            "orig_x": info["x"],
            "orig_y": info["y"],
            "neighbors": info["neighbors"]
        })

    edges = []
    seen = set()
    for node_id, info in locations_meta.items():
        for neighbor in info["neighbors"]:
            nbr_id = int(neighbor[0])
            dist = float(neighbor[1])
            edge_key = tuple(sorted((node_id, nbr_id)))
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append({
                    "from": node_id,
                    "to": nbr_id,
                    "distance": dist,
                    "label": f"{dist} km"
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "locations": locations_meta
    }

if __name__ == "__main__":
    print("Loading data!")
    print("Data loaded successfully!")

    # Generate and save the interactive HTML file
    # notebook=False tells Pyvis you are running this as a regular Python script, not in a Jupyter Notebook
    graph.toggle_physics(False)
    graph.show("kargograph_map.html", notebook=False)
    print("Graph exported to kargograph_map.html! Open this file in your web browser.")

    total_km, route = dijkstra(1, 9)
    print(f"Shortest distance: {total_km} km | Path: {route}")

import json
from pyvis.network import Network
# JSON is a way to store 
# Pyvis is a Python library dedicated to visualizing data structures such as graphs  |  https://pyvis.readthedocs.io/en/latest/tutorial.html#getting-started


# -----------------------
# HELPER FUNCTIONS: GRAPH
# -----------------------

# Helper functions validate user input before passing it to Pyvis
def add_location(node_id:int, place:str):
    """Adds a new location on the map as a node on the graph. def add_location(id:int, place:str, x_loc:float = None, y_loc:float = None):"""
    graph.add_node(node_id, label=place)

def add_road(node_a, node_b, distance):
    """Denotes the distance between two locations as an edge"""    
    graph.add_edge(node_a, node_b, length=distance)

def remove_location():
    pass

def remove_road():
    pass


# HELPER FUNCTIONS: MATH
def convert_code_to_location():
    """
    Coming soon: Converts an area code to an x and y tuple
    """
    pass



# =========
# MAIN CODE
# =========

# Initialize the graph
graph = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
graph.barnes_hut()

# Open and read the JSON file
with open("./data/test_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)
print("Loading data!")

for key, value in data.items():
    # Add a location (node_id, place)
    key = int(key)
    add_location(key, value["place"])

for key, value in data.items():
    # Add a road (node_a, node_b, distance) --> raises AssertionError: non existent node '2'
    key = int(key)
    for i in value["neighbors"]:
        add_road(key, i[0], i[1])

print("Data loaded successfuly!")


"""
node_id = graph
node_data = zip(node_ids, locations)

start_ids = graph_data['Node A']
end_ids = graph_data['Node B']
lengths = graph_data['Distance']
edge_data = zip(starts, ends, lengths)

for edge in edge_data:
    start = edge[0]
    end = edge[1]
    length = edge[2]

    graph.add_node(start, start)
"""
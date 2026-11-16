import json
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
        x = x_loc,
        y = y_loc,
    )

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
    # Add a location (node_id, place). Keys must be added first to prevent errors for values.
    key = int(key)
    scale = 100
    add_location(key, value['place'][0], value['place'][1]*scale, value['place'][2]*scale*-1)

for key, value in data.items():
    # Add a road (node_a, node_b, distance) --> raises AssertionError: non existent node '2'
    key = int(key)
    for i in value["neighbors"]:
        add_road(key, i[0], i[1], )

print("Data loaded successfully!")

# Generate and save the interactive HTML file
# notebook=False tells Pyvis you are running this as a regular Python script, not in a Jupyter Notebook
graph.toggle_physics(False)
graph.show("kargograph_map.html", notebook=False)
print("Graph exported to kargograph_map.html! Open this file in your web browser.")
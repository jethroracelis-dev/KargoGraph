import json
from pyvis.network import Network
# JSON is a way to store 
# Pyvis is a Python library dedicated to visualizing data structures such as graphs  |  https://pyvis.readthedocs.io/en/latest/tutorial.html#getting-started


# -----------------------
# HELPER FUNCTIONS: GRAPH
# -----------------------

# Helper functions validate user input before passing it to Pyvis
def add_location(id:int, place:str, x_loc:float = None, y_loc:float = None):
    """Adds a new location on the map as a node on the graph. def add_location(id:int, place:str, x_loc:float = None, y_loc:float = None):"""
    graph.add_node(
        int,
        label = place,
        """
        Coming soon: x and y positions
        x = x_loc,
        y = y_loc,
        """
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

graph = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
graph.barnes_hut()

# For test we use a JSON file but in the end we must use DB
pass



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
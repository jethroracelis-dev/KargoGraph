import unittest
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.graph import dijkstra, adj_list, register_undirected_edge, load_graph_data

class TestDijkstra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure test data is loaded
        load_graph_data()

    def test_shortest_path_known_route(self):
        # Shortest path between node 1 and 9 in test_data.json
        dist, path = dijkstra(1, 9)
        self.assertEqual(dist, 6.0)
        self.assertEqual(path, [1, 2, 5, 3, 8, 9])

    def test_same_start_and_destination(self):
        dist, path = dijkstra(1, 1)
        self.assertEqual(dist, 0.0)
        self.assertEqual(path, [1])

    def test_direct_neighbors(self):
        dist, path = dijkstra(1, 2)
        self.assertEqual(dist, 2.0)
        self.assertEqual(path, [1, 2])

    def test_nonexistent_node(self):
        dist, path = dijkstra(999, 1)
        self.assertEqual(dist, float("inf"))
        self.assertEqual(path, [])

if __name__ == "__main__":
    unittest.main()

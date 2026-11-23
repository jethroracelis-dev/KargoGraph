#!/usr/bin/env python3
"""
KargoGraph - Fuel-Efficient Logistics Route Optimizer
Group 5 | CPE 3104
Ayap | Lastimozo | Racelis

Frontend Web Server & API Handler
Runs Dijkstra's algorithm from backend/graph.py and serves the interactive UI.
"""

import sys
import json
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import webbrowser

# Ensure root directory is in sys.path so backend modules can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent
LIB_DIR = ROOT_DIR / "lib"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from backend.graph import dijkstra, get_graph_dict, locations_meta, adj_list
except Exception as e:
    print(f"[Warning] Error importing from backend.graph: {e}")
    dijkstra = None
    get_graph_dict = None
    locations_meta = {}
    adj_list = {}

PORT = 5000
HOST = "127.0.0.1"

# Average cargo truck fuel consumption (approx 0.12 liters per km for light-medium logistics)
FUEL_RATE_L_PER_KM = 0.12
FUEL_COST_PER_LITER = 65.50  # PHP per liter reference


class KargoGraphHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving frontend assets and JSON API routes."""

    def end_headers(self):
        # Enable CORS for local testing
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Route 1: Serve Main UI
        if path in ("/", "/index.html"):
            index_file = FRONTEND_DIR / "index.html"
            if index_file.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                content = index_file.read_bytes()
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, "frontend/index.html not found.")
                return

        # Route 2: API - Get Graph Structure
        if path == "/api/graph":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            graph_data = get_graph_dict() if get_graph_dict else {}
            payload = json.dumps(graph_data).encode("utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Route 3: API - Calculate Route via GET query params
        if path == "/api/route":
            try:
                start_id = int(query.get("start", [None])[0])
                dest_id = int(query.get("destination", [None])[0])
                result = self._calculate_route_response(start_id, dest_id)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                payload = json.dumps(result).encode("utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                error_resp = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_header("Content-Length", str(len(error_resp)))
                self.end_headers()
                self.wfile.write(error_resp)
                return

        # Route 4: Static assets in lib/ (vis-network, etc.)
        if path.startswith("/lib/"):
            rel_path = path[len("/lib/"):]
            file_path = LIB_DIR / rel_path
            if file_path.exists() and file_path.is_file():
                self._serve_static_file(file_path)
                return

        # Route 5: Static assets in frontend/
        if path.startswith("/frontend/"):
            rel_path = path[len("/frontend/"):]
            file_path = FRONTEND_DIR / rel_path
            if file_path.exists() and file_path.is_file():
                self._serve_static_file(file_path)
                return

        # Fallback to standard handler
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/route":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                params = json.loads(body)
                start_id = int(params.get("start"))
                dest_id = int(params.get("destination"))
                result = self._calculate_route_response(start_id, dest_id)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                payload = json.dumps(result).encode("utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                error_resp = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_header("Content-Length", str(len(error_resp)))
                self.end_headers()
                self.wfile.write(error_resp)
                return

        self.send_error(404, "API endpoint not found")

    def _serve_static_file(self, file_path: Path):
        suffix = file_path.suffix.lower()
        content_types = {
            ".js": "application/javascript",
            ".css": "text/css",
            ".html": "text/html; charset=utf-8",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".svg": "image/svg+xml"
        }
        content_type = content_types.get(suffix, "application/octet-stream")
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _calculate_route_response(self, start_id: int, dest_id: int):
        """Executes Dijkstra's algorithm from backend.graph and prepares detailed metrics."""
        if dijkstra is None:
            raise RuntimeError("Backend Dijkstra algorithm is not loaded.")

        total_distance, path = dijkstra(start_id, dest_id)

        if total_distance == float("inf") or not path:
            return {
                "success": False,
                "reachable": False,
                "start": start_id,
                "destination": dest_id,
                "total_distance": None,
                "path": [],
                "hops": [],
                "message": f"No accessible route found between Stop {start_id} and Stop {dest_id}."
            }

        # Build detailed step-by-step hops
        hops = []
        cumulative = 0.0
        for i in range(len(path)):
            curr_id = path[i]
            curr_info = locations_meta.get(curr_id, {})
            curr_name = curr_info.get("place", f"Stop {curr_id}")

            leg_dist = 0.0
            if i > 0:
                prev_id = path[i - 1]
                # Look up edge distance between prev_id and curr_id in adj_list
                for nbr_id, weight in adj_list.get(prev_id, []):
                    if nbr_id == curr_id:
                        leg_dist = weight
                        break
                cumulative += leg_dist

            hops.append({
                "step": i + 1,
                "node_id": curr_id,
                "place_name": f"Stop {curr_name}",
                "leg_distance": leg_dist,
                "cumulative_distance": round(cumulative, 2)
            })

        # Calculate estimated fuel consumption and cost
        est_liters = round(total_distance * FUEL_RATE_L_PER_KM, 2)
        est_cost = round(est_liters * FUEL_COST_PER_LITER, 2)

        start_name = locations_meta.get(start_id, {}).get("place", str(start_id))
        dest_name = locations_meta.get(dest_id, {}).get("place", str(dest_id))

        return {
            "success": True,
            "reachable": True,
            "start": start_id,
            "start_name": f"Stop {start_name}",
            "destination": dest_id,
            "destination_name": f"Stop {dest_name}",
            "total_distance": round(total_distance, 2),
            "path": path,
            "hops": hops,
            "total_stops": len(path),
            "fuel_liters": est_liters,
            "fuel_cost_php": est_cost,
            "algorithm": "Dijkstra's Algorithm (backend/graph.py)"
        }


def run_server(port=PORT):
    # Try preferred port, fallback to alternatives if occupied
    for candidate_port in [port, 5001, 5002, 8080]:
        try:
            server = socketserver.TCPServer((HOST, candidate_port), KargoGraphHandler)
            print("=" * 60)
            print("  KARGO GRAPH - Fuel-Efficient Logistics Route Optimizer")
            print("  CPE 3104 | GROUP 5 (Ayap | Lastimozo | Racelis)")
            print("=" * 60)
            print(f"  ✓ Server running at: http://{HOST}:{candidate_port}")
            print(f"  ✓ Interactive graph & Dijkstra loaded from backend/graph.py")
            print(f"  ✓ Open http://{HOST}:{candidate_port} in your browser")
            print("=" * 60)
            print("Press Ctrl+C to stop the server.")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("\nServer shutting down.")
            finally:
                server.server_close()
            return
        except OSError as e:
            if "Address already in use" in str(e) or e.errno == 10048:
                continue
            raise e

    print(f"Error: Unable to bind server to ports {port}-8080.")


if __name__ == "__main__":
    cli_port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PORT
    run_server(cli_port)

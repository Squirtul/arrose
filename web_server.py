
# lets you see log and change airport online

import http.server
import json
import os
import socketserver
import sys
import urllib.parse

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

sys.path.insert(0, BASE_DIR)
from airports import AIRPORTS
from set_airport import change_airport


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/airports":
            self._send_json(sorted(AIRPORTS.keys()))
            return

        if parsed.path == "/set-airport":
            params = urllib.parse.parse_qs(parsed.query)
            icao = params.get("icao", [""])[0]
            success, message = change_airport(icao)
            self._send_json({"success": success, "message": message})
            return

        super().do_GET()

    def _send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Online on port {PORT}")
        httpd.serve_forever()
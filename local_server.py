import os
import json
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

# Add root directory to python path
sys.path.insert(0, os.path.dirname(__file__))

from src.app import lambda_handler

PORT = int(os.environ.get("PORT", 8000))
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("local_server")

class SchemeFinderRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/schemes") or self.path.startswith("/api/schemes"):
            self._handle_api_request("GET", "/schemes")
            return

        # Serve static web assets
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/chat") or self.path.startswith("/api/chat"):
            self._handle_api_request("POST", "/chat")
        elif self.path.startswith("/check") or self.path.startswith("/api/check"):
            self._handle_api_request("POST", "/check")
        else:
            self._handle_api_request("POST", self.path)

    def _handle_api_request(self, method: str, path: str):
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
        body_str = body_bytes.decode("utf-8") if body_bytes else "{}"

        # Construct AWS Lambda event object
        event = {
            "httpMethod": method,
            "path": path,
            "headers": dict(self.headers),
            "body": body_str
        }

        # Invoke Lambda handler
        response = lambda_handler(event, context=None)

        status_code = response.get("statusCode", 200)
        headers = response.get("headers", {})
        body = response.get("body", "{}")

        self.send_response(status_code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

def main():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, SchemeFinderRequestHandler)
    print("\n==========================================================")
    print(f"[+] SchemeFinder Assistant running locally on http://localhost:{PORT}")
    print(f"[*] Architecture: Chat UI -> API Layer (Lambda) -> Strands Agent -> Tools")
    print("==========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    main()

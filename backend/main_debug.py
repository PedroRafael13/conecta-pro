#!/usr/bin/env python3
"""
Servidor HTTP ultra-simples com debug.
"""

print("[DEBUG] Starting main_debug.py")
print("[DEBUG] Importing sys...")
print("[DEBUG] sys imported OK")

print("[DEBUG] Importing os...")
print("[DEBUG] os imported OK")

print("[DEBUG] Importing http.server...")
from http.server import BaseHTTPRequestHandler, HTTPServer  # noqa: E402

print("[DEBUG] http.server imported OK")

print("[DEBUG] Importing json...")
import json  # noqa: E402

print("[DEBUG] json imported OK")

print("[DEBUG] All imports completed!")


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "message": "Ultra simple server working"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Simple server is working!")

    def log_message(self, format_str, *args):
        return  # Disable logs


if __name__ == "__main__":
    print("[DEBUG] Starting server setup...")
    port = 8080
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"[DEBUG] Server created, starting on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[DEBUG] Server stopped")
        server.shutdown()

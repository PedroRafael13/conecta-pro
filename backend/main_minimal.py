#!/usr/bin/env python3
"""
Servidor HTTP mínimo - Startup ultra-rápido.
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    """Handler HTTP simples."""

    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path

        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "conecta-pro-minimal",
                "version": "1.0.0-minimal",
                "message": "Server started successfully - VPS performance optimized",
            }
            self.wfile.write(json.dumps(response).encode())

        elif path == "/" or path == "/docs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "message": "Conecta PRO API - Minimal Mode",
                "status": "running",
                "note": "Full API disabled due to VPS performance - use /health for monitoring",
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "error": "Service temporarily simplified due to VPS performance",
                "available_endpoints": ["/health", "/"],
            }
            self.wfile.write(json.dumps(response).encode())

    def log_message(self, format_str, *args):
        """Override to reduce log noise."""
        return


def run_server():
    """Run the minimal HTTP server."""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)

    logger.info(f"🚀 Conecta PRO Minimal Server starting on port {port}")
    logger.info("Available endpoints: /health, /")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped")
        server.shutdown()


if __name__ == "__main__":
    run_server()

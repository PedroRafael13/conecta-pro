"""Testes para Security Headers Middleware.

Coverage: core/middleware/security_headers.py
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.middleware.security_headers import SecurityHeadersMiddleware


@pytest.fixture
def app_with_security():
    """App com middleware de security headers."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    return app


@pytest.fixture
def client(app_with_security):
    """Test client."""
    return TestClient(app_with_security)


class TestSecurityHeaders:
    """Testa todos os headers de segurança."""

    def test_x_content_type_options(self, client):
        """X-Content-Type-Options: nosniff."""
        response = client.get("/test")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options(self, client):
        """X-Frame-Options: DENY."""
        response = client.get("/test")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_strict_transport_security(self, client):
        """Strict-Transport-Security: HSTS."""
        response = client.get("/test")
        hsts = response.headers["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_content_security_policy(self, client):
        """Content-Security-Policy presente."""
        response = client.get("/test")
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp

    def test_x_xss_protection(self, client):
        """X-XSS-Protection: 1; mode=block."""
        response = client.get("/test")
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_referrer_policy(self, client):
        """Referrer-Policy: strict-origin-when-cross-origin."""
        response = client.get("/test")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_permissions_policy(self, client):
        """Permissions-Policy presente."""
        response = client.get("/test")
        policy = response.headers["Permissions-Policy"]
        assert "geolocation=()" in policy
        assert "microphone=()" in policy

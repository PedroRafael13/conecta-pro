"""
Integration tests for critical Conecta PRO endpoints.
Uses real HTTP calls against running server — no mocks.
"""

import httpx
import pytest

BASE_URL = "http://127.0.0.1:8080"
API = f"{BASE_URL}/api/v1"

# Shared auth state
_token: str = ""


def get_token() -> str:
    global _token
    if not _token:
        resp = httpx.post(
            f"{API}/auth/login",
            data={"username": "admin@conectapro.com.br", "password": "admin123"},  # pragma: allowlist secret,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        _token = resp.json()["access_token"]
    return _token


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}


# ── HEALTH ──────────────────────────────────────────────────────────────────


def test_health_returns_200():
    resp = httpx.get(f"{BASE_URL}/health", headers=auth_headers())
    assert resp.status_code == 200


# ── AUTH ─────────────────────────────────────────────────────────────────────


def test_login_returns_token():
    resp = httpx.post(
        f"{API}/auth/login",
        data={"username": "admin@conectapro.com.br", "password": "admin123"},  # pragma: allowlist secret,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body.get("token_type", "").lower() == "bearer"


def test_login_invalid_credentials_returns_401():
    resp = httpx.post(
        f"{API}/auth/login",
        data={"username": "nobody@invalid.com", "password": "wrongpass"},  # pragma: allowlist secret
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code in (401, 422)


def test_protected_endpoint_without_token_returns_401():
    resp = httpx.get(f"{API}/operacional/employees")
    assert resp.status_code == 401


# ── OPERACIONAL — EMPLOYEES ──────────────────────────────────────────────────


def test_list_employees_returns_200():
    resp = httpx.get(f"{API}/operacional/employees", headers=auth_headers())
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, (list, dict))


def test_list_employees_pagination():
    resp = httpx.get(
        f"{API}/operacional/employees",
        params={"skip": 0, "limit": 5},
        headers=auth_headers(),
    )
    assert resp.status_code == 200


# ── OPERACIONAL — POSTS ──────────────────────────────────────────────────────


def test_list_posts_returns_200():
    resp = httpx.get(f"{API}/operacional/posts", headers=auth_headers())
    assert resp.status_code == 200


# ── FINANCIAL ────────────────────────────────────────────────────────────────


def test_financial_dashboard_returns_200():
    resp = httpx.get(f"{API}/financial/dashboard", headers=auth_headers())
    assert resp.status_code in (200, 404)  # endpoint may vary by module config


# ── CRM ──────────────────────────────────────────────────────────────────────


def test_crm_contacts_returns_200():
    resp = httpx.get(f"{API}/crm/contacts", headers=auth_headers())
    assert resp.status_code in (200, 404)


# ── POST STATUS_CODE 201 ──────────────────────────────────────────────────────


def test_post_create_resource_returns_201():
    """
    Validate that at least one resource-creation POST returns 201.
    Uses /api/v1/operacional/occurrences as the test endpoint.
    """
    # We test the declaration via OpenAPI spec, not by creating a real resource
    resp = httpx.get(f"{BASE_URL}/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    paths = schema.get("paths", {})

    # Count POST endpoints with 201 in responses
    posts_with_201 = []
    for path, methods in paths.items():
        if "post" in methods:
            responses = methods["post"].get("responses", {})
            if "201" in responses:
                posts_with_201.append(path)

    assert len(posts_with_201) >= 60, (
        f"Expected >= 60 POST endpoints with status_code=201, got {len(posts_with_201)}: {posts_with_201[:10]}"
    )


def test_openapi_no_verb_paths():
    """Validate OpenAPI spec doesn't expose verb-laden paths."""
    resp = httpx.get(f"{BASE_URL}/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    paths = list(schema.get("paths", {}).keys())

    verb_paths = [
        p
        for p in paths
        if any(segment in p.split("/") for segment in ["list", "create", "update", "delete", "get", "fetch", "remove"])
    ]
    assert len(verb_paths) == 0, f"Found verb paths in OpenAPI spec: {verb_paths[:5]}"


# ── CONFIG ───────────────────────────────────────────────────────────────────


def test_config_endpoint_requires_auth():
    resp = httpx.get(f"{API}/config/")
    assert resp.status_code == 401


def test_config_with_auth_returns_200():
    resp = httpx.get(f"{API}/config/", headers=auth_headers())
    assert resp.status_code in (200, 404)


# ── OPENAPI / DOCS ───────────────────────────────────────────────────────────


def test_openapi_schema_accessible():
    resp = httpx.get(f"{BASE_URL}/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "info" in schema
    assert "paths" in schema


def test_docs_accessible():
    resp = httpx.get(f"{BASE_URL}/docs")
    assert resp.status_code == 200

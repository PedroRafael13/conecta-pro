"""
Integration tests for critical Conecta PRO endpoints.
Uses real HTTP calls against running server (127.0.0.1:8080) — no mocks.
Validates: auth, GED, CRM, REST aliases, status_code=201 deployment.
"""

import subprocess

import httpx
import pytest

BASE_URL = "http://127.0.0.1:8080"
API = f"{BASE_URL}/api/v1"

_token: str = ""


def get_token() -> str:
    global _token
    if not _token:
        resp = httpx.post(
            f"{API}/auth/login",
            data={"username": "admin@conectapro.com.br", "password": "admin123"},  # pragma: allowlist secret
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        assert resp.status_code == 200, f"Login failed: {resp.status_code}"
        _token = resp.json()["access_token"]
    return _token


def auth() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}


# ── 1. HEALTH ──────────────────────────────────────────────────────────────


def test_health_returns_200():
    resp = httpx.get(f"{BASE_URL}/health", headers=auth(), timeout=5)
    assert resp.status_code == 200


# ── 2. AUTH ────────────────────────────────────────────────────────────────


def test_login_returns_bearer_token():
    resp = httpx.post(
        f"{API}/auth/login",
        data={"username": "admin@conectapro.com.br", "password": "admin123"},  # pragma: allowlist secret
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body.get("token_type", "").lower() == "bearer"


def test_login_wrong_password_returns_401_or_422():
    resp = httpx.post(
        f"{API}/auth/login",
        data={"username": "admin@conectapro.com.br", "password": "errado123"},  # pragma: allowlist secret
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    # 429 = rate limit ativo (também é "bloqueado" — credenciais rejeitadas)
    assert resp.status_code in (401, 422, 429), f"Got {resp.status_code}"


def test_protected_endpoint_without_token_returns_401():
    resp = httpx.get(f"{API}/auth/me", timeout=5)
    assert resp.status_code == 401


def test_auth_me_with_valid_token():
    resp = httpx.get(f"{API}/auth/me", headers=auth(), timeout=5)
    assert resp.status_code == 200
    body = resp.json()
    assert "email" in body or "id" in body


# ── 3. GED ─────────────────────────────────────────────────────────────────


def test_ged_documents_list():
    resp = httpx.get(f"{API}/ged/documents", headers=auth(), timeout=10)
    assert resp.status_code == 200
    assert isinstance(resp.json(), (list, dict))


def test_ged_folders_list():
    resp = httpx.get(f"{API}/ged/folders", headers=auth(), timeout=10)
    assert resp.status_code == 200


def test_ged_dashboard():
    resp = httpx.get(f"{API}/ged/dashboard", headers=auth(), timeout=10)
    assert resp.status_code == 200


def test_ged_document_tags():
    resp = httpx.get(f"{API}/ged/document-tags", headers=auth(), timeout=10)
    assert resp.status_code == 200


# ── 4. REST ALIASES — backward compat paths must still work (Skill 03) ──────


def test_ged_expired_verb_path_works():
    """GET /expired/list must keep returning 200 for backward compat."""
    resp = httpx.get(f"{API}/ged/documents/expired/list", headers=auth(), timeout=10)
    assert resp.status_code == 200


def test_ged_owner_shares_verb_path_works():
    resp = httpx.get(f"{API}/ged/document-shares/owner/list", headers=auth(), timeout=10)
    assert resp.status_code == 200


def test_ged_signer_list_verb_path_works():
    resp = httpx.get(f"{API}/ged/document-signatures/signer/list", headers=auth(), timeout=10)
    assert resp.status_code == 200


# ── 5. CRM ─────────────────────────────────────────────────────────────────


def test_crm_contacts_list():
    resp = httpx.get(f"{API}/crm/contacts/", headers=auth(), timeout=10)
    assert resp.status_code == 200


# ── 6. CONFIG AUTH ─────────────────────────────────────────────────────────


def test_config_without_auth_blocked():
    resp = httpx.get(f"{API}/config/system", timeout=5)
    assert resp.status_code in (401, 403)


def test_config_with_auth_accessible():
    resp = httpx.get(f"{API}/config/system", headers=auth(), timeout=10)
    assert resp.status_code in (200, 404)


# ── 7. PRODUCTION SECURITY ─────────────────────────────────────────────────


def test_openapi_json_disabled_in_production():
    """OpenAPI spec must be disabled in production (ENVIRONMENT=production)."""
    resp = httpx.get(f"{BASE_URL}/openapi.json", timeout=5)
    assert resp.status_code == 404, (
        f"openapi.json must be 404 in production. Got {resp.status_code} — check ENVIRONMENT setting."
    )


def test_unknown_route_returns_404():
    resp = httpx.get(f"{API}/rota-inexistente-xyz-123", headers=auth(), timeout=5)
    assert resp.status_code == 404


def test_wrong_method_on_get_endpoint_returns_405():
    resp = httpx.post(f"{BASE_URL}/health", headers=auth(), timeout=5)
    assert resp.status_code == 405


# ── 8. SKILL 03 METRIC — status_code=201 count ─────────────────────────────


def test_at_least_198_status_code_201_in_container():
    """
    Core Skill 03 metric: >=198 POST decorators must have status_code=201.
    Verified via grep in the running container.
    """
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "docker",
            "exec",
            "conecta-pro-backend",
            "bash",
            "-c",
            "grep -rn 'status_code=201' /app/modules/ 2>/dev/null | wc -l",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    count = int(result.stdout.strip())
    assert count >= 198, (
        f"Expected >=198 status_code=201 decorators in /app/modules/, got {count}. "
        "Skill 03 fix may not be deployed in the container."
    )

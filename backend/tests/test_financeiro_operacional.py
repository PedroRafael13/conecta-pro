"""
Testes de integração — Financeiro + Operacional + CRM + Segurança
Conecta PRO ERP — chamadas HTTP reais, sem mocks.
"""

import httpx
import pytest

BASE = "http://127.0.0.1:8080/api/v1"

_token: str = ""


def get_token() -> str:
    global _token
    if not _token:
        r = httpx.post(
            f"{BASE}/auth/login",
            data={"username": "jjesus@conectamais.pro", "password": "Jordan0612"},  # pragma: allowlist secret
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        assert r.status_code == 200, f"Login failed: {r.status_code}"
        _token = r.json()["access_token"]
    return _token


def h() -> dict:
    return {"Authorization": f"Bearer {get_token()}"}


# ── FINANCEIRO ────────────────────────────────────────────────────────────────


def test_fin_bi_dashboard_200():
    r = httpx.get(f"{BASE}/financial/bi/dashboard", headers=h(), timeout=10)
    assert r.status_code == 200


def test_fin_contracts_200():
    r = httpx.get(f"{BASE}/financial/contracts", headers=h(), timeout=10)
    assert r.status_code == 200


def test_fin_sem_token_401():
    r = httpx.get(f"{BASE}/financial/contracts", timeout=5)
    assert r.status_code == 401


def test_fin_contratos_paginado():
    r = httpx.get(f"{BASE}/financial/contracts?page_size=5", headers=h(), timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, (list, dict))


def test_fin_tem_contratos_reais():
    r = httpx.get(f"{BASE}/financial/contracts?page_size=50", headers=h(), timeout=10)
    assert r.status_code == 200
    body = r.json()
    items = body.get("items", body) if isinstance(body, dict) else body
    assert len(items) >= 5, f"Esperado 5+ contratos, encontrado {len(items)}"


# ── OPERACIONAL ───────────────────────────────────────────────────────────────


def test_op_posts_200():
    r = httpx.get(f"{BASE}/operacional/posts/", headers=h(), timeout=10)
    assert r.status_code == 200


def test_op_posts_sem_token_401():
    r = httpx.get(f"{BASE}/operacional/posts/", timeout=5)
    assert r.status_code == 401


def test_op_posts_paginado():
    r = httpx.get(f"{BASE}/operacional/posts/?page_size=5", headers=h(), timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "total" in body


def test_op_tem_postos_cadastrados():
    r = httpx.get(f"{BASE}/operacional/posts/?page_size=100", headers=h(), timeout=10)
    assert r.status_code == 200
    total = r.json().get("total", 0)
    assert total >= 10, f"Esperado 10+ postos, encontrado {total}"


def test_op_scales_200():
    r = httpx.get(f"{BASE}/operacional/scales/", headers=h(), timeout=10)
    assert r.status_code == 200


def test_op_allocations_200():
    r = httpx.get(f"{BASE}/operacional/allocations/", headers=h(), timeout=10)
    assert r.status_code == 200


def test_op_occurrences_200():
    r = httpx.get(f"{BASE}/operacional/occurrences/", headers=h(), timeout=10)
    assert r.status_code == 200


# ── CRM ───────────────────────────────────────────────────────────────────────


def test_crm_clients_200():
    r = httpx.get(f"{BASE}/crm/clients", headers=h(), timeout=10)
    assert r.status_code == 200


def test_crm_clients_sem_token_401():
    r = httpx.get(f"{BASE}/crm/clients", timeout=5)
    assert r.status_code == 401


def test_crm_tem_clientes_reais():
    r = httpx.get(f"{BASE}/crm/clients?page_size=50", headers=h(), timeout=10)
    assert r.status_code == 200
    body = r.json()
    total = body.get("total", len(body.get("items", body)))
    assert total >= 10, f"Esperado 10+ clientes, encontrado {total}"


def test_crm_leads_200():
    r = httpx.get(f"{BASE}/crm/leads", headers=h(), timeout=10)
    assert r.status_code == 200


def test_crm_contracts_200():
    r = httpx.get(f"{BASE}/crm/contracts", headers=h(), timeout=10)
    assert r.status_code == 200


# ── LICITAÇÕES ────────────────────────────────────────────────────────────────


def test_bidding_tenders_200():
    r = httpx.get(f"{BASE}/bidding/tenders", headers=h(), timeout=10)
    assert r.status_code == 200


def test_bidding_documents_200():
    r = httpx.get(f"{BASE}/bidding/documents", headers=h(), timeout=10)
    assert r.status_code == 200


# ── ANALYTICS + LGPD ──────────────────────────────────────────────────────────


def test_analytics_executive_dashboard_200():
    r = httpx.get(f"{BASE}/analytics/executive/dashboard", headers=h(), timeout=10)
    assert r.status_code == 200


def test_analytics_churn_200():
    r = httpx.get(f"{BASE}/analytics/churn/analytics", headers=h(), timeout=10)
    assert r.status_code == 200


def test_lgpd_audit_logs_200():
    r = httpx.get(f"{BASE}/security/lgpd/audit/logs", headers=h(), timeout=10)
    assert r.status_code == 200


def test_lgpd_sem_token_401():
    r = httpx.get(f"{BASE}/security/lgpd/audit/logs", timeout=5)
    assert r.status_code == 401


# ── CONFIG ────────────────────────────────────────────────────────────────────


def test_config_tenants_200():
    r = httpx.get(f"{BASE}/config/tenants", headers=h(), timeout=10)
    assert r.status_code == 200


def test_config_system_200():
    r = httpx.get(f"{BASE}/config/system", headers=h(), timeout=10)
    assert r.status_code == 200


# ── SEGURANÇA — 8 ENDPOINTS CRÍTICOS SEM TOKEN ───────────────────────────────


def test_seg_todos_criticos_bloqueados_sem_token():
    """Nenhum endpoint crítico deve retornar 200 sem autenticação."""
    endpoints = [
        f"{BASE}/people-management/hr/employees",
        f"{BASE}/financial/contracts",
        f"{BASE}/operacional/posts/",
        f"{BASE}/crm/clients",
        f"{BASE}/ged/documents",
        f"{BASE}/security/lgpd/audit/logs",
        f"{BASE}/config/tenants",
        f"{BASE}/analytics/executive/dashboard",
    ]
    expostos = [ep for ep in endpoints if httpx.get(ep, timeout=5).status_code == 200]
    assert len(expostos) == 0, f"Endpoints expostos sem auth: {expostos}"

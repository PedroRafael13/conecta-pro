"""Testes de integração — FASE 4 BLOCO 3 / T2 (§27.8 — 10 cenários).

Usa TestClient (sync) + dependency_overrides para auth.
Banco real via SyncSessionLocal (sem mocks de DB).
Inclui teste 🔴 de regressão do BUG 7 (endpoint sem auth → 401).
"""

import time
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from core.database.session import SyncSessionLocal

MES_REF_VALIDO = "03.2026"


@pytest.fixture(scope="module")
def app_production():
    from main_production import app

    return app


@pytest.fixture(scope="module")
def client(app_production):
    """TestClient SEM auth — para testar regressão BUG 7."""
    return TestClient(app_production, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def client_auth(app_production):
    """TestClient COM auth override."""
    from core.auth.dependencies import get_current_user

    def _mock_user():
        return {"id": "test-user", "email": "test@conectamais.pro", "role": "admin"}

    app_production.dependency_overrides[get_current_user] = _mock_user
    yield TestClient(app_production, raise_server_exceptions=False)
    app_production.dependency_overrides.clear()


@pytest.fixture(scope="module")
def condominio_id_ideal_flores() -> UUID:
    db = SyncSessionLocal()
    row = db.execute(text("SELECT id FROM condominios WHERE nome_normalizado='ideal_flores'")).fetchone()
    db.close()
    assert row, "ideal_flores não encontrado — rodar BLOCO 1 seed"
    return UUID(str(row[0]))


@pytest.fixture(scope="module")
def condominio_id_escritorio() -> UUID:
    db = SyncSessionLocal()
    row = db.execute(text("SELECT id FROM condominios WHERE nome_normalizado='escritorio'")).fetchone()
    db.close()
    assert row, "escritorio não encontrado"
    return UUID(str(row[0]))


# ============================================================================
# Cenário 1 — GET /completude sem auth → 401 (TESTE 🔴 BUG 7)
# ============================================================================
def test_completude_sem_auth_retorna_401(client, condominio_id_ideal_flores):
    resp = client.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 401, f"BUG 7 REGRESSÃO — endpoint retornou {resp.status_code} sem auth"


def test_lote_sem_auth_retorna_401(client):
    resp = client.get("/api/v1/gedeon/kits/lote", params={"mes_ref": MES_REF_VALIDO})
    assert resp.status_code == 401, f"BUG 7 REGRESSÃO — /lote retornou {resp.status_code} sem auth"


# ============================================================================
# Cenário 2 — mes_ref inválido → 400 ou 422
# ============================================================================
def test_completude_mes_ref_invalido_retorna_400_ou_422(client_auth, condominio_id_ideal_flores):
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": "2026-03"},
    )
    assert resp.status_code in (400, 422), f"Esperado 400/422, foi {resp.status_code}"


# ============================================================================
# Cenário 3 — UUID inexistente → 404
# ============================================================================
def test_completude_condominio_inexistente_retorna_404(client_auth):
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{uuid4()}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 404, f"Esperado 404, foi {resp.status_code}"


# ============================================================================
# Cenário 4 — UUID mal formatado → 422
# ============================================================================
def test_completude_uuid_invalido_retorna_422(client_auth):
    resp = client_auth.get(
        "/api/v1/gedeon/kits/completude/not-a-uuid",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 422, f"Esperado 422, foi {resp.status_code}"


# ============================================================================
# Cenário 5 — kit_mensal retorna CompletudeKit válido
# ============================================================================
def test_completude_kit_mensal_retorna_200_valido(client_auth, condominio_id_ideal_flores):
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 200, f"Esperado 200, foi {resp.status_code}: {resp.text}"
    body = resp.json()

    for field in (
        "condominio_id",
        "condominio_nome",
        "tipo_servico",
        "mes_ref",
        "gerado_em",
        "docs_presentes",
        "docs_faltantes",
        "metricas",
    ):
        assert field in body, f"Campo '{field}' ausente no response"

    m = body["metricas"]
    assert set(m.keys()) == {
        "total_esperado",
        "total_presente_confirmado",
        "total_presente_pendente_revisao",
        "total_faltante",
        "pct_completude_confirmada",
        "pct_completude_total",
    }, f"Campos de metricas divergem: {set(m.keys())}"

    assert body["tipo_servico"] == "kit_mensal"
    assert m["total_esperado"] == 32


# ============================================================================
# Cenário 6 — administrativo → total_esperado=0
# ============================================================================
def test_completude_administrativo_kit_vazio(client_auth, condominio_id_escritorio):
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_escritorio}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tipo_servico"] == "administrativo"
    assert body["metricas"]["total_esperado"] == 0
    assert body["docs_presentes"] == []
    assert body["docs_faltantes"] == []


# ============================================================================
# Cenário 7 — /lote retorna 11 condomínios
# ============================================================================
def test_lote_retorna_11_condominios(client_auth):
    resp = client_auth.get("/api/v1/gedeon/kits/lote", params={"mes_ref": MES_REF_VALIDO})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 11, f"Esperado 11 condomínios, foi {len(body)}"


# ============================================================================
# Cenário 8 — /lote mes_ref inválido → 400 ou 422
# ============================================================================
def test_lote_mes_ref_invalido_retorna_400_ou_422(client_auth):
    resp = client_auth.get("/api/v1/gedeon/kits/lote", params={"mes_ref": "abril-2026"})
    assert resp.status_code in (400, 422)


# ============================================================================
# Cenário 9 — Response JSON valida com Pydantic (§27.4 snapshot)
# ============================================================================
def test_completude_response_valida_pydantic(client_auth, condominio_id_ideal_flores):
    from modules.gedeon.schemas.kit_completude import CompletudeKitResponse

    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 200
    parsed = CompletudeKitResponse.model_validate(resp.json())
    assert parsed.condominio_nome == "IDEAL FLORES"
    assert set(CompletudeKitResponse.model_fields.keys()) == {
        "condominio_id",
        "condominio_nome",
        "tipo_servico",
        "mes_ref",
        "gerado_em",
        "docs_presentes",
        "docs_faltantes",
        "metricas",
    }


# ============================================================================
# Cenário 10 — Performance (<500ms / <3s)
# ============================================================================
def test_completude_performance_abaixo_500ms(client_auth, condominio_id_ideal_flores):
    t0 = time.time()
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    elapsed_ms = (time.time() - t0) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < 500, f"Excedeu 500ms: {elapsed_ms:.1f}ms"


def test_lote_performance_abaixo_3s(client_auth):
    t0 = time.time()
    resp = client_auth.get("/api/v1/gedeon/kits/lote", params={"mes_ref": MES_REF_VALIDO})
    elapsed_s = time.time() - t0
    assert resp.status_code == 200
    assert elapsed_s < 3.0, f"Excedeu 3s: {elapsed_s:.2f}s"

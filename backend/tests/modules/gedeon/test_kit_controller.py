"""Testes de integração — FASE 4 BLOCO 3 / T2 (§27.8 — 10 cenários).

Usa TestClient + fixture de usuário autenticado para cobrir §27.5 (erros).
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
    """TestClient sem override de auth → exige token real (teste 🔴 possível)."""
    return TestClient(app_production)


@pytest.fixture(scope="module")
def client_auth(app_production):
    """TestClient com auth override (bypassa Depends(get_current_user))."""
    from core.auth.dependencies import get_current_user

    def _override():
        return {"id": "test-user", "email": "test@conectamais.pro"}

    app_production.dependency_overrides[get_current_user] = _override
    yield TestClient(app_production)
    app_production.dependency_overrides.clear()


@pytest.fixture(scope="module")
def condominio_id_ideal_flores() -> UUID:
    db = SyncSessionLocal()
    row = db.execute(text("SELECT id FROM condominios WHERE nome_normalizado='ideal_flores'")).fetchone()
    db.close()
    assert row, "ideal_flores não encontrado no DB — rodar BLOCO 1 seed"
    return UUID(str(row[0]))


@pytest.fixture(scope="module")
def condominio_id_escritorio() -> UUID:
    db = SyncSessionLocal()
    row = db.execute(text("SELECT id FROM condominios WHERE nome_normalizado='escritorio'")).fetchone()
    db.close()
    assert row
    return UUID(str(row[0]))


# ============================================================================
# Cenário 1 — §27.8 — GET /completude sem auth → 401 (TESTE 🔴 BUG 7)
# ============================================================================
def test_completude_sem_auth_retorna_401(client, condominio_id_ideal_flores):
    resp = client.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 401, f"BUG 7 REGRESSÃO — endpoint retornou {resp.status_code} sem auth"


def test_lote_sem_auth_retorna_401(client):
    resp = client.get("/api/v1/gedeon/kits/lote", params={"mes_ref": MES_REF_VALIDO})
    assert resp.status_code == 401


# ============================================================================
# Cenário 2 — mes_ref inválido → 400
# ============================================================================
def test_completude_mes_ref_invalido_retorna_400(client_auth, condominio_id_ideal_flores):
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": "2026-03"},
    )
    # Pode ser 400 (service-level) ou 422 (Pydantic Query regex)
    assert resp.status_code in (400, 422)


# ============================================================================
# Cenário 3 — UUID inexistente → 404
# ============================================================================
def test_completude_condominio_inexistente_retorna_404(client_auth):
    fake = uuid4()
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{fake}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 404


# ============================================================================
# Cenário 4 — UUID mal formatado → 422 (FastAPI path validation)
# ============================================================================
def test_completude_uuid_invalido_retorna_422(client_auth):
    resp = client_auth.get(
        "/api/v1/gedeon/kits/completude/not-a-uuid",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 422


# ============================================================================
# Cenário 5 — kit_mensal retorna CompletudeKit válido
# ============================================================================
def test_completude_kit_mensal_retorna_200_valido(client_auth, condominio_id_ideal_flores):
    resp = client_auth.get(
        f"/api/v1/gedeon/kits/completude/{condominio_id_ideal_flores}",
        params={"mes_ref": MES_REF_VALIDO},
    )
    assert resp.status_code == 200
    body = resp.json()

    # §27.4 — campos obrigatórios
    assert "condominio_id" in body
    assert "condominio_nome" in body
    assert "tipo_servico" in body
    assert "mes_ref" in body
    assert "gerado_em" in body
    assert "docs_presentes" in body
    assert "docs_faltantes" in body
    assert "metricas" in body

    # Métricas — 6 campos
    m = body["metricas"]
    assert set(m.keys()) == {
        "total_esperado",
        "total_presente_confirmado",
        "total_presente_pendente_revisao",
        "total_faltante",
        "pct_completude_confirmada",
        "pct_completude_total",
    }
    assert body["tipo_servico"] == "kit_mensal"
    # total_esperado dinâmico (§35.4): mínimo 17 (IF com 0 func)
    assert m["total_esperado"] >= 17


# ============================================================================
# Cenário 6 — administrativo retorna total_esperado=0
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
# Cenário 7 — /lote retorna array de 11 condomínios
# ============================================================================
def test_lote_retorna_array_11_condominios(client_auth):
    resp = client_auth.get("/api/v1/gedeon/kits/lote", params={"mes_ref": MES_REF_VALIDO})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 11


# ============================================================================
# Cenário 8 — /lote com mes_ref inválido → 400 ou 422
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
    # Valida schema
    parsed = CompletudeKitResponse.model_validate(resp.json())
    assert parsed.condominio_nome == "IDEAL FLORES"


# ============================================================================
# Cenário 10 — Performance
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

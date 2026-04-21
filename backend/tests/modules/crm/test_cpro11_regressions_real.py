"""
Testes de regressão CPRO11-Rodada1.5 — runtime real.

Cada teste valida um bug confirmado em produção via chamada real ao DB/HTTP.
Todos os 10 testes devem passar para o GATE FASE 4.
"""

import datetime
import os

import jwt
import pytest
import pytest_asyncio
from httpx import AsyncClient

_user_id_cache = None
_token_cache = None


# ============================================================
# Token JWT real (usa JWT_SECRET_KEY do ambiente)
# Token gerado UMA VEZ e cacheado para evitar loop issues
# ============================================================
def _get_sync_db():
    """Retorna engine síncrono para queries simples."""
    from core.database.session import sync_engine

    return sync_engine


def _run_sync_query(sql: str) -> list:
    """Executa query síncrona via psycopg2."""
    from sqlalchemy import text as sa_text

    engine = _get_sync_db()
    with engine.connect() as conn:
        result = conn.execute(sa_text(sql))
        return [list(row) for row in result.fetchall()]


def _get_token() -> str:
    global _token_cache, _user_id_cache
    if _token_cache:
        return _token_cache
    secret = os.environ.get("JWT_SECRET_KEY", "")
    if not secret:
        pytest.skip("JWT_SECRET_KEY não disponível")
    rows = _run_sync_query("SELECT id, email FROM users WHERE email='jjesus@conectamais.pro' LIMIT 1")
    if not rows:
        pytest.skip("usuário jjesus@conectamais.pro não encontrado")
    user_id = str(rows[0][0])
    email = rows[0][1]
    _user_id_cache = user_id
    payload = {
        "sub": user_id,
        "email": email,
        "type": "access",
        "role": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=4),
    }
    _token_cache = jwt.encode(payload, secret, algorithm="HS256")
    return _token_cache


# ============================================================
# Fixture: http_client contra servidor real (porta 8080)
# Evita event loop conflict do ASGITransport + asyncpg
# ============================================================
@pytest_asyncio.fixture
async def http_client():
    token = _get_token()
    async with AsyncClient(base_url="http://127.0.0.1:8080") as ac:
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac


# ============================================================
# TEST 1 — ContractStatus enum existe no PG
# ============================================================
def test_contractstatus_enum_exists_in_pg():
    """REG-01: O tipo enum 'contractstatus' deve existir no PostgreSQL."""
    rows = _run_sync_query("SELECT typname FROM pg_type WHERE typtype='e' AND typname='contractstatus'")
    assert len(rows) > 0, "PG type 'contractstatus' não encontrado"
    assert rows[0][0] == "contractstatus"


# ============================================================
# TEST 2 — ContractStatus values são lowercase
# ============================================================
def test_contractstatus_values_lowercase():
    """REG-02: Os valores do enum contractstatus devem ser lowercase (não UPPERCASE)."""
    rows = _run_sync_query(
        "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid WHERE t.typname='contractstatus'"
    )
    values = [r[0] for r in rows]
    assert len(values) > 0, "Nenhum valor encontrado no enum contractstatus"
    for v in values:
        assert v == v.lower(), f"Valor '{v}' no enum contractstatus não é lowercase"


# ============================================================
# TEST 3 — contracts/alerts retorna 200
# ============================================================
@pytest.mark.asyncio
async def test_contracts_alerts_endpoint_200(http_client: AsyncClient):
    """REG-03: GET /api/v1/crm/contracts/alerts deve retornar 200."""
    resp = await http_client.get("/api/v1/crm/contracts/alerts")  # real server
    assert resp.status_code == 200, f"contracts/alerts retornou {resp.status_code}: {resp.text[:300]}"


# ============================================================
# TEST 4 — contracts/templates retorna 200
# ============================================================
@pytest.mark.asyncio
async def test_contracts_templates_endpoint_200(http_client: AsyncClient):
    """REG-04: GET /api/v1/crm/contracts/templates deve retornar 200."""
    resp = await http_client.get("/api/v1/crm/contracts/templates")
    assert resp.status_code == 200, f"contracts/templates retornou {resp.status_code}: {resp.text[:300]}"


# ============================================================
# TEST 5 — proposals/templates routing correto (não conflita com /{id})
# ============================================================
@pytest.mark.asyncio
async def test_proposals_templates_routing(http_client: AsyncClient):
    """REG-05: GET /api/v1/crm/proposals/templates deve retornar 200, não 422 (path conflict)."""
    resp = await http_client.get("/api/v1/crm/proposals/templates")
    assert resp.status_code == 200, f"proposals/templates retornou {resp.status_code}: {resp.text[:300]}"


# ============================================================
# TEST 6 — DashboardKPIs tem todos os 6 campos P0
# ============================================================
@pytest.mark.asyncio
async def test_dashboard_kpis_all_fields_present(http_client: AsyncClient):
    """REG-06: GET /api/v1/crm/dashboard/kpis deve conter todos os campos P0."""
    resp = await http_client.get("/api/v1/crm/dashboard/kpis")
    assert resp.status_code == 200, f"dashboard/kpis retornou {resp.status_code}"
    data = resp.json()
    required_fields = [
        "clientes_total",
        "condominios_total",
        "mrr",
        "em_negociacao",
        "em_proposta",
        "leads_conversion_rate",
    ]
    for field in required_fields:
        assert field in data, f"Campo '{field}' ausente na resposta de dashboard/kpis"


# ============================================================
# TEST 7 — mrr nunca NaN
# ============================================================
@pytest.mark.asyncio
async def test_dashboard_kpis_mrr_never_nan(http_client: AsyncClient):
    """REG-07: O campo mrr não pode ser NaN ou None."""
    import math

    resp = await http_client.get("/api/v1/crm/dashboard/kpis")
    assert resp.status_code == 200
    data = resp.json()
    mrr = data.get("mrr")
    assert mrr is not None, "mrr é None"
    assert not math.isnan(float(mrr)), "mrr é NaN"
    assert float(mrr) >= 0.0, f"mrr negativo: {mrr}"


# ============================================================
# TEST 8 — clientes_total positivo (há clientes no banco)
# ============================================================
@pytest.mark.asyncio
async def test_dashboard_kpis_clientes_total_positive(http_client: AsyncClient):
    """REG-08: clientes_total deve ser > 0 pois há clientes cadastrados."""
    resp = await http_client.get("/api/v1/crm/dashboard/kpis")
    assert resp.status_code == 200
    data = resp.json()
    clientes = data.get("clientes_total", 0)
    assert clientes > 0, f"clientes_total={clientes} — esperado > 0 (há clientes ativos no banco)"


# ============================================================
# TEST 9 — conversion_rate quando há leads convertidos
# ============================================================
def test_conversion_rate_when_has_converted_leads():
    """REG-09: leads_conversion_rate > 0 quando há leads com status won/converted."""
    from unittest.mock import MagicMock

    from modules.crm.models.lead import Lead, LeadStatus
    from modules.crm.services.dashboard_service import DashboardService

    service = DashboardService()
    # Simula leads won
    mock_lead_won = MagicMock(spec=Lead)
    mock_lead_won.status = LeadStatus.WON
    mock_lead_won.created_at = MagicMock()
    mock_lead_won.created_at.date.return_value = MagicMock()
    mock_lead_won.created_at.date.return_value.__ge__ = MagicMock(return_value=False)
    mock_lead_won.created_at.date.return_value.__eq__ = MagicMock(return_value=False)

    mock_lead_new = MagicMock(spec=Lead)
    mock_lead_new.status = LeadStatus.NEW
    mock_lead_new.created_at = MagicMock()
    mock_lead_new.created_at.date.return_value = MagicMock()
    mock_lead_new.created_at.date.return_value.__ge__ = MagicMock(return_value=False)
    mock_lead_new.created_at.date.return_value.__eq__ = MagicMock(return_value=False)

    leads = [mock_lead_won] * 5 + [mock_lead_new] * 5

    kpis = service.calculate_kpis(leads=leads, opportunities=[], proposals=[], commissions=[])
    assert kpis.leads_conversion_rate > 0, f"leads_conversion_rate={kpis.leads_conversion_rate} — esperado > 0"


# ============================================================
# TEST 10 — clients endpoint retorna endereco_texto como string
# ============================================================
@pytest.mark.asyncio
async def test_clients_endpoint_returns_endereco_texto(http_client: AsyncClient):
    """REG-10: GET /api/v1/crm/clients deve retornar campo endereco_texto como string."""
    resp = await http_client.get("/api/v1/crm/clients")
    assert resp.status_code == 200, f"clients retornou {resp.status_code}: {resp.text[:300]}"
    data = resp.json()
    items = data if isinstance(data, list) else data.get("items", data.get("data", []))
    if not items:
        pytest.skip("Nenhum cliente no banco para validar endereco_texto")
    for item in items[:3]:
        et = item.get("endereco_texto")
        if et is not None:
            assert isinstance(et, str), f"endereco_texto é {type(et).__name__}, esperado str: {et}"
        # Se None é aceitável — cliente sem endereço

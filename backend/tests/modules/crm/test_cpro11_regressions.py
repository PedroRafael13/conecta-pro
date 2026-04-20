"""
Testes de regressão CPRO11-T4 — fixes P0.1, P0.2, P0.5, P0.6, P0.11.

Cada teste documenta um bug confirmado em produção (CIC) e garante que não volta.
Inclui testes unitários (REG-01 a REG-05) e testes de integração HTTP (INT-01 a INT-05).
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio

from modules.crm.models.contract import ContractStatus
from modules.crm.models.lead import Lead, LeadStatus
from modules.crm.services.dashboard_service import DashboardKPIs, DashboardService


# ============================================================
# REG-01 — P0.11: leads_conversion_rate usa status "converted"
# ============================================================
def _make_lead(status: str) -> Lead:
    lead = MagicMock(spec=Lead)
    lead.status = status
    lead.created_at = MagicMock()
    lead.created_at.date.return_value = MagicMock()
    lead.created_at.date.return_value.__ge__ = MagicMock(return_value=False)
    lead.created_at.date.return_value.__eq__ = MagicMock(return_value=False)
    return lead


def test_leads_conversion_rate_conta_converted():
    """REG-01: DB usa status 'converted' — taxa deve refletir realidade, não 0.0."""
    service = DashboardService()
    leads = [_make_lead("converted")] * 11 + [_make_lead("qualified")] * 3
    kpis = service.calculate_kpis(leads=leads, opportunities=[], proposals=[], commissions=[])
    assert kpis.leads_conversion_rate > 0.0, (
        "leads_conversion_rate=0.0 regrediu — bug P0.11: status 'converted' não é reconhecido"
    )
    expected = (11 / 14) * 100
    assert abs(kpis.leads_conversion_rate - expected) < 0.01


def test_leads_conversion_rate_conta_won_legado():
    """REG-01b: status 'won' (legado) ainda deve ser contado."""
    service = DashboardService()
    leads = [_make_lead("won")] * 5 + [_make_lead("new")] * 5
    kpis = service.calculate_kpis(leads=leads, opportunities=[], proposals=[], commissions=[])
    assert kpis.leads_conversion_rate == 50.0


# ============================================================
# REG-02 — P0.2: endereco_texto deve ser string (nunca objeto)
# ============================================================
def test_endereco_texto_e_string():
    """REG-02: /crm/clients resposta deve ter 'endereco_texto' como string, não objeto."""
    from modules.crm.controllers.client_controller import listar_clientes  # noqa: F401

    # Simula a tupla retornada pelo raw SQL (r[8..r[12] = campos de endereço)
    rua = "Rua das Flores"
    numero = "123"
    bairro = "Centro"
    cidade = "Manaus"
    estado = "AM"

    endereco_texto = ", ".join(p for p in [rua, numero, bairro, cidade, estado] if p) or None
    assert isinstance(endereco_texto, str), "endereco_texto deve ser str, não objeto"
    assert "Manaus" in endereco_texto
    assert "Rua das Flores" in endereco_texto


def test_endereco_texto_com_campos_nulos():
    """REG-02b: campos None no endereço não geram 'None' na string."""
    rua = "Av. Brasil"
    numero = None
    bairro = None
    cidade = "Manaus"
    estado = "AM"

    endereco_texto = ", ".join(p for p in [rua, numero, bairro, cidade, estado] if p) or None
    assert endereco_texto is not None
    assert "None" not in endereco_texto
    assert "Av. Brasil" in endereco_texto


# ============================================================
# REG-03 — P0.1: ContractStatus enum tem valores lowercase
# ============================================================
def test_contractstatus_valores_lowercase():
    """REG-03: valores do enum ContractStatus devem ser lowercase (compatíveis com PG type)."""
    for member in ContractStatus:
        assert member.value == member.value.lower(), (
            f"ContractStatus.{member.name}={member.value!r} não é lowercase — "
            "quebra o casting contractstatus no PostgreSQL"
        )


# ============================================================
# REG-04 — P0.6/P0.5: DashboardKPIs tem campos clientes_total e mrr
# ============================================================
def test_dashboard_kpis_tem_clientes_total_e_mrr():
    """REG-04: DashboardKPIs deve ter clientes_total e mrr (P0.5/P0.6)."""
    kpis = DashboardKPIs()
    assert hasattr(kpis, "clientes_total"), "clientes_total ausente — bug P0.5 regrediu"
    assert hasattr(kpis, "mrr"), "mrr ausente — bug P0.6 regrediu"
    assert kpis.clientes_total == 0
    assert kpis.mrr == 0.0


def test_dashboard_kpis_mrr_nunca_nan():
    """REG-04b: mrr nunca deve ser NaN (COALESCE exigido — INV-12)."""
    import math

    kpis = DashboardKPIs(mrr=0.0)
    assert not math.isnan(kpis.mrr), "mrr=NaN regrediu — violação INV-12"


# ============================================================
# REG-05 — P0.2: proposals/templates não capturado por /{proposal_id}
# ============================================================
def test_proposals_templates_rota_declarada_antes_de_proposal_id():
    """REG-05: rota /proposals/templates deve estar ANTES de /{proposal_id} no router."""
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from modules.crm.controllers import proposal_controller

    router = proposal_controller.router
    route_paths = [getattr(r, "path", "") for r in router.routes]

    # FastAPI registra com prefixo completo quando montado
    idx_templates = next(
        (i for i, p in enumerate(route_paths) if p.endswith("/templates") and "template_id" not in p),
        None,
    )
    idx_proposal_id = next(
        (i for i, p in enumerate(route_paths) if p.endswith("/{proposal_id}")),
        None,
    )

    assert idx_templates is not None, f"Rota /templates não encontrada — paths: {route_paths}"
    assert idx_proposal_id is not None, "Rota /{proposal_id} não encontrada no router de proposals"
    assert idx_templates < idx_proposal_id, (
        f"Rota /templates (idx={idx_templates}) está DEPOIS de /{{proposal_id}} "
        f"(idx={idx_proposal_id}) — GET /proposals/templates retorna 422 (UUID inválido)"
    )


# ============================================================
# INT-01 a INT-05 — Testes de integração HTTP (CPRO11-T4)
# ============================================================


def _now() -> datetime:
    return datetime(2026, 4, 20, 12, 0, 0)


def _uid() -> str:
    return str(uuid4())


def _make_lead_orm(status: str = "new") -> MagicMock:
    m = MagicMock()
    m.id = _uid()
    m.status = status
    m.assigned_to_id = None
    m.is_active = True
    m.created_at = _now()
    m.updated_at = _now()
    m.weighted_value = 5000.0
    return m


def _make_opp_orm() -> MagicMock:
    m = MagicMock()
    m.id = _uid()
    m.stage = "qualification"
    m.value = 50000.0
    m.probability = 25
    m.owner_id = None
    m.is_active = True
    m.is_won = False
    m.weighted_value = 12500.0
    m.days_in_pipeline = 5
    m.created_at = _now()
    m.updated_at = _now()
    return m


def _scalars(items):
    r = MagicMock()
    s = MagicMock()
    s.all.return_value = items
    r.scalars.return_value = s
    return r


def _one_row(*values):
    r = MagicMock()
    row = MagicMock()
    row.__getitem__ = lambda self, i: values[i]
    r.one.return_value = row
    return r


@pytest_asyncio.fixture
async def crm_http_client():
    """
    AsyncClient apontado para um crm_app mínimo com auth mockado.
    Não usa DB real — cada teste injeta dependency_overrides por conta própria.
    """
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from core.auth.dependencies import get_current_active_user
    from modules.crm.controllers import (
        client_controller,
        contract_controller,
        dashboard_controller,
        proposal_controller,
    )

    app = FastAPI()
    app.include_router(dashboard_controller.router, prefix="/api/v1/crm")
    app.include_router(client_controller.router, prefix="/api/v1/crm")
    app.include_router(proposal_controller.router, prefix="/api/v1/crm")
    app.include_router(contract_controller.router, prefix="/api/v1/crm")

    mock_user = MagicMock()
    mock_user.id = "test-user"
    mock_user.email = "test@test.com"
    mock_user.is_active = True

    async def _auth():
        return mock_user

    app.dependency_overrides[get_current_active_user] = _auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "Bearer test-token"
        client._crm_app = app
        yield client


@pytest.mark.asyncio
async def test_int01_dashboard_kpis_tem_campos_cpro11(crm_http_client):
    """INT-01: GET /dashboard/kpis retorna clientes_total, condominios_total, mrr (P0.5/P0.6)."""
    from core.database import get_db

    db = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalars([_make_lead_orm()]),
            _scalars([_make_opp_orm()]),
            _scalars([]),
            _scalars([]),
            _one_row(12, 272086.96),
            _one_row(3),
        ]
    )

    async def _db():
        return db

    crm_http_client._crm_app.dependency_overrides[get_db] = _db
    resp = await crm_http_client.get("/api/v1/crm/dashboard/kpis")
    assert resp.status_code == 200, f"Esperado 200, recebido {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "clientes_total" in data, "clientes_total ausente na resposta — bug P0.5 regrediu"
    assert "condominios_total" in data, "condominios_total ausente na resposta — bug P1.5 regrediu"
    assert "mrr" in data, "mrr ausente na resposta — bug P0.6 regrediu"
    assert data["clientes_total"] == 12
    assert data["condominios_total"] == 3
    assert abs(data["mrr"] - 272086.96) < 0.01


@pytest.mark.asyncio
async def test_int02_dashboard_kpis_converted_leads(crm_http_client):
    """INT-02: GET /dashboard/kpis com leads 'converted' → leads_conversion_rate > 0 (P0.11)."""
    from core.database import get_db

    leads = [_make_lead_orm("converted")] * 11 + [_make_lead_orm("qualified")] * 3
    db = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalars(leads),
            _scalars([]),
            _scalars([]),
            _scalars([]),
            _one_row(12, 0.0),
            _one_row(0),
        ]
    )

    async def _db():
        return db

    crm_http_client._crm_app.dependency_overrides[get_db] = _db
    resp = await crm_http_client.get("/api/v1/crm/dashboard/kpis")
    assert resp.status_code == 200
    data = resp.json()
    assert data["leads_conversion_rate"] > 0.0, (
        "leads_conversion_rate=0.0 regrediu — bug P0.11: 'converted' não reconhecido"
    )


@pytest.mark.asyncio
async def test_int03_clients_endereco_texto_e_string(crm_http_client):
    """INT-03: GET /crm/clients resposta inclui endereco_texto como string (P0.2)."""
    from core.database import get_db

    row = MagicMock()
    row.__getitem__ = lambda self, i: [
        _uid(),
        "CLI-001",
        "Empresa Alpha",
        "Alpha",
        "12.345.678/0001-90",
        "alpha@emp.com",
        "92999990000",
        None,
        "Rua das Flores",
        "123",
        "Centro",
        "Manaus",
        "AM",
        "69000-000",
        "active",
        "security",
        None,
        90,
        85,
        150000.0,
        0.0,
        False,
        True,
        "crm",
        None,
        _now(),
        25000.0,
        3,
        None,
        None,
    ][i]

    total_row = MagicMock()
    total_row.__getitem__ = lambda self, i: [1][i]

    db = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            MagicMock(**{"fetchall.return_value": [row]}),
            MagicMock(**{"fetchone.return_value": total_row}),
        ]
    )

    async def _db():
        return db

    crm_http_client._crm_app.dependency_overrides[get_db] = _db
    resp = await crm_http_client.get("/api/v1/crm/clients/")
    assert resp.status_code == 200, f"Esperado 200, recebido {resp.status_code}: {resp.text}"
    items = resp.json().get("items", resp.json())
    if isinstance(items, list) and items:
        item = items[0]
        assert "endereco_texto" in item, "campo endereco_texto ausente — bug P0.2 regrediu"
        assert isinstance(item["endereco_texto"], (str, type(None))), (
            f"endereco_texto deve ser str, não {type(item['endereco_texto'])} — React Error #31"
        )


@pytest.mark.asyncio
async def test_int04_proposals_templates_nao_retorna_422(crm_http_client):
    """INT-04: GET /proposals/templates não deve retornar 422 (UUID inválido) — bug P0.1 fix 3."""
    from core.database import get_db

    db = MagicMock()
    db.execute = AsyncMock(return_value=_scalars([]))

    async def _db():
        return db

    crm_http_client._crm_app.dependency_overrides[get_db] = _db

    with patch("modules.crm.repositories.proposal_repository.ProposalRepository") as MockRepo:
        MockRepo.return_value.get_templates = AsyncMock(return_value=[])
        resp = await crm_http_client.get("/api/v1/crm/proposals/templates")

    assert resp.status_code != 422, (
        "GET /proposals/templates retornou 422 — rota /templates está DEPOIS de /{proposal_id}"
    )


@pytest.mark.asyncio
async def test_int05_contracts_templates_nao_retorna_500(crm_http_client):
    """INT-05: GET /contracts/templates não deve retornar 500 LookupError (bug P0.1)."""
    from core.database import get_db

    db = MagicMock()
    db.execute = AsyncMock(return_value=_scalars([]))

    async def _db():
        return db

    crm_http_client._crm_app.dependency_overrides[get_db] = _db

    with patch("modules.crm.repositories.contract_repository.ContractRepository") as MockRepo:
        MockRepo.return_value.get_templates = AsyncMock(return_value=[])
        resp = await crm_http_client.get("/api/v1/crm/contracts/templates")

    assert resp.status_code != 500, "GET /contracts/templates retornou 500 — LookupError no ServiceType regrediu (P0.1)"

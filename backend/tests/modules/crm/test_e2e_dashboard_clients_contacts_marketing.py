"""
Testes E2E para os submodulos Dashboard, Clients, Contacts/Activities e Marketing do CRM.

Endpoints testados:

DASHBOARD (12 endpoints, 14 testes):
    GET /api/v1/crm/dashboard/kpis                          → 200
    GET /api/v1/crm/dashboard/funnel                        → 200
    GET /api/v1/crm/dashboard/trends/leads                  → 200
    GET /api/v1/crm/dashboard/trends/sales                  → 200
    GET /api/v1/crm/dashboard/trends/commissions            → 200
    GET /api/v1/crm/dashboard/conversion-rates              → 200
    GET /api/v1/crm/dashboard/seller/{seller_id}/performance → 200
    GET /api/v1/crm/dashboard/top-performers                → 200
    GET /api/v1/crm/dashboard/charts/leads-by-status        → 200
    GET /api/v1/crm/dashboard/charts/opportunities-by-stage → 200
    GET /api/v1/crm/dashboard/charts/proposals-by-status    → 200
    GET /api/v1/crm/dashboard/charts/commissions-by-status  → 200

CLIENTS (3 endpoints, 5 testes):
    GET /api/v1/crm/clients/        → 200 lista + filtros
    GET /api/v1/crm/clients/resumo  → 200 resumo
    GET /api/v1/crm/clients/{id}    → 200 + 404

CONTACTS & ACTIVITIES (7 endpoints, 10 testes):
    GET    /api/v1/crm/contacts/              → 200
    POST   /api/v1/crm/contacts/              → 200
    DELETE /api/v1/crm/contacts/{contact_id} → 200
    GET    /api/v1/crm/activities/recent      → 200
    GET    /api/v1/crm/activities/            → 200
    POST   /api/v1/crm/activities/            → 200
    GET    /api/v1/crm/clients/{id}/360       → 200 + 404

MARKETING (8 endpoints, 12 testes):
    GET  /api/v1/marketing/campaigns/           → 200
    POST /api/v1/marketing/campaigns/           → 200
    PUT  /api/v1/marketing/campaigns/{id}       → 200
    GET  /api/v1/marketing/leads/               → 200 + filtros
    POST /api/v1/marketing/leads/               → 200
    POST /api/v1/marketing/leads/{id}/convert   → 200 + 404
    GET  /api/v1/marketing/leads/stats          → 200
    POST /api/v1/marketing/licitacao/convert-to-crm → 200

Estrategia de mock:
    - Todos os controllers usam get_db (dashboard) ou get_async_session (outros).
    - Cada teste atualiza crm_app.dependency_overrides[_get_db / _get_async_session]
      para injetar o mock correto antes de fazer a requisicao HTTP.
    - A app FastAPI minima (sem lifespan/Redis) evita hangs no startup.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Importar as dependencias de DB uma unica vez para uso nos overrides
from core.auth.dependencies import get_current_active_user
from core.database import get_async_session as _get_async_session
from core.database import get_db as _get_db

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime(2026, 3, 30, 12, 0, 0)


def _make_mock_user() -> MagicMock:
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@erp.com.br"
    user.role = "admin"
    user.is_active = True
    return user


# ---------------------------------------------------------------------------
# Mock builders — ORM objects para DashboardService (acessa atributos diretamente)
# ---------------------------------------------------------------------------


def _make_lead_orm(**kwargs) -> MagicMock:
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.status = kwargs.get("status", "new")
    m.assigned_to_id = kwargs.get("assigned_to_id")
    m.is_active = True
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = _now()
    m.weighted_value = 5000.0
    return m


def _make_opportunity_orm(**kwargs) -> MagicMock:
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.stage = kwargs.get("stage", "qualification")
    m.value = kwargs.get("value", 50000.0)
    m.probability = kwargs.get("probability", 25)
    m.owner_id = kwargs.get("owner_id")
    m.is_active = True
    m.is_won = kwargs.get("is_won", False)
    m.weighted_value = 12500.0
    m.days_in_pipeline = 10
    m.created_at = _now()
    m.updated_at = _now()
    return m


def _make_proposal_orm(**kwargs) -> MagicMock:
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.status = kwargs.get("status", "draft")
    m.total = kwargs.get("total", 30000.0)
    m.is_active = True
    m.created_at = _now()
    m.updated_at = _now()
    return m


def _make_commission_orm(**kwargs) -> MagicMock:
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.status = kwargs.get("status", "pending")
    m.final_commission = kwargs.get("final_commission", 2500.0)
    m.seller_id = kwargs.get("seller_id")
    m.is_active = True
    m.created_at = _now()
    m.updated_at = _now()
    return m


# ---------------------------------------------------------------------------
# Mock builders — DB sessions para Dashboard (usa select() + scalars())
# ---------------------------------------------------------------------------


def _scalars_result(items):
    """Cria resultado de db.execute() com .scalars().all()."""
    r = MagicMock()
    s = MagicMock()
    s.all.return_value = items
    r.scalars.return_value = s
    return r


def _db_dashboard(leads=None, opps=None, props=None, comms=None):
    """
    Session para endpoints de dashboard que chamam 4 queries sequenciais
    (leads, opportunities, proposals, commissions).
    """
    db = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalars_result(leads or []),
            _scalars_result(opps or []),
            _scalars_result(props or []),
            _scalars_result(comms or []),
        ]
    )
    return db


def _db_single(items):
    """Session para endpoints que fazem uma query."""
    db = MagicMock()
    db.execute = AsyncMock(return_value=_scalars_result(items))
    return db


def _db_triple(items1, items2, items3):
    """Session para endpoints que fazem 3 queries (leads+opps+comms)."""
    db = MagicMock()
    db.execute = AsyncMock(
        side_effect=[
            _scalars_result(items1),
            _scalars_result(items2),
            _scalars_result(items3),
        ]
    )
    return db


# ---------------------------------------------------------------------------
# Mock builders — SQL text() results para clients/contacts/marketing
# (usam db.execute(text(...)) com fetchall() / fetchone() / scalar())
# ---------------------------------------------------------------------------


def _text_list(rows):
    r = MagicMock()
    r.fetchall.return_value = rows
    return r


def _text_one(row):
    r = MagicMock()
    r.fetchone.return_value = row
    return r


def _scalar_result(value):
    r = MagicMock()
    r.scalar.return_value = value
    return r


def _make_row_client():
    row = MagicMock()
    row.__getitem__ = lambda self, idx: [
        _uid(),  # 0  id
        "CLI-001",  # 1  code
        "Empresa Alpha",  # 2  name
        "Alpha",  # 3  trading_name
        "12.345.678/0001-90",  # 4  document_number
        "alpha@emp.com",  # 5  email
        "92999990000",  # 6  phone
        None,  # 7  mobile
        "Av Principal",  # 8  address_street
        "100",  # 9  address_number
        "Centro",  # 10 address_neighborhood
        "Manaus",  # 11 address_city
        "AM",  # 12 address_state
        "69000-000",  # 13 address_zipcode
        "active",  # 14 status
        "security",  # 15 segment
        None,  # 16 contract_start_date
        90,  # 17 health_score
        85,  # 18 satisfaction_score
        150000.0,  # 19 total_revenue
        0.0,  # 20 total_debt
        False,  # 21 is_defaulter
        True,  # 22 is_vip
        "crm",  # 23 crm_origin
        None,  # 24 lead_id
        _now(),  # 25 created_at
        25000.0,  # 26 mrr
        3,  # 27 contratos_ativos
        None,  # 28 lead_name
        None,  # 29 lead_source
    ][idx]
    return row


def _make_row_resumo():
    row = MagicMock()
    row.__getitem__ = lambda self, idx: [
        10,  # 0 ativos
        2,  # 1 inativos
        1,  # 2 inadimplentes
        3,  # 3 vip
        5,  # 4 originados_crm
        272000.0,  # 5 mrr_total
        4,  # 6 segmentos
    ][idx]
    return row


def _make_row_client_detail():
    row = MagicMock()
    row.id = _uid()
    row.name = "Empresa Alpha"
    row.document_number = "12.345.678/0001-90"
    row.email = "alpha@emp.com"
    row.phone = "92999990000"
    row.status = "active"
    row.segment = "security"
    row.health_score = 90
    row.crm_origin = "crm"
    row.lead_name = None
    return row


def _make_row_contrato():
    row = MagicMock()
    row.id = _uid()
    row.service_type = "vigilancia"
    row.monthly_value = 15000.0
    row.start_date = None
    row.status = "active"
    return row


def _make_row_contact():
    row = MagicMock()
    row.__getitem__ = lambda self, idx: [
        _uid(),  # 0  id
        _uid(),  # 1  client_id
        "Maria Contato",  # 2  name
        "Gerente",  # 3  role
        "maria@emp.com",  # 4  email
        "92999990001",  # 5  phone
        "92999990001",  # 6  whatsapp
        True,  # 7  is_primary
        None,  # 8  notes
        _now(),  # 9  created_at
        "Empresa Alpha",  # 10 client_name
    ][idx]
    return row


def _make_row_activity():
    row = MagicMock()
    row.__getitem__ = lambda self, idx: [
        _uid(),  # 0  id
        _uid(),  # 1  client_id
        "call",  # 2  type
        "Reuniao de apresentacao",  # 3  subject
        "Apresentamos o servico",  # 4  description
        "Positivo",  # 5  outcome
        _now(),  # 6  created_at
        "Empresa Alpha",  # 7  client_name
    ][idx]
    return row


def _make_row_activity_full():
    row = MagicMock()
    row.__getitem__ = lambda self, idx: [
        _uid(),  # 0  id
        _uid(),  # 1  client_id
        "email",  # 2  type
        "Proposta enviada",  # 3  subject
        "Detalhes da proposta",  # 4  description
        "Aguardando resposta",  # 5  outcome
        None,  # 6  scheduled_at
        None,  # 7  completed_at
        _now(),  # 8  created_at
        "Empresa Alpha",  # 9  client_name
    ][idx]
    return row


def _make_row_campaign():
    row = MagicMock()
    row.id = _uid()
    row.name = "Campanha Q1 2026"
    row.type = "digital"
    row.status = "active"
    row.budget = 5000.0
    row.spent = 1200.0
    row.start_date = None
    row.end_date = None
    row.description = "Campanha de aquisicao"
    row.total_leads = 20
    row.converted = 5
    return row


def _make_row_mkt_lead(converted=False):
    row = MagicMock()
    row.id = _uid()
    row.name = "Pedro Prospect"
    row.email = "pedro@prospect.com"
    row.phone = "92999990002"
    row.whatsapp = "92999990002"
    row.source = "google_ads"
    row.status = "converted" if converted else "new"
    row.campaign_name = "Campanha Q1 2026"
    row.campaign_id = _uid()
    row.crm_lead_id = _uid() if converted else None
    row.created_at = _now()
    return row


def _make_row_stats():
    row = MagicMock()
    row.__getitem__ = lambda self, idx: [
        "Campanha Q1 2026",  # 0 campanha
        20,  # 1 total
        10,  # 2 novos
        5,  # 3 contactados
        3,  # 4 qualificados
        2,  # 5 convertidos
        0,  # 6 perdidos
        10.0,  # 7 taxa_conversao
    ][idx]
    return row


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_db_override(mock_db):
    """Envolve mock de DB como generator async para dependency_overrides."""

    async def _dep():
        yield mock_db

    return _dep


def _build_test_app():
    """
    Constroi FastAPI minima de teste com os 4 routers alvo.

    Usa FastAPI() do zero (sem lifespan/Redis/DB startup) para evitar
    hangs de conexao e ImportError em cascata de modules.clients.
    """
    from fastapi import FastAPI

    from modules.crm.controllers.client_controller import router as client_router
    from modules.crm.controllers.contact_controller import router as contact_router
    from modules.crm.controllers.dashboard_controller import router as dashboard_router
    from modules.crm.controllers.marketing_controller import router as marketing_router

    application = FastAPI(title="CRM Test App")
    application.include_router(dashboard_router, prefix="/api/v1/crm")
    application.include_router(client_router, prefix="/api/v1/crm")
    application.include_router(contact_router, prefix="/api/v1/crm")
    application.include_router(marketing_router, prefix="/api/v1")
    return application


@pytest.fixture
def crm_app():
    """
    FastAPI app minima com os 4 routers CRM e auth ja sobrescrita.
    Cada teste define dependency_overrides para get_db / get_async_session.
    """
    app = _build_test_app()
    mock_user = _make_mock_user()

    async def _auth():
        return mock_user

    app.dependency_overrides[get_current_active_user] = _auth
    return app


@pytest_asyncio.fixture
async def crm_client(crm_app):
    """AsyncClient autenticado apontado para crm_app."""
    transport = ASGITransport(app=crm_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "Bearer test-token-valid"
        yield client


# ===========================================================================
# TESTES — DASHBOARD
# ===========================================================================


class TestDashboardKpis:
    """GET /api/v1/crm/dashboard/kpis"""

    @pytest.mark.asyncio
    async def test_get_kpis_returns_200(self, crm_app, crm_client):
        """Retorna KPIs calculados a partir dos dados mockados."""
        mock_db = _db_dashboard(
            leads=[_make_lead_orm()],
            opps=[_make_opportunity_orm()],
            props=[_make_proposal_orm()],
            comms=[_make_commission_orm()],
        )
        crm_app.dependency_overrides[_get_db] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/dashboard/kpis")

        assert resp.status_code == 200
        data = resp.json()
        assert "leads_total" in data
        assert "opportunities_total" in data
        assert "proposals_total" in data
        assert "commissions_total" in data
        assert data["leads_total"] == 1
        assert data["opportunities_total"] == 1

    @pytest.mark.asyncio
    async def test_get_kpis_with_date_filters(self, crm_app, crm_client):
        """Aceita parametros de data_from e data_to."""
        mock_db = _db_dashboard()
        crm_app.dependency_overrides[_get_db] = _make_db_override(mock_db)

        resp = await crm_client.get(
            "/api/v1/crm/dashboard/kpis",
            params={"date_from": "2026-01-01", "date_to": "2026-03-31"},
        )

        assert resp.status_code == 200
        assert "leads_total" in resp.json()


class TestDashboardFunnel:
    """GET /api/v1/crm/dashboard/funnel"""

    @pytest.mark.asyncio
    async def test_get_funnel_returns_200(self, crm_app, crm_client):
        """Retorna grafico de funil com opportunities por estagio."""
        opps = [
            _make_opportunity_orm(stage="qualification"),
            _make_opportunity_orm(stage="proposal"),
            _make_opportunity_orm(stage="closed_won", is_won=True),
        ]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(opps))

        resp = await crm_client.get("/api/v1/crm/dashboard/funnel")

        assert resp.status_code == 200
        data = resp.json()
        assert data["chart_type"] == "funnel"
        assert "labels" in data
        assert "datasets" in data


class TestDashboardTrends:
    """GET /api/v1/crm/dashboard/trends/*"""

    @pytest.mark.asyncio
    async def test_trends_leads_returns_200(self, crm_app, crm_client):
        """Retorna tendencia de leads por mes."""
        leads = [_make_lead_orm(created_at=datetime(2026, 3, 10, 10, 0, 0))]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(leads))

        resp = await crm_client.get("/api/v1/crm/dashboard/trends/leads")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 6  # default periods_count=6
        for item in data:
            assert "period" in item
            assert "value" in item

    @pytest.mark.asyncio
    async def test_trends_sales_returns_200(self, crm_app, crm_client):
        """Retorna tendencia de vendas (won opportunities)."""
        won_opp = _make_opportunity_orm(stage="closed_won", is_won=True)
        won_opp.actual_close_date = datetime(2026, 3, 15, 10, 0, 0)
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single([won_opp]))

        resp = await crm_client.get(
            "/api/v1/crm/dashboard/trends/sales",
            params={"period": "month", "periods_count": 3},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_trends_commissions_returns_200(self, crm_app, crm_client):
        """Retorna tendencia de comissoes."""
        comms = [_make_commission_orm(final_commission=3000.0)]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(comms))

        resp = await crm_client.get("/api/v1/crm/dashboard/trends/commissions")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestDashboardConversionRates:
    """GET /api/v1/crm/dashboard/conversion-rates"""

    @pytest.mark.asyncio
    async def test_conversion_rates_returns_200(self, crm_app, crm_client):
        """Retorna dict com taxas de conversao entre estagios."""
        opps = [
            _make_opportunity_orm(stage="qualification"),
            _make_opportunity_orm(stage="needs_analysis"),
            _make_opportunity_orm(stage="closed_won"),
        ]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(opps))

        resp = await crm_client.get("/api/v1/crm/dashboard/conversion-rates")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert len(data) > 0


class TestDashboardSellerPerformance:
    """GET /api/v1/crm/dashboard/seller/{seller_id}/performance"""

    @pytest.mark.asyncio
    async def test_seller_performance_returns_200(self, crm_app, crm_client):
        """Retorna metricas de performance do vendedor."""
        seller_id = _uid()
        leads = [_make_lead_orm(assigned_to_id=seller_id)]
        opps = [_make_opportunity_orm(owner_id=seller_id, stage="closed_won", is_won=True, value=80000.0)]
        comms = [_make_commission_orm(seller_id=seller_id, final_commission=4000.0)]

        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_triple(leads, opps, comms))

        resp = await crm_client.get(f"/api/v1/crm/dashboard/seller/{seller_id}/performance")

        assert resp.status_code == 200
        data = resp.json()
        assert data["seller_id"] == seller_id
        assert "leads_assigned" in data
        assert "opportunities_won" in data
        assert "total_sales" in data

    @pytest.mark.asyncio
    async def test_seller_performance_with_target(self, crm_app, crm_client):
        """Aceita parametro target e retorna target_percentage."""
        seller_id = _uid()
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_triple([], [], []))

        resp = await crm_client.get(
            f"/api/v1/crm/dashboard/seller/{seller_id}/performance",
            params={"target": 100000},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["target"] == 100000.0


class TestDashboardTopPerformers:
    """GET /api/v1/crm/dashboard/top-performers"""

    @pytest.mark.asyncio
    async def test_top_performers_returns_200(self, crm_app, crm_client):
        """Retorna lista de top performers."""
        seller_id = _uid()
        leads = [_make_lead_orm(assigned_to_id=seller_id)]
        opps = [_make_opportunity_orm(owner_id=seller_id, stage="closed_won", is_won=True, value=60000.0)]
        comms = [_make_commission_orm(seller_id=seller_id)]

        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_triple(leads, opps, comms))

        resp = await crm_client.get("/api/v1/crm/dashboard/top-performers")

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_top_performers_respects_limit(self, crm_app, crm_client):
        """Respeita o parametro limit."""
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_triple([], [], []))

        resp = await crm_client.get(
            "/api/v1/crm/dashboard/top-performers",
            params={"limit": 3},
        )

        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestDashboardCharts:
    """GET /api/v1/crm/dashboard/charts/*"""

    @pytest.mark.asyncio
    async def test_leads_by_status_chart(self, crm_app, crm_client):
        """Retorna grafico de leads por status."""
        leads = [
            _make_lead_orm(status="new"),
            _make_lead_orm(status="new"),
            _make_lead_orm(status="qualified"),
        ]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(leads))

        resp = await crm_client.get("/api/v1/crm/dashboard/charts/leads-by-status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["chart_type"] == "pie"
        assert data["title"] == "Leads por Status"
        assert "new" in data["labels"]

    @pytest.mark.asyncio
    async def test_opportunities_by_stage_chart(self, crm_app, crm_client):
        """Retorna grafico de opportunities por estagio."""
        opps = [
            _make_opportunity_orm(stage="qualification"),
            _make_opportunity_orm(stage="proposal"),
        ]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(opps))

        resp = await crm_client.get("/api/v1/crm/dashboard/charts/opportunities-by-stage")

        assert resp.status_code == 200
        data = resp.json()
        assert data["chart_type"] == "pie"
        assert data["title"] == "Opportunities por Estágio"

    @pytest.mark.asyncio
    async def test_proposals_by_status_chart(self, crm_app, crm_client):
        """Retorna grafico de propostas por status."""
        props = [
            _make_proposal_orm(status="draft"),
            _make_proposal_orm(status="accepted"),
        ]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(props))

        resp = await crm_client.get("/api/v1/crm/dashboard/charts/proposals-by-status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["chart_type"] == "pie"
        assert data["title"] == "Propostas por Status"

    @pytest.mark.asyncio
    async def test_commissions_by_status_chart(self, crm_app, crm_client):
        """Retorna grafico de comissoes por status."""
        comms = [
            _make_commission_orm(status="pending"),
            _make_commission_orm(status="paid"),
        ]
        crm_app.dependency_overrides[_get_db] = _make_db_override(_db_single(comms))

        resp = await crm_client.get("/api/v1/crm/dashboard/charts/commissions-by-status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["chart_type"] == "pie"
        assert data["title"] == "Comissões por Status"


# ===========================================================================
# TESTES — CLIENTS
# ===========================================================================


class TestListClients:
    """GET /api/v1/crm/clients/"""

    @pytest.mark.asyncio
    async def test_list_clients_returns_200(self, crm_app, crm_client):
        """Lista clientes ativos com dados financeiros."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([_make_row_client()]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/clients/")

        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_clients_with_status_filter(self, crm_app, crm_client):
        """Aceita filtro por status."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/clients/", params={"status": "active"})

        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_list_clients_with_segment_filter(self, crm_app, crm_client):
        """Aceita filtro por segmento."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/clients/", params={"segment": "security"})

        assert resp.status_code == 200


class TestClientResumo:
    """GET /api/v1/crm/clients/resumo"""

    @pytest.mark.asyncio
    async def test_resumo_returns_200(self, crm_app, crm_client):
        """Retorna resumo agregado da base de clientes."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(_make_row_resumo()))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/clients/resumo")

        assert resp.status_code == 200
        data = resp.json()
        assert "clientes_ativos" in data
        assert "mrr_total" in data
        assert "inadimplentes" in data
        assert data["clientes_ativos"] == 10
        assert data["mrr_total"] == 272000.0


class TestClientDetail:
    """GET /api/v1/crm/clients/{client_id}"""

    @pytest.mark.asyncio
    async def test_get_client_found_returns_200(self, crm_app, crm_client):
        """Retorna detalhe do cliente com contratos."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(
            side_effect=[
                _text_one(_make_row_client_detail()),  # cliente
                _text_list([_make_row_contrato()]),  # contratos
            ]
        )
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get(f"/api/v1/crm/clients/{uuid4()}")

        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "contratos" in data
        assert len(data["contratos"]) == 1

    @pytest.mark.asyncio
    async def test_get_client_not_found_returns_404(self, crm_app, crm_client):
        """Retorna 404 quando cliente nao existe."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(None))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get(f"/api/v1/crm/clients/{uuid4()}")

        assert resp.status_code == 404
        assert "não encontrado" in resp.json()["detail"]


# ===========================================================================
# TESTES — CONTACTS
# ===========================================================================


class TestListContacts:
    """GET /api/v1/crm/contacts/"""

    @pytest.mark.asyncio
    async def test_list_contacts_returns_200(self, crm_app, crm_client):
        """Lista todos os contatos CRM."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([_make_row_contact()]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/contacts/")

        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_contacts_with_client_filter(self, crm_app, crm_client):
        """Filtra contatos por client_id."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/contacts/", params={"client_id": _uid()})

        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestCreateContact:
    """POST /api/v1/crm/contacts/"""

    @pytest.mark.asyncio
    async def test_create_contact_returns_200(self, crm_app, crm_client):
        """Cria novo contato vinculado a um cliente."""
        new_id = _uid()
        returned_row = MagicMock()
        returned_row.__getitem__ = lambda s, i: new_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(returned_row))
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {
            "client_id": _uid(),
            "name": "Ana Gestora",
            "role": "Diretora",
            "email": "ana@empresa.com",
            "phone": "92988880000",
            "is_primary": True,
        }

        resp = await crm_client.post("/api/v1/crm/contacts/", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "message" in data


class TestDeleteContact:
    """DELETE /api/v1/crm/contacts/{contact_id}"""

    @pytest.mark.asyncio
    async def test_delete_contact_returns_200(self, crm_app, crm_client):
        """Remove contato existente."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.delete(f"/api/v1/crm/contacts/{uuid4()}")

        assert resp.status_code == 200
        assert "removido" in resp.json()["message"].lower()


# ===========================================================================
# TESTES — ACTIVITIES
# ===========================================================================


class TestRecentActivities:
    """GET /api/v1/crm/activities/recent"""

    @pytest.mark.asyncio
    async def test_recent_activities_returns_200(self, crm_app, crm_client):
        """Retorna as ultimas 20 atividades de todos os clientes."""
        rows = [_make_row_activity() for _ in range(3)]
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list(rows))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/activities/recent")

        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 3


class TestListActivities:
    """GET /api/v1/crm/activities/"""

    @pytest.mark.asyncio
    async def test_list_activities_returns_200(self, crm_app, crm_client):
        """Lista todas as atividades CRM."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([_make_row_activity_full()]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/activities/")

        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_activities_with_client_filter(self, crm_app, crm_client):
        """Filtra atividades por client_id."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/crm/activities/", params={"client_id": _uid()})

        assert resp.status_code == 200


class TestCreateActivity:
    """POST /api/v1/crm/activities/"""

    @pytest.mark.asyncio
    async def test_create_activity_returns_200(self, crm_app, crm_client):
        """Registra nova atividade (chamada, email, visita, nota)."""
        new_id = _uid()
        returned_row = MagicMock()
        returned_row.__getitem__ = lambda s, i: new_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(returned_row))
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {
            "client_id": _uid(),
            "type": "call",
            "subject": "Apresentacao do servico",
            "description": "Apresentamos o portfolio completo",
            "outcome": "Cliente demonstrou interesse",
        }

        resp = await crm_client.post("/api/v1/crm/activities/", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "registrada" in data["message"].lower()


class TestClient360:
    """GET /api/v1/crm/clients/{client_id}/360"""

    @pytest.mark.asyncio
    async def test_client_360_found_returns_200(self, crm_app, crm_client):
        """Retorna visao 360 completa do cliente."""
        client_uid = _uid()
        client_row = MagicMock()
        client_row.__getitem__ = lambda self, idx: [
            client_uid,  # 0  id
            "Empresa Alpha",  # 1  name
            "12.345.678/0001-90",  # 2  document_number
            "alpha@emp.com",  # 3  email
            "92999990000",  # 4  phone
            "active",  # 5  status
            "security",  # 6  segment
            90,  # 7  health_score
            False,  # 8  is_defaulter
            True,  # 9  is_vip
            "crm",  # 10 crm_origin
            None,  # 11 lead_name
            None,  # 12 lead_source
        ][idx]

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(
            side_effect=[
                _text_one(client_row),  # cliente
                _text_list([]),  # contratos
                _scalar_result(25000.0),  # mrr scalar
                _text_list([]),  # oportunidades
                _text_list([]),  # contatos
                _text_list([]),  # atividades
                _text_list([]),  # nfse
                _text_list([]),  # funcionarios
                _text_list([]),  # mrr historico
            ]
        )
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get(f"/api/v1/crm/clients/{uuid4()}/360")

        assert resp.status_code == 200
        data = resp.json()
        assert "cliente" in data
        assert "contratos" in data
        assert "oportunidades" in data
        assert "contatos" in data
        assert "atividades" in data
        assert "nfse" in data
        assert data["cliente"]["name"] == "Empresa Alpha"

    @pytest.mark.asyncio
    async def test_client_360_not_found_returns_404(self, crm_app, crm_client):
        """Retorna 404 quando cliente nao existe."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(None))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get(f"/api/v1/crm/clients/{uuid4()}/360")

        assert resp.status_code == 404


# ===========================================================================
# TESTES — MARKETING
# ===========================================================================


class TestListCampaigns:
    """GET /api/v1/marketing/campaigns/"""

    @pytest.mark.asyncio
    async def test_list_campaigns_returns_200(self, crm_app, crm_client):
        """Lista todas as campanhas de marketing."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([_make_row_campaign()]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/marketing/campaigns/")

        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Campanha Q1 2026"

    @pytest.mark.asyncio
    async def test_list_campaigns_empty_returns_200(self, crm_app, crm_client):
        """Retorna lista vazia quando nao ha campanhas."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/marketing/campaigns/")

        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestCreateCampaign:
    """POST /api/v1/marketing/campaigns/"""

    @pytest.mark.asyncio
    async def test_create_campaign_returns_200(self, crm_app, crm_client):
        """Cria nova campanha de marketing."""
        new_id = _uid()
        returned_row = MagicMock()
        returned_row.__getitem__ = lambda s, i: new_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(returned_row))
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {
            "name": "Campanha Outono 2026",
            "type": "digital",
            "budget": 8000.0,
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "outono2026",
        }

        resp = await crm_client.post("/api/v1/marketing/campaigns/", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "criada" in data["message"].lower()


class TestUpdateCampaign:
    """PUT /api/v1/marketing/campaigns/{campaign_id}"""

    @pytest.mark.asyncio
    async def test_update_campaign_returns_200(self, crm_app, crm_client):
        """Atualiza campanha existente."""
        campaign_id = _uid()

        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {"name": "Campanha Atualizada", "type": "digital", "budget": 10000.0}

        resp = await crm_client.put(f"/api/v1/marketing/campaigns/{campaign_id}", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert "atualizada" in data["message"].lower()
        assert data["id"] == campaign_id


class TestListMarketingLeads:
    """GET /api/v1/marketing/leads/"""

    @pytest.mark.asyncio
    async def test_list_mkt_leads_returns_200(self, crm_app, crm_client):
        """Lista leads de marketing."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([_make_row_mkt_lead()]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/marketing/leads/")

        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Pedro Prospect"

    @pytest.mark.asyncio
    async def test_list_mkt_leads_with_filters(self, crm_app, crm_client):
        """Aceita filtros por campaign_id e status."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get(
            "/api/v1/marketing/leads/",
            params={"status": "new", "campaign_id": _uid()},
        )

        assert resp.status_code == 200


class TestCreateMarketingLead:
    """POST /api/v1/marketing/leads/"""

    @pytest.mark.asyncio
    async def test_create_mkt_lead_returns_200(self, crm_app, crm_client):
        """Cria novo lead de marketing."""
        new_id = _uid()
        returned_row = MagicMock()
        returned_row.__getitem__ = lambda s, i: new_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(returned_row))
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {
            "name": "Lucas Novo Prospect",
            "email": "lucas@prospect.com",
            "phone": "92988880001",
            "source": "instagram",
        }

        resp = await crm_client.post("/api/v1/marketing/leads/", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "criado" in data["message"].lower()


class TestConvertMarketingLead:
    """POST /api/v1/marketing/leads/{lead_id}/convert"""

    @pytest.mark.asyncio
    async def test_convert_lead_success_returns_200(self, crm_app, crm_client):
        """Converte lead de marketing em lead CRM."""
        lead_id = _uid()
        crm_lead_id = _uid()

        mkt_lead_row = _make_row_mkt_lead(converted=False)

        camp_row = MagicMock()
        camp_row.__getitem__ = lambda s, i: "Campanha Q1 2026"

        new_crm_row = MagicMock()
        new_crm_row.__getitem__ = lambda s, i: crm_lead_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(
            side_effect=[
                _text_one(mkt_lead_row),  # buscar mkt lead
                _text_one(camp_row),  # buscar campanha
                _text_one(new_crm_row),  # inserir lead CRM
                MagicMock(),  # update mkt lead
            ]
        )
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.post(f"/api/v1/marketing/leads/{lead_id}/convert")

        assert resp.status_code == 200
        data = resp.json()
        assert "crm_lead_id" in data
        assert "convertido" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_convert_lead_already_converted(self, crm_app, crm_client):
        """Retorna mensagem de ja convertido sem criar novo lead."""
        lead_id = _uid()
        mkt_lead_row = _make_row_mkt_lead(converted=True)

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(mkt_lead_row))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.post(f"/api/v1/marketing/leads/{lead_id}/convert")

        assert resp.status_code == 200
        data = resp.json()
        assert "ja convertido" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_convert_lead_not_found_returns_404(self, crm_app, crm_client):
        """Retorna 404 quando lead de marketing nao existe."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(None))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.post(f"/api/v1/marketing/leads/{_uid()}/convert")

        assert resp.status_code == 404


class TestMarketingLeadStats:
    """GET /api/v1/marketing/leads/stats"""

    @pytest.mark.asyncio
    async def test_stats_returns_200(self, crm_app, crm_client):
        """Retorna estatisticas de leads por campanha."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_list([_make_row_stats()]))
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        resp = await crm_client.get("/api/v1/marketing/leads/stats")

        assert resp.status_code == 200
        data = resp.json()
        assert "campanhas" in data
        assert "gerado_em" in data
        assert len(data["campanhas"]) == 1
        camp = data["campanhas"][0]
        assert "campanha" in camp
        assert "total" in camp
        assert "taxa_conversao" in camp


class TestLicitacaoConvertToCRM:
    """POST /api/v1/marketing/licitacao/convert-to-crm"""

    @pytest.mark.asyncio
    async def test_convert_licitacao_returns_200(self, crm_app, crm_client):
        """Converte licitacao vencida em lead CRM qualificado."""
        crm_lead_id = _uid()
        new_row = MagicMock()
        new_row.__getitem__ = lambda s, i: crm_lead_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(new_row))
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {
            "orgao": "Prefeitura de Manaus",
            "objeto": "Servicos de vigilancia patrimonial",
            "valor": 350000.0,
            "numero_edital": "001/2026",
        }

        resp = await crm_client.post("/api/v1/marketing/licitacao/convert-to-crm", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert "crm_lead_id" in data
        assert data["orgao"] == "Prefeitura de Manaus"
        assert data["valor"] == 350000.0
        assert "convertida" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_convert_licitacao_sem_edital(self, crm_app, crm_client):
        """Funciona sem numero_edital (campo opcional)."""
        crm_lead_id = _uid()
        new_row = MagicMock()
        new_row.__getitem__ = lambda s, i: crm_lead_id

        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=_text_one(new_row))
        mock_db.commit = AsyncMock()
        crm_app.dependency_overrides[_get_async_session] = _make_db_override(mock_db)

        payload = {
            "orgao": "Governo do Amazonas",
            "objeto": "Vigilancia em edificios publicos",
            "valor": 180000.0,
        }

        resp = await crm_client.post("/api/v1/marketing/licitacao/convert-to-crm", json=payload)

        assert resp.status_code == 200
        assert "crm_lead_id" in resp.json()

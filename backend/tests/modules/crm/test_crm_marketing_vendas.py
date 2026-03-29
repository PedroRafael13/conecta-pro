"""
Testes de cobertura — CRM Marketing & Vendas.

Cobre:
  - MarketingController (campanhas, leads mkt, conversão mkt→CRM, stats, licitação→CRM)
  - ClientController (listar, resumo, detalhe)
  - ContactController (contatos CRUD, atividades CRUD, visão 360°)
  - LeadScoringEngine (score, probabilidade, ação recomendada, próximo contato)
  - PipelineService (pipeline ponderado, win rate, velocidade, forecast, health)
  - DashboardService (KPIs, funil, trends, conversion rates, performance)
  - CRM360Service (360° view, interactions, journey, segmentation, analytics)
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid() -> str:
    return str(uuid.uuid4())


def _mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


def _row(**kw):
    """Cria um mock Row com acesso por atributo e por índice."""
    m = MagicMock()
    for k, v in kw.items():
        setattr(m, k, v)
    vals = list(kw.values())
    m.__getitem__ = lambda self, i: vals[i]
    return m


# ===========================================================================
# 1. LEAD SCORING ENGINE
# ===========================================================================


class TestLeadScoringEngine:
    """Testes do motor de scoring de leads."""

    @pytest.fixture
    def engine(self):
        from modules.crm.services.lead_service import LeadScoringEngine

        return LeadScoringEngine()

    def test_calculate_score_complete_lead(self, engine):
        lead = MagicMock()
        lead.name = "Empresa Teste"
        lead.email = "teste@empresa.com"
        lead.phone = "92999999999"
        lead.company = "Empresa Teste LTDA"
        lead.position = "Gerente"
        lead.company_size = "large"
        lead.industry = "security"
        lead.source = MagicMock(value="referral")
        lead.notes = "Interessado em vigilância"
        lead.last_contact_at = datetime.now() - timedelta(hours=12)
        lead.created_at = datetime.now() - timedelta(days=2)
        lead.status = MagicMock(value="qualified")

        score = engine.calculate_score(lead)
        assert 0 <= score <= 100

    def test_calculate_score_minimal_lead(self, engine):
        lead = MagicMock()
        lead.name = "Lead Minimo"
        lead.email = "min@test.com"
        lead.phone = None
        lead.company = None
        lead.position = None
        lead.company_size = None
        lead.industry = None
        lead.source = MagicMock(value="other")
        lead.notes = None
        lead.last_contact_at = None
        lead.created_at = datetime.now()
        lead.status = MagicMock(value="new")

        score = engine.calculate_score(lead)
        assert 0 <= score <= 100
        # Lead mínimo deve ter score baixo
        assert score < 60

    def test_calculate_probability(self, engine):
        lead = MagicMock()
        lead.score = 80
        lead.status = MagicMock(value="qualified")

        prob = engine.calculate_probability(lead)
        assert 0 <= prob <= 1.0

    def test_calculate_probability_won(self, engine):
        lead = MagicMock()
        lead.score = 90
        lead.status = MagicMock(value="won")

        prob = engine.calculate_probability(lead)
        assert prob >= 0.9

    def test_calculate_probability_lost(self, engine):
        lead = MagicMock()
        lead.score = 50
        lead.status = MagicMock(value="lost")

        prob = engine.calculate_probability(lead)
        assert prob <= 0.15


class TestLeadService:
    """Testes do serviço de leads."""

    @pytest.fixture
    def service(self):
        from modules.crm.services.lead_service import LeadService

        return LeadService()

    def test_get_recommended_action_hot_new(self, service):
        lead = MagicMock()
        lead.score = 85
        lead.status = MagicMock(value="new")

        action = service.get_recommended_action(lead)
        assert isinstance(action, str)
        assert len(action) > 0

    def test_get_recommended_action_cold(self, service):
        lead = MagicMock()
        lead.score = 20
        lead.status = MagicMock(value="contacted")

        action = service.get_recommended_action(lead)
        assert isinstance(action, str)

    def test_get_next_contact_date_hot(self, service):
        lead = MagicMock()
        lead.score = 80
        lead.status = MagicMock(value="new")
        lead.last_contact_at = datetime.now()

        next_date = service.get_next_contact_date(lead)
        assert next_date is not None
        assert next_date > datetime.now()

    def test_get_next_contact_date_cold(self, service):
        lead = MagicMock()
        lead.score = 25
        lead.status = MagicMock(value="new")
        lead.last_contact_at = datetime.now()

        next_date = service.get_next_contact_date(lead)
        assert next_date is not None

    def test_get_next_contact_date_no_last_contact(self, service):
        lead = MagicMock()
        lead.score = 50
        lead.status = MagicMock(value="new")
        lead.last_contact_at = None

        next_date = service.get_next_contact_date(lead)
        # Deve retornar algo válido mesmo sem contato anterior
        assert next_date is None or isinstance(next_date, datetime)


# ===========================================================================
# 2. PIPELINE SERVICE
# ===========================================================================


class TestPipelineService:
    """Testes do serviço de pipeline de vendas."""

    @pytest.fixture
    def service(self):
        from modules.crm.services.pipeline_service import PipelineService

        return PipelineService()

    def _make_opportunity(self, **overrides):
        opp = MagicMock()
        defaults = {
            "id": _uid(),
            "title": "Oportunidade Teste",
            "stage": MagicMock(value="proposal"),
            "value": Decimal("50000"),
            "probability": 0.6,
            "is_active": True,
            "is_won": False,
            "is_lost": False,
            "created_at": datetime.now() - timedelta(days=30),
            "updated_at": datetime.now(),
            "expected_close_date": date.today() + timedelta(days=30),
            "actual_close_date": None,
            "loss_reason": None,
            "competitor": None,
            "owner_id": _uid(),
        }
        defaults.update(overrides)
        for k, v in defaults.items():
            setattr(opp, k, v)
        return opp

    def test_calculate_weighted_pipeline(self, service):
        opps = [
            self._make_opportunity(value=Decimal("100000"), probability=0.5),
            self._make_opportunity(value=Decimal("50000"), probability=0.8),
        ]
        weighted = service.calculate_weighted_pipeline(opps)
        assert weighted > 0

    def test_calculate_win_rate(self, service):
        opps = [
            self._make_opportunity(is_won=True, is_lost=False),
            self._make_opportunity(is_won=True, is_lost=False),
            self._make_opportunity(is_won=False, is_lost=True),
        ]
        rate = service.calculate_win_rate(opps)
        assert 0 <= rate <= 100

    def test_calculate_win_rate_no_closed(self, service):
        opps = [self._make_opportunity()]
        rate = service.calculate_win_rate(opps)
        assert rate == 0

    def test_calculate_avg_deal_size(self, service):
        opps = [
            self._make_opportunity(is_won=True, value=Decimal("100000")),
            self._make_opportunity(is_won=True, value=Decimal("60000")),
        ]
        avg = service.calculate_avg_deal_size(opps)
        assert avg > 0

    def test_calculate_avg_deal_size_no_won(self, service):
        opps = [self._make_opportunity()]
        avg = service.calculate_avg_deal_size(opps)
        assert avg == 0

    def test_get_overdue_opportunities(self, service):
        opps = [
            self._make_opportunity(
                expected_close_date=date.today() - timedelta(days=10),
                is_won=False,
                is_lost=False,
            ),
            self._make_opportunity(
                expected_close_date=date.today() + timedelta(days=10),
            ),
        ]
        overdue = service.get_overdue_opportunities(opps)
        assert len(overdue) >= 1

    def test_get_stagnant_opportunities(self, service):
        opps = [
            self._make_opportunity(
                updated_at=datetime.now() - timedelta(days=30),
                is_won=False,
                is_lost=False,
            ),
        ]
        stagnant = service.get_stagnant_opportunities(opps, days=15)
        assert len(stagnant) >= 1

    def test_get_health_score(self, service):
        opps = [
            self._make_opportunity(is_won=True, value=Decimal("80000")),
            self._make_opportunity(value=Decimal("50000"), probability=0.7),
        ]
        health = service.get_health_score(opps)
        assert hasattr(health, "score") or isinstance(health, dict)

    def test_forecast_revenue(self, service):
        opps = [
            self._make_opportunity(
                value=Decimal("100000"),
                probability=0.8,
                expected_close_date=date.today() + timedelta(days=15),
            ),
        ]
        forecast = service.forecast_revenue(opps, months=3)
        assert isinstance(forecast, list)

    def test_calculate_loss_analysis(self, service):
        opps = [
            self._make_opportunity(
                is_lost=True,
                loss_reason="price",
                competitor="Concorrente A",
            ),
            self._make_opportunity(
                is_lost=True,
                loss_reason="timing",
                competitor=None,
            ),
        ]
        analysis = service.calculate_loss_analysis(opps)
        assert isinstance(analysis, dict)


# ===========================================================================
# 3. DASHBOARD SERVICE
# ===========================================================================


class TestDashboardService:
    """Testes do serviço de dashboard CRM."""

    @pytest.fixture
    def service(self):
        from modules.crm.services.dashboard_service import DashboardService

        return DashboardService()

    def _make_lead(self, **kw):
        lead = MagicMock()
        defaults = {
            "id": _uid(),
            "status": MagicMock(value="new"),
            "source": MagicMock(value="website"),
            "score": 50,
            "is_active": True,
            "assigned_to_id": _uid(),
            "created_at": datetime.now() - timedelta(days=5),
            "updated_at": datetime.now(),
        }
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(lead, k, v)
        return lead

    def _make_opp(self, **kw):
        opp = MagicMock()
        defaults = {
            "id": _uid(),
            "stage": MagicMock(value="proposal"),
            "value": Decimal("50000"),
            "probability": 0.5,
            "is_active": True,
            "is_won": False,
            "is_lost": False,
            "owner_id": _uid(),
            "created_at": datetime.now() - timedelta(days=10),
            "updated_at": datetime.now(),
        }
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(opp, k, v)
        return opp

    def _make_proposal(self, **kw):
        p = MagicMock()
        defaults = {
            "id": _uid(),
            "status": MagicMock(value="sent"),
            "total_value": Decimal("45000"),
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=3),
        }
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(p, k, v)
        return p

    def _make_commission(self, **kw):
        c = MagicMock()
        defaults = {
            "id": _uid(),
            "status": MagicMock(value="pending"),
            "final_commission": Decimal("2500"),
            "is_active": True,
            "seller_id": _uid(),
            "created_at": datetime.now() - timedelta(days=2),
        }
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(c, k, v)
        return c

    def test_calculate_kpis(self, service):
        leads = [self._make_lead(), self._make_lead(status=MagicMock(value="qualified"))]
        opps = [self._make_opp()]
        proposals = [self._make_proposal()]
        commissions = [self._make_commission()]

        kpis = service.calculate_kpis(
            leads=leads,
            opportunities=opps,
            proposals=proposals,
            commissions=commissions,
        )
        assert kpis.total_leads == 2
        assert kpis.total_opportunities == 1

    def test_generate_funnel_chart(self, service):
        opps = [
            self._make_opp(stage=MagicMock(value="prospecting")),
            self._make_opp(stage=MagicMock(value="proposal")),
            self._make_opp(stage=MagicMock(value="negotiation")),
        ]
        chart = service.generate_funnel_chart(opps)
        assert chart.chart_type == "funnel"
        assert len(chart.data) > 0

    def test_generate_trends(self, service):
        leads = [self._make_lead(created_at=datetime.now() - timedelta(days=i * 30)) for i in range(6)]
        trends = service.generate_trends(
            data=leads,
            date_field="created_at",
            value_field="count",
            period="month",
            periods_count=6,
        )
        assert isinstance(trends, list)

    def test_generate_pie_chart_by_status(self, service):
        leads = [
            self._make_lead(status=MagicMock(value="new")),
            self._make_lead(status=MagicMock(value="new")),
            self._make_lead(status=MagicMock(value="qualified")),
        ]
        chart = service.generate_pie_chart_by_status(
            items=leads,
            status_field="status",
            title="Leads por Status",
        )
        assert chart.chart_type == "pie"

    def test_calculate_conversion_rates(self, service):
        opps = [
            self._make_opp(stage=MagicMock(value="prospecting")),
            self._make_opp(stage=MagicMock(value="qualification")),
            self._make_opp(stage=MagicMock(value="proposal")),
            self._make_opp(stage=MagicMock(value="closed_won"), is_won=True),
        ]
        rates = service.calculate_conversion_rates(opps)
        assert isinstance(rates, dict)

    def test_calculate_seller_performance(self, service):
        seller_id = _uid()
        leads = [self._make_lead(assigned_to_id=seller_id)]
        opps = [self._make_opp(owner_id=seller_id, is_won=True, value=Decimal("80000"))]
        commissions = [self._make_commission(seller_id=seller_id)]

        perf = service.calculate_seller_performance(
            seller_id=seller_id,
            leads=leads,
            opportunities=opps,
            commissions=commissions,
        )
        assert perf.seller_id == seller_id

    def test_get_top_performers(self, service):
        s1, s2 = _uid(), _uid()
        leads = [self._make_lead(assigned_to_id=s1), self._make_lead(assigned_to_id=s2)]
        opps = [
            self._make_opp(owner_id=s1, is_won=True, value=Decimal("100000")),
            self._make_opp(owner_id=s2, is_won=True, value=Decimal("50000")),
        ]
        commissions = [self._make_commission(seller_id=s1)]

        top = service.get_top_performers(
            leads=leads,
            opportunities=opps,
            commissions=commissions,
            sellers={s1: None, s2: None},
            limit=5,
        )
        assert isinstance(top, list)


# ===========================================================================
# 4. CRM 360 SERVICE
# ===========================================================================


class TestCRM360Service:
    """Testes do serviço CRM 360°."""

    @pytest.fixture
    def service(self):
        from modules.crm.services.crm_360_service import CRM360Service

        return CRM360Service()

    def test_get_all_customers(self, service):
        customers = service.get_all_customers()
        assert len(customers) > 0  # tem demo data

    def test_get_customer_360(self, service):
        customers = service.get_all_customers()
        if customers:
            first_id = customers[0].customer_id if hasattr(customers[0], "customer_id") else customers[0]["customer_id"]
            view = service.get_customer_360(first_id)
            assert view is not None

    def test_get_customer_360_not_found(self, service):
        result = service.get_customer_360("nonexistent-id")
        assert result is None

    def test_track_customer_interaction(self, service):
        customers = service.get_all_customers()
        if customers:
            cid = customers[0].customer_id if hasattr(customers[0], "customer_id") else customers[0]["customer_id"]
            from modules.crm.services.crm_360_service import InteractionType

            result = service.track_customer_interaction(
                customer_id=cid,
                interaction_type=InteractionType.PHONE,
                description="Ligação de follow-up",
            )
            assert result is not None

    def test_segment_customers(self, service):
        segments = service.segment_customers()
        assert isinstance(segments, (list, dict))

    def test_get_predictive_insights(self, service):
        customers = service.get_all_customers()
        if customers:
            cid = customers[0].customer_id if hasattr(customers[0], "customer_id") else customers[0]["customer_id"]
            insights = service.get_predictive_insights(cid)
            assert isinstance(insights, list)

    def test_generate_customer_health_score(self, service):
        customers = service.get_all_customers()
        if customers:
            cid = customers[0].customer_id if hasattr(customers[0], "customer_id") else customers[0]["customer_id"]
            score = service.generate_customer_health_score(cid)
            assert isinstance(score, (int, float, dict))

    def test_get_crm_analytics(self, service):
        analytics = service.get_crm_analytics()
        assert analytics is not None

    def test_get_customer_recommendations(self, service):
        customers = service.get_all_customers()
        if customers:
            cid = customers[0].customer_id if hasattr(customers[0], "customer_id") else customers[0]["customer_id"]
            recs = service.get_customer_recommendations(cid)
            assert isinstance(recs, list)

    def test_search_customers(self, service):
        results = service.search_customers(query="")
        assert isinstance(results, list)

    def test_update_customer_journey_stage(self, service):
        customers = service.get_all_customers()
        if customers:
            cid = customers[0].customer_id if hasattr(customers[0], "customer_id") else customers[0]["customer_id"]
            from modules.crm.services.crm_360_service import JourneyStage

            result = service.update_customer_journey_stage(cid, JourneyStage.ONBOARDING)
            assert result is not None


# ===========================================================================
# 5. MARKETING CONTROLLER — Schemas
# ===========================================================================


class TestMarketingSchemas:
    """Testes dos schemas Pydantic do marketing controller."""

    def test_campaign_create_defaults(self):
        from modules.crm.controllers.marketing_controller import CampaignCreate

        c = CampaignCreate(name="Campanha Teste")
        assert c.name == "Campanha Teste"
        assert c.type == "organic"
        assert c.budget == 0
        assert c.utm_source is None

    def test_campaign_create_full(self):
        from modules.crm.controllers.marketing_controller import CampaignCreate

        c = CampaignCreate(
            name="Google Ads Q1",
            type="google_ads",
            budget=5000.0,
            description="Campanha Google Ads primeiro trimestre",
            start_date="2026-01-01",
            end_date="2026-03-31",
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="q1-2026",
        )
        assert c.budget == 5000.0
        assert c.utm_campaign == "q1-2026"

    def test_mkt_lead_create_minimal(self):
        from modules.crm.controllers.marketing_controller import MktLeadCreate

        ml = MktLeadCreate(name="João Silva")
        assert ml.name == "João Silva"
        assert ml.campaign_id is None
        assert ml.email is None

    def test_mkt_lead_create_full(self):
        from modules.crm.controllers.marketing_controller import MktLeadCreate

        ml = MktLeadCreate(
            campaign_id=_uid(),
            name="Maria Souza",
            email="maria@teste.com",
            phone="92999887766",
            whatsapp="92999887766",
            source="instagram",
        )
        assert ml.email == "maria@teste.com"

    def test_licitacao_convert_request(self):
        from modules.crm.controllers.marketing_controller import LicitacaoConvertRequest

        req = LicitacaoConvertRequest(
            orgao="Prefeitura de Manaus",
            objeto="Vigilância patrimonial",
            valor=500000.0,
            numero_edital="PE-001/2026",
        )
        assert req.valor == 500000.0
        assert req.numero_edital == "PE-001/2026"


# ===========================================================================
# 6. CONTACT CONTROLLER — Schemas
# ===========================================================================


class TestContactSchemas:
    """Testes dos schemas do contact controller."""

    def test_contact_create(self):
        from modules.crm.controllers.contact_controller import ContactCreate

        c = ContactCreate(
            client_id=_uid(),
            name="Carlos Mendes",
            role="Síndico",
            email="carlos@cond.com",
            phone="92988776655",
            is_primary=True,
        )
        assert c.is_primary is True

    def test_activity_create(self):
        from modules.crm.controllers.contact_controller import ActivityCreate

        a = ActivityCreate(
            client_id=_uid(),
            type="visit",
            subject="Visita técnica ao condomínio",
            description="Verificação das câmeras",
        )
        assert a.type == "visit"

    def test_activity_create_defaults(self):
        from modules.crm.controllers.contact_controller import ActivityCreate

        a = ActivityCreate(client_id=_uid(), subject="Nota interna")
        assert a.type == "note"


# ===========================================================================
# 7. LEAD SCHEMAS — Validação
# ===========================================================================


class TestLeadSchemas:
    """Testes dos schemas Pydantic de Lead."""

    def test_lead_create_valid(self):
        from modules.crm.schemas.lead import LeadCreate

        data = LeadCreate(
            name="Lead Teste",
            email="lead@teste.com",
            phone="11999998888",
            company="Empresa Teste",
        )
        assert data.name == "Lead Teste"

    def test_lead_create_minimal(self):
        from modules.crm.schemas.lead import LeadCreate

        data = LeadCreate(name="Minimo", email="min@test.com")
        assert data.name == "Minimo"

    def test_lead_filter_defaults(self):
        from modules.crm.schemas.lead import LeadFilter

        f = LeadFilter()
        assert f.status is None
        assert f.source is None
        assert f.is_hot is None

    def test_lead_status_update(self):
        from modules.crm.models.lead import LeadStatus
        from modules.crm.schemas.lead import LeadStatusUpdate

        u = LeadStatusUpdate(status=LeadStatus.QUALIFIED, notes="Lead qualificado após reunião")
        assert u.status == LeadStatus.QUALIFIED

    def test_lead_update_partial(self):
        from modules.crm.schemas.lead import LeadUpdate

        u = LeadUpdate(company="Nova Empresa")
        assert u.company == "Nova Empresa"
        assert u.name is None


# ===========================================================================
# 8. LEAD MODEL
# ===========================================================================


class TestLeadModel:
    """Testes do modelo Lead."""

    def test_lead_status_enum(self):
        from modules.crm.models.lead import LeadStatus

        assert LeadStatus.NEW == "new"
        assert LeadStatus.WON == "won"
        assert LeadStatus.LOST == "lost"
        assert len(LeadStatus) == 7

    def test_lead_source_enum(self):
        from modules.crm.models.lead import LeadSource

        assert LeadSource.WEBSITE == "website"
        assert LeadSource.REFERRAL == "referral"
        assert len(LeadSource) == 8

    def test_lead_properties(self):
        from modules.crm.models.lead import Lead

        lead = Lead(
            name="Test",
            email="t@t.com",
            score=75,
            probability=0.6,
            expected_value=100000,
            status="qualified",
        )
        assert lead.is_hot is True  # score >= 70
        assert lead.is_qualified is True
        assert lead.weighted_value == 60000.0  # 100000 * 0.6

    def test_lead_not_hot(self):
        from modules.crm.models.lead import Lead

        lead = Lead(name="Cold", email="c@c.com", score=30, status="new")
        assert lead.is_hot is False

    def test_lead_not_qualified(self):
        from modules.crm.models.lead import Lead

        lead = Lead(name="New", email="n@n.com", score=50, status="new")
        assert lead.is_qualified is False


# ===========================================================================
# 9. MARKETING CONTROLLER — Lógica de endpoint (mock DB)
# ===========================================================================


class TestMarketingControllerLogic:
    """Testa lógica dos endpoints de marketing com mock DB."""

    @pytest.mark.asyncio
    async def test_listar_campanhas_empty(self):
        from modules.crm.controllers.marketing_controller import listar_campanhas

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = []
        db.execute.return_value = result_mock

        result = await listar_campanhas(db=db)
        assert result["items"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_criar_campanha(self):
        from modules.crm.controllers.marketing_controller import CampaignCreate, criar_campanha

        db = _mock_db()
        camp_id = _uid()
        row_mock = MagicMock()
        row_mock.__getitem__ = lambda self, i: camp_id
        result_mock = MagicMock()
        result_mock.fetchone.return_value = row_mock
        db.execute.return_value = result_mock

        data = CampaignCreate(name="Nova Campanha", type="facebook", budget=3000)
        result = await criar_campanha(data=data, db=db)
        assert result["id"] == camp_id
        assert "Campanha criada" in result["message"]
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_atualizar_campanha(self):
        from modules.crm.controllers.marketing_controller import CampaignCreate, atualizar_campanha

        db = _mock_db()
        camp_id = _uid()
        data = CampaignCreate(name="Atualizada", budget=5000)
        result = await atualizar_campanha(campaign_id=camp_id, data=data, db=db)
        assert result["id"] == camp_id
        assert "atualizada" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_criar_mkt_lead(self):
        from modules.crm.controllers.marketing_controller import MktLeadCreate, criar_mkt_lead

        db = _mock_db()
        lead_id = _uid()
        row_mock = MagicMock()
        row_mock.__getitem__ = lambda self, i: lead_id
        result_mock = MagicMock()
        result_mock.fetchone.return_value = row_mock
        db.execute.return_value = result_mock

        data = MktLeadCreate(name="Lead Facebook", email="fb@lead.com", source="facebook")
        result = await criar_mkt_lead(data=data, db=db)
        assert result["id"] == lead_id

    @pytest.mark.asyncio
    async def test_stats_mkt_leads(self):
        from modules.crm.controllers.marketing_controller import stats_mkt_leads

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = [
            ("Google Ads", 50, 20, 15, 10, 3, 2, Decimal("6.0")),
        ]
        db.execute.return_value = result_mock

        result = await stats_mkt_leads(db=db)
        assert len(result["campanhas"]) == 1
        assert result["campanhas"][0]["campanha"] == "Google Ads"
        assert result["campanhas"][0]["total"] == 50

    @pytest.mark.asyncio
    async def test_converter_lead_para_crm_not_found(self):
        from fastapi import HTTPException

        from modules.crm.controllers.marketing_controller import converter_lead_para_crm

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchone.return_value = None
        db.execute.return_value = result_mock

        with pytest.raises(HTTPException) as exc:
            await converter_lead_para_crm(lead_id=_uid(), db=db)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_converter_lead_already_converted(self):
        from modules.crm.controllers.marketing_controller import converter_lead_para_crm

        db = _mock_db()
        crm_lead_id = _uid()
        mkt_lead = _row(
            id=_uid(),
            name="Já Convertido",
            email="jc@test.com",
            phone=None,
            whatsapp=None,
            source="google",
            status="converted",
            campaign_id=None,
            crm_lead_id=crm_lead_id,
        )
        result_mock = MagicMock()
        result_mock.fetchone.return_value = mkt_lead
        db.execute.return_value = result_mock

        result = await converter_lead_para_crm(lead_id=_uid(), db=db)
        assert "ja convertido" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_converter_licitacao_para_crm(self):
        from modules.crm.controllers.marketing_controller import (
            LicitacaoConvertRequest,
            converter_licitacao_para_crm,
        )

        db = _mock_db()
        crm_id = _uid()
        row_mock = MagicMock()
        row_mock.__getitem__ = lambda self, i: crm_id
        result_mock = MagicMock()
        result_mock.fetchone.return_value = row_mock
        db.execute.return_value = result_mock

        data = LicitacaoConvertRequest(
            orgao="SEMSA Manaus",
            objeto="Vigilância hospitalar",
            valor=800000,
            numero_edital="PE-042/2026",
        )
        result = await converter_licitacao_para_crm(data=data, db=db)
        assert result["crm_lead_id"] == crm_id
        assert result["orgao"] == "SEMSA Manaus"
        db.commit.assert_awaited_once()


# ===========================================================================
# 10. CLIENT CONTROLLER — Lógica (mock DB)
# ===========================================================================


class TestClientControllerLogic:
    """Testa lógica dos endpoints de clientes com mock DB."""

    @pytest.mark.asyncio
    async def test_listar_clientes_empty(self):
        from modules.crm.controllers.client_controller import listar_clientes

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = []
        db.execute.return_value = result_mock

        result = await listar_clientes(db=db)
        assert result["items"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_resumo_clientes(self):
        from modules.crm.controllers.client_controller import resumo_clientes

        db = _mock_db()
        row = MagicMock()
        # ativos, inativos, inadimplentes, vip, originados_crm, mrr_total, segmentos
        row.__getitem__ = lambda self, i: [13, 2, 1, 3, 5, Decimal("272086.96"), 4][i]
        result_mock = MagicMock()
        result_mock.fetchone.return_value = row
        db.execute.return_value = result_mock

        result = await resumo_clientes(db=db)
        assert result["clientes_ativos"] == 13
        assert result["mrr_total"] == 272086.96

    @pytest.mark.asyncio
    async def test_detalhe_cliente_not_found(self):
        from fastapi import HTTPException

        from modules.crm.controllers.client_controller import detalhe_cliente

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchone.return_value = None
        db.execute.return_value = result_mock

        with pytest.raises(HTTPException) as exc:
            await detalhe_cliente(client_id=uuid.uuid4(), db=db)
        assert exc.value.status_code == 404


# ===========================================================================
# 11. CONTACT CONTROLLER — Lógica (mock DB)
# ===========================================================================


class TestContactControllerLogic:
    """Testa lógica dos endpoints de contatos com mock DB."""

    @pytest.mark.asyncio
    async def test_listar_contatos_empty(self):
        from modules.crm.controllers.contact_controller import listar_contatos

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = []
        db.execute.return_value = result_mock

        result = await listar_contatos(db=db)
        assert result["items"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_criar_contato(self):
        from modules.crm.controllers.contact_controller import ContactCreate, criar_contato

        db = _mock_db()
        contact_id = _uid()
        row_mock = MagicMock()
        row_mock.__getitem__ = lambda self, i: contact_id
        result_mock = MagicMock()
        result_mock.fetchone.return_value = row_mock
        db.execute.return_value = result_mock

        data = ContactCreate(
            client_id=_uid(),
            name="João Síndico",
            role="Síndico",
            email="joao@cond.com",
            is_primary=True,
        )
        result = await criar_contato(data=data, db=db)
        assert result["id"] == contact_id
        assert "Contato criado" in result["message"]

    @pytest.mark.asyncio
    async def test_deletar_contato(self):
        from modules.crm.controllers.contact_controller import deletar_contato

        db = _mock_db()
        result = await deletar_contato(contact_id=uuid.uuid4(), db=db)
        assert "removido" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_atividades_recentes_empty(self):
        from modules.crm.controllers.contact_controller import atividades_recentes

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchall.return_value = []
        db.execute.return_value = result_mock

        result = await atividades_recentes(db=db)
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_criar_atividade(self):
        from modules.crm.controllers.contact_controller import ActivityCreate, criar_atividade

        db = _mock_db()
        activity_id = _uid()
        row_mock = MagicMock()
        row_mock.__getitem__ = lambda self, i: activity_id
        result_mock = MagicMock()
        result_mock.fetchone.return_value = row_mock
        db.execute.return_value = result_mock

        data = ActivityCreate(
            client_id=_uid(),
            type="call",
            subject="Ligação comercial",
            description="Prospecção de novo serviço",
        )
        result = await criar_atividade(data=data, db=db)
        assert result["id"] == activity_id

    @pytest.mark.asyncio
    async def test_visao_360_not_found(self):
        from fastapi import HTTPException

        from modules.crm.controllers.contact_controller import visao_360_cliente

        db = _mock_db()
        result_mock = MagicMock()
        result_mock.fetchone.return_value = None
        db.execute.return_value = result_mock

        with pytest.raises(HTTPException) as exc:
            await visao_360_cliente(client_id=uuid.uuid4(), db=db)
        assert exc.value.status_code == 404


# ===========================================================================
# 12. PIPELINE SERVICE — Stage Conversion
# ===========================================================================


class TestPipelineServiceConversion:
    """Testes adicionais de conversão do pipeline."""

    @pytest.fixture
    def service(self):
        from modules.crm.services.pipeline_service import PipelineService

        return PipelineService()

    def _make_opp(self, stage_val, **kw):
        opp = MagicMock()
        opp.id = _uid()
        opp.stage = MagicMock(value=stage_val)
        opp.value = Decimal(str(kw.get("value", 50000)))
        opp.probability = kw.get("probability", 0.5)
        opp.is_active = True
        opp.is_won = kw.get("is_won", False)
        opp.is_lost = kw.get("is_lost", False)
        opp.created_at = kw.get("created_at", datetime.now() - timedelta(days=30))
        opp.updated_at = kw.get("updated_at", datetime.now())
        opp.expected_close_date = kw.get("expected_close_date", date.today() + timedelta(days=30))
        opp.actual_close_date = kw.get("actual_close_date")
        opp.loss_reason = kw.get("loss_reason")
        opp.competitor = kw.get("competitor")
        opp.owner_id = kw.get("owner_id", _uid())
        return opp

    def test_get_stage_conversion_rates(self, service):
        opps = [
            self._make_opp("prospecting"),
            self._make_opp("qualification"),
            self._make_opp("proposal"),
            self._make_opp("negotiation"),
            self._make_opp("closed_won", is_won=True),
        ]
        rates = service.get_stage_conversion_rates(opps)
        assert isinstance(rates, (list, dict))

    def test_calculate_avg_sales_cycle(self, service):
        opps = [
            self._make_opp(
                "closed_won",
                is_won=True,
                created_at=datetime.now() - timedelta(days=45),
                actual_close_date=date.today(),
            ),
            self._make_opp(
                "closed_won",
                is_won=True,
                created_at=datetime.now() - timedelta(days=30),
                actual_close_date=date.today(),
            ),
        ]
        cycle = service.calculate_avg_sales_cycle(opps)
        assert cycle > 0

    def test_calculate_sales_velocity(self, service):
        opps = [
            self._make_opp("proposal", value=Decimal("100000"), probability=0.7),
            self._make_opp(
                "closed_won",
                is_won=True,
                value=Decimal("80000"),
                created_at=datetime.now() - timedelta(days=30),
                actual_close_date=date.today(),
            ),
            self._make_opp("closed_lost", is_lost=True),
        ]
        velocity = service.calculate_sales_velocity(opps)
        assert isinstance(velocity, (int, float, Decimal))

    def test_empty_pipeline(self, service):
        weighted = service.calculate_weighted_pipeline([])
        assert weighted == 0
        rate = service.calculate_win_rate([])
        assert rate == 0


# ===========================================================================
# 13. DASHBOARD SERVICE — Edge Cases
# ===========================================================================


class TestDashboardServiceEdgeCases:
    """Edge cases do dashboard service."""

    @pytest.fixture
    def service(self):
        from modules.crm.services.dashboard_service import DashboardService

        return DashboardService()

    def test_kpis_empty_data(self, service):
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=[],
            commissions=[],
        )
        assert kpis.total_leads == 0
        assert kpis.total_opportunities == 0

    def test_funnel_empty(self, service):
        chart = service.generate_funnel_chart([])
        assert chart.chart_type == "funnel"

    def test_trends_empty(self, service):
        trends = service.generate_trends(
            data=[],
            date_field="created_at",
            value_field="count",
            period="month",
            periods_count=6,
        )
        assert isinstance(trends, list)

    def test_conversion_rates_empty(self, service):
        rates = service.calculate_conversion_rates([])
        assert isinstance(rates, dict)

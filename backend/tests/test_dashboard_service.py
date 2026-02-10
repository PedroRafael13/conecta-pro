"""
Testes para Dashboard Service.
Sprint 5 - Dashboard CRM.
"""

import uuid
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from modules.crm.models.commission import Commission, CommissionStatus
from modules.crm.models.lead import Lead, LeadSource, LeadStatus
from modules.crm.models.opportunity import Opportunity, OpportunityStage
from modules.crm.models.proposal import Proposal, ProposalStatus
from modules.crm.services.dashboard_service import (
    DashboardChart,
    DashboardKPIs,
    DashboardService,
    DashboardTrend,
    PerformanceMetrics,
)


class TestDashboardService:
    """Testes para DashboardService."""

    @pytest.fixture
    def service(self):
        """Fixture para o serviço."""
        return DashboardService()

    @pytest.fixture
    def seller_id(self):
        """ID de vendedor para testes."""
        return str(uuid.uuid4())

    @pytest.fixture
    def sample_leads(self, seller_id) -> list[Lead]:
        """Fixture para leads de exemplo."""
        now = datetime.utcnow()
        date.today()

        leads = []
        statuses = [
            LeadStatus.NEW.value,
            LeadStatus.CONTACTED.value,
            LeadStatus.QUALIFIED.value,
            LeadStatus.QUALIFIED.value,
            LeadStatus.WON.value,
            LeadStatus.WON.value,
            LeadStatus.LOST.value,
        ]

        for i, status in enumerate(statuses):
            lead = MagicMock(spec=Lead)
            lead.id = str(uuid.uuid4())
            lead.name = f"Lead {i + 1}"
            lead.status = status
            lead.assigned_to_id = seller_id if i < 5 else str(uuid.uuid4())
            lead.is_active = True

            # Variar datas de criação
            if i < 2:
                lead.created_at = now  # Hoje
            elif i < 4:
                lead.created_at = now - timedelta(days=3)  # Esta semana
            else:
                lead.created_at = now - timedelta(days=15)  # Este mês

            leads.append(lead)

        return leads

    @pytest.fixture
    def sample_opportunities(self, seller_id) -> list[Opportunity]:
        """Fixture para opportunities de exemplo."""
        now = datetime.utcnow()

        opportunities = []
        stages_values = [
            (OpportunityStage.QUALIFICATION.value, 10000, 0.2),
            (OpportunityStage.NEEDS_ANALYSIS.value, 15000, 0.4),
            (OpportunityStage.PROPOSAL.value, 20000, 0.6),
            (OpportunityStage.NEGOTIATION.value, 25000, 0.8),
            (OpportunityStage.CLOSED_WON.value, 30000, 1.0),
            (OpportunityStage.CLOSED_WON.value, 35000, 1.0),
            (OpportunityStage.CLOSED_LOST.value, 12000, 0.0),
        ]

        for i, (stage, value, prob) in enumerate(stages_values):
            opp = MagicMock(spec=Opportunity)
            opp.id = str(uuid.uuid4())
            opp.name = f"Opportunity {i + 1}"
            opp.stage = stage
            opp.value = value
            opp.probability = prob
            opp.weighted_value = value * prob
            opp.owner_id = seller_id if i < 5 else str(uuid.uuid4())
            opp.is_active = True
            opp.is_won = stage == OpportunityStage.CLOSED_WON.value
            opp.days_in_pipeline = 30 + i * 5
            opp.created_at = now - timedelta(days=30 + i)
            opp.updated_at = now - timedelta(days=i)

            opportunities.append(opp)

        return opportunities

    @pytest.fixture
    def sample_proposals(self) -> list[Proposal]:
        """Fixture para propostas de exemplo."""
        now = datetime.utcnow()

        proposals = []
        statuses_totals = [
            (ProposalStatus.DRAFT.value, 5000),
            (ProposalStatus.PENDING_APPROVAL.value, 8000),
            (ProposalStatus.SENT.value, 12000),
            (ProposalStatus.VIEWED.value, 15000),
            (ProposalStatus.ACCEPTED.value, 20000),
            (ProposalStatus.ACCEPTED.value, 25000),
            (ProposalStatus.REJECTED.value, 10000),
        ]

        for i, (status, total) in enumerate(statuses_totals):
            prop = MagicMock(spec=Proposal)
            prop.id = str(uuid.uuid4())
            prop.number = f"PROP-2024-{i + 1:05d}"
            prop.status = status
            prop.total = total
            prop.is_active = True
            prop.created_at = now - timedelta(days=i * 2)

            proposals.append(prop)

        return proposals

    @pytest.fixture
    def sample_commissions(self, seller_id) -> list[Commission]:
        """Fixture para comissões de exemplo."""
        now = datetime.utcnow()

        commissions = []
        statuses_values = [
            (CommissionStatus.PENDING.value, 1000),
            (CommissionStatus.PENDING.value, 1500),
            (CommissionStatus.APPROVED.value, 2000),
            (CommissionStatus.PAID.value, 2500),
            (CommissionStatus.PAID.value, 3000),
        ]

        for i, (status, value) in enumerate(statuses_values):
            comm = MagicMock(spec=Commission)
            comm.id = str(uuid.uuid4())
            comm.reference_number = f"COM-2024-{i + 1:05d}"
            comm.seller_id = seller_id
            comm.status = status
            comm.final_commission = value
            comm.is_active = True
            comm.created_at = now - timedelta(days=i * 3)

            commissions.append(comm)

        return commissions

    # ==================== Testes de KPIs ====================

    def test_calculate_kpis_empty_data(self, service):
        """Testa KPIs com dados vazios."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=[],
            commissions=[],
        )

        assert isinstance(kpis, DashboardKPIs)
        assert kpis.leads_total == 0
        assert kpis.opportunities_total == 0
        assert kpis.proposals_total == 0
        assert kpis.commissions_total == 0

    def test_calculate_kpis_leads(self, service, sample_leads):
        """Testa KPIs de leads."""
        kpis = service.calculate_kpis(
            leads=sample_leads,
            opportunities=[],
            proposals=[],
            commissions=[],
        )

        assert kpis.leads_total == 7
        assert kpis.leads_qualified == 2  # 2 QUALIFIED
        assert kpis.leads_conversion_rate > 0  # 2 WON de 7

    def test_calculate_kpis_leads_today(self, service, sample_leads):
        """Testa contagem de leads de hoje."""
        kpis = service.calculate_kpis(
            leads=sample_leads,
            opportunities=[],
            proposals=[],
            commissions=[],
        )

        assert kpis.leads_new_today == 2  # 2 criados hoje

    def test_calculate_kpis_opportunities(self, service, sample_opportunities):
        """Testa KPIs de opportunities."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=sample_opportunities,
            proposals=[],
            commissions=[],
        )

        assert kpis.opportunities_total == 7
        assert kpis.opportunities_won == 2  # 2 CLOSED_WON
        assert kpis.opportunities_lost == 1  # 1 CLOSED_LOST
        assert kpis.opportunities_open == 4  # 4 em estágios abertos

    def test_calculate_kpis_win_rate(self, service, sample_opportunities):
        """Testa cálculo de win rate."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=sample_opportunities,
            proposals=[],
            commissions=[],
        )

        # 2 won / (2 won + 1 lost) = 66.67%
        expected_win_rate = (2 / 3) * 100
        assert abs(kpis.opportunities_win_rate - expected_win_rate) < 0.01

    def test_calculate_kpis_pipeline_value(self, service, sample_opportunities):
        """Testa cálculo de valor do pipeline."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=sample_opportunities,
            proposals=[],
            commissions=[],
        )

        # Soma dos valores das opportunities abertas
        # 10000 + 15000 + 20000 + 25000 = 70000
        assert kpis.pipeline_value == 70000

    def test_calculate_kpis_weighted_pipeline(self, service, sample_opportunities):
        """Testa cálculo de pipeline ponderado."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=sample_opportunities,
            proposals=[],
            commissions=[],
        )

        # Soma dos weighted_values das opportunities abertas
        # 10000*0.2 + 15000*0.4 + 20000*0.6 + 25000*0.8 = 40000
        assert kpis.weighted_pipeline == 40000

    def test_calculate_kpis_avg_deal_size(self, service, sample_opportunities):
        """Testa cálculo de tamanho médio de negócio."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=sample_opportunities,
            proposals=[],
            commissions=[],
        )

        # Média dos valores ganhos: (30000 + 35000) / 2 = 32500
        assert kpis.avg_deal_size == 32500

    def test_calculate_kpis_proposals(self, service, sample_proposals):
        """Testa KPIs de propostas."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=sample_proposals,
            commissions=[],
        )

        assert kpis.proposals_total == 7
        assert kpis.proposals_pending == 2  # DRAFT + PENDING_APPROVAL
        assert kpis.proposals_sent == 2  # SENT + VIEWED
        assert kpis.proposals_accepted == 2  # 2 ACCEPTED

    def test_calculate_kpis_proposal_acceptance_rate(self, service, sample_proposals):
        """Testa taxa de aceitação de propostas."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=sample_proposals,
            commissions=[],
        )

        # 2 accepted / (2 accepted + 1 rejected) = 66.67%
        expected_rate = (2 / 3) * 100
        assert abs(kpis.proposals_acceptance_rate - expected_rate) < 0.01

    def test_calculate_kpis_proposal_values(self, service, sample_proposals):
        """Testa valores de propostas."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=sample_proposals,
            commissions=[],
        )

        # Total: 5000+8000+12000+15000+20000+25000+10000 = 95000
        assert kpis.proposals_total_value == 95000
        # Accepted: 20000 + 25000 = 45000
        assert kpis.proposals_accepted_value == 45000

    def test_calculate_kpis_commissions(self, service, sample_commissions):
        """Testa KPIs de comissões."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=[],
            commissions=sample_commissions,
        )

        assert kpis.commissions_total == 5
        assert kpis.commissions_pending == 2  # 2 PENDING
        assert kpis.commissions_paid == 2  # 2 PAID

    def test_calculate_kpis_commission_values(self, service, sample_commissions):
        """Testa valores de comissões."""
        kpis = service.calculate_kpis(
            leads=[],
            opportunities=[],
            proposals=[],
            commissions=sample_commissions,
        )

        # Total: 1000+1500+2000+2500+3000 = 10000
        assert kpis.commissions_total_value == 10000
        # Pending: 1000+1500 = 2500
        assert kpis.commissions_pending_value == 2500
        # Paid: 2500+3000 = 5500
        assert kpis.commissions_paid_value == 5500

    def test_calculate_kpis_full(
        self, service, sample_leads, sample_opportunities, sample_proposals, sample_commissions
    ):
        """Testa KPIs com todos os dados."""
        kpis = service.calculate_kpis(
            leads=sample_leads,
            opportunities=sample_opportunities,
            proposals=sample_proposals,
            commissions=sample_commissions,
        )

        assert kpis.leads_total == 7
        assert kpis.opportunities_total == 7
        assert kpis.proposals_total == 7
        assert kpis.commissions_total == 5

    # ==================== Testes de Funil ====================

    def test_generate_funnel_chart_empty(self, service):
        """Testa funil com dados vazios."""
        chart = service.generate_funnel_chart([])

        assert isinstance(chart, DashboardChart)
        assert chart.chart_type == "funnel"
        assert chart.title == "Funil de Vendas"
        assert len(chart.labels) == 5
        assert all(v == 0 for v in chart.datasets[0]["data"])

    def test_generate_funnel_chart(self, service, sample_opportunities):
        """Testa geração de funil de vendas."""
        chart = service.generate_funnel_chart(sample_opportunities)

        assert chart.chart_type == "funnel"
        assert "Qualificação" in chart.labels
        assert "Negociação" in chart.labels
        assert "Ganho" in chart.labels

        # Verificar contagens
        data = chart.datasets[0]["data"]
        assert data[0] == 1  # QUALIFICATION
        assert data[1] == 1  # NEEDS_ANALYSIS
        assert data[2] == 1  # PROPOSAL
        assert data[3] == 1  # NEGOTIATION
        assert data[4] == 2  # CLOSED_WON

    # ==================== Testes de Tendências ====================

    def test_generate_trends_empty(self, service):
        """Testa tendências com dados vazios."""
        trends = service.generate_trends(
            data=[],
            date_field="created_at",
            value_field="count",
            period="month",
            periods_count=6,
        )

        assert len(trends) == 6
        assert all(t.value == 0 for t in trends)

    def test_generate_trends_monthly(self, service, sample_leads):
        """Testa tendências mensais."""
        trends = service.generate_trends(
            data=sample_leads,
            date_field="created_at",
            value_field="count",
            period="month",
            periods_count=3,
        )

        assert len(trends) == 3
        assert all(isinstance(t, DashboardTrend) for t in trends)
        # O último período deve ter os leads de hoje
        assert trends[-1].value > 0

    def test_generate_trends_weekly(self, service, sample_leads):
        """Testa tendências semanais."""
        trends = service.generate_trends(
            data=sample_leads,
            date_field="created_at",
            value_field="count",
            period="week",
            periods_count=4,
        )

        assert len(trends) == 4
        # Formato de período semanal
        assert "-W" in trends[0].period

    def test_generate_trends_daily(self, service, sample_leads):
        """Testa tendências diárias."""
        trends = service.generate_trends(
            data=sample_leads,
            date_field="created_at",
            value_field="count",
            period="day",
            periods_count=7,
        )

        assert len(trends) == 7

    def test_generate_trends_change_percent(self, service):
        """Testa cálculo de mudança percentual."""
        now = datetime.utcnow()

        # Criar dados com valores conhecidos
        data = []
        for i in range(60):
            item = MagicMock()
            item.created_at = now - timedelta(days=i)
            item.value = 100
            data.append(item)

        trends = service.generate_trends(
            data=data,
            date_field="created_at",
            value_field="count",
            period="month",
            periods_count=3,
        )

        # Verificar que change_percent é calculado
        # (exceto para o primeiro período)
        assert trends[0].change_percent is None
        for t in trends[1:]:
            if t.previous_value and t.previous_value > 0:
                assert t.change_percent is not None

    # ==================== Testes de Performance ====================

    def test_calculate_seller_performance_empty(self, service, seller_id):
        """Testa performance com dados vazios."""
        metrics = service.calculate_seller_performance(
            seller_id=seller_id,
            leads=[],
            opportunities=[],
            commissions=[],
        )

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.seller_id == seller_id
        assert metrics.leads_assigned == 0
        assert metrics.total_sales == 0

    def test_calculate_seller_performance(
        self, service, seller_id, sample_leads, sample_opportunities, sample_commissions
    ):
        """Testa cálculo de performance do vendedor."""
        metrics = service.calculate_seller_performance(
            seller_id=seller_id,
            leads=sample_leads,
            opportunities=sample_opportunities,
            commissions=sample_commissions,
            seller_name="João Silva",
        )

        assert metrics.seller_id == seller_id
        assert metrics.seller_name == "João Silva"
        assert metrics.leads_assigned == 5  # 5 leads atribuídos
        assert metrics.leads_converted > 0

    def test_calculate_seller_performance_with_target(
        self, service, seller_id, sample_leads, sample_opportunities, sample_commissions
    ):
        """Testa performance com meta."""
        metrics = service.calculate_seller_performance(
            seller_id=seller_id,
            leads=sample_leads,
            opportunities=sample_opportunities,
            commissions=sample_commissions,
            target=100000,
        )

        assert metrics.target == 100000
        assert metrics.target_percentage is not None
        assert metrics.target_percentage >= 0

    def test_calculate_seller_conversion_rate(
        self, service, seller_id, sample_leads, sample_opportunities, sample_commissions
    ):
        """Testa taxa de conversão do vendedor."""
        metrics = service.calculate_seller_performance(
            seller_id=seller_id,
            leads=sample_leads,
            opportunities=sample_opportunities,
            commissions=sample_commissions,
        )

        if metrics.leads_assigned > 0:
            expected_rate = (metrics.leads_converted / metrics.leads_assigned) * 100
            assert abs(metrics.conversion_rate - expected_rate) < 0.01

    # ==================== Testes de Top Performers ====================

    def test_get_top_performers_empty(self, service):
        """Testa top performers com dados vazios."""
        top = service.get_top_performers(
            leads=[],
            opportunities=[],
            commissions=[],
            sellers={},
            limit=5,
        )

        assert len(top) == 0

    def test_get_top_performers(self, service, sample_leads, sample_opportunities, sample_commissions):
        """Testa busca de top performers."""
        sellers = {
            str(uuid.uuid4()): "Vendedor 1",
            str(uuid.uuid4()): "Vendedor 2",
            str(uuid.uuid4()): "Vendedor 3",
        }

        top = service.get_top_performers(
            leads=sample_leads,
            opportunities=sample_opportunities,
            commissions=sample_commissions,
            sellers=sellers,
            limit=2,
        )

        assert len(top) <= 2
        # Verificar ordenação por vendas (decrescente)
        if len(top) >= 2:
            assert top[0].total_sales >= top[1].total_sales

    def test_get_top_performers_limit(self, service, sample_leads, sample_opportunities, sample_commissions):
        """Testa limite de top performers."""
        sellers = {str(uuid.uuid4()): f"Vendedor {i}" for i in range(10)}

        top = service.get_top_performers(
            leads=sample_leads,
            opportunities=sample_opportunities,
            commissions=sample_commissions,
            sellers=sellers,
            limit=3,
        )

        assert len(top) <= 3

    # ==================== Testes de Gráficos ====================

    def test_generate_pie_chart_empty(self, service):
        """Testa gráfico de pizza com dados vazios."""
        chart = service.generate_pie_chart_by_status(
            items=[],
            status_field="status",
            title="Teste",
        )

        assert isinstance(chart, DashboardChart)
        assert chart.chart_type == "pie"
        assert chart.title == "Teste"
        assert len(chart.labels) == 0

    def test_generate_pie_chart_leads(self, service, sample_leads):
        """Testa gráfico de pizza de leads por status."""
        chart = service.generate_pie_chart_by_status(
            items=sample_leads,
            status_field="status",
            title="Leads por Status",
        )

        assert chart.chart_type == "pie"
        assert chart.title == "Leads por Status"
        assert len(chart.labels) > 0
        assert sum(chart.datasets[0]["data"]) == len(sample_leads)

    def test_generate_pie_chart_opportunities(self, service, sample_opportunities):
        """Testa gráfico de pizza de opportunities por estágio."""
        chart = service.generate_pie_chart_by_status(
            items=sample_opportunities,
            status_field="stage",
            title="Opportunities por Estágio",
        )

        assert len(chart.labels) > 0
        assert sum(chart.datasets[0]["data"]) == len(sample_opportunities)

    # ==================== Testes de Taxas de Conversão ====================

    def test_calculate_conversion_rates_empty(self, service):
        """Testa taxas de conversão com dados vazios."""
        rates = service.calculate_conversion_rates([])

        assert isinstance(rates, dict)
        assert len(rates) > 0
        assert all(v == 0.0 for v in rates.values())

    def test_calculate_conversion_rates(self, service):
        """Testa cálculo de taxas de conversão."""
        # Criar opportunities apenas nos estágios do funil (sem CLOSED_LOST)
        opportunities = []
        stages = [
            OpportunityStage.QUALIFICATION.value,
            OpportunityStage.NEEDS_ANALYSIS.value,
            OpportunityStage.PROPOSAL.value,
            OpportunityStage.NEGOTIATION.value,
            OpportunityStage.CLOSED_WON.value,
        ]
        for _i, stage in enumerate(stages):
            opp = MagicMock(spec=Opportunity)
            opp.id = str(uuid.uuid4())
            opp.stage = stage
            opp.is_active = True
            opportunities.append(opp)

        rates = service.calculate_conversion_rates(opportunities)

        assert isinstance(rates, dict)
        # Verificar chaves esperadas
        assert "qualification_to_needs_analysis" in rates
        assert "needs_analysis_to_proposal" in rates
        assert "proposal_to_negotiation" in rates
        assert "negotiation_to_closed_won" in rates

    def test_calculate_conversion_rates_values(self, service):
        """Testa valores das taxas de conversão."""
        # Criar opportunities apenas nos estágios do funil (sem CLOSED_LOST)
        opportunities = []
        stages = [
            OpportunityStage.QUALIFICATION.value,
            OpportunityStage.NEEDS_ANALYSIS.value,
            OpportunityStage.PROPOSAL.value,
            OpportunityStage.CLOSED_WON.value,
        ]
        for stage in stages:
            opp = MagicMock(spec=Opportunity)
            opp.id = str(uuid.uuid4())
            opp.stage = stage
            opp.is_active = True
            opportunities.append(opp)

        rates = service.calculate_conversion_rates(opportunities)

        # Todas as taxas devem estar entre 0 e 100
        for rate in rates.values():
            assert 0 <= rate <= 100


class TestDashboardKPIsModel:
    """Testes para o modelo DashboardKPIs."""

    def test_default_values(self):
        """Testa valores padrão do modelo."""
        kpis = DashboardKPIs()

        assert kpis.leads_total == 0
        assert kpis.opportunities_total == 0
        assert kpis.proposals_total == 0
        assert kpis.commissions_total == 0
        assert kpis.leads_conversion_rate == 0.0
        assert kpis.opportunities_win_rate == 0.0

    def test_custom_values(self):
        """Testa valores customizados."""
        kpis = DashboardKPIs(
            leads_total=100,
            leads_qualified=30,
            leads_conversion_rate=15.5,
            pipeline_value=500000.0,
        )

        assert kpis.leads_total == 100
        assert kpis.leads_qualified == 30
        assert kpis.leads_conversion_rate == 15.5
        assert kpis.pipeline_value == 500000.0


class TestDashboardTrendModel:
    """Testes para o modelo DashboardTrend."""

    def test_creation(self):
        """Testa criação de trend."""
        trend = DashboardTrend(
            period="2024-01",
            value=100.0,
        )

        assert trend.period == "2024-01"
        assert trend.value == 100.0
        assert trend.previous_value is None
        assert trend.change_percent is None

    def test_with_change(self):
        """Testa trend com mudança."""
        trend = DashboardTrend(
            period="2024-02",
            value=120.0,
            previous_value=100.0,
            change_percent=20.0,
        )

        assert trend.value == 120.0
        assert trend.previous_value == 100.0
        assert trend.change_percent == 20.0


class TestDashboardChartModel:
    """Testes para o modelo DashboardChart."""

    def test_creation(self):
        """Testa criação de chart."""
        chart = DashboardChart(
            chart_type="bar",
            title="Vendas por Mês",
            labels=["Jan", "Fev", "Mar"],
            datasets=[{"data": [100, 150, 200]}],
        )

        assert chart.chart_type == "bar"
        assert chart.title == "Vendas por Mês"
        assert len(chart.labels) == 3
        assert chart.datasets[0]["data"] == [100, 150, 200]


class TestPerformanceMetricsModel:
    """Testes para o modelo PerformanceMetrics."""

    def test_default_values(self):
        """Testa valores padrão."""
        metrics = PerformanceMetrics(seller_id="seller-123")

        assert metrics.seller_id == "seller-123"
        assert metrics.seller_name is None
        assert metrics.leads_assigned == 0
        assert metrics.total_sales == 0.0
        assert metrics.target is None

    def test_with_target(self):
        """Testa métricas com meta."""
        metrics = PerformanceMetrics(
            seller_id="seller-123",
            seller_name="João",
            total_sales=75000.0,
            target=100000.0,
            target_percentage=75.0,
        )

        assert metrics.total_sales == 75000.0
        assert metrics.target == 100000.0
        assert metrics.target_percentage == 75.0

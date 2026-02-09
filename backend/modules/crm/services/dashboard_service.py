"""
Service para Dashboard e Analytics do CRM.
Centraliza KPIs, métricas e análises de desempenho comercial.
"""

from datetime import date, timedelta

from pydantic import BaseModel

from modules.crm.models.commission import Commission, CommissionStatus
from modules.crm.models.lead import Lead, LeadStatus
from modules.crm.models.opportunity import Opportunity, OpportunityStage
from modules.crm.models.proposal import Proposal, ProposalStatus


class DashboardKPIs(BaseModel):
    """KPIs principais do CRM."""

    # Leads
    leads_total: int = 0
    leads_new_today: int = 0
    leads_new_week: int = 0
    leads_new_month: int = 0
    leads_qualified: int = 0
    leads_conversion_rate: float = 0.0

    # Opportunities
    opportunities_total: int = 0
    opportunities_open: int = 0
    opportunities_won: int = 0
    opportunities_lost: int = 0
    opportunities_win_rate: float = 0.0
    pipeline_value: float = 0.0
    weighted_pipeline: float = 0.0
    avg_deal_size: float = 0.0
    avg_sales_cycle_days: float = 0.0

    # Proposals
    proposals_total: int = 0
    proposals_pending: int = 0
    proposals_sent: int = 0
    proposals_accepted: int = 0
    proposals_acceptance_rate: float = 0.0
    proposals_total_value: float = 0.0
    proposals_accepted_value: float = 0.0

    # Commissions
    commissions_total: int = 0
    commissions_pending: int = 0
    commissions_paid: int = 0
    commissions_total_value: float = 0.0
    commissions_pending_value: float = 0.0
    commissions_paid_value: float = 0.0


class DashboardTrend(BaseModel):
    """Tendência de um métrica ao longo do tempo."""

    period: str  # "2024-01", "2024-W01", "2024-01-15"
    value: float
    previous_value: float | None = None
    change_percent: float | None = None


class DashboardChart(BaseModel):
    """Dados para gráfico."""

    chart_type: str  # bar, line, pie, funnel
    title: str
    labels: list[str]
    datasets: list[dict]


class PerformanceMetrics(BaseModel):
    """Métricas de performance de vendedor."""

    seller_id: str
    seller_name: str | None = None
    leads_assigned: int = 0
    leads_converted: int = 0
    conversion_rate: float = 0.0
    opportunities_created: int = 0
    opportunities_won: int = 0
    win_rate: float = 0.0
    total_sales: float = 0.0
    avg_deal_size: float = 0.0
    total_commissions: float = 0.0
    target: float | None = None
    target_percentage: float | None = None


class DashboardService:
    """Service para Dashboard e Analytics do CRM."""

    def calculate_kpis(  # pylint: disable=too-many-locals
        self,
        leads: list[Lead],
        opportunities: list[Opportunity],
        proposals: list[Proposal],
        commissions: list[Commission],
        date_from: date | None = None,  # pylint: disable=unused-argument
        date_to: date | None = None,  # pylint: disable=unused-argument
    ) -> DashboardKPIs:
        """
        Calcula todos os KPIs principais do CRM.

        Args:
            leads: Lista de leads
            opportunities: Lista de opportunities
            proposals: Lista de propostas
            commissions: Lista de comissões
            date_from: Data inicial para filtro
            date_to: Data final para filtro

        Returns:
            KPIs calculados
        """
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        kpis = DashboardKPIs()

        # ========== Leads KPIs ==========
        kpis.leads_total = len(leads)

        kpis.leads_new_today = sum(1 for lead in leads if lead.created_at.date() == today)

        kpis.leads_new_week = sum(1 for lead in leads if lead.created_at.date() >= week_ago)

        kpis.leads_new_month = sum(1 for lead in leads if lead.created_at.date() >= month_ago)

        kpis.leads_qualified = sum(1 for lead in leads if lead.status in (LeadStatus.QUALIFIED.value, "qualified"))

        converted_leads = sum(1 for lead in leads if lead.status in (LeadStatus.WON.value, "won"))
        if kpis.leads_total > 0:
            kpis.leads_conversion_rate = (converted_leads / kpis.leads_total) * 100

        # ========== Opportunities KPIs ==========
        kpis.opportunities_total = len(opportunities)

        kpis.opportunities_open = sum(
            1
            for opp in opportunities
            if opp.stage
            not in (
                OpportunityStage.CLOSED_WON.value,
                OpportunityStage.CLOSED_LOST.value,
                "closed_won",
                "closed_lost",
            )
        )

        kpis.opportunities_won = sum(
            1 for opp in opportunities if opp.stage in (OpportunityStage.CLOSED_WON.value, "closed_won")
        )

        kpis.opportunities_lost = sum(
            1 for opp in opportunities if opp.stage in (OpportunityStage.CLOSED_LOST.value, "closed_lost")
        )

        closed_total = kpis.opportunities_won + kpis.opportunities_lost
        if closed_total > 0:
            kpis.opportunities_win_rate = (kpis.opportunities_won / closed_total) * 100

        # Pipeline value (apenas opportunities abertas)
        open_opps = [
            opp
            for opp in opportunities
            if opp.stage
            not in (
                OpportunityStage.CLOSED_WON.value,
                OpportunityStage.CLOSED_LOST.value,
                "closed_won",
                "closed_lost",
            )
        ]
        kpis.pipeline_value = sum(opp.value for opp in open_opps if hasattr(opp, "value"))

        # Weighted pipeline
        kpis.weighted_pipeline = sum(opp.weighted_value for opp in open_opps if hasattr(opp, "weighted_value"))

        # Average deal size (apenas ganhos)
        won_values = [
            opp.value
            for opp in opportunities
            if opp.stage in (OpportunityStage.CLOSED_WON.value, "closed_won") and hasattr(opp, "value")
        ]
        if won_values:
            kpis.avg_deal_size = sum(won_values) / len(won_values)

        # Average sales cycle
        cycles = [
            opp.days_in_pipeline
            for opp in opportunities
            if opp.stage
            in (
                OpportunityStage.CLOSED_WON.value,
                OpportunityStage.CLOSED_LOST.value,
                "closed_won",
                "closed_lost",
            )
            and hasattr(opp, "days_in_pipeline")
        ]
        if cycles:
            kpis.avg_sales_cycle_days = sum(cycles) / len(cycles)

        # ========== Proposals KPIs ==========
        kpis.proposals_total = len(proposals)

        kpis.proposals_pending = sum(
            1
            for p in proposals
            if p.status
            in (
                ProposalStatus.DRAFT.value,
                ProposalStatus.PENDING_REVIEW.value,
                ProposalStatus.PENDING_APPROVAL.value,
                "draft",
                "pending_review",
                "pending_approval",
            )
        )

        kpis.proposals_sent = sum(
            1
            for p in proposals
            if p.status
            in (
                ProposalStatus.SENT.value,
                ProposalStatus.VIEWED.value,
                "sent",
                "viewed",
            )
        )

        kpis.proposals_accepted = sum(1 for p in proposals if p.status in (ProposalStatus.ACCEPTED.value, "accepted"))

        responded = sum(
            1
            for p in proposals
            if p.status
            in (
                ProposalStatus.ACCEPTED.value,
                ProposalStatus.REJECTED.value,
                "accepted",
                "rejected",
            )
        )
        if responded > 0:
            kpis.proposals_acceptance_rate = (kpis.proposals_accepted / responded) * 100

        kpis.proposals_total_value = sum(p.total for p in proposals if hasattr(p, "total"))
        kpis.proposals_accepted_value = sum(
            p.total
            for p in proposals
            if p.status in (ProposalStatus.ACCEPTED.value, "accepted") and hasattr(p, "total")
        )

        # ========== Commissions KPIs ==========
        kpis.commissions_total = len(commissions)

        kpis.commissions_pending = sum(
            1 for c in commissions if c.status in (CommissionStatus.PENDING.value, "pending")
        )

        kpis.commissions_paid = sum(1 for c in commissions if c.status in (CommissionStatus.PAID.value, "paid"))

        kpis.commissions_total_value = sum(c.final_commission for c in commissions if hasattr(c, "final_commission"))

        kpis.commissions_pending_value = sum(
            c.final_commission
            for c in commissions
            if c.status in (CommissionStatus.PENDING.value, "pending") and hasattr(c, "final_commission")
        )

        kpis.commissions_paid_value = sum(
            c.final_commission
            for c in commissions
            if c.status in (CommissionStatus.PAID.value, "paid") and hasattr(c, "final_commission")
        )

        return kpis

    def generate_funnel_chart(
        self,
        opportunities: list[Opportunity],
    ) -> DashboardChart:
        """
        Gera dados para gráfico de funil de vendas.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Dados do gráfico
        """
        stages = [
            ("Qualificação", OpportunityStage.QUALIFICATION.value),
            ("Análise", OpportunityStage.NEEDS_ANALYSIS.value),
            ("Proposta", OpportunityStage.PROPOSAL.value),
            ("Negociação", OpportunityStage.NEGOTIATION.value),
            ("Ganho", OpportunityStage.CLOSED_WON.value),
        ]

        labels = []
        values = []

        for label, stage in stages:
            count = sum(1 for opp in opportunities if opp.stage == stage)
            labels.append(label)
            values.append(count)

        return DashboardChart(
            chart_type="funnel",
            title="Funil de Vendas",
            labels=labels,
            datasets=[{"data": values}],
        )

    def generate_trends(  # pylint: disable=too-many-locals
        self,
        data: list,
        date_field: str,
        value_field: str,
        period: str = "month",  # day, week, month
        periods_count: int = 6,
    ) -> list[DashboardTrend]:
        """
        Gera tendências de uma métrica ao longo do tempo.

        Args:
            data: Lista de objetos
            date_field: Nome do campo de data
            value_field: Nome do campo de valor ou 'count' para contagem
            period: Tipo de período (day, week, month)
            periods_count: Número de períodos

        Returns:
            Lista de tendências
        """
        today = date.today()
        trends = []

        for i in range(periods_count - 1, -1, -1):
            if period == "month":
                # Calcular mês
                month = today.month - i
                year = today.year
                while month <= 0:
                    month += 12
                    year -= 1
                period_start = date(year, month, 1)
                if month == 12:
                    period_end = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    period_end = date(year, month + 1, 1) - timedelta(days=1)
                period_label = f"{year}-{month:02d}"
            elif period == "week":
                period_end = today - timedelta(days=i * 7)
                period_start = period_end - timedelta(days=6)
                period_label = f"{period_start.year}-W{period_start.isocalendar()[1]:02d}"
            else:  # day
                period_date = today - timedelta(days=i)
                period_start = period_date
                period_end = period_date
                period_label = period_date.isoformat()

            # Filtrar dados do período
            period_data = [item for item in data if period_start <= getattr(item, date_field).date() <= period_end]

            # Calcular valor
            if value_field == "count":
                value = len(period_data)
            else:
                value = sum(getattr(item, value_field, 0) for item in period_data)

            trend = DashboardTrend(
                period=period_label,
                value=value,
            )

            # Calcular mudança em relação ao período anterior
            if trends:
                prev = trends[-1]
                if prev.value > 0:
                    trend.previous_value = prev.value
                    trend.change_percent = ((value - prev.value) / prev.value) * 100

            trends.append(trend)

        return trends

    def calculate_seller_performance(
        self,
        seller_id: str,
        leads: list[Lead],
        opportunities: list[Opportunity],
        commissions: list[Commission],
        seller_name: str | None = None,
        target: float | None = None,
    ) -> PerformanceMetrics:
        """
        Calcula métricas de performance de um vendedor.

        Args:
            seller_id: ID do vendedor
            leads: Leads do vendedor
            opportunities: Opportunities do vendedor
            commissions: Comissões do vendedor
            seller_name: Nome do vendedor
            target: Meta de vendas

        Returns:
            Métricas de performance
        """
        # Filtrar por vendedor
        seller_leads = [lead for lead in leads if lead.assigned_to_id == seller_id]
        seller_opps = [o for o in opportunities if o.owner_id == seller_id]
        seller_comms = [c for c in commissions if c.seller_id == seller_id]

        metrics = PerformanceMetrics(
            seller_id=seller_id,
            seller_name=seller_name,
        )

        # Leads
        metrics.leads_assigned = len(seller_leads)
        metrics.leads_converted = sum(1 for lead in seller_leads if lead.status in (LeadStatus.WON.value, "won"))
        if metrics.leads_assigned > 0:
            metrics.conversion_rate = (metrics.leads_converted / metrics.leads_assigned) * 100

        # Opportunities
        metrics.opportunities_created = len(seller_opps)
        metrics.opportunities_won = sum(
            1 for o in seller_opps if o.stage in (OpportunityStage.CLOSED_WON.value, "closed_won")
        )

        closed = sum(
            1
            for o in seller_opps
            if o.stage
            in (
                OpportunityStage.CLOSED_WON.value,
                OpportunityStage.CLOSED_LOST.value,
                "closed_won",
                "closed_lost",
            )
        )
        if closed > 0:
            metrics.win_rate = (metrics.opportunities_won / closed) * 100

        # Sales
        won_values = [
            o.value
            for o in seller_opps
            if o.stage in (OpportunityStage.CLOSED_WON.value, "closed_won") and hasattr(o, "value")
        ]
        metrics.total_sales = sum(won_values)
        if won_values:
            metrics.avg_deal_size = metrics.total_sales / len(won_values)

        # Commissions
        metrics.total_commissions = sum(c.final_commission for c in seller_comms if hasattr(c, "final_commission"))

        # Target
        if target:
            metrics.target = target
            if target > 0:
                metrics.target_percentage = (metrics.total_sales / target) * 100

        return metrics

    def get_top_performers(
        self,
        leads: list[Lead],
        opportunities: list[Opportunity],
        commissions: list[Commission],
        sellers: dict[str, str],  # {seller_id: seller_name}
        limit: int = 5,
    ) -> list[PerformanceMetrics]:
        """
        Retorna os top performers.

        Args:
            leads: Todos os leads
            opportunities: Todas as opportunities
            commissions: Todas as comissões
            sellers: Dict de vendedores
            limit: Número de vendedores a retornar

        Returns:
            Lista de métricas ordenada por vendas
        """
        performances = []

        for seller_id, seller_name in sellers.items():
            metrics = self.calculate_seller_performance(
                seller_id=seller_id,
                leads=leads,
                opportunities=opportunities,
                commissions=commissions,
                seller_name=seller_name,
            )
            performances.append(metrics)

        # Ordenar por total de vendas
        performances.sort(key=lambda p: p.total_sales, reverse=True)

        return performances[:limit]

    def generate_pie_chart_by_status(
        self,
        items: list,
        status_field: str = "status",
        title: str = "Distribuição por Status",
    ) -> DashboardChart:
        """
        Gera gráfico de pizza por status.

        Args:
            items: Lista de itens
            status_field: Nome do campo de status
            title: Título do gráfico

        Returns:
            Dados do gráfico
        """
        status_counts = {}
        for item in items:
            status = getattr(item, status_field, "unknown")
            if hasattr(status, "value"):
                status = status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        labels = list(status_counts.keys())
        values = list(status_counts.values())

        return DashboardChart(
            chart_type="pie",
            title=title,
            labels=labels,
            datasets=[{"data": values}],
        )

    def calculate_conversion_rates(
        self,
        opportunities: list[Opportunity],
    ) -> dict:
        """
        Calcula taxas de conversão entre estágios do pipeline.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Dict com taxas por transição
        """
        stages_order = [
            OpportunityStage.QUALIFICATION.value,
            OpportunityStage.NEEDS_ANALYSIS.value,
            OpportunityStage.PROPOSAL.value,
            OpportunityStage.NEGOTIATION.value,
            OpportunityStage.CLOSED_WON.value,
        ]

        stage_counts = {}
        for stage in stages_order:
            stage_counts[stage] = sum(1 for o in opportunities if o.stage == stage)

        # Também contar quantos chegaram em cada estágio
        # (inclui quem já passou por ele)
        reached_stage = {}
        for i, stage in enumerate(stages_order):
            reached = sum(1 for o in opportunities if stages_order.index(o.stage) >= i)
            reached_stage[stage] = reached

        rates = {}
        for i in range(len(stages_order) - 1):
            from_stage = stages_order[i]
            to_stage = stages_order[i + 1]
            key = f"{from_stage}_to_{to_stage}"

            if reached_stage[from_stage] > 0:
                rate = (reached_stage[to_stage] / reached_stage[from_stage]) * 100
            else:
                rate = 0.0

            rates[key] = round(rate, 1)

        return rates


# Instância singleton
dashboard_service = DashboardService()

"""
Controller (endpoints) para Dashboard CRM.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.crm.models.commission import Commission
from modules.crm.models.lead import Lead
from modules.crm.models.opportunity import Opportunity
from modules.crm.models.proposal import Proposal
from modules.crm.services.dashboard_service import (
    DashboardChart,
    DashboardKPIs,
    DashboardService,
    DashboardTrend,
    PerformanceMetrics,
)

router = APIRouter(prefix="/dashboard", tags=["CRM - Dashboard"])


async def _get_all_leads(db: AsyncSession) -> list[Lead]:
    """Busca todos os leads ativos."""
    result = await db.execute(select(Lead).where(Lead.is_active.is_(True)))
    return list(result.scalars().all())


async def _get_all_opportunities(db: AsyncSession) -> list[Opportunity]:
    """Busca todas as opportunities ativas."""
    result = await db.execute(select(Opportunity).where(Opportunity.is_active.is_(True)))
    return list(result.scalars().all())


async def _get_all_proposals(db: AsyncSession) -> list[Proposal]:
    """Busca todas as propostas ativas."""
    result = await db.execute(select(Proposal).where(Proposal.is_active.is_(True)))
    return list(result.scalars().all())


async def _get_all_commissions(db: AsyncSession) -> list[Commission]:
    """Busca todas as comissões ativas."""
    result = await db.execute(select(Commission).where(Commission.is_active.is_(True)))
    return list(result.scalars().all())


@router.get("/kpis", response_model=DashboardKPIs)
async def get_dashboard_kpis(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    date_from: date | None = None,
    date_to: date | None = None,
) -> DashboardKPIs:
    """
    Retorna todos os KPIs principais do CRM.

    Inclui métricas de leads, opportunities, propostas e comissões.
    """
    service = DashboardService()

    leads = await _get_all_leads(db)
    opportunities = await _get_all_opportunities(db)
    proposals = await _get_all_proposals(db)
    commissions = await _get_all_commissions(db)

    kpis = service.calculate_kpis(
        leads=leads,
        opportunities=opportunities,
        proposals=proposals,
        commissions=commissions,
        date_from=date_from,
        date_to=date_to,
    )

    logger.info(f"Dashboard KPIs calculados por {current_user.email}")
    return kpis


@router.get("/funnel", response_model=DashboardChart)
async def get_sales_funnel(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> DashboardChart:
    """
    Retorna dados para o gráfico de funil de vendas.

    Mostra quantidade de opportunities em cada estágio.
    """
    service = DashboardService()
    opportunities = await _get_all_opportunities(db)

    chart = service.generate_funnel_chart(opportunities)
    return chart


@router.get("/trends/leads", response_model=list[DashboardTrend])
async def get_leads_trends(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    period: str = Query("month", pattern="^(day|week|month)$"),
    periods_count: int = Query(6, ge=2, le=12),
) -> list[DashboardTrend]:
    """
    Retorna tendência de novos leads ao longo do tempo.

    Args:
        period: Tipo de período (day, week, month)
        periods_count: Número de períodos para análise
    """
    service = DashboardService()
    leads = await _get_all_leads(db)

    trends = service.generate_trends(
        data=leads,
        date_field="created_at",
        value_field="count",
        period=period,
        periods_count=periods_count,
    )

    return trends


@router.get("/trends/sales", response_model=list[DashboardTrend])
async def get_sales_trends(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    period: str = Query("month", pattern="^(day|week|month)$"),
    periods_count: int = Query(6, ge=2, le=12),
) -> list[DashboardTrend]:
    """
    Retorna tendência de vendas (opportunities ganhas) ao longo do tempo.
    """
    service = DashboardService()
    opportunities = await _get_all_opportunities(db)

    # Filtrar apenas opportunities ganhas
    won_opps = [o for o in opportunities if o.is_won]

    has_close_date = won_opps and hasattr(won_opps[0], "actual_close_date")
    date_fld = "actual_close_date" if has_close_date else "updated_at"
    trends = service.generate_trends(
        data=won_opps,
        date_field=date_fld,
        value_field="value",
        period=period,
        periods_count=periods_count,
    )

    return trends


@router.get("/trends/commissions", response_model=list[DashboardTrend])
async def get_commissions_trends(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    period: str = Query("month", pattern="^(day|week|month)$"),
    periods_count: int = Query(6, ge=2, le=12),
) -> list[DashboardTrend]:
    """
    Retorna tendência de comissões ao longo do tempo.
    """
    service = DashboardService()
    commissions = await _get_all_commissions(db)

    trends = service.generate_trends(
        data=commissions,
        date_field="created_at",
        value_field="final_commission",
        period=period,
        periods_count=periods_count,
    )

    return trends


@router.get("/conversion-rates", response_model=dict)
async def get_conversion_rates(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Retorna taxas de conversão entre estágios do pipeline.

    Mostra percentual de progresso entre cada estágio.
    """
    service = DashboardService()
    opportunities = await _get_all_opportunities(db)

    rates = service.calculate_conversion_rates(opportunities)
    return rates


@router.get("/seller/{seller_id}/performance", response_model=PerformanceMetrics)
async def get_seller_performance(
    seller_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    target: float | None = None,
) -> PerformanceMetrics:
    """
    Retorna métricas de performance de um vendedor específico.
    """
    service = DashboardService()

    leads = await _get_all_leads(db)
    opportunities = await _get_all_opportunities(db)
    commissions = await _get_all_commissions(db)

    metrics = service.calculate_seller_performance(
        seller_id=seller_id,
        leads=leads,
        opportunities=opportunities,
        commissions=commissions,
        target=target,
    )

    return metrics


@router.get("/top-performers", response_model=list[PerformanceMetrics])
async def get_top_performers(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    limit: int = Query(5, ge=1, le=20),
) -> list[PerformanceMetrics]:
    """
    Retorna os top performers (vendedores com maior volume de vendas).
    """
    service = DashboardService()

    leads = await _get_all_leads(db)
    opportunities = await _get_all_opportunities(db)
    commissions = await _get_all_commissions(db)

    # Coletar IDs únicos de vendedores
    seller_ids = set()
    for lead in leads:
        if lead.assigned_to_id:
            seller_ids.add(str(lead.assigned_to_id))
    for opp in opportunities:
        if opp.owner_id:
            seller_ids.add(str(opp.owner_id))

    # Criar dict de vendedores (sem nomes por enquanto)
    sellers = dict.fromkeys(seller_ids)

    top = service.get_top_performers(
        leads=leads,
        opportunities=opportunities,
        commissions=commissions,
        sellers=sellers,
        limit=limit,
    )

    return top


@router.get("/charts/leads-by-status", response_model=DashboardChart)
async def get_leads_by_status_chart(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> DashboardChart:
    """Retorna gráfico de distribuição de leads por status."""
    service = DashboardService()
    leads = await _get_all_leads(db)

    chart = service.generate_pie_chart_by_status(
        items=leads,
        status_field="status",
        title="Leads por Status",
    )

    return chart


@router.get("/charts/opportunities-by-stage", response_model=DashboardChart)
async def get_opportunities_by_stage_chart(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> DashboardChart:
    """Retorna gráfico de distribuição de opportunities por estágio."""
    service = DashboardService()
    opportunities = await _get_all_opportunities(db)

    chart = service.generate_pie_chart_by_status(
        items=opportunities,
        status_field="stage",
        title="Opportunities por Estágio",
    )

    return chart


@router.get("/charts/proposals-by-status", response_model=DashboardChart)
async def get_proposals_by_status_chart(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> DashboardChart:
    """Retorna gráfico de distribuição de propostas por status."""
    service = DashboardService()
    proposals = await _get_all_proposals(db)

    chart = service.generate_pie_chart_by_status(
        items=proposals,
        status_field="status",
        title="Propostas por Status",
    )

    return chart


@router.get("/charts/commissions-by-status", response_model=DashboardChart)
async def get_commissions_by_status_chart(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> DashboardChart:
    """Retorna gráfico de distribuição de comissões por status."""
    service = DashboardService()
    commissions = await _get_all_commissions(db)

    chart = service.generate_pie_chart_by_status(
        items=commissions,
        status_field="status",
        title="Comissões por Status",
    )

    return chart

"""Controller para fluxo de caixa e análise de IA."""

import logging
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session
from modules.financial.services.cashflow_service import CashFlowService
from modules.financial.services.payable_ai_service import PayableAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cashflow", tags=["Fluxo de Caixa"])


def get_cashflow_service(
    session: AsyncSession = Depends(get_session),
) -> CashFlowService:
    """Retorna instância do CashFlowService."""
    return CashFlowService(session)


def get_ai_service(session: AsyncSession = Depends(get_session)) -> PayableAIService:
    """Retorna instância do PayableAIService."""
    return PayableAIService(session)


# ==================== PROJEÇÕES ====================


@router.get(
    "/projection",
    summary="Projeção de fluxo de caixa",
)
async def get_projection(
    condominio_id: UUID,
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    include_pending: bool = Query(True, description="Incluir pendentes"),
    include_scheduled: bool = Query(True, description="Incluir agendados"),
    group_by: str = Query("day", description="Agrupar por: day, week, month"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
):
    """Gera projeção de fluxo de caixa."""
    projections = await service.get_projection(
        condominio_id=condominio_id,
        start_date=start_date,
        end_date=end_date,
        include_pending=include_pending,
        include_scheduled=include_scheduled,
        group_by=group_by,
    )
    return [p.to_dict() for p in projections]


@router.get(
    "/summary",
    summary="Resumo de fluxo de caixa",
)
async def get_summary(
    condominio_id: UUID,
    period_days: int = Query(30, ge=7, le=365, description="Período em dias"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna resumo do fluxo de caixa."""
    return await service.get_summary(condominio_id, period_days)


@router.get(
    "/category-breakdown",
    summary="Breakdown por categoria",
)
async def get_category_breakdown(
    condominio_id: UUID,
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna breakdown de despesas por categoria."""
    return await service.get_category_breakdown(condominio_id, start_date, end_date)


@router.get(
    "/supplier-breakdown",
    summary="Breakdown por fornecedor",
)
async def get_supplier_breakdown(
    condominio_id: UUID,
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=50, description="Quantidade de fornecedores"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna breakdown de despesas por fornecedor."""
    return await service.get_supplier_breakdown(condominio_id, start_date, end_date, limit)


@router.get(
    "/monthly-trend",
    summary="Tendência mensal",
)
async def get_monthly_trend(
    condominio_id: UUID,
    months: int = Query(12, ge=3, le=24, description="Meses de histórico"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna tendência mensal de pagamentos."""
    return await service.get_monthly_trend(condominio_id, months)


# ==================== INTELIGÊNCIA ARTIFICIAL ====================


@router.get(
    "/ai/anomalies",
    summary="Detectar anomalias",
)
async def detect_anomalies(
    condominio_id: UUID,
    period_months: int = Query(6, ge=3, le=12, description="Meses de histórico"),
    service: PayableAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
):
    """Detecta anomalias em contas a pagar."""
    anomalies = await service.detect_anomalies(
        condominio_id=condominio_id,
        period_months=period_months,
    )
    return {
        "anomalies": anomalies,
        "total": len(anomalies),
        "by_severity": {
            "high": len([a for a in anomalies if a.get("severity") == "high"]),
            "medium": len([a for a in anomalies if a.get("severity") == "medium"]),
            "low": len([a for a in anomalies if a.get("severity") == "low"]),
        },
    }


@router.get(
    "/ai/anomalies/{account_id}",
    summary="Detectar anomalias em conta específica",
)
async def detect_account_anomalies(
    account_id: UUID,
    period_months: int = Query(6, ge=3, le=12),
    session: AsyncSession = Depends(get_session),
    service: PayableAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
):
    """Detecta anomalias em uma conta específica."""
    from modules.financial.repositories.payable_repository import PayableAccountRepository

    repo = PayableAccountRepository(session)
    account = await repo.get_by_id(account_id)

    if not account:
        return {"anomalies": [], "message": "Conta não encontrada"}

    anomalies = await service.detect_anomalies(
        condominio_id=account.condominio_id,
        account=account,
        period_months=period_months,
    )
    return {"anomalies": anomalies, "total": len(anomalies)}


@router.get(
    "/ai/predict",
    summary="Previsão de fluxo de caixa",
)
async def predict_cashflow(
    condominio_id: UUID,
    months_ahead: int = Query(3, ge=1, le=6, description="Meses para prever"),
    service: PayableAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
):
    """Prevê fluxo de caixa futuro baseado em histórico."""
    predictions = await service.predict_cashflow(condominio_id, months_ahead)
    return {"predictions": predictions, "months_ahead": months_ahead}


@router.get(
    "/ai/suggestions",
    summary="Sugestões de otimização",
)
async def get_suggestions(
    condominio_id: UUID,
    service: PayableAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna sugestões de otimização baseadas em análise de dados."""
    suggestions = await service.suggest_optimizations(condominio_id)
    return {
        "suggestions": suggestions,
        "total": len(suggestions),
        "total_potential_savings": sum(s.get("potential_savings", 0) for s in suggestions),
    }


# ==================== DASHBOARD ====================


@router.get(
    "/dashboard",
    summary="Dashboard financeiro completo",
)
async def get_dashboard(
    condominio_id: UUID,
    cashflow_service: CashFlowService = Depends(get_cashflow_service),
    ai_service: PayableAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna dados completos para dashboard financeiro."""
    # Coleta dados em paralelo
    summary = await cashflow_service.get_summary(condominio_id)
    monthly_trend = await cashflow_service.get_monthly_trend(condominio_id, 6)
    category_breakdown = await cashflow_service.get_category_breakdown(condominio_id)
    supplier_breakdown = await cashflow_service.get_supplier_breakdown(condominio_id)

    # IA
    anomalies = await ai_service.detect_anomalies(condominio_id)
    predictions = await ai_service.predict_cashflow(condominio_id, 3)
    suggestions = await ai_service.suggest_optimizations(condominio_id)

    return {
        "summary": summary,
        "monthly_trend": monthly_trend,
        "category_breakdown": category_breakdown[:5],  # Top 5
        "supplier_breakdown": supplier_breakdown[:5],  # Top 5
        "ai": {
            "anomalies_count": len(anomalies),
            "high_priority_anomalies": [a for a in anomalies if a.get("severity") == "high"][:3],
            "predictions": predictions,
            "suggestions_count": len(suggestions),
            "potential_savings": sum(s.get("potential_savings", 0) for s in suggestions),
        },
    }

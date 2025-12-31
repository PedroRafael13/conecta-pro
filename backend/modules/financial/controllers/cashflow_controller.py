"""Controller para fluxo de caixa, entradas, previsões e análise de IA."""

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session
from modules.financial.models import (
    CashFlowEntryStatus,
    CashFlowEntryType,
    CashFlowSourceType,
    ForecastConfidence,
    ForecastPeriodType,
    ForecastStatus,
    RecurrenceFrequency,
)
from modules.financial.repositories import (
    BankAccountRepository,
    CashFlowEntryRepository,
    CashFlowForecastRepository,
)
from modules.financial.schemas import (
    AIForecastRequest,
    AIForecastResponse,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    CashFlowDashboard,
    CashFlowEntryCreate,
    CashFlowEntryFilter,
    CashFlowEntryRealize,
    CashFlowEntryResponse,
    CashFlowEntryUpdate,
    CashFlowForecastCreate,
    CashFlowForecastFilter,
    CashFlowForecastResponse,
    CashFlowForecastUpdate,
    CashFlowProjection,
    CashFlowSummary,
    CashFlowTrend,
    ForecastActualsUpdate,
    ForecastOpportunity,
    ForecastRisk,
    OptimizationSuggestion,
)
from modules.financial.services.cashflow_ai_service import CashFlowAIService
from modules.financial.services.cashflow_service import CashFlowService
from modules.financial.services.payable_ai_service import PayableAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cashflow", tags=["Fluxo de Caixa"])


# ==================== DEPENDÊNCIAS ====================


def get_cashflow_service(session: AsyncSession = Depends(get_session)) -> CashFlowService:
    """Retorna instância do CashFlowService."""
    return CashFlowService(session)


def get_ai_service(session: AsyncSession = Depends(get_session)) -> CashFlowAIService:
    """Retorna instância do CashFlowAIService."""
    return CashFlowAIService(session)


def get_payable_ai_service(session: AsyncSession = Depends(get_session)) -> PayableAIService:
    """Retorna instância do PayableAIService."""
    return PayableAIService(session)


def get_entry_repository(session: AsyncSession = Depends(get_session)) -> CashFlowEntryRepository:
    """Retorna instância do CashFlowEntryRepository."""
    return CashFlowEntryRepository(session)


def get_forecast_repository(
    session: AsyncSession = Depends(get_session),
) -> CashFlowForecastRepository:
    """Retorna instância do CashFlowForecastRepository."""
    return CashFlowForecastRepository(session)


def get_account_repository(session: AsyncSession = Depends(get_session)) -> BankAccountRepository:
    """Retorna instância do BankAccountRepository."""
    return BankAccountRepository(session)


# ==================== PROJEÇÕES E RESUMO ====================


@router.get(
    "/projection",
    response_model=List[CashFlowProjection],
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
) -> List[CashFlowProjection]:
    """Gera projeção de fluxo de caixa."""
    projections = await service.get_projection(
        condominio_id=condominio_id,
        start_date=start_date,
        end_date=end_date,
        include_pending=include_pending,
        include_scheduled=include_scheduled,
        group_by=group_by,
    )
    return [CashFlowProjection(**p.to_dict()) for p in projections]


@router.get(
    "/summary",
    response_model=CashFlowSummary,
    summary="Resumo de fluxo de caixa",
)
async def get_summary(
    condominio_id: UUID,
    period_days: int = Query(30, ge=7, le=365, description="Período em dias"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
) -> CashFlowSummary:
    """Retorna resumo do fluxo de caixa."""
    return await service.get_summary(condominio_id, period_days)


@router.get(
    "/trends",
    response_model=List[CashFlowTrend],
    summary="Tendências de fluxo de caixa",
)
async def get_trends(
    condominio_id: UUID,
    months: int = Query(12, ge=3, le=24, description="Meses de histórico"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),
) -> List[CashFlowTrend]:
    """Retorna tendências mensais de fluxo de caixa."""
    data = await service.get_monthly_trend(condominio_id, months)
    return [CashFlowTrend(**item) for item in data]


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
) -> dict:
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
) -> dict:
    """Retorna breakdown de despesas por fornecedor."""
    return await service.get_supplier_breakdown(condominio_id, start_date, end_date, limit)


@router.get(
    "/dashboard",
    response_model=CashFlowDashboard,
    summary="Dashboard financeiro completo",
)
async def get_dashboard(
    condominio_id: UUID,
    cashflow_service: CashFlowService = Depends(get_cashflow_service),
    ai_service: CashFlowAIService = Depends(get_ai_service),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowDashboard:
    """Retorna dados completos para dashboard financeiro."""
    # Saldo atual
    total_balance = await account_repo.get_total_balance(condominio_id)

    # Dados de fluxo
    summary = await cashflow_service.get_summary(condominio_id)
    monthly_trend = await cashflow_service.get_monthly_trend(condominio_id, 6)
    category_breakdown = await cashflow_service.get_category_breakdown(condominio_id)
    supplier_breakdown = await cashflow_service.get_supplier_breakdown(condominio_id)

    # IA
    forecast_request = AIForecastRequest(
        condominio_id=condominio_id,
        period_days=90,
    )
    ai_forecast = await ai_service.generate_forecast(forecast_request)

    return CashFlowDashboard(
        current_balance=total_balance,
        projected_balance_30d=(
            ai_forecast.projections[29].projected_balance
            if len(ai_forecast.projections) >= 30
            else total_balance
        ),
        projected_balance_60d=(
            ai_forecast.projections[59].projected_balance
            if len(ai_forecast.projections) >= 60
            else total_balance
        ),
        projected_balance_90d=(
            ai_forecast.projections[-1].projected_balance
            if ai_forecast.projections
            else total_balance
        ),
        total_inflows_30d=summary.get("total_receivables", Decimal("0")),
        total_outflows_30d=summary.get("total_payables", Decimal("0")),
        net_flow_30d=summary.get("net_flow", Decimal("0")),
        monthly_trends=monthly_trend,
        category_breakdown=category_breakdown[:5],
        top_suppliers=supplier_breakdown[:5],
        ai_confidence=ai_forecast.confidence,
        alerts=ai_forecast.alerts[:5],
        risks=[r.model_dump() for r in ai_forecast.risks[:3]],
        opportunities=[o.model_dump() for o in ai_forecast.opportunities[:3]],
    )


# ==================== ENTRADAS DE FLUXO DE CAIXA ====================


@router.post(
    "/entries",
    response_model=CashFlowEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar entrada de fluxo de caixa",
)
async def create_entry(
    data: CashFlowEntryCreate,
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowEntryResponse:
    """Cria nova entrada de fluxo de caixa."""
    try:
        entry = await repo.create(data.model_dump())
        logger.info(f"Entrada de fluxo criada: {entry.id} por {current_user.get('email')}")
        return CashFlowEntryResponse.model_validate(entry)
    except Exception as e:
        logger.error(f"Erro ao criar entrada: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar entrada de fluxo de caixa",
        )


@router.get(
    "/entries",
    response_model=List[CashFlowEntryResponse],
    summary="Listar entradas",
)
async def list_entries(
    condominio_id: UUID,
    entry_type: Optional[CashFlowEntryType] = Query(None),
    source_type: Optional[CashFlowSourceType] = Query(None),
    entry_status: Optional[CashFlowEntryStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    is_recurring: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> List[CashFlowEntryResponse]:
    """Lista entradas de fluxo de caixa com filtros."""
    filters = CashFlowEntryFilter(
        condominio_id=condominio_id,
        entry_type=entry_type,
        source_type=source_type,
        status=entry_status,
        start_date=start_date,
        end_date=end_date,
        is_recurring=is_recurring,
    )
    entries = await repo.list_with_filters(filters, skip=skip, limit=limit)
    return [CashFlowEntryResponse.model_validate(e) for e in entries]


@router.get(
    "/entries/pending",
    response_model=List[CashFlowEntryResponse],
    summary="Entradas pendentes",
)
async def get_pending_entries(
    condominio_id: UUID,
    days_ahead: int = Query(30, ge=1, le=90),
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> List[CashFlowEntryResponse]:
    """Retorna entradas pendentes nos próximos dias."""
    entries = await repo.get_pending(condominio_id, days_ahead)
    return [CashFlowEntryResponse.model_validate(e) for e in entries]


@router.get(
    "/entries/totals",
    summary="Totais por tipo",
)
async def get_entry_totals(
    condominio_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Retorna totais de entradas por tipo."""
    return await repo.get_totals_by_type(condominio_id, start_date, end_date)


@router.get(
    "/entries/{entry_id}",
    response_model=CashFlowEntryResponse,
    summary="Obter entrada",
)
async def get_entry(
    entry_id: UUID,
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowEntryResponse:
    """Retorna entrada pelo ID."""
    entry = await repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada não encontrada",
        )
    return CashFlowEntryResponse.model_validate(entry)


@router.put(
    "/entries/{entry_id}",
    response_model=CashFlowEntryResponse,
    summary="Atualizar entrada",
)
async def update_entry(
    entry_id: UUID,
    data: CashFlowEntryUpdate,
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowEntryResponse:
    """Atualiza entrada de fluxo de caixa."""
    entry = await repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada não encontrada",
        )

    if entry.status == CashFlowEntryStatus.REALIZADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar entrada já realizada",
        )

    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update(entry_id, update_data)
    logger.info(f"Entrada atualizada: {entry_id} por {current_user.get('email')}")
    return CashFlowEntryResponse.model_validate(updated)


@router.delete(
    "/entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir entrada",
)
async def delete_entry(
    entry_id: UUID,
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Exclui entrada de fluxo de caixa."""
    entry = await repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada não encontrada",
        )

    await repo.delete(entry_id)
    logger.info(f"Entrada excluída: {entry_id} por {current_user.get('email')}")


@router.post(
    "/entries/{entry_id}/realize",
    response_model=CashFlowEntryResponse,
    summary="Realizar entrada",
)
async def realize_entry(
    entry_id: UUID,
    data: CashFlowEntryRealize,
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> CashFlowEntryResponse:
    """Realiza entrada de fluxo de caixa (marca como efetivada)."""
    entry = await repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada não encontrada",
        )

    if entry.status == CashFlowEntryStatus.REALIZADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrada já está realizada",
        )

    # Atualiza entrada
    update_data = {
        "status": CashFlowEntryStatus.REALIZADO,
        "realized_amount": data.realized_amount,
        "realized_date": data.realized_date or date.today(),
    }

    # Se valor diferente, registra diferença
    if data.realized_amount != entry.expected_amount:
        update_data["notes"] = (
            f"{entry.notes or ''}\n"
            f"Diferença: {data.realized_amount - entry.expected_amount:.2f}"
        ).strip()

    updated = await repo.update(entry_id, update_data)

    # Cria transação bancária se especificado
    if data.bank_account_id:
        from modules.financial.models import TransactionCategory, TransactionStatus, TransactionType
        from modules.financial.repositories import BankTransactionRepository

        tx_repo = BankTransactionRepository(session)
        await tx_repo.create(
            {
                "bank_account_id": data.bank_account_id,
                "transaction_type": (
                    TransactionType.CREDITO
                    if entry.entry_type == CashFlowEntryType.ENTRADA
                    else TransactionType.DEBITO
                ),
                "category": TransactionCategory.OUTROS,
                "amount": data.realized_amount,
                "description": f"Fluxo de caixa: {entry.description}",
                "transaction_date": data.realized_date or date.today(),
                "status": TransactionStatus.EFETIVADA,
                "cashflow_entry_id": entry_id,
            }
        )

    await session.commit()
    logger.info(f"Entrada realizada: {entry_id} por {current_user.get('email')}")
    return CashFlowEntryResponse.model_validate(updated)


# ==================== PREVISÕES ====================


@router.post(
    "/forecasts",
    response_model=CashFlowForecastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar previsão",
)
async def create_forecast(
    data: CashFlowForecastCreate,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowForecastResponse:
    """Cria nova previsão de fluxo de caixa."""
    try:
        forecast = await repo.create(data.model_dump())
        logger.info(f"Previsão criada: {forecast.id} por {current_user.get('email')}")
        return CashFlowForecastResponse.model_validate(forecast)
    except Exception as e:
        logger.error(f"Erro ao criar previsão: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar previsão",
        )


@router.get(
    "/forecasts",
    response_model=List[CashFlowForecastResponse],
    summary="Listar previsões",
)
async def list_forecasts(
    condominio_id: UUID,
    period_type: Optional[ForecastPeriodType] = Query(None),
    forecast_status: Optional[ForecastStatus] = Query(None),
    confidence: Optional[ForecastConfidence] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> List[CashFlowForecastResponse]:
    """Lista previsões com filtros."""
    filters = CashFlowForecastFilter(
        condominio_id=condominio_id,
        period_type=period_type,
        status=forecast_status,
        confidence=confidence,
        start_date=start_date,
        end_date=end_date,
    )
    forecasts = await repo.list_with_filters(filters, skip=skip, limit=limit)
    return [CashFlowForecastResponse.model_validate(f) for f in forecasts]


@router.get(
    "/forecasts/active",
    response_model=List[CashFlowForecastResponse],
    summary="Previsões ativas",
)
async def get_active_forecasts(
    condominio_id: UUID,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> List[CashFlowForecastResponse]:
    """Retorna previsões ativas do condomínio."""
    forecasts = await repo.get_active(condominio_id)
    return [CashFlowForecastResponse.model_validate(f) for f in forecasts]


@router.get(
    "/forecasts/{forecast_id}",
    response_model=CashFlowForecastResponse,
    summary="Obter previsão",
)
async def get_forecast(
    forecast_id: UUID,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowForecastResponse:
    """Retorna previsão pelo ID."""
    forecast = await repo.get_by_id(forecast_id)
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsão não encontrada",
        )
    return CashFlowForecastResponse.model_validate(forecast)


@router.put(
    "/forecasts/{forecast_id}",
    response_model=CashFlowForecastResponse,
    summary="Atualizar previsão",
)
async def update_forecast(
    forecast_id: UUID,
    data: CashFlowForecastUpdate,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowForecastResponse:
    """Atualiza previsão."""
    forecast = await repo.get_by_id(forecast_id)
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsão não encontrada",
        )

    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update(forecast_id, update_data)
    logger.info(f"Previsão atualizada: {forecast_id} por {current_user.get('email')}")
    return CashFlowForecastResponse.model_validate(updated)


@router.post(
    "/forecasts/{forecast_id}/update-actuals",
    response_model=CashFlowForecastResponse,
    summary="Atualizar valores realizados",
)
async def update_forecast_actuals(
    forecast_id: UUID,
    data: ForecastActualsUpdate,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> CashFlowForecastResponse:
    """Atualiza valores realizados da previsão."""
    forecast = await repo.get_by_id(forecast_id)
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsão não encontrada",
        )

    # Atualiza valores
    forecast.update_actuals(
        inflows=data.actual_inflows,
        outflows=data.actual_outflows,
        balance=data.actual_balance,
    )

    await repo.update(
        forecast_id,
        {
            "actual_inflows": forecast.actual_inflows,
            "actual_outflows": forecast.actual_outflows,
            "actual_balance": forecast.actual_balance,
            "variance_inflows": forecast.variance_inflows,
            "variance_outflows": forecast.variance_outflows,
            "variance_balance": forecast.variance_balance,
            "variance_percentage": forecast.variance_percentage,
        },
    )

    logger.info(f"Valores realizados atualizados: {forecast_id} por {current_user.get('email')}")
    return CashFlowForecastResponse.model_validate(forecast)


@router.delete(
    "/forecasts/{forecast_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir previsão",
)
async def delete_forecast(
    forecast_id: UUID,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Exclui previsão."""
    forecast = await repo.get_by_id(forecast_id)
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsão não encontrada",
        )

    await repo.delete(forecast_id)
    logger.info(f"Previsão excluída: {forecast_id} por {current_user.get('email')}")


# ==================== INTELIGÊNCIA ARTIFICIAL ====================


@router.post(
    "/ai/forecast",
    response_model=AIForecastResponse,
    summary="Gerar previsão com IA",
)
async def generate_ai_forecast(
    data: AIForecastRequest,
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> AIForecastResponse:
    """Gera previsão de fluxo de caixa usando IA."""
    try:
        forecast = await service.generate_forecast(data)
        logger.info(
            f"Previsão IA gerada para condomínio {data.condominio_id} "
            f"por {current_user.get('email')}"
        )
        return forecast
    except Exception as e:
        logger.error(f"Erro ao gerar previsão IA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar previsão com IA",
        )


@router.post(
    "/ai/anomalies",
    response_model=AnomalyDetectionResponse,
    summary="Detectar anomalias",
)
async def detect_anomalies(
    data: AnomalyDetectionRequest,
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> AnomalyDetectionResponse:
    """Detecta anomalias em fluxo de caixa usando IA."""
    try:
        anomalies = await service.detect_anomalies(data)
        logger.info(
            f"Detecção de anomalias para condomínio {data.condominio_id}: "
            f"{len(anomalies.anomalies)} encontradas, por {current_user.get('email')}"
        )
        return anomalies
    except Exception as e:
        logger.error(f"Erro ao detectar anomalias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao detectar anomalias",
        )


@router.get(
    "/ai/suggestions",
    response_model=List[OptimizationSuggestion],
    summary="Sugestões de otimização",
)
async def get_optimization_suggestions(
    condominio_id: UUID,
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> List[OptimizationSuggestion]:
    """Retorna sugestões de otimização baseadas em IA."""
    try:
        suggestions = await service.suggest_optimizations(condominio_id)
        logger.info(
            f"Sugestões de otimização para condomínio {condominio_id}: "
            f"{len(suggestions)} sugestões, por {current_user.get('email')}"
        )
        return suggestions
    except Exception as e:
        logger.error(f"Erro ao gerar sugestões: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar sugestões",
        )


@router.get(
    "/ai/risks",
    response_model=List[ForecastRisk],
    summary="Riscos identificados",
)
async def get_risks(
    condominio_id: UUID,
    period_days: int = Query(90, ge=30, le=365),
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> List[ForecastRisk]:
    """Retorna riscos identificados pela IA."""
    try:
        forecast_request = AIForecastRequest(
            condominio_id=condominio_id,
            period_days=period_days,
        )
        forecast = await service.generate_forecast(forecast_request)
        return forecast.risks
    except Exception as e:
        logger.error(f"Erro ao identificar riscos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao identificar riscos",
        )


@router.get(
    "/ai/opportunities",
    response_model=List[ForecastOpportunity],
    summary="Oportunidades identificadas",
)
async def get_opportunities(
    condominio_id: UUID,
    period_days: int = Query(90, ge=30, le=365),
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> List[ForecastOpportunity]:
    """Retorna oportunidades identificadas pela IA."""
    try:
        forecast_request = AIForecastRequest(
            condominio_id=condominio_id,
            period_days=period_days,
        )
        forecast = await service.generate_forecast(forecast_request)
        return forecast.opportunities
    except Exception as e:
        logger.error(f"Erro ao identificar oportunidades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao identificar oportunidades",
        )


# ==================== ANÁLISES LEGADAS (COMPATIBILIDADE) ====================


@router.get(
    "/legacy/anomalies",
    summary="[Legacy] Detectar anomalias",
    deprecated=True,
)
async def detect_anomalies_legacy(
    condominio_id: UUID,
    period_months: int = Query(6, ge=3, le=12, description="Meses de histórico"),
    service: PayableAIService = Depends(get_payable_ai_service),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """[Deprecated] Detecta anomalias em contas a pagar."""
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
    "/legacy/predict",
    summary="[Legacy] Previsão de fluxo de caixa",
    deprecated=True,
)
async def predict_cashflow_legacy(
    condominio_id: UUID,
    months_ahead: int = Query(3, ge=1, le=6, description="Meses para prever"),
    service: PayableAIService = Depends(get_payable_ai_service),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """[Deprecated] Prevê fluxo de caixa futuro baseado em histórico."""
    predictions = await service.predict_cashflow(condominio_id, months_ahead)
    return {"predictions": predictions, "months_ahead": months_ahead}


@router.get(
    "/legacy/suggestions",
    summary="[Legacy] Sugestões de otimização",
    deprecated=True,
)
async def get_suggestions_legacy(
    condominio_id: UUID,
    service: PayableAIService = Depends(get_payable_ai_service),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """[Deprecated] Retorna sugestões de otimização baseadas em análise de dados."""
    suggestions = await service.suggest_optimizations(condominio_id)
    return {
        "suggestions": suggestions,
        "total": len(suggestions),
        "total_potential_savings": sum(s.get("potential_savings", 0) for s in suggestions),
    }

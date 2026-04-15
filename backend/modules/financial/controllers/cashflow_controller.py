"""Controller para fluxo de caixa, entradas, previsões e análise de IA."""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
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
    TransactionCategory,
    TransactionStatus,
    TransactionType,
)
from modules.financial.repositories import (
    BankAccountRepository,
    BankTransactionRepository,
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
    response_model=list[CashFlowProjection],
    summary="Projeção de fluxo de caixa",
)
async def get_projection(
    condominio_id: UUID,
    start_date: date | None = Query(None, description="Data inicial"),
    end_date: date | None = Query(None, description="Data final"),
    include_pending: bool = Query(True, description="Incluir pendentes"),
    include_scheduled: bool = Query(True, description="Incluir agendados"),
    group_by: str = Query("day", description="Agrupar por: day, week, month"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CashFlowProjection]:
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> CashFlowSummary:
    """Retorna resumo do fluxo de caixa."""
    return await service.get_summary(condominio_id, period_days)


@router.get(
    "/trends",
    response_model=list[CashFlowTrend],
    summary="Tendências de fluxo de caixa",
)
async def get_trends(
    condominio_id: UUID,
    months: int = Query(12, ge=3, le=24, description="Meses de histórico"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CashFlowTrend]:
    """Retorna tendências mensais de fluxo de caixa."""
    data = await service.get_monthly_trend(condominio_id, months)
    return [CashFlowTrend(**item) for item in data]


@router.get(
    "/category-breakdown",
    summary="Breakdown por categoria",
)
async def get_category_breakdown(
    condominio_id: UUID,
    start_date: date | None = Query(None, description="Data inicial"),
    end_date: date | None = Query(None, description="Data final"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna breakdown de despesas por categoria."""
    return await service.get_category_breakdown(condominio_id, start_date, end_date)


@router.get(
    "/supplier-breakdown",
    summary="Breakdown por fornecedor",
)
async def get_supplier_breakdown(
    condominio_id: UUID,
    start_date: date | None = Query(None, description="Data inicial"),
    end_date: date | None = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=50, description="Quantidade de fornecedores"),
    service: CashFlowService = Depends(get_cashflow_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
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
    session: AsyncSession = Depends(get_session),
    account_repo: BankAccountRepository = Depends(get_account_repository),
    current_user=Depends(get_current_user),  # pylint: disable=unused-argument
) -> CashFlowDashboard:
    """Retorna dados completos para dashboard financeiro."""
    today = date.today()
    period_start = today.replace(day=1)
    cid = str(condominio_id)

    # ── Saldo real das contas bancárias (closing_balance) ──────────────────
    # Usa SUM direto para incluir TODAS as contas ativas (status='ativa')
    bal_result = await session.execute(
        text("""
            SELECT COALESCE(SUM(current_balance), 0) as total
            FROM bank_accounts
            WHERE condominio_id = :cid
              AND ativo = true
              AND status = 'ativa'
        """),
        {"cid": cid},
    )
    closing_balance = Decimal(str(bal_result.scalar_one() or 0))

    # ── Entradas e saídas do mês atual (realized_amount, TODOS os source_types) ──
    flows_result = await session.execute(
        text("""
            SELECT
                COALESCE(SUM(CASE WHEN entry_type = 'entrada' THEN realized_amount ELSE 0 END), 0) AS total_in,
                COALESCE(SUM(CASE WHEN entry_type = 'saida'   THEN realized_amount ELSE 0 END), 0) AS total_out
            FROM cashflow_entries
            WHERE condominio_id = :cid
              AND ativo = true
              AND entry_date BETWEEN :start AND :end
        """),
        {"cid": cid, "start": period_start, "end": today},
    )
    flows_row = flows_result.one()
    total_inflows = Decimal(str(flows_row.total_in or 0))
    total_outflows = Decimal(str(flows_row.total_out or 0))
    net_flow = total_inflows - total_outflows

    # opening_balance = saldo real atual - fluxo líquido do período
    opening_balance = closing_balance - net_flow

    # ── Breakdown por categoria ─────────────────────────────────────────────
    cat_result = await session.execute(
        text("""
            SELECT entry_type, category,
                   COALESCE(SUM(realized_amount), 0) as total
            FROM cashflow_entries
            WHERE condominio_id = :cid
              AND ativo = true
              AND entry_date BETWEEN :start AND :end
            GROUP BY entry_type, category
        """),
        {"cid": cid, "start": period_start, "end": today},
    )
    inflows_by_category: dict = {}
    outflows_by_category: dict = {}
    for row in cat_result:
        cat = row.category or "outros"
        val = Decimal(str(row.total or 0))
        if row.entry_type == "entrada":
            inflows_by_category[cat] = str(val)
        else:
            outflows_by_category[cat] = str(val)

    summary = CashFlowSummary(
        period_start=period_start,
        period_end=today,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        total_inflows=total_inflows,
        total_outflows=total_outflows,
        net_flow=net_flow,
        inflows_by_category=inflows_by_category,
        outflows_by_category=outflows_by_category,
        pending_receivables=Decimal("0"),
        pending_payables=Decimal("0"),
        overdue_receivables=Decimal("0"),
        overdue_payables=Decimal("0"),
    )

    return CashFlowDashboard(
        summary=summary,
        trends=[],
        projections=[],
        accounts=[],
        alerts=[],
        upcoming_payables=0,
        upcoming_receivables=0,
        overdue_payables=0,
        overdue_receivables=0,
    )


# ==================== ENTRADAS DE FLUXO DE CAIXA ====================


@router.post(
    "/sync",
    summary="Sincronizar bank_transactions → cashflow_entries",
)
async def sync_cashflow_entries(
    current_user=Depends(get_current_user),
) -> dict:
    """Dispara sync manual de bank_transactions pendentes → cashflow_entries."""
    try:
        from modules.financial.services.auto_sync_service import run_full_sync

        result = run_full_sync(limit=500)
        logger.info("Sync cashflow manual: %s", result)
        return {"ok": True, **result}
    except Exception as e:
        logger.error("Erro no sync cashflow: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no sync: {e}",
        )


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
    response_model=list[CashFlowEntryResponse],
    summary="Listar entradas",
)
async def list_entries(
    condominio_id: UUID | None = Query(None),
    entry_type: CashFlowEntryType | None = Query(None),
    source_type: CashFlowSourceType | None = Query(None),
    entry_status: CashFlowEntryStatus | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    is_recurring: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CashFlowEntryResponse]:
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
    response_model=list[CashFlowEntryResponse],
    summary="Entradas pendentes",
)
async def get_pending_entries(
    condominio_id: UUID,
    days_ahead: int = Query(30, ge=1, le=90),
    repo: CashFlowEntryRepository = Depends(get_entry_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CashFlowEntryResponse]:
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
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
    "/entries/{entry_id}/realize", response_model=CashFlowEntryResponse, summary="Realizar entrada", status_code=201
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
            f"{entry.notes or ''}\nDiferença: {data.realized_amount - entry.expected_amount:.2f}"
        ).strip()

    updated = await repo.update(entry_id, update_data)

    # Cria transação bancária se especificado
    if data.bank_account_id:
        tx_repo = BankTransactionRepository(session)
        await tx_repo.create(
            {
                "bank_account_id": data.bank_account_id,
                "transaction_type": (
                    TransactionType.CREDITO if entry.entry_type == CashFlowEntryType.ENTRADA else TransactionType.DEBITO
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
    response_model=list[CashFlowForecastResponse],
    summary="Listar previsões",
)
async def list_forecasts(
    condominio_id: UUID,
    period_type: ForecastPeriodType | None = Query(None),
    forecast_status: ForecastStatus | None = Query(None),
    confidence: ForecastConfidence | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CashFlowForecastResponse]:
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
    response_model=list[CashFlowForecastResponse],
    summary="Previsões ativas",
)
async def get_active_forecasts(
    condominio_id: UUID,
    repo: CashFlowForecastRepository = Depends(get_forecast_repository),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[CashFlowForecastResponse]:
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
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
    status_code=201,
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


@router.post("/ai/forecast", response_model=AIForecastResponse, summary="Gerar previsão com IA", status_code=201)
async def generate_ai_forecast(
    data: AIForecastRequest,
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> AIForecastResponse:
    """Gera previsão de fluxo de caixa usando IA."""
    try:
        forecast = await service.generate_forecast(data)
        logger.info(f"Previsão IA gerada para condomínio {data.condominio_id} por {current_user.get('email')}")
        return forecast
    except Exception as e:
        logger.error(f"Erro ao gerar previsão IA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar previsão com IA",
        )


@router.post("/ai/anomalies", response_model=AnomalyDetectionResponse, summary="Detectar anomalias", status_code=201)
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
    response_model=list[OptimizationSuggestion],
    summary="Sugestões de otimização",
)
async def get_optimization_suggestions(
    condominio_id: UUID,
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),
) -> list[OptimizationSuggestion]:
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
    response_model=list[ForecastRisk],
    summary="Riscos identificados",
)
async def get_risks(
    condominio_id: UUID,
    period_days: int = Query(90, ge=30, le=365),
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[ForecastRisk]:
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
    response_model=list[ForecastOpportunity],
    summary="Oportunidades identificadas",
)
async def get_opportunities(
    condominio_id: UUID,
    period_days: int = Query(90, ge=30, le=365),
    service: CashFlowAIService = Depends(get_ai_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[ForecastOpportunity]:
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
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
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """[Deprecated] Retorna sugestões de otimização baseadas em análise de dados."""
    suggestions = await service.suggest_optimizations(condominio_id)
    return {
        "suggestions": suggestions,
        "total": len(suggestions),
        "total_potential_savings": sum(s.get("potential_savings", 0) for s in suggestions),
    }


# ──────────────────────────────────────────────────────────────────────────────
# ENDPOINTS COMPATÍVEIS COM ORVAL — prefixo /cashflow/cashflow/... gerado auto
# ──────────────────────────────────────────────────────────────────────────────


@router.get(
    "/cashflow/entries",
    summary="Lançamentos do fluxo de caixa — formato paginado { items, total }",
    include_in_schema=True,
)
async def list_cashflow_entries_paginated(
    condominio_id: UUID | None = Query(None),
    entry_type: str | None = Query(None, description="entrada|saida"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_session),
) -> dict:
    """
    Endpoint compatível com Orval (/cashflow/cashflow/entries).
    Retorna { items, total, total_entradas, total_saidas } — formato que o frontend espera.
    Fonte: cashflow_entries (2.875 lançamentos reais jan-abr/2026).
    """
    try:
        tipo_filter = ""
        if entry_type == "entrada":
            tipo_filter = "AND ce.entry_type = 'entrada'"
        elif entry_type == "saida":
            tipo_filter = "AND ce.entry_type = 'saida'"

        cond_filter = ""
        params: dict = {"limit": limit, "offset": skip}
        if condominio_id is not None:
            cond_filter = "AND ce.condominio_id = :condominio_id"
            params["condominio_id"] = str(condominio_id)

        result = await db.execute(
            text(f"""
            SELECT
                ce.id,
                ce.entry_date,
                ce.description,
                ce.entry_type,
                ce.category,
                ce.expected_amount,
                ce.realized_amount,
                ce.status,
                ce.source_type,
                ce.bank_account_id,
                ce.condominio_id,
                ba.bank_name
            FROM cashflow_entries ce
            LEFT JOIN bank_accounts ba ON ba.id = ce.bank_account_id
            WHERE ce.ativo = true {cond_filter} {tipo_filter}
            ORDER BY ce.entry_date DESC, ce.created_at DESC
            LIMIT :limit OFFSET :offset
        """),
            params,
        )
        rows = result.fetchall()

        count_params: dict = {}
        if condominio_id is not None:
            count_params["condominio_id"] = str(condominio_id)

        count_result = await db.execute(
            text(f"""
            SELECT
                COUNT(*) as total,
                ROUND(SUM(CASE WHEN ce.entry_type = 'entrada'
                    THEN COALESCE(ce.realized_amount, ce.expected_amount, 0) ELSE 0 END)::numeric, 2)
                    as total_entradas,
                ROUND(SUM(CASE WHEN ce.entry_type = 'saida'
                    THEN COALESCE(ce.realized_amount, ce.expected_amount, 0) ELSE 0 END)::numeric, 2)
                    as total_saidas
            FROM cashflow_entries ce
            WHERE ce.ativo = true {cond_filter} {tipo_filter}
        """),
            count_params,
        )
        count_row = count_result.fetchone()

        return {
            "items": [
                {
                    "id": str(r.id),
                    "entry_date": r.entry_date.isoformat() if r.entry_date else None,
                    "description": r.description or "",
                    "entry_type": "income" if r.entry_type == "entrada" else "expense",
                    "category": r.category or "sem_categoria",
                    "expected_amount": float(r.expected_amount or 0),
                    "realized_amount": float(r.realized_amount or r.expected_amount or 0),
                    "amount": float(r.realized_amount or r.expected_amount or 0),
                    "status": r.status or "realizado",
                    "source_type": r.source_type or "manual",
                    "bank_name": r.bank_name or "Inter",
                    "condominio_id": str(r.condominio_id) if r.condominio_id else None,
                }
                for r in rows
            ],
            "total": int(count_row.total or 0),
            "total_entradas": float(count_row.total_entradas or 0),
            "total_saidas": float(count_row.total_saidas or 0),
            "saldo_periodo": float((count_row.total_entradas or 0) - (count_row.total_saidas or 0)),
            "skip": skip,
            "limit": limit,
        }
    except Exception as exc:
        import traceback

        return {"items": [], "total": 0, "error": str(exc), "detail": traceback.format_exc()[-300:]}


@router.get(
    "/lancamentos",
    summary="Lançamentos do fluxo de caixa (alias /cashflow/lancamentos)",
    include_in_schema=True,
)
async def get_lancamentos(
    condominio_id: UUID | None = Query(None),
    tipo: str | None = Query(None, description="entrada|saida|todos"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_session),
) -> dict:
    """
    Lançamentos reais do fluxo de caixa — 2.875 transações jan-abr/2026.
    Suporta paginação e filtro por tipo (entrada|saida).
    """
    try:
        tipo_filter = ""
        if tipo == "entrada":
            tipo_filter = "AND ce.entry_type = 'entrada'"
        elif tipo == "saida":
            tipo_filter = "AND ce.entry_type = 'saida'"

        cond_filter = ""
        params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
        if condominio_id is not None:
            cond_filter = "AND ce.condominio_id = :condominio_id"
            params["condominio_id"] = str(condominio_id)

        result = await db.execute(
            text(f"""
            SELECT
                ce.id,
                ce.entry_date,
                ce.description,
                ce.entry_type,
                ce.category,
                ce.expected_amount,
                ce.realized_amount,
                ce.status,
                ba.bank_name,
                SUM(COALESCE(ce.realized_amount, ce.expected_amount, 0))
                    OVER (ORDER BY ce.entry_date, ce.id
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as saldo_acumulado
            FROM cashflow_entries ce
            LEFT JOIN bank_accounts ba ON ba.id = ce.bank_account_id
            WHERE ce.ativo = true {cond_filter} {tipo_filter}
            ORDER BY ce.entry_date DESC, ce.created_at DESC
            LIMIT :limit OFFSET :offset
        """),
            params,
        )
        rows = result.fetchall()

        count_params: dict = {}
        if condominio_id is not None:
            count_params["condominio_id"] = str(condominio_id)

        count_result = await db.execute(
            text(f"""
            SELECT
                COUNT(*) as total,
                ROUND(SUM(CASE WHEN entry_type = 'entrada'
                    THEN COALESCE(realized_amount, expected_amount, 0) ELSE 0 END)::numeric, 2)
                    as total_entradas,
                ROUND(SUM(CASE WHEN entry_type = 'saida'
                    THEN COALESCE(realized_amount, expected_amount, 0) ELSE 0 END)::numeric, 2)
                    as total_saidas
            FROM cashflow_entries
            WHERE ativo = true {cond_filter} {tipo_filter}
        """),
            count_params,
        )
        count_row = count_result.fetchone()

        return {
            "items": [
                {
                    "id": str(r.id),
                    "data": r.entry_date.isoformat() if r.entry_date else None,
                    "descricao": r.description or "",
                    "valor": float(r.realized_amount or r.expected_amount or 0),
                    "tipo": r.entry_type or "saida",
                    "categoria": r.category or "sem_categoria",
                    "banco": r.bank_name or "Inter",
                    "status": r.status or "realizado",
                    "saldo_acumulado": float(r.saldo_acumulado or 0),
                }
                for r in rows
            ],
            "total": int(count_row.total or 0),
            "total_entradas": float(count_row.total_entradas or 0),
            "total_saidas": float(count_row.total_saidas or 0),
            "saldo_periodo": float((count_row.total_entradas or 0) - (count_row.total_saidas or 0)),
            "page": page,
            "per_page": per_page,
            "pages": max(1, (int(count_row.total or 0) + per_page - 1) // per_page),
        }
    except Exception as exc:
        import traceback

        return {"items": [], "total": 0, "error": str(exc), "detail": traceback.format_exc()[-300:]}


@router.get(
    "/cashflow/projection",
    summary="Projeção de saldo 30 dias (compatível Orval)",
)
async def get_cashflow_projection_orval(
    condominio_id: UUID | None = Query(None),
    days: int = Query(30, ge=1, le=90),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Projeção de saldo diário nos próximos N dias.
    Usa histórico real de cashflow_entries (média diária por tipo).
    Endpoint no path /cashflow/projection para compatibilidade com Orval
    que gera URL /api/v1/financial/cashflow/cashflow/projection.
    """
    import datetime as dt

    cond_filter = ""
    params: dict = {}
    if condominio_id is not None:
        cond_filter = "AND condominio_id = :condominio_id"
        params["condominio_id"] = str(condominio_id)

    try:
        hist = await db.execute(
            text(f"""
                SELECT
                    DATE(entry_date) as dia,
                    entry_type,
                    COALESCE(SUM(realized_amount), SUM(expected_amount), 0) as total
                FROM cashflow_entries
                WHERE ativo = true
                  AND entry_date >= CURRENT_DATE - INTERVAL '90 days'
                  {cond_filter}
                GROUP BY DATE(entry_date), entry_type
            """),
            params,
        )
        rows = hist.fetchall()

        saldo_q = await db.execute(
            text(f"""
                SELECT
                    COALESCE(SUM(CASE WHEN entry_type='entrada'
                        THEN COALESCE(realized_amount, expected_amount, 0)
                        ELSE -COALESCE(realized_amount, expected_amount, 0) END), 0) as saldo
                FROM cashflow_entries
                WHERE ativo = true
                {cond_filter}
            """),
            params,
        )
        saldo_row = saldo_q.fetchone()
        saldo_atual = float(saldo_row.saldo if saldo_row and saldo_row.saldo else 0)

        dias_com_entrada: list[float] = []
        dias_com_saida: list[float] = []
        for r in rows:
            if r.entry_type in ("entrada", "income"):
                dias_com_entrada.append(float(r.total))
            else:
                dias_com_saida.append(float(r.total))

        media_entrada = sum(dias_com_entrada) / max(len(dias_com_entrada), 1)
        media_saida = sum(dias_com_saida) / max(len(dias_com_saida), 1)

        projection = []
        saldo_acum = saldo_atual
        today = dt.date.today()
        for i in range(1, days + 1):
            d = today + dt.timedelta(days=i)
            saldo_acum += media_entrada - media_saida
            projection.append(
                {
                    "date": d.isoformat(),
                    "balance": round(media_entrada - media_saida, 2),
                    "cumulative_balance": round(saldo_acum, 2),
                    "receivables": round(media_entrada, 2),
                    "payables": round(media_saida, 2),
                }
            )
        return projection

    except Exception as proj_exc:
        import traceback

        logging.error(f"Erro em /cashflow/projection: {proj_exc}\n{traceback.format_exc()}")
        return []

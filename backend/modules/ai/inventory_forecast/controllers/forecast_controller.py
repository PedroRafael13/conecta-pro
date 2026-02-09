"""
Forecast Controller - AI Inventory Forecasting

Endpoints REST para previsao de estoque e demanda.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.ai.inventory_forecast.models.forecast import (
    ForecastStatus,
    ForecastType,
)
from modules.ai.inventory_forecast.repositories.forecast_repository import (
    ForecastRepository,
)
from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    DemandPatternResponse,
    ForecastListResponse,
    ForecastRequest,
    ForecastResponse,
    ForecastSummary,
    ReorderListResponse,
    ReorderSuggestion,
)
from modules.ai.inventory_forecast.services.demand_analyzer import DemandAnalyzer
from modules.ai.inventory_forecast.services.forecast_engine import ForecastEngine
from modules.ai.inventory_forecast.services.reorder_service import ReorderService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inventory-forecast",
    tags=["AI - Inventory Forecast"],
)


# ============================================================
# Forecast Endpoints
# ============================================================


@router.post(
    "/forecasts",
    response_model=ForecastResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar previsao de demanda",
)
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> ForecastResponse:
    """
    Gera previsao de demanda para um produto.

    - **product_id**: ID do produto
    - **horizon_days**: Dias de previsao (7-365)
    - **historical_days**: Dias de historico a usar (30-1095)
    - **model_type**: auto, prophet, arima, exp_smoothing
    """
    engine = ForecastEngine(db)

    # TODO: Buscar dados do produto e historico do modulo de estoque
    # Por enquanto, usar dados mock para demonstracao
    product_info = {
        "code": f"PROD-{str(request.product_id)[:8]}",
        "name": "Produto de Teste",
    }

    # Mock de dados historicos (em producao, buscar do banco)
    import random
    from datetime import date, timedelta

    historical_data = []
    base_date = date.today() - timedelta(days=request.historical_days)

    for i in range(request.historical_days):
        d = base_date + timedelta(days=i)
        # Simular demanda com tendencia e sazonalidade
        base = 100
        trend = i * 0.05
        seasonal = 20 * (1 if d.weekday() < 5 else 0.5)  # Menor no fim de semana
        noise = random.uniform(-15, 15)  # noqa: S311
        quantity = max(0, base + trend + seasonal + noise)
        historical_data.append({"date": d, "quantity": quantity})

    try:
        forecast = await engine.generate_forecast(
            request=request,
            product_info=product_info,
            historical_data=historical_data,
            created_by=UUID(current_user.id) if hasattr(current_user, "id") else None,
        )

        return ForecastResponse.model_validate(forecast)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao gerar previsao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar previsao",
        )


@router.get(
    "/forecasts/{forecast_id}",
    response_model=ForecastResponse,
    summary="Buscar previsao por ID",
)
async def get_forecast(
    forecast_id: UUID,
    include_results: bool = Query(False, description="Incluir resultados detalhados"),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> ForecastResponse:
    """Busca previsao por ID."""
    engine = ForecastEngine(db)
    forecast = engine.get_forecast(forecast_id, include_results)

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsao nao encontrada",
        )

    return ForecastResponse.model_validate(forecast)


@router.get(
    "/forecasts",
    response_model=ForecastListResponse,
    summary="Listar previsoes",
)
async def list_forecasts(
    product_id: UUID | None = Query(None, description="Filtrar por produto"),
    status_filter: ForecastStatus | None = Query(None, alias="status"),
    forecast_type: ForecastType | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> ForecastListResponse:
    """Lista previsoes com filtros."""
    engine = ForecastEngine(db)
    items, total = engine.get_forecasts(
        product_id=product_id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )

    pages = (total + page_size - 1) // page_size

    return ForecastListResponse(
        items=[ForecastResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/forecasts/product/{product_id}/latest",
    response_model=ForecastResponse,
    summary="Buscar previsao mais recente do produto",
)
async def get_latest_forecast(
    product_id: UUID,
    forecast_type: ForecastType = Query(ForecastType.DEMAND),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> ForecastResponse:
    """Busca previsao mais recente para um produto."""
    engine = ForecastEngine(db)
    forecast = engine.get_latest_forecast(product_id, forecast_type)

    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma previsao encontrada para este produto",
        )

    return ForecastResponse.model_validate(forecast)


# ============================================================
# Demand Pattern Endpoints
# ============================================================


@router.post(
    "/patterns/analyze",
    response_model=DemandPatternResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analisar padrao de demanda",
)
async def analyze_demand_pattern(
    product_id: UUID,
    days: int = Query(365, ge=30, le=1095, description="Dias de historico"),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> DemandPatternResponse:
    """
    Analisa padrao de demanda de um produto.

    Identifica:
    - Tipo de padrao (constante, tendencia, sazonal, etc.)
    - Sazonalidade (semanal, mensal, anual)
    - Tendencia (crescente, decrescente, estavel)
    - Anomalias
    """
    analyzer = DemandAnalyzer(db)

    # TODO: Buscar dados reais do modulo de estoque
    product_info = {
        "code": f"PROD-{str(product_id)[:8]}",
        "name": "Produto de Teste",
    }

    # Mock de dados historicos
    import random
    from datetime import date, timedelta

    historical_data = []
    base_date = date.today() - timedelta(days=days)

    for i in range(days):
        d = base_date + timedelta(days=i)
        base = 100
        trend = i * 0.03
        seasonal = 15 * (1 if d.weekday() < 5 else 0.6)
        monthly = 10 * (1.2 if d.month in [11, 12] else 0.9)  # Pico no fim do ano
        noise = random.uniform(-10, 10)  # noqa: S311
        quantity = max(0, base + trend + seasonal + monthly + noise)
        historical_data.append({"date": d, "quantity": quantity})

    try:
        pattern = await analyzer.analyze_demand_pattern(
            product_id=product_id,
            product_info=product_info,
            historical_data=historical_data,
            analyzed_by=UUID(current_user.id) if hasattr(current_user, "id") else None,
        )

        return DemandPatternResponse.model_validate(pattern)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao analisar padrao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao analisar padrao",
        )


@router.get(
    "/patterns/{pattern_id}",
    response_model=DemandPatternResponse,
    summary="Buscar padrao por ID",
)
async def get_pattern(
    pattern_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> DemandPatternResponse:
    """Busca padrao de demanda por ID."""
    analyzer = DemandAnalyzer(db)
    pattern = analyzer.get_pattern(pattern_id)

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Padrao nao encontrado",
        )

    return DemandPatternResponse.model_validate(pattern)


@router.get(
    "/patterns/product/{product_id}/latest",
    response_model=DemandPatternResponse,
    summary="Buscar padrao mais recente do produto",
)
async def get_latest_pattern(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> DemandPatternResponse:
    """Busca padrao de demanda mais recente para um produto."""
    analyzer = DemandAnalyzer(db)
    pattern = analyzer.get_latest_pattern(product_id)

    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum padrao encontrado para este produto",
        )

    return DemandPatternResponse.model_validate(pattern)


# ============================================================
# Reorder Endpoints
# ============================================================


@router.post(
    "/reorder/suggestions",
    response_model=ReorderListResponse,
    summary="Gerar sugestoes de reposicao",
)
async def generate_reorder_suggestions(
    product_ids: list[UUID],
    default_lead_time: int = Query(7, ge=1, le=90),
    service_level: float = Query(0.95, ge=0.90, le=0.99),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> ReorderListResponse:
    """
    Gera sugestoes de reposicao para lista de produtos.

    Retorna urgencia (CRITICAL, HIGH, MEDIUM, LOW) e quantidades sugeridas.
    """
    reorder_service = ReorderService(db)

    # TODO: Buscar estoque atual do modulo de estoque
    import random

    products_stock = [
        {
            "product_id": pid,
            "current_stock": random.uniform(10, 200),  # noqa: S311
            "lead_time_days": default_lead_time,
            "code": f"PROD-{str(pid)[:8]}",
            "name": f"Produto {i + 1}",
        }
        for i, pid in enumerate(product_ids)
    ]

    return reorder_service.generate_reorder_suggestions(
        products_stock=products_stock,
        default_lead_time=default_lead_time,
        service_level=service_level,
    )


@router.get(
    "/reorder/critical",
    response_model=list[ReorderSuggestion],
    summary="Listar produtos criticos",
)
async def get_critical_products(
    default_lead_time: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> list[ReorderSuggestion]:
    """
    Lista produtos com urgencia CRITICAL ou HIGH.

    Util para alertas automaticos.
    """
    reorder_service = ReorderService(db)
    repository = ForecastRepository(db)

    # Buscar todos os forecasts ativos
    forecasts, _ = repository.get_forecasts(
        status=ForecastStatus.COMPLETED,
        is_active=True,
        page_size=1000,
    )

    if not forecasts:
        return []

    # TODO: Buscar estoque real do modulo de estoque
    import random

    products_stock = [
        {
            "product_id": f.product_id,
            "current_stock": random.uniform(5, 50),  # noqa: S311  # Estoque baixo para teste
            "lead_time_days": default_lead_time,
            "code": f.product_code,
            "name": f.product_name,
        }
        for f in forecasts
    ]

    return reorder_service.get_critical_products(
        products_stock=products_stock,
        default_lead_time=default_lead_time,
    )


@router.get(
    "/reorder/eoq/{product_id}",
    summary="Calcular quantidade otima de pedido (EOQ)",
)
async def calculate_eoq(
    product_id: UUID,
    current_stock: float = Query(..., ge=0),
    lead_time_days: int = Query(7, ge=1, le=90),
    ordering_cost: float = Query(50.0, ge=0),
    holding_cost_pct: float = Query(0.25, ge=0.01, le=1.0),
    unit_cost: float = Query(10.0, ge=0.01),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> dict:
    """
    Calcula quantidade economica de pedido (EOQ).

    Retorna:
    - EOQ (quantidade otima)
    - Numero de pedidos por ano
    - Custos estimados
    """
    reorder_service = ReorderService(db)

    result = reorder_service.calculate_optimal_order(
        product_id=product_id,
        current_stock=current_stock,
        lead_time_days=lead_time_days,
        ordering_cost=ordering_cost,
        holding_cost_pct=holding_cost_pct,
        unit_cost=unit_cost,
    )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return result


@router.get(
    "/reorder/simulate/{product_id}",
    summary="Simular niveis de estoque",
)
async def simulate_stock(
    product_id: UUID,
    current_stock: float = Query(..., ge=0),
    reorder_point: float = Query(..., ge=0),
    reorder_quantity: float = Query(..., ge=1),
    lead_time_days: int = Query(7, ge=1, le=90),
    simulation_days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> list[dict]:
    """
    Simula niveis de estoque futuros.

    Util para visualizar comportamento do estoque
    com parametros de reposicao definidos.
    """
    reorder_service = ReorderService(db)

    return reorder_service.simulate_stock_levels(
        product_id=product_id,
        current_stock=current_stock,
        reorder_point=reorder_point,
        reorder_quantity=reorder_quantity,
        lead_time_days=lead_time_days,
        simulation_days=simulation_days,
    )


# ============================================================
# Analytics Endpoints
# ============================================================


@router.get(
    "/analytics/accuracy",
    summary="Estatisticas de acuracidade",
)
async def get_accuracy_stats(
    product_id: UUID | None = None,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> dict:
    """
    Retorna estatisticas de acuracidade das previsoes.

    Compara valores previstos vs reais.
    """
    repository = ForecastRepository(db)
    return repository.get_forecast_accuracy_stats(product_id, days)


@router.get(
    "/analytics/trends",
    summary="Distribuicao de tendencias",
)
async def get_trend_distribution(
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> dict:
    """
    Retorna distribuicao de produtos por direcao de tendencia.

    Util para dashboard de analise.
    """
    repository = ForecastRepository(db)
    return repository.count_products_by_trend()


@router.get(
    "/analytics/needs-update",
    summary="Previsoes que precisam atualizacao",
)
async def get_forecasts_needing_update(
    days_old: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = ...,  # Required
) -> list[ForecastSummary]:
    """
    Lista previsoes que precisam ser atualizadas.

    Retorna previsoes mais antigas que X dias ou expiradas.
    """
    repository = ForecastRepository(db)
    forecasts = repository.get_forecasts_needing_update(days_old)

    return [
        ForecastSummary(
            product_id=f.product_id,
            product_code=f.product_code,
            product_name=f.product_name,
            avg_daily_demand=f.avg_daily_demand,
            trend_direction="unknown",
            confidence_score=f.confidence_score or 0,
            suggested_action="REVIEW",
        )
        for f in forecasts
    ]

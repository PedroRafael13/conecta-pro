"""
Sentiment Analysis Controller - Sprint 46

Endpoints para analise de sentimento.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.auth.dependencies import get_current_user, CurrentActiveUser

from modules.ai.sentiment_analysis.models import (
    TrendPeriod,
    TrendDirection,
    InsightType,
    InsightPriority,
    RuleCategory,
    SourceType,
    SentimentType,
)
from modules.ai.sentiment_analysis.models.sentiment_trend import TrendCategory
from modules.ai.sentiment_analysis.models.feedback_insight import InsightStatus
from modules.ai.sentiment_analysis.repositories import SentimentRepository
from modules.ai.sentiment_analysis.services import (
    SentimentAnalyzer,
    TrendCalculator,
    InsightGenerator,
    SentimentAlertService,
)
from modules.ai.sentiment_analysis.schemas import (
    # Analysis
    AnalyzeTextRequest,
    AnalyzeTextResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    SentimentAnalysisResponse,
    SentimentAnalysisListResponse,
    SentimentAnalysisSummary,
    SentimentAnalysisUpdate,
    SentimentAnalysisFilter,
    # Rule
    SentimentRuleCreate,
    SentimentRuleUpdate,
    SentimentRuleResponse,
    SentimentRuleListResponse,
    # Trend
    SentimentTrendResponse,
    SentimentTrendListResponse,
    TrendSummary,
    TrendComparisonResponse,
    TrendFilter,
    # Insight
    FeedbackInsightCreate,
    FeedbackInsightUpdate,
    FeedbackInsightResponse,
    FeedbackInsightListResponse,
    InsightSummary,
    InsightFilter,
    # Dashboard
    SentimentDashboardResponse,
    SentimentMetricsResponse,
    EmotionDistributionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sentiment", tags=["AI - Sentiment Analysis"])


# ============================================================
# Analysis Endpoints
# ============================================================

@router.post(
    "/analyze",
    response_model=AnalyzeTextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analisar texto",
)
async def analyze_text(
    request: AnalyzeTextRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> AnalyzeTextResponse:
    """
    Analisa sentimento de um texto.

    Retorna:
    - Tipo e score de sentimento
    - Emocoes detectadas
    - Aspectos identificados
    - Keywords e topicos
    - Indicadores especiais (urgencia, reclamacao, churn)
    - Regras acionadas
    """
    analyzer = SentimentAnalyzer(session)
    return await analyzer.analyze_text(request)


@router.post(
    "/analyze/batch",
    response_model=BatchAnalyzeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analisar textos em lote",
)
async def batch_analyze(
    request: BatchAnalyzeRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> BatchAnalyzeResponse:
    """Analisa multiplos textos em lote (max 100)."""
    analyzer = SentimentAnalyzer(session)
    return await analyzer.batch_analyze(request)


@router.get(
    "/analyses",
    response_model=SentimentAnalysisListResponse,
    summary="Listar analises",
)
async def list_analyses(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sentiment_type: Optional[SentimentType] = None,
    source_type: Optional[SourceType] = None,
    customer_id: Optional[UUID] = None,
    has_urgency: Optional[bool] = None,
    has_complaint: Optional[bool] = None,
    requires_action: Optional[bool] = None,
    is_reviewed: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    order_by: str = Query("created_at", regex="^(created_at|sentiment_score|analyzed_at)$"),
    order_desc: bool = True,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentAnalysisListResponse:
    """Lista analises de sentimento com filtros."""
    repository = SentimentRepository(session)

    filters = {
        "sentiment_types": [sentiment_type] if sentiment_type else None,
        "source_types": [source_type] if source_type else None,
        "customer_id": customer_id,
        "has_urgency": has_urgency,
        "has_complaint": has_complaint,
        "requires_action": requires_action,
        "is_reviewed": is_reviewed,
        "date_from": date_from,
        "date_to": date_to,
    }

    # Remover None
    filters = {k: v for k, v in filters.items() if v is not None}

    items, total = await repository.list_analyses(
        filters=filters,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_desc=order_desc,
    )

    pages = (total + page_size - 1) // page_size

    return SentimentAnalysisListResponse(
        items=[SentimentAnalysisSummary(**a.to_summary()) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/analyses/{analysis_id}",
    response_model=SentimentAnalysisResponse,
    summary="Buscar analise",
)
async def get_analysis(
    analysis_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentAnalysisResponse:
    """Busca analise de sentimento por ID."""
    repository = SentimentRepository(session)
    analysis = await repository.get_analysis(analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analise nao encontrada",
        )

    return SentimentAnalysisResponse.model_validate(analysis)


@router.patch(
    "/analyses/{analysis_id}",
    response_model=SentimentAnalysisResponse,
    summary="Atualizar analise",
)
async def update_analysis(
    analysis_id: UUID,
    data: SentimentAnalysisUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentAnalysisResponse:
    """Atualiza analise (revisao, tags, etc)."""
    repository = SentimentRepository(session)

    updates = data.model_dump(exclude_unset=True)
    if data.is_reviewed:
        updates["reviewed_by"] = current_user.id
        updates["reviewed_at"] = datetime.utcnow()

    analysis = await repository.update_analysis(analysis_id, **updates)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analise nao encontrada",
        )

    return SentimentAnalysisResponse.model_validate(analysis)


@router.get(
    "/analyses/customer/{customer_id}",
    response_model=List[SentimentAnalysisSummary],
    summary="Analises por cliente",
)
async def get_customer_analyses(
    customer_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[SentimentAnalysisSummary]:
    """Busca analises de um cliente especifico."""
    repository = SentimentRepository(session)
    analyses = await repository.get_analyses_by_customer(customer_id, limit)
    return [SentimentAnalysisSummary(**a.to_summary()) for a in analyses]


@router.get(
    "/analyses/critical",
    response_model=List[SentimentAnalysisSummary],
    summary="Analises criticas",
)
async def get_critical_analyses(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[SentimentAnalysisSummary]:
    """Busca analises criticas recentes."""
    repository = SentimentRepository(session)
    analyses = await repository.get_critical_analyses(hours=hours, limit=limit)
    return [SentimentAnalysisSummary(**a.to_summary()) for a in analyses]


# ============================================================
# Rule Endpoints
# ============================================================

@router.post(
    "/rules",
    response_model=SentimentRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar regra",
)
async def create_rule(
    data: SentimentRuleCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentRuleResponse:
    """Cria nova regra de sentimento."""
    service = SentimentAlertService(session)
    rule = await service.create_rule(data, user_id=current_user.id)
    return SentimentRuleResponse.model_validate(rule)


@router.get(
    "/rules",
    response_model=SentimentRuleListResponse,
    summary="Listar regras",
)
async def list_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[RuleCategory] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentRuleListResponse:
    """Lista regras de sentimento."""
    repository = SentimentRepository(session)

    items, total = await repository.list_rules(
        category=category,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    return SentimentRuleListResponse(
        items=[SentimentRuleResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/rules/{rule_id}",
    response_model=SentimentRuleResponse,
    summary="Buscar regra",
)
async def get_rule(
    rule_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentRuleResponse:
    """Busca regra por ID."""
    repository = SentimentRepository(session)
    rule = await repository.get_rule(rule_id)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada",
        )

    return SentimentRuleResponse.model_validate(rule)


@router.patch(
    "/rules/{rule_id}",
    response_model=SentimentRuleResponse,
    summary="Atualizar regra",
)
async def update_rule(
    rule_id: UUID,
    data: SentimentRuleUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentRuleResponse:
    """Atualiza regra de sentimento."""
    service = SentimentAlertService(session)

    updates = data.model_dump(exclude_unset=True)
    rule = await service.update_rule(rule_id, updates, user_id=current_user.id)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada ou e do sistema",
        )

    return SentimentRuleResponse.model_validate(rule)


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover regra",
)
async def delete_rule(
    rule_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> None:
    """Remove regra de sentimento (apenas regras customizadas)."""
    service = SentimentAlertService(session)

    deleted = await service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada ou e do sistema",
        )


@router.post(
    "/rules/{rule_id}/toggle",
    response_model=SentimentRuleResponse,
    summary="Ativar/desativar regra",
)
async def toggle_rule(
    rule_id: UUID,
    is_active: bool,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentRuleResponse:
    """Ativa ou desativa uma regra."""
    service = SentimentAlertService(session)
    rule = await service.toggle_rule(rule_id, is_active)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada",
        )

    return SentimentRuleResponse.model_validate(rule)


@router.post(
    "/rules/{rule_id}/feedback",
    response_model=SentimentRuleResponse,
    summary="Feedback de regra",
)
async def rule_feedback(
    rule_id: UUID,
    is_correct: bool,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentRuleResponse:
    """Registra feedback de precisao de uma regra."""
    service = SentimentAlertService(session)
    rule = await service.record_rule_feedback(rule_id, is_correct)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada",
        )

    return SentimentRuleResponse.model_validate(rule)


@router.post(
    "/rules/initialize",
    summary="Inicializar regras padrao",
)
async def initialize_default_rules(
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Inicializa regras padrao do sistema."""
    service = SentimentAlertService(session)
    rules = await service.initialize_default_rules()
    return {"created": len(rules), "rules": [r.code for r in rules]}


# ============================================================
# Trend Endpoints
# ============================================================

@router.get(
    "/trends",
    response_model=SentimentTrendListResponse,
    summary="Listar tendencias",
)
async def list_trends(
    period_type: Optional[TrendPeriod] = None,
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentTrendListResponse:
    """Lista tendencias de sentimento."""
    repository = SentimentRepository(session)

    trends = await repository.list_trends(
        period_type=period_type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )

    return SentimentTrendListResponse(
        items=[TrendSummary(**t.to_summary()) for t in trends],
        total=len(trends),
    )


@router.get(
    "/trends/{trend_id}",
    response_model=SentimentTrendResponse,
    summary="Buscar tendencia",
)
async def get_trend(
    trend_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentTrendResponse:
    """Busca tendencia por ID."""
    repository = SentimentRepository(session)
    trend = await repository.get_trend(trend_id)

    if not trend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tendencia nao encontrada",
        )

    return SentimentTrendResponse.model_validate(trend)


@router.post(
    "/trends/calculate",
    response_model=SentimentTrendResponse,
    summary="Calcular tendencia",
)
async def calculate_trend(
    period_type: TrendPeriod,
    period_start: datetime,
    period_end: datetime,
    category: TrendCategory = TrendCategory.OVERALL,
    category_value: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> SentimentTrendResponse:
    """Calcula tendencia para um periodo especifico."""
    calculator = TrendCalculator(session)

    trend = await calculator.calculate_trend(
        period_type=period_type,
        period_start=period_start,
        period_end=period_end,
        category=category,
        category_value=category_value,
    )

    return SentimentTrendResponse.model_validate(trend)


@router.get(
    "/trends/compare",
    summary="Comparar tendencias",
)
async def compare_trends(
    period_type: TrendPeriod = TrendPeriod.WEEKLY,
    category: TrendCategory = TrendCategory.OVERALL,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Compara tendencia atual com periodo anterior."""
    calculator = TrendCalculator(session)

    now = datetime.utcnow()
    if period_type == TrendPeriod.DAILY:
        current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        current_end = now
    elif period_type == TrendPeriod.WEEKLY:
        days_since_monday = now.weekday()
        current_start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        current_end = now
    else:
        current_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_end = now

    comparison = await calculator.get_trend_comparison(
        period_type=period_type,
        current_start=current_start,
        current_end=current_end,
        category=category,
    )

    return comparison


@router.get(
    "/trends/timeline",
    summary="Timeline de tendencias",
)
async def get_trend_timeline(
    period_type: TrendPeriod = TrendPeriod.DAILY,
    periods: int = Query(30, ge=1, le=365),
    category: TrendCategory = TrendCategory.OVERALL,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna timeline de tendencias."""
    calculator = TrendCalculator(session)

    timeline = await calculator.get_trend_timeline(
        period_type=period_type,
        periods=periods,
        category=category,
    )

    return {"period_type": period_type.value, "periods": periods, "data": timeline}


# ============================================================
# Insight Endpoints
# ============================================================

@router.post(
    "/insights",
    response_model=FeedbackInsightResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar insight",
)
async def create_insight(
    data: FeedbackInsightCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Cria insight manualmente."""
    from modules.ai.sentiment_analysis.models import FeedbackInsight

    repository = SentimentRepository(session)

    insight = FeedbackInsight(
        title=data.title,
        description=data.description,
        insight_type=data.insight_type,
        priority=data.priority,
        category=data.category,
        subcategory=data.subcategory,
        tags=data.tags or [],
        scope=data.scope,
        scope_value=data.scope_value,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        entity_name=data.entity_name,
        impact_score=data.impact_score,
        confidence_score=data.confidence_score,
        urgency_score=data.urgency_score,
        actionability_score=data.actionability_score,
        supporting_data=data.supporting_data or {},
        analysis_ids=[str(aid) for aid in data.analysis_ids] if data.analysis_ids else [],
        period_start=data.period_start,
        period_end=data.period_end,
        avg_sentiment=data.avg_sentiment,
        sentiment_change=data.sentiment_change,
        volume=data.volume,
        affected_customers=data.affected_customers,
        related_keywords=data.related_keywords or [],
        related_topics=data.related_topics or [],
        related_aspects=data.related_aspects or [],
        recommendations=[r.model_dump() for r in data.recommendations] if data.recommendations else [],
        predicted_impact=data.predicted_impact,
        predicted_revenue_impact=data.predicted_revenue_impact,
        predicted_churn_impact=data.predicted_churn_impact,
        valid_until=data.valid_until,
        is_recurring=data.is_recurring,
        notify_recipients=data.notify_recipients or [],
        generated_by="manual",
    )

    insight = await repository.create_insight(insight)
    return FeedbackInsightResponse.model_validate(insight)


@router.get(
    "/insights",
    response_model=FeedbackInsightListResponse,
    summary="Listar insights",
)
async def list_insights(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    insight_type: Optional[InsightType] = None,
    priority: Optional[InsightPriority] = None,
    status_filter: Optional[InsightStatus] = Query(None, alias="status"),
    category: Optional[str] = None,
    is_actionable: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightListResponse:
    """Lista insights com filtros."""
    repository = SentimentRepository(session)

    filters = {
        "insight_types": [insight_type] if insight_type else None,
        "priorities": [priority] if priority else None,
        "statuses": [status_filter] if status_filter else None,
        "category": category,
    }
    filters = {k: v for k, v in filters.items() if v is not None}

    items, total = await repository.list_insights(
        filters=filters,
        page=page,
        page_size=page_size,
    )

    return FeedbackInsightListResponse(
        items=[InsightSummary(**i.to_summary()) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/insights/active",
    response_model=List[InsightSummary],
    summary="Insights ativos",
)
async def get_active_insights(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[InsightSummary]:
    """Retorna insights ativos."""
    generator = InsightGenerator(session)
    insights = await generator.get_active_insights(limit=limit)
    return [InsightSummary(**i.to_summary()) for i in insights]


@router.get(
    "/insights/critical",
    response_model=List[InsightSummary],
    summary="Insights criticos",
)
async def get_critical_insights(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[InsightSummary]:
    """Retorna insights criticos."""
    generator = InsightGenerator(session)
    insights = await generator.get_critical_insights(limit=limit)
    return [InsightSummary(**i.to_summary()) for i in insights]


@router.get(
    "/insights/{insight_id}",
    response_model=FeedbackInsightResponse,
    summary="Buscar insight",
)
async def get_insight(
    insight_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Busca insight por ID."""
    repository = SentimentRepository(session)
    insight = await repository.get_insight(insight_id)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight nao encontrado",
        )

    return FeedbackInsightResponse.model_validate(insight)


@router.patch(
    "/insights/{insight_id}",
    response_model=FeedbackInsightResponse,
    summary="Atualizar insight",
)
async def update_insight(
    insight_id: UUID,
    data: FeedbackInsightUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Atualiza insight."""
    repository = SentimentRepository(session)

    updates = data.model_dump(exclude_unset=True)
    insight = await repository.update_insight(insight_id, **updates)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight nao encontrado",
        )

    return FeedbackInsightResponse.model_validate(insight)


@router.post(
    "/insights/{insight_id}/acknowledge",
    response_model=FeedbackInsightResponse,
    summary="Reconhecer insight",
)
async def acknowledge_insight(
    insight_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Reconhece um insight."""
    generator = InsightGenerator(session)
    insight = await generator.acknowledge_insight(insight_id, current_user.id)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight nao encontrado",
        )

    return FeedbackInsightResponse.model_validate(insight)


@router.post(
    "/insights/{insight_id}/assign",
    response_model=FeedbackInsightResponse,
    summary="Atribuir insight",
)
async def assign_insight(
    insight_id: UUID,
    user_id: UUID,
    team: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Atribui insight a um usuario."""
    generator = InsightGenerator(session)
    insight = await generator.assign_insight(insight_id, user_id, team)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight nao encontrado",
        )

    return FeedbackInsightResponse.model_validate(insight)


@router.post(
    "/insights/{insight_id}/resolve",
    response_model=FeedbackInsightResponse,
    summary="Resolver insight",
)
async def resolve_insight(
    insight_id: UUID,
    outcome: str,
    notes: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Resolve um insight."""
    generator = InsightGenerator(session)
    insight = await generator.resolve_insight(
        insight_id, current_user.id, outcome, notes
    )

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight nao encontrado",
        )

    return FeedbackInsightResponse.model_validate(insight)


@router.post(
    "/insights/{insight_id}/feedback",
    response_model=FeedbackInsightResponse,
    summary="Feedback de insight",
)
async def insight_feedback(
    insight_id: UUID,
    was_useful: bool,
    rating: Optional[int] = Query(None, ge=1, le=5),
    notes: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> FeedbackInsightResponse:
    """Adiciona feedback sobre utilidade do insight."""
    generator = InsightGenerator(session)
    insight = await generator.add_insight_feedback(
        insight_id, was_useful, rating, notes
    )

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight nao encontrado",
        )

    return FeedbackInsightResponse.model_validate(insight)


@router.post(
    "/insights/generate",
    summary="Gerar insights",
)
async def generate_insights(
    period_type: TrendPeriod = TrendPeriod.DAILY,
    days_back: int = Query(1, ge=1, le=30),
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Gera insights automaticamente baseado em tendencias."""
    generator = InsightGenerator(session)
    insights = await generator.analyze_and_generate(
        period_type=period_type,
        days_back=days_back,
    )
    return {
        "generated": len(insights),
        "insights": [i.to_summary() for i in insights],
    }


# ============================================================
# Dashboard & Stats Endpoints
# ============================================================

@router.get(
    "/dashboard",
    summary="Dashboard de sentimento",
)
async def get_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna dashboard completo de sentimento."""
    calculator = TrendCalculator(session)
    return await calculator.get_dashboard_summary()


@router.get(
    "/stats",
    summary="Estatisticas de sentimento",
)
async def get_stats(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna estatisticas de analises."""
    repository = SentimentRepository(session)
    return await repository.get_analysis_stats(
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/stats/emotions",
    summary="Distribuicao de emocoes",
)
async def get_emotion_stats(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna distribuicao de emocoes."""
    repository = SentimentRepository(session)
    distribution = await repository.get_emotion_distribution(
        date_from=date_from,
        date_to=date_to,
    )

    total = sum(distribution.values())
    primary = max(distribution, key=distribution.get) if distribution else "neutral"

    return {
        "emotions": distribution,
        "total": total,
        "primary_emotion": primary,
        "primary_emotion_pct": (
            (distribution.get(primary, 0) / total * 100) if total > 0 else 0
        ),
    }


@router.get(
    "/stats/keywords",
    summary="Top keywords",
)
async def get_top_keywords(
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna keywords mais frequentes."""
    repository = SentimentRepository(session)
    keywords = await repository.get_top_keywords(
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
    return {"keywords": keywords, "total": len(keywords)}


@router.get(
    "/stats/rules",
    summary="Estatisticas de regras",
)
async def get_rule_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna estatisticas das regras."""
    service = SentimentAlertService(session)
    return await service.get_rule_stats()


@router.get(
    "/stats/insights",
    summary="Estatisticas de insights",
)
async def get_insight_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
):
    """Retorna estatisticas de insights."""
    generator = InsightGenerator(session)
    return await generator.get_insight_stats()

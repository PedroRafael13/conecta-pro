"""Controller de Notificações Inteligentes - Sprint 03."""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligent", tags=["Intelligent Notifications"])


# ============================================================================
# Schemas
# ============================================================================


class PersonalizeRequest(BaseModel):
    """Request para personalização."""

    user_id: int
    notification_type: str
    template_title: str
    template_body: str
    context: dict[str, Any] | None = None
    tone: str = "friendly"


class PersonalizeResponse(BaseModel):
    """Response de personalização."""

    title: str
    body: str
    summary: str | None
    channel_recommendation: str
    optimal_send_time: datetime
    personalization_score: float
    engagement_prediction: float


class TimingRequest(BaseModel):
    """Request para otimização de timing."""

    user_id: int
    notification_type: str
    earliest_time: datetime | None = None
    deadline: datetime | None = None


class TimingResponse(BaseModel):
    """Response de timing."""

    optimal_datetime: datetime
    confidence: float
    reasoning: str
    alternative_times: list[datetime]
    should_delay: bool


class ChannelRequest(BaseModel):
    """Request para seleção de canal."""

    user_id: int
    notification_type: str
    content: dict[str, Any] | None = None


class ChannelResponse(BaseModel):
    """Response de canal."""

    primary_channel: str
    fallback_channels: list[str]
    confidence: float
    reasoning: str
    expected_delivery_rate: float


class BehaviorAnalysisResponse(BaseModel):
    """Response de análise comportamental."""

    user_id: int
    engagement_level: str
    patterns: list[str]
    preferred_hours: list[int]
    notification_fatigue_score: float
    churn_risk_score: float
    segment: str


class ExperimentCreateRequest(BaseModel):
    """Request para criar experimento."""

    name: str
    description: str
    variants: list[dict[str, Any]]
    primary_metric: str = "open_rate"
    target_sample_size: int = 1000
    min_confidence: float = 0.95


class ExperimentResponse(BaseModel):
    """Response de experimento."""

    id: str
    name: str
    status: str
    variants_count: int
    created_at: datetime


class ExperimentResultResponse(BaseModel):
    """Response de resultado de experimento."""

    experiment_id: str
    winning_variant: str | None
    is_significant: bool
    confidence_level: float
    lift_percentage: float
    recommendation: str


class ConsentRequest(BaseModel):
    """Request para consentimento."""

    consent_type: str
    granted: bool
    consent_text: str
    version: str


class ConsentResponse(BaseModel):
    """Response de consentimento."""

    id: str
    consent_type: str
    status: str
    granted_at: datetime | None


class DataRequestCreate(BaseModel):
    """Request para solicitação de dados LGPD."""

    request_type: str = Field(..., description="access, portability, deletion, rectification")
    requester_email: str


class DataRequestResponse(BaseModel):
    """Response de solicitação de dados."""

    id: str
    request_type: str
    status: str
    deadline: datetime
    verification_required: bool


class AnalyticsDashboardResponse(BaseModel):
    """Response do dashboard de analytics."""

    generated_at: datetime
    summary: dict[str, Any]
    health_score: float
    alerts: list[str]


# ============================================================================
# Personalization Endpoints
# ============================================================================


@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize_notification(
    request: PersonalizeRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> PersonalizeResponse:
    """
    Personaliza uma notificação com base no perfil do usuário.

    Utiliza:
    - Análise comportamental
    - Otimização de timing
    - Seleção de canal
    - Personalização de conteúdo
    """
    from modules.notifications.engine import (
        ChannelSelector,
        PersonalizationEngine,
        TimingOptimizer,
    )

    engine = PersonalizationEngine()
    timing = TimingOptimizer()
    channel_selector = ChannelSelector()

    # Personalizar
    result = await engine.personalize_notification(
        db=db,
        user_id=request.user_id,
        notification_type=request.notification_type,
        template_title=request.template_title,
        template_body=request.template_body,
        context=request.context,
    )

    # Timing
    timing_result = await timing.optimize_send_time(
        db=db,
        user_id=request.user_id,
        notification_type=request.notification_type,
    )

    # Canal
    channel_result = await channel_selector.select_channel(
        db=db,
        user_id=request.user_id,
        notification_type=request.notification_type,
    )

    return PersonalizeResponse(
        title=result.content.title,
        body=result.content.body,
        summary=result.content.summary,
        channel_recommendation=channel_result.primary_channel.value,
        optimal_send_time=timing_result.optimal_datetime,
        personalization_score=result.content.personalization_score,
        engagement_prediction=result.engagement_prediction,
    )


@router.post("/timing/optimize", response_model=TimingResponse)
async def optimize_send_timing(
    request: TimingRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> TimingResponse:
    """Otimiza horário de envio de notificação."""
    from modules.notifications.engine import TimingOptimizer

    optimizer = TimingOptimizer()

    result = await optimizer.optimize_send_time(
        db=db,
        user_id=request.user_id,
        notification_type=request.notification_type,
        earliest_time=request.earliest_time,
        deadline=request.deadline,
    )

    return TimingResponse(
        optimal_datetime=result.optimal_datetime,
        confidence=result.confidence,
        reasoning=result.reasoning,
        alternative_times=result.alternative_times,
        should_delay=result.should_delay,
    )


@router.post("/channel/select", response_model=ChannelResponse)
async def select_notification_channel(
    request: ChannelRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ChannelResponse:
    """Seleciona melhor canal para notificação."""
    from modules.notifications.engine import ChannelSelector

    selector = ChannelSelector()

    result = await selector.select_channel(
        db=db,
        user_id=request.user_id,
        notification_type=request.notification_type,
        content=request.content,
    )

    return ChannelResponse(
        primary_channel=result.primary_channel.value,
        fallback_channels=[c.value for c in result.fallback_channels],
        confidence=result.confidence,
        reasoning=result.reasoning,
        expected_delivery_rate=result.expected_delivery_rate,
    )


# ============================================================================
# Behavior Analysis Endpoints
# ============================================================================


@router.get("/behavior/{user_id}", response_model=BehaviorAnalysisResponse)
async def get_user_behavior_analysis(
    user_id: int,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> BehaviorAnalysisResponse:
    """Obtém análise comportamental do usuário."""
    from modules.notifications.engine import BehavioralAnalyzer

    analyzer = BehavioralAnalyzer()
    profile = await analyzer.analyze_user(db, user_id)

    return BehaviorAnalysisResponse(
        user_id=user_id,
        engagement_level=profile.engagement_level.value,
        patterns=[p.value for p in profile.patterns],
        preferred_hours=profile.preferred_hours,
        notification_fatigue_score=profile.notification_fatigue_score,
        churn_risk_score=profile.churn_risk_score,
        segment=profile.segment,
    )


@router.get("/behavior/{user_id}/insights")
async def get_behavior_insights(
    user_id: int,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Obtém insights comportamentais."""
    from modules.notifications.engine import BehavioralAnalyzer

    analyzer = BehavioralAnalyzer()
    insights = await analyzer.get_insights(db, user_id)

    return [
        {
            "type": i.insight_type,
            "description": i.description,
            "confidence": i.confidence,
            "recommendation": i.recommendation,
        }
        for i in insights
    ]


@router.get("/behavior/{user_id}/engagement-prediction")
async def predict_engagement(
    user_id: int,
    notification_type: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Prediz engajamento do usuário com notificação."""
    from modules.notifications.engine import BehavioralAnalyzer

    analyzer = BehavioralAnalyzer()
    prediction = await analyzer.predict_engagement(
        db=db,
        user_id=user_id,
        notification_type=notification_type,
    )

    return {
        "will_open": prediction.will_open,
        "open_probability": prediction.open_probability,
        "will_click": prediction.will_click,
        "click_probability": prediction.click_probability,
        "best_time_to_send": prediction.best_time_to_send,
        "reasoning": prediction.reasoning,
    }


# ============================================================================
# A/B Testing Endpoints
# ============================================================================


@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(
    request: ExperimentCreateRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    """Cria novo experimento A/B."""
    from modules.notifications.testing import ABTestingEngine, MetricType

    engine = ABTestingEngine()

    metric = MetricType(request.primary_metric)

    experiment = await engine.create_experiment(
        db=db,
        name=request.name,
        description=request.description,
        variants=request.variants,
        primary_metric=metric,
        target_sample_size=request.target_sample_size,
        min_confidence=request.min_confidence,
    )

    return ExperimentResponse(
        id=str(experiment.id),
        name=experiment.name,
        status=experiment.status.value,
        variants_count=len(experiment.variants),
        created_at=experiment.created_at,
    )


@router.post("/experiments/{experiment_id}/start", response_model=ExperimentResponse)
async def start_experiment(
    experiment_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ExperimentResponse:
    """Inicia um experimento."""
    from modules.notifications.testing import ABTestingEngine

    engine = ABTestingEngine()

    experiment = await engine.start_experiment(db, UUID(experiment_id))

    return ExperimentResponse(
        id=str(experiment.id),
        name=experiment.name,
        status=experiment.status.value,
        variants_count=len(experiment.variants),
        created_at=experiment.created_at,
    )


@router.get("/experiments/{experiment_id}/results", response_model=ExperimentResultResponse)
async def get_experiment_results(
    experiment_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ExperimentResultResponse:
    """Obtém resultados de um experimento."""
    from modules.notifications.testing import ABTestingEngine

    engine = ABTestingEngine()

    result = await engine.get_results(db, UUID(experiment_id))

    return ExperimentResultResponse(
        experiment_id=str(result.experiment_id),
        winning_variant=result.winning_variant,
        is_significant=result.statistical_significance.is_significant,
        confidence_level=result.statistical_significance.confidence_level,
        lift_percentage=result.statistical_significance.lift_percentage,
        recommendation=result.recommendation,
    )


@router.get("/experiments/{experiment_id}/allocate/{user_id}")
async def allocate_user_to_variant(
    experiment_id: str,
    user_id: int,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Aloca usuário a uma variante do experimento."""
    from modules.notifications.testing import ABTestingEngine

    engine = ABTestingEngine()

    variant = engine.allocate_user(UUID(experiment_id), user_id)

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found or not running",
        )

    return {
        "experiment_id": experiment_id,
        "user_id": user_id,
        "variant_id": variant.variant_id,
        "variant_name": variant.name,
        "config": variant.config,
    }


@router.post("/experiments/{experiment_id}/event")
async def record_experiment_event(
    experiment_id: str,
    variant_id: str,
    event_type: str,
    user_id: int,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Registra evento de experimento."""
    from modules.notifications.testing import ABTestingEngine

    engine = ABTestingEngine()

    await engine.record_event(
        db=db,
        experiment_id=UUID(experiment_id),
        variant_id=variant_id,
        event_type=event_type,
        user_id=user_id,
    )

    return {"status": "recorded"}


# ============================================================================
# Analytics Endpoints
# ============================================================================


@router.get("/analytics/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> AnalyticsDashboardResponse:
    """Obtém dashboard de analytics."""
    from modules.notifications.analytics import NotificationAnalytics

    analytics = NotificationAnalytics()
    dashboard = await analytics.get_dashboard(db)

    return AnalyticsDashboardResponse(
        generated_at=dashboard.generated_at,
        summary=dashboard.summary,
        health_score=dashboard.health_score,
        alerts=dashboard.alerts,
    )


@router.get("/analytics/channels")
async def get_channel_analytics(
    days: int = Query(default=30, ge=1, le=90),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Obtém analytics por canal."""
    from modules.notifications.analytics import NotificationAnalytics

    analytics = NotificationAnalytics()
    dashboard = await analytics.get_dashboard(db)

    return [
        {
            "channel": c.channel,
            "total_sent": c.total_sent,
            "delivery_rate": c.delivery_rate,
            "open_rate": c.open_rate,
            "click_rate": c.click_rate,
            "trend": c.trend.value,
        }
        for c in dashboard.channel_breakdown
    ]


@router.get("/analytics/user/{user_id}")
async def get_user_analytics(
    user_id: int,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Obtém analytics de um usuário."""
    from modules.notifications.analytics import NotificationAnalytics

    analytics = NotificationAnalytics()
    return await analytics.get_user_analytics(db, user_id)


@router.get("/analytics/report")
async def generate_report(
    start_date: datetime,
    end_date: datetime,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Gera relatório de métricas."""
    from modules.notifications.analytics import NotificationAnalytics

    analytics = NotificationAnalytics()
    report = await analytics.generate_report(db, start_date, end_date)

    return {
        "period": f"{report.period_start} - {report.period_end}",
        "total_notifications": report.total_notifications,
        "total_users": report.total_unique_users,
        "insights": report.insights,
        "recommendations": report.recommendations,
    }


# ============================================================================
# LGPD Compliance Endpoints
# ============================================================================


@router.post("/consent", response_model=ConsentResponse)
async def record_consent(
    request: ConsentRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ConsentResponse:
    """Registra consentimento do usuário."""
    from modules.notifications.compliance import ConsentType, LGPDComplianceManager

    manager = LGPDComplianceManager()

    consent = await manager.record_consent(
        db=db,
        user_id=current_user.id,
        consent_type=ConsentType(request.consent_type),
        granted=request.granted,
        consent_text=request.consent_text,
        version=request.version,
    )

    return ConsentResponse(
        id=str(consent.id),
        consent_type=consent.consent_type.value,
        status=consent.status.value,
        granted_at=consent.granted_at,
    )


@router.delete("/consent/{consent_type}")
async def withdraw_consent(
    consent_type: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Retira consentimento."""
    from modules.notifications.compliance import ConsentType, LGPDComplianceManager

    manager = LGPDComplianceManager()

    await manager.withdraw_consent(
        db=db,
        user_id=current_user.id,
        consent_type=ConsentType(consent_type),
    )

    return {"status": "withdrawn"}


@router.get("/consent")
async def get_user_consents(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Obtém consentimentos do usuário."""
    from modules.notifications.compliance import LGPDComplianceManager

    manager = LGPDComplianceManager()
    consents = await manager.get_user_consents(db, current_user.id)

    return [
        {
            "id": str(c.id),
            "type": c.consent_type.value,
            "status": c.status.value,
            "granted_at": c.granted_at,
            "expires_at": c.expires_at,
        }
        for c in consents
    ]


@router.post("/data-request", response_model=DataRequestResponse)
async def create_data_request(
    request: DataRequestCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> DataRequestResponse:
    """Cria solicitação de dados (LGPD)."""
    from modules.notifications.compliance import DataRequestType, LGPDComplianceManager

    manager = LGPDComplianceManager()

    data_request = await manager.create_data_request(
        db=db,
        user_id=current_user.id,
        request_type=DataRequestType(request.request_type),
        requester_email=request.requester_email,
    )

    return DataRequestResponse(
        id=str(data_request.id),
        request_type=data_request.request_type.value,
        status=data_request.status.value,
        deadline=data_request.deadline,
        verification_required=not data_request.verified,
    )


@router.post("/data-request/{request_id}/verify")
async def verify_data_request(
    request_id: str,
    token: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Verifica solicitação de dados."""
    from modules.notifications.compliance import LGPDComplianceManager

    manager = LGPDComplianceManager()
    verified = await manager.verify_data_request(db, UUID(request_id), token)

    return {"verified": verified}


@router.get("/compliance/audit-logs")
async def get_audit_logs(
    user_id: int | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Obtém logs de auditoria de compliance."""
    from modules.notifications.compliance import LGPDComplianceManager

    manager = LGPDComplianceManager()
    logs = await manager.get_audit_logs(db, user_id=user_id, limit=limit)

    return [
        {
            "id": str(log.id),
            "timestamp": log.timestamp,
            "action": log.action,
            "user_id": log.user_id,
            "resource_type": log.resource_type,
            "reason": log.reason,
        }
        for log in logs
    ]


# ============================================================================
# Utility Endpoints
# ============================================================================


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check do módulo de notificações inteligentes."""
    return {
        "status": "healthy",
        "module": "intelligent_notifications",
        "version": "1.0.0",
    }


@router.get("/can-send/{user_id}")
async def can_send_notification(
    user_id: int,
    notification_type: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Verifica se pode enviar notificação para usuário."""
    from modules.notifications.compliance import LGPDComplianceManager
    from modules.notifications.engine import BehavioralAnalyzer

    # Verificar compliance
    compliance_manager = LGPDComplianceManager()
    can_send, reason = await compliance_manager.can_send_notification(db, user_id, notification_type)

    if not can_send:
        return {
            "can_send": False,
            "reason": reason,
        }

    # Verificar comportamento
    analyzer = BehavioralAnalyzer()
    should_send, behavior_reason = await analyzer.should_send_notification(db, user_id, notification_type)

    return {
        "can_send": should_send,
        "reason": behavior_reason,
        "compliance_check": "passed",
    }

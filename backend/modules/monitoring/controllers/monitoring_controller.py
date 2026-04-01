"""
Controller de monitoramento - Early Warning System.

Endpoints para:
- Dashboard de monitoramento
- Gerenciamento de alertas
- Configuracao de thresholds
- Metricas em tempo real
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_active_user, require_roles
from core.database import get_db
from core.logging import logger

from ..models.alert import AlertLevel
from ..schemas.alert_schemas import (
    AlertAcknowledge,
    AlertResolve,
    AlertResponse,
    AlertsListResponse,
    AlertStats,
)
from ..schemas.dashboard_schemas import (
    SystemHealthResponse,
)
from ..schemas.threshold_schemas import (
    ThresholdCreate,
    ThresholdResponse,
    ThresholdUpdate,
)
from ..services.alert_manager import AlertManagerService
from ..services.dashboard_service import DashboardService
from ..services.early_warning import EarlyWarningService
from ..services.metric_collector import get_metric_collector

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


# ============================================================
# Dashboard Endpoints
# ============================================================


@router.get("/dashboard", response_model=dict)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Retorna dashboard completo de monitoramento.

    Inclui:
    - Saude geral do sistema
    - Metricas em tempo real
    - Alertas recentes
    - Estatisticas
    """
    service = DashboardService(db)
    return await service.get_full_dashboard()


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Retorna saude geral do sistema.

    Niveis:
    - green: Operacao normal
    - yellow: Atencao necessaria
    - orange: Acao corretiva em 24-48h
    - red: Intervencao imediata
    """
    service = DashboardService(db)
    return await service.get_system_health()


@router.get("/metrics")
async def get_current_metrics(
    current_user=Depends(get_current_active_user),
):
    """Retorna metricas coletadas em tempo real."""
    collector = get_metric_collector()
    return collector.get_latest_metrics()


# ============================================================
# Alert Endpoints
# ============================================================


@router.get("/alerts", response_model=AlertsListResponse)
async def list_alerts(
    level: AlertLevel | None = Query(None, description="Filtrar por nivel"),
    active_only: bool = Query(True, description="Apenas alertas ativos"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Lista alertas do sistema."""
    service = EarlyWarningService(db)
    alerts = await service.get_active_alerts(level=level, limit=limit)

    return AlertsListResponse(
        total=len(alerts),
        active=sum(1 for a in alerts if a.status.value == "active"),
        critical=sum(1 for a in alerts if a.is_critical),
        alerts=[AlertResponse.model_validate(a) for a in alerts],
    )


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Retorna detalhes de um alerta."""
    from ..repositories.alert_repository import AlertRepository

    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta nao encontrado",
        )

    return AlertResponse.model_validate(alert)


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
    data: AlertAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Reconhece um alerta."""
    service = EarlyWarningService(db)
    alert = await service.acknowledge_alert(
        alert_id=alert_id,
        user_id=current_user.id,
        notes=data.notes,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta nao encontrado",
        )

    logger.info(f"Alerta {alert_id} reconhecido por {current_user.email}")
    return AlertResponse.model_validate(alert)


@router.post("/alerts/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: UUID,
    data: AlertResolve,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Resolve um alerta."""
    service = EarlyWarningService(db)
    alert = await service.resolve_alert(
        alert_id=alert_id,
        user_id=current_user.id,
        notes=data.notes,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta nao encontrado",
        )

    logger.info(f"Alerta {alert_id} resolvido por {current_user.email}")
    return AlertResponse.model_validate(alert)


@router.get("/alerts/statistics", response_model=AlertStats)
async def get_alert_statistics(
    period_hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Retorna estatisticas de alertas."""
    service = AlertManagerService(db)
    stats = await service.get_alert_statistics(period_hours=period_hours)
    return AlertStats(**stats)


# ============================================================
# Threshold Endpoints
# ============================================================


@router.get("/thresholds", response_model=list[ThresholdResponse])
async def list_thresholds(
    category: str | None = Query(None),
    enabled_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Lista todos os thresholds configurados."""
    from ..repositories.threshold_repository import ThresholdRepository

    repo = ThresholdRepository(db)
    thresholds = await repo.get_all(enabled_only=enabled_only, category=category)
    return [ThresholdResponse.model_validate(t) for t in thresholds]


@router.post("/thresholds", response_model=ThresholdResponse, status_code=status.HTTP_201_CREATED)
async def create_threshold(
    data: ThresholdCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "operator")),
):
    """Cria um novo threshold."""
    from ..models.metric_threshold import MetricThreshold
    from ..repositories.threshold_repository import ThresholdRepository

    repo = ThresholdRepository(db)

    # Verificar se ja existe
    if await repo.exists(data.metric_name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Threshold para metrica '{data.metric_name}' ja existe",
        )

    threshold = MetricThreshold(**data.model_dump())
    threshold = await repo.create(threshold)

    logger.info(f"Threshold criado: {data.metric_name} por {current_user.email}")
    return ThresholdResponse.model_validate(threshold)


@router.get("/thresholds/{threshold_id}", response_model=ThresholdResponse)
async def get_threshold(
    threshold_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Retorna detalhes de um threshold."""
    from ..repositories.threshold_repository import ThresholdRepository

    repo = ThresholdRepository(db)
    threshold = await repo.get_by_id(threshold_id)

    if not threshold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threshold nao encontrado",
        )

    return ThresholdResponse.model_validate(threshold)


@router.patch("/thresholds/{threshold_id}", response_model=ThresholdResponse)
async def update_threshold(
    threshold_id: UUID,
    data: ThresholdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "operator")),
):
    """Atualiza um threshold."""
    from ..repositories.threshold_repository import ThresholdRepository

    repo = ThresholdRepository(db)
    threshold = await repo.get_by_id(threshold_id)

    if not threshold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threshold nao encontrado",
        )

    # Atualizar campos
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(threshold, field, value)

    threshold = await repo.update(threshold)

    logger.info(f"Threshold {threshold_id} atualizado por {current_user.email}")
    return ThresholdResponse.model_validate(threshold)


@router.delete("/thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_threshold(
    threshold_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    """Remove um threshold."""
    from ..repositories.threshold_repository import ThresholdRepository

    repo = ThresholdRepository(db)
    deleted = await repo.delete(threshold_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threshold nao encontrado",
        )

    logger.info(f"Threshold {threshold_id} removido por {current_user.email}")


# ============================================================
# Admin Endpoints
# ============================================================


@router.post("/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_thresholds(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    """
    Inicializa thresholds padrao do Pre-Mortem Analysis.

    Este endpoint cria os thresholds padrao definidos no
    Early Warning System se ainda nao existirem.
    """
    service = EarlyWarningService(db)
    created = await service.initialize_thresholds()

    return {
        "message": f"{created} thresholds criados",
        "status": "initialized",
    }


@router.post("/check-escalations")
async def check_escalations(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "operator")),
):
    """
    Verifica e executa escalacoes de alertas.

    Escala automaticamente alertas que ultrapassaram
    o tempo maximo sem resolucao.
    """
    service = AlertManagerService(db)
    escalated = await service.check_escalations()

    return {
        "escalated_count": len(escalated),
        "alerts": [str(a.id) for a in escalated],
    }


@router.post("/cleanup")
async def cleanup_old_alerts(
    days: int = Query(90, ge=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    """
    Remove alertas antigos resolvidos.

    Desativa alertas resolvidos ha mais de X dias.
    """
    service = AlertManagerService(db)
    cleaned = await service.cleanup_old_alerts(days=days)

    return {
        "cleaned_count": cleaned,
        "retention_days": days,
    }

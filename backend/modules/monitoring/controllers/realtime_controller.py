"""
Real-time Analytics Controller - FASE 3 ONDA 1
==============================================

Endpoints para analytics e alertas em tempo real.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Path, Query, WebSocket, WebSocketDisconnect

from core.auth.dependencies import CurrentActiveUser

from ..services.realtime_analytics_service import AlertSeverity, MetricPoint, MetricType, realtime_analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["Real-time Analytics"])

# WebSocket connections para streaming
active_connections: list[WebSocket] = []


async def broadcast_to_websockets(data: dict[str, Any]):
    """Broadcast data para todas as conexões WebSocket ativas."""
    if not active_connections:
        return

    message = json.dumps(data, default=str)
    disconnected = []

    for websocket in active_connections:
        try:
            await websocket.send_text(message)
        except Exception:
            disconnected.append(websocket)

    # Remove conexões desconectadas
    for ws in disconnected:
        active_connections.remove(ws)


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint para streaming de métricas em tempo real.
    """
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Envia métricas em tempo real a cada 5 segundos
            metrics = await realtime_analytics_service.get_realtime_metrics()

            data = {
                "type": "metrics_update",
                "timestamp": metrics.timestamp.isoformat(),
                "metrics": [
                    {"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat(), "tags": m.tags}
                    for m in metrics.metrics
                ],
                "active_alerts": len(metrics.active_alerts),
                "system_health": metrics.system_health,
            }

            await websocket.send_text(json.dumps(data, default=str))
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        active_connections.remove(websocket)


@router.post("/metrics", summary="Enviar Métrica", description="Envia uma métrica para análise em tempo real")
async def send_metric(
    current_user: CurrentActiveUser,
    name: str,
    value: float,
    metric_type: MetricType = MetricType.GAUGE,
    tags: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Envia uma métrica para o sistema de analytics.
    """
    try:
        metric = MetricPoint(name=name, value=value, timestamp=datetime.now(), tags=tags or {}, type=metric_type)

        await realtime_analytics_service.collect_metric(metric)

        # Broadcast para WebSockets
        await broadcast_to_websockets(
            {"type": "new_metric", "metric": {"name": name, "value": value, "timestamp": metric.timestamp.isoformat()}}
        )

        return {"status": "success", "metric_name": name, "value": value, "timestamp": metric.timestamp.isoformat()}

    except Exception as e:
        logger.error(f"Erro ao enviar métrica {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/metrics/current", summary="Métricas Atuais", description="Retorna snapshot das métricas em tempo real")
async def get_current_metrics(current_user: CurrentActiveUser) -> dict[str, Any]:
    """
    Retorna todas as métricas atuais em tempo real.
    """
    try:
        metrics = await realtime_analytics_service.get_realtime_metrics()

        return {
            "timestamp": metrics.timestamp.isoformat(),
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "tags": m.tags,
                    "type": m.type.value,
                }
                for m in metrics.metrics
            ],
            "total_count": len(metrics.metrics),
            "system_health": metrics.system_health,
        }

    except Exception as e:
        logger.error(f"Erro ao buscar métricas atuais: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/alerts/active", summary="Alertas Ativos", description="Retorna todos os alertas ativos no sistema")
async def get_active_alerts(current_user: CurrentActiveUser) -> dict[str, Any]:
    """
    Retorna alertas ativos em tempo real.
    """
    try:
        metrics = await realtime_analytics_service.get_realtime_metrics()

        alerts_data = [
            {
                "id": alert.id,
                "title": alert.title,
                "description": alert.description,
                "metric": alert.metric,
                "current_value": alert.current_value,
                "threshold": alert.threshold,
                "severity": alert.severity.value,
                "triggered_at": alert.triggered_at.isoformat(),
                "actions": alert.actions,
                "tags": alert.tags,
            }
            for alert in metrics.active_alerts
        ]

        # Agrupa por severidade
        by_severity = {}
        for alert in metrics.active_alerts:
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "alerts": alerts_data,
            "total_count": len(alerts_data),
            "by_severity": by_severity,
            "has_critical": any(alert.severity == AlertSeverity.CRITICAL for alert in metrics.active_alerts),
        }

    except Exception as e:
        logger.error(f"Erro ao buscar alertas ativos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/alerts/{alert_id}/resolve", summary="Resolver Alerta", description="Marca um alerta como resolvido")
async def resolve_alert(
    current_user: CurrentActiveUser, alert_id: str = Path(..., description="ID do alerta")
) -> dict[str, Any]:
    """
    Resolve um alerta específico.
    """
    try:
        success = await realtime_analytics_service.resolve_alert(alert_id)

        if success:
            # Broadcast resolução para WebSockets
            await broadcast_to_websockets(
                {"type": "alert_resolved", "alert_id": alert_id, "resolved_at": datetime.now().isoformat()}
            )

            return {"status": "success", "alert_id": alert_id, "resolved_at": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=404, detail=f"Alerta {alert_id} não encontrado")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resolver alerta {alert_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get(
    "/metrics/{metric_name}/history",
    summary="Histórico da Métrica",
    description="Retorna histórico de uma métrica específica",
)
async def get_metric_history(
    current_user: CurrentActiveUser,
    metric_name: str = Path(..., description="Nome da métrica"),
    points: int = Query(100, description="Número de pontos (max 1000)"),
) -> dict[str, Any]:
    """
    Retorna histórico de uma métrica.
    """
    try:
        if points > 1000:
            points = 1000

        history = await realtime_analytics_service.get_metric_history(metric_name, points)

        if not history:
            raise HTTPException(status_code=404, detail=f"Métrica '{metric_name}' não encontrada")

        # Calcula estatísticas
        values = [point["value"] for point in history]
        stats = {"min": min(values), "max": max(values), "avg": sum(values) / len(values), "count": len(values)}

        return {
            "metric_name": metric_name,
            "history": history,
            "statistics": stats,
            "points_requested": points,
            "points_returned": len(history),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de {metric_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post(
    "/thresholds", summary="Configurar Threshold", description="Configura threshold customizado para uma métrica"
)
async def set_custom_threshold(
    metric_name: str,
    current_user: CurrentActiveUser,
    min_value: float | None = None,
    max_value: float | None = None,
    severity: AlertSeverity = AlertSeverity.MEDIUM,
) -> dict[str, Any]:
    """
    Configura threshold customizado para alertas.
    """
    try:
        await realtime_analytics_service.add_custom_threshold(
            metric_name=metric_name, min_value=min_value, max_value=max_value, severity=severity
        )

        return {
            "status": "success",
            "metric_name": metric_name,
            "min_value": min_value,
            "max_value": max_value,
            "severity": severity.value,
            "configured_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro ao configurar threshold para {metric_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/anomalies/summary", summary="Resumo de Anomalias", description="Retorna resumo de anomalias detectadas")
async def get_anomaly_summary(
    current_user: CurrentActiveUser, hours: int = Query(24, description="Período em horas (max 168)")
) -> dict[str, Any]:
    """
    Retorna resumo de anomalias detectadas.
    """
    try:
        if hours > 168:  # 1 semana
            hours = 168

        summary = await realtime_analytics_service.get_anomaly_summary(hours)

        return summary

    except Exception as e:
        logger.error(f"Erro ao gerar resumo de anomalias: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/dashboard", summary="Dashboard em Tempo Real", description="Retorna dashboard consolidado em tempo real")
async def get_realtime_dashboard(current_user: CurrentActiveUser) -> dict[str, Any]:
    """
    Retorna dashboard consolidado em tempo real.
    """
    try:
        metrics = await realtime_analytics_service.get_realtime_metrics()

        # Organiza métricas por categoria
        metrics_by_category = {"system": [], "business": [], "performance": [], "other": []}

        for metric in metrics.metrics:
            if metric.name in ["cpu_usage", "memory_usage", "disk_usage"]:
                metrics_by_category["system"].append(metric)
            elif metric.name in ["receita_diaria", "active_users", "transactions"]:
                metrics_by_category["business"].append(metric)
            elif metric.name in ["response_time", "error_rate", "throughput"]:
                metrics_by_category["performance"].append(metric)
            else:
                metrics_by_category["other"].append(metric)

        # Converte para JSON serializable
        dashboard_data = {}
        for category, metric_list in metrics_by_category.items():
            dashboard_data[category] = [
                {"name": m.name, "value": m.value, "timestamp": m.timestamp.isoformat(), "tags": m.tags}
                for m in metric_list
            ]

        return {
            "timestamp": metrics.timestamp.isoformat(),
            "metrics_by_category": dashboard_data,
            "active_alerts_count": len(metrics.active_alerts),
            "critical_alerts_count": sum(
                1 for alert in metrics.active_alerts if alert.severity == AlertSeverity.CRITICAL
            ),
            "system_health": metrics.system_health,
            "anomalies_count": len(metrics.anomalies),
            "total_metrics": len(metrics.metrics),
        }

    except Exception as e:
        logger.error(f"Erro ao gerar dashboard em tempo real: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/health", summary="Health Check Monitoring", description="Verifica saúde do sistema de monitoramento")
async def monitoring_health_check(current_user: CurrentActiveUser) -> dict[str, Any]:
    """
    Health check do sistema de monitoramento em tempo real.
    """
    try:
        metrics = await realtime_analytics_service.get_realtime_metrics()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(metrics.metrics),
            "alerts_count": len(metrics.active_alerts),
            "websocket_connections": len(active_connections),
            "system_health": metrics.system_health,
            "anomaly_detection": "active",
            "real_time_processing": "active",
        }

    except Exception as e:
        logger.error(f"Health check do monitoramento falhou: {str(e)}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

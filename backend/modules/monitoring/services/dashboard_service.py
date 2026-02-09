"""
Dashboard Service.

Fornece dados agregados para o dashboard de monitoramento.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert import Alert, AlertStatus
from ..models.metric_threshold import MetricThreshold
from .metric_collector import get_metric_collector


class DashboardService:
    """
    Servico de dashboard de monitoramento.

    Agrega dados de:
    - Saude do sistema
    - Alertas ativos
    - Metricas em tempo real
    - Estatisticas historicas
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._startup_time = datetime.utcnow()

    async def get_full_dashboard(self) -> dict[str, Any]:
        """
        Retorna dados completos do dashboard.

        Returns:
            Dicionario com todos os dados do dashboard
        """
        return {
            "health": await self.get_system_health(),
            "metrics": await self.get_current_metrics(),
            "alerts": await self.get_recent_alerts(),
            "statistics": await self.get_statistics(),
            "thresholds": await self.get_threshold_status(),
        }

    async def get_system_health(self) -> dict[str, Any]:
        """Retorna saude geral do sistema."""
        # Alertas ativos
        stmt = select(Alert).where(
            Alert.status == AlertStatus.ACTIVE,
            Alert.is_active,
        )
        result = await self.db.execute(stmt)
        active_alerts = result.scalars().all()

        # Determinar nivel geral
        overall_level = "green"
        level_priority = {"green": 0, "yellow": 1, "orange": 2, "red": 3}

        for alert in active_alerts:
            if level_priority[alert.level.value] > level_priority[overall_level]:
                overall_level = alert.level.value

        # Score baseado no nivel
        scores = {"green": 100, "yellow": 75, "orange": 50, "red": 25}

        # Agrupar por categoria
        categories = {}
        for alert in active_alerts:
            cat = alert.details.get("category", "general") if alert.details else "general"
            if cat not in categories:
                categories[cat] = {
                    "name": cat,
                    "display_name": cat.replace("_", " ").title(),
                    "overall_level": "green",
                    "metrics_count": 0,
                    "green_count": 0,
                    "yellow_count": 0,
                    "orange_count": 0,
                    "red_count": 0,
                }
            categories[cat]["metrics_count"] += 1
            categories[cat][f"{alert.level.value}_count"] += 1
            if level_priority[alert.level.value] > level_priority[categories[cat]["overall_level"]]:
                categories[cat]["overall_level"] = alert.level.value

        # Uptime
        uptime = (datetime.utcnow() - self._startup_time).total_seconds()

        return {
            "overall_level": overall_level,
            "overall_score": scores[overall_level],
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "categories": list(categories.values()),
            "active_alerts": len(active_alerts),
            "critical_alerts": sum(1 for a in active_alerts if a.is_critical),
        }

    async def get_current_metrics(self) -> list[dict[str, Any]]:
        """Retorna metricas atuais com status."""
        collector = get_metric_collector()
        raw_metrics = collector.get_latest_metrics()

        # Buscar thresholds para determinar status
        stmt = select(MetricThreshold).where(
            MetricThreshold.enabled,
            MetricThreshold.is_active,
        )
        result = await self.db.execute(stmt)
        thresholds = {t.metric_name: t for t in result.scalars().all()}

        metrics = []
        for name, value in raw_metrics.get("metrics", {}).items():
            if not isinstance(value, (int, float)):
                continue

            threshold = thresholds.get(name)
            if threshold:
                level = threshold.get_level_for_value(value)
                metrics.append(
                    {
                        "name": name,
                        "display_name": threshold.display_name,
                        "category": threshold.category,
                        "current_value": value,
                        "unit": threshold.unit,
                        "level": level,
                        "threshold_yellow": threshold.yellow_threshold,
                        "threshold_orange": threshold.orange_threshold,
                        "threshold_red": threshold.red_threshold,
                        "last_updated": raw_metrics.get("last_collection"),
                    }
                )
            else:
                # Metrica sem threshold definido
                metrics.append(
                    {
                        "name": name,
                        "display_name": name.replace("_", " ").title(),
                        "category": "other",
                        "current_value": value,
                        "unit": "",
                        "level": "green",
                        "threshold_yellow": None,
                        "threshold_orange": None,
                        "threshold_red": None,
                        "last_updated": raw_metrics.get("last_collection"),
                    }
                )

        return metrics

    async def get_recent_alerts(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Retorna alertas recentes."""
        stmt = select(Alert).where(Alert.is_active).order_by(Alert.triggered_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        alerts = result.scalars().all()

        return [
            {
                "id": str(alert.id),
                "metric_name": alert.metric_name,
                "level": alert.level.value,
                "status": alert.status.value,
                "title": alert.title,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "triggered_at": alert.triggered_at.isoformat(),
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "duration_seconds": alert.duration_seconds,
            }
            for alert in alerts
        ]

    async def get_statistics(self) -> dict[str, Any]:
        """Retorna estatisticas gerais."""
        now = datetime.utcnow()

        # Alertas 24h
        threshold_24h = now - timedelta(hours=24)
        stmt = select(func.count(Alert.id)).where(
            Alert.triggered_at >= threshold_24h,
            Alert.is_active,
        )
        result = await self.db.execute(stmt)
        alerts_24h = result.scalar() or 0

        # Alertas 7d
        threshold_7d = now - timedelta(days=7)
        stmt = select(func.count(Alert.id)).where(
            Alert.triggered_at >= threshold_7d,
            Alert.is_active,
        )
        result = await self.db.execute(stmt)
        alerts_7d = result.scalar() or 0

        # Alertas resolvidos 24h
        stmt = select(func.count(Alert.id)).where(
            Alert.triggered_at >= threshold_24h,
            Alert.status == AlertStatus.RESOLVED,
            Alert.is_active,
        )
        result = await self.db.execute(stmt)
        resolved_24h = result.scalar() or 0

        # MTTR medio
        stmt = select(Alert).where(
            Alert.triggered_at >= threshold_7d,
            Alert.status == AlertStatus.RESOLVED,
            Alert.is_active,
        )
        result = await self.db.execute(stmt)
        resolved_alerts = result.scalars().all()

        mttr = 0.0
        if resolved_alerts:
            total_time = sum((a.resolved_at - a.triggered_at).total_seconds() for a in resolved_alerts if a.resolved_at)
            mttr = total_time / len(resolved_alerts)

        return {
            "alerts_24h": alerts_24h,
            "alerts_7d": alerts_7d,
            "resolved_24h": resolved_24h,
            "resolution_rate_24h": round(resolved_24h / alerts_24h * 100, 1) if alerts_24h > 0 else 100,
            "mttr_seconds": mttr,
            "mttr_formatted": self._format_uptime(mttr),
        }

    async def get_threshold_status(self) -> list[dict[str, Any]]:
        """Retorna status de todos os thresholds."""
        stmt = (
            select(MetricThreshold)
            .where(
                MetricThreshold.is_active,
            )
            .order_by(MetricThreshold.category, MetricThreshold.metric_name)
        )

        result = await self.db.execute(stmt)
        thresholds = result.scalars().all()

        collector = get_metric_collector()
        metrics = collector.get_latest_metrics().get("metrics", {})

        return [
            {
                "id": str(t.id),
                "metric_name": t.metric_name,
                "display_name": t.display_name,
                "category": t.category,
                "enabled": t.enabled,
                "current_value": metrics.get(t.metric_name),
                "current_level": t.get_level_for_value(metrics.get(t.metric_name, 0)),
                "yellow_threshold": t.yellow_threshold,
                "orange_threshold": t.orange_threshold,
                "red_threshold": t.red_threshold,
                "unit": t.unit,
                "last_alert_at": t.last_alert_at.isoformat() if t.last_alert_at else None,
            }
            for t in thresholds
        ]

    def _format_uptime(self, seconds: float) -> str:
        """Formata tempo em formato legivel."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}min"
        elif seconds < 86400:
            return f"{seconds / 3600:.1f}h"
        else:
            return f"{seconds / 86400:.1f}d"

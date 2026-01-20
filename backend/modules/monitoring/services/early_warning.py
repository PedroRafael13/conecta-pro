"""
Early Warning System - Servico principal.

Monitora metricas do sistema e gera alertas quando
thresholds sao ultrapassados.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from core.monitoring import get_metrics, set_gauge

from ..models.alert import Alert, AlertLevel, AlertStatus
from ..models.metric_threshold import MetricThreshold, ThresholdType


class EarlyWarningService:
    """
    Servico de Early Warning System.

    Responsavel por:
    - Monitorar metricas continuamente
    - Avaliar thresholds
    - Gerar alertas quando necessario
    - Escalar alertas criticos
    """

    # Definicao de thresholds padrao (Pre-Mortem Analysis)
    DEFAULT_THRESHOLDS = [
        # Performance
        {
            "metric_name": "http_response_time_p95",
            "display_name": "Response Time P95",
            "category": "performance",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 500,
            "orange_threshold": 1000,
            "red_threshold": 2000,
            "unit": "ms",
        },
        {
            "metric_name": "http_error_rate",
            "display_name": "HTTP Error Rate",
            "category": "performance",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 1.0,
            "orange_threshold": 3.0,
            "red_threshold": 5.0,
            "unit": "%",
        },
        {
            "metric_name": "cpu_usage",
            "display_name": "CPU Usage",
            "category": "performance",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 70,
            "orange_threshold": 85,
            "red_threshold": 95,
            "unit": "%",
        },
        {
            "metric_name": "memory_usage",
            "display_name": "Memory Usage",
            "category": "performance",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 70,
            "orange_threshold": 85,
            "red_threshold": 95,
            "unit": "%",
        },
        # Database
        {
            "metric_name": "db_connection_pool_usage",
            "display_name": "DB Connection Pool",
            "category": "database",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 70,
            "orange_threshold": 85,
            "red_threshold": 95,
            "unit": "%",
        },
        {
            "metric_name": "db_query_time_p95",
            "display_name": "DB Query Time P95",
            "category": "database",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 100,
            "orange_threshold": 500,
            "red_threshold": 1000,
            "unit": "ms",
        },
        # Redis
        {
            "metric_name": "redis_memory_usage",
            "display_name": "Redis Memory Usage",
            "category": "cache",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 70,
            "orange_threshold": 85,
            "red_threshold": 95,
            "unit": "%",
        },
        {
            "metric_name": "redis_hit_rate",
            "display_name": "Redis Hit Rate",
            "category": "cache",
            "threshold_type": ThresholdType.LOWER,
            "yellow_threshold": 90,
            "orange_threshold": 80,
            "red_threshold": 70,
            "unit": "%",
        },
        # API
        {
            "metric_name": "api_rate_limit_hits",
            "display_name": "Rate Limit Hits",
            "category": "api",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 50,
            "orange_threshold": 100,
            "red_threshold": 200,
            "unit": "/min",
        },
        # ML (para sprints futuros)
        {
            "metric_name": "ml_model_latency",
            "display_name": "ML Model Latency",
            "category": "ml",
            "threshold_type": ThresholdType.UPPER,
            "yellow_threshold": 200,
            "orange_threshold": 500,
            "red_threshold": 1000,
            "unit": "ms",
        },
        {
            "metric_name": "ml_prediction_accuracy",
            "display_name": "ML Prediction Accuracy",
            "category": "ml",
            "threshold_type": ThresholdType.LOWER,
            "yellow_threshold": 85,
            "orange_threshold": 80,
            "red_threshold": 75,
            "unit": "%",
        },
    ]

    def __init__(self, db: AsyncSession):
        self.db = db
        self._running = False
        self._check_interval = 30  # segundos
        self._consecutive_breaches: Dict[str, int] = {}
        self._last_alert_times: Dict[str, datetime] = {}

    async def initialize_thresholds(self) -> int:
        """
        Inicializa thresholds padrao no banco de dados.

        Returns:
            Numero de thresholds criados
        """
        created = 0

        for threshold_data in self.DEFAULT_THRESHOLDS:
            # Verificar se ja existe
            stmt = select(MetricThreshold).where(
                MetricThreshold.metric_name == threshold_data["metric_name"]
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                threshold = MetricThreshold(**threshold_data)
                self.db.add(threshold)
                created += 1
                logger.info(f"Threshold criado: {threshold_data['metric_name']}")

        await self.db.commit()
        logger.info(f"Inicializacao de thresholds concluida: {created} criados")
        return created

    async def check_metric(
        self,
        metric_name: str,
        value: float,
        source: str = "system",
    ) -> Optional[Alert]:
        """
        Verifica uma metrica contra seu threshold.

        Args:
            metric_name: Nome da metrica
            value: Valor atual
            source: Fonte da metrica

        Returns:
            Alert se threshold foi ultrapassado, None caso contrario
        """
        # Buscar threshold
        stmt = select(MetricThreshold).where(
            MetricThreshold.metric_name == metric_name,
            MetricThreshold.enabled == True,
            MetricThreshold.is_active == True,
        )
        result = await self.db.execute(stmt)
        threshold = result.scalar_one_or_none()

        if not threshold:
            logger.debug(f"Threshold nao encontrado para metrica: {metric_name}")
            return None

        # Determinar nivel
        level_str = threshold.get_level_for_value(value)

        if level_str == "green":
            # Resetar contador de breaches consecutivos
            self._consecutive_breaches[metric_name] = 0
            return None

        # Incrementar contador de breaches
        self._consecutive_breaches[metric_name] = (
            self._consecutive_breaches.get(metric_name, 0) + 1
        )

        # Verificar se atingiu numero minimo de breaches
        if self._consecutive_breaches[metric_name] < threshold.consecutive_breaches:
            logger.debug(
                f"Metrica {metric_name} em breach {self._consecutive_breaches[metric_name]}/{threshold.consecutive_breaches}"
            )
            return None

        # Verificar cooldown
        last_alert = self._last_alert_times.get(metric_name)
        if last_alert:
            elapsed = (datetime.utcnow() - last_alert).total_seconds()
            if elapsed < threshold.cooldown_seconds:
                logger.debug(f"Metrica {metric_name} em cooldown ({elapsed:.0f}s)")
                return None

        # Criar alerta
        level = AlertLevel(level_str)
        alert = await self._create_alert(
            metric_name=metric_name,
            value=value,
            threshold=threshold,
            level=level,
            source=source,
        )

        # Atualizar timestamps
        self._last_alert_times[metric_name] = datetime.utcnow()
        threshold.last_alert_at = datetime.utcnow()
        threshold.last_value = value
        await self.db.commit()

        # Registrar metrica de alerta
        set_gauge(
            "early_warning_alert_level",
            {"red": 4, "orange": 3, "yellow": 2, "green": 1}.get(level_str, 0),
            {"metric": metric_name},
        )

        return alert

    async def _create_alert(
        self,
        metric_name: str,
        value: float,
        threshold: MetricThreshold,
        level: AlertLevel,
        source: str,
    ) -> Alert:
        """Cria um novo alerta."""
        threshold_value = threshold.get_threshold_for_level(level.value)

        alert = Alert(
            metric_name=metric_name,
            source=source,
            level=level,
            status=AlertStatus.ACTIVE,
            current_value=value,
            threshold_value=threshold_value,
            title=f"{threshold.display_name} em nivel {level.value.upper()}",
            message=self._generate_alert_message(threshold, value, level),
            details={
                "category": threshold.category,
                "unit": threshold.unit,
                "threshold_type": threshold.threshold_type.value,
                "consecutive_breaches": self._consecutive_breaches.get(metric_name, 1),
            },
            threshold_id=threshold.id,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(
            f"ALERTA [{level.value.upper()}] {metric_name}: {value}{threshold.unit} "
            f"(threshold: {threshold_value}{threshold.unit})"
        )

        return alert

    def _generate_alert_message(
        self,
        threshold: MetricThreshold,
        value: float,
        level: AlertLevel,
    ) -> str:
        """Gera mensagem descritiva para o alerta."""
        threshold_value = threshold.get_threshold_for_level(level.value)

        if threshold.threshold_type == ThresholdType.UPPER:
            direction = "acima"
            diff = value - threshold_value
        else:
            direction = "abaixo"
            diff = threshold_value - value

        severity_messages = {
            AlertLevel.YELLOW: "Atencao necessaria. Tendencia preocupante detectada.",
            AlertLevel.ORANGE: "Acao corretiva necessaria nas proximas 24-48h.",
            AlertLevel.RED: "CRITICO: Intervencao imediata necessaria!",
        }

        return (
            f"A metrica '{threshold.display_name}' esta {direction} do limite {level.value}.\n"
            f"Valor atual: {value}{threshold.unit}\n"
            f"Threshold: {threshold_value}{threshold.unit}\n"
            f"Diferenca: {abs(diff):.2f}{threshold.unit}\n\n"
            f"{severity_messages.get(level, '')}"
        )

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Retorna status de saude geral do sistema.

        Returns:
            Dicionario com status de saude
        """
        # Buscar alertas ativos
        stmt = select(Alert).where(
            Alert.status == AlertStatus.ACTIVE,
            Alert.is_active == True,
        )
        result = await self.db.execute(stmt)
        active_alerts = result.scalars().all()

        # Determinar nivel geral
        overall_level = "green"
        level_priority = {"green": 0, "yellow": 1, "orange": 2, "red": 3}

        for alert in active_alerts:
            if level_priority[alert.level.value] > level_priority[overall_level]:
                overall_level = alert.level.value

        # Calcular score (0-100)
        scores = {"green": 100, "yellow": 75, "orange": 50, "red": 25}
        overall_score = scores[overall_level]

        # Contar por categoria
        categories = {}
        for alert in active_alerts:
            cat = alert.details.get("category", "general") if alert.details else "general"
            if cat not in categories:
                categories[cat] = {"level": "green", "count": 0}
            categories[cat]["count"] += 1
            if level_priority[alert.level.value] > level_priority[categories[cat]["level"]]:
                categories[cat]["level"] = alert.level.value

        return {
            "overall_level": overall_level,
            "overall_score": overall_score,
            "active_alerts": len(active_alerts),
            "critical_alerts": sum(1 for a in active_alerts if a.is_critical),
            "categories": categories,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_active_alerts(
        self,
        level: Optional[AlertLevel] = None,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> List[Alert]:
        """Retorna alertas ativos."""
        stmt = select(Alert).where(
            Alert.status == AlertStatus.ACTIVE,
            Alert.is_active == True,
        )

        if level:
            stmt = stmt.where(Alert.level == level)

        stmt = stmt.order_by(Alert.triggered_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        alerts = result.scalars().all()

        # Filtrar por categoria se especificado
        if category:
            alerts = [
                a for a in alerts
                if a.details and a.details.get("category") == category
            ]

        return list(alerts)

    async def acknowledge_alert(
        self,
        alert_id: UUID,
        user_id: UUID,
        notes: Optional[str] = None,
    ) -> Optional[Alert]:
        """Reconhece um alerta."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.acknowledge(user_id)
        if notes:
            alert.details = alert.details or {}
            alert.details["acknowledge_notes"] = notes

        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"Alerta {alert_id} reconhecido por {user_id}")
        return alert

    async def resolve_alert(
        self,
        alert_id: UUID,
        user_id: UUID,
        notes: Optional[str] = None,
    ) -> Optional[Alert]:
        """Resolve um alerta."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.resolve(user_id, notes)
        await self.db.commit()
        await self.db.refresh(alert)

        # Resetar contadores
        self._consecutive_breaches[alert.metric_name] = 0

        logger.info(f"Alerta {alert_id} resolvido por {user_id}")
        return alert

    async def escalate_alert(self, alert_id: UUID) -> Optional[Alert]:
        """Escala um alerta."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.escalate()
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(f"Alerta {alert_id} escalado!")
        return alert

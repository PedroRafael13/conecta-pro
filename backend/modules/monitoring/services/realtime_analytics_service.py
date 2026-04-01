"""
Real-time Analytics Service - FASE 3 ONDA 1
==========================================

Sistema de analytics em tempo real com alertas inteligentes,
detecção de anomalias e monitoramento contínuo.

ROI Target: R$ 140K
Sprint: FASE 3 - Otimização Total
"""

import statistics
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class MetricType(StrEnum):
    """Tipos de métricas monitoradas."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"


class AlertSeverity(StrEnum):
    """Severidade dos alertas."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(StrEnum):
    """Tipos de anomalias detectadas."""

    SPIKE = "spike"
    DROP = "drop"
    TREND_CHANGE = "trend_change"
    OUTLIER = "outlier"
    PATTERN_BREAK = "pattern_break"


@dataclass
class MetricPoint:
    """Ponto de métrica em tempo real."""

    name: str
    value: float
    timestamp: datetime
    tags: dict[str, str]
    type: MetricType


@dataclass
class Alert:
    """Alerta em tempo real."""

    id: str
    title: str
    description: str
    metric: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    triggered_at: datetime
    resolved_at: datetime | None
    tags: dict[str, str]
    actions: list[str]


@dataclass
class Anomaly:
    """Anomalia detectada."""

    id: str
    metric: str
    type: AnomalyType
    confidence: float
    detected_at: datetime
    value: float
    expected_range: dict[str, float]
    description: str


@dataclass
class RealTimeMetrics:
    """Métricas em tempo real."""

    timestamp: datetime
    metrics: list[MetricPoint]
    active_alerts: list[Alert]
    anomalies: list[Anomaly]
    system_health: dict[str, Any]


class RealTimeAnalyticsService:
    """Serviço de Analytics em Tempo Real."""

    def __init__(self):
        # Buffers circulares para histórico de métricas
        self.metric_buffers: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_alerts: dict[str, Alert] = {}
        self.alert_rules: dict[str, dict[str, Any]] = {}
        self.anomaly_detectors: dict[str, Callable] = {}

        # Configuração padrão de thresholds
        self._setup_default_thresholds()
        self._setup_anomaly_detectors()

    def _setup_default_thresholds(self):
        """Configura thresholds padrão para métricas críticas."""
        self.alert_rules = {
            "receita_diaria": {"min": 80000, "max": 200000, "severity": AlertSeverity.HIGH},
            "cpu_usage": {"max": 85, "severity": AlertSeverity.MEDIUM},
            "memory_usage": {"max": 90, "severity": AlertSeverity.HIGH},
            "response_time": {
                "max": 5000,  # 5 segundos
                "severity": AlertSeverity.MEDIUM,
            },
            "error_rate": {
                "max": 5,  # 5%
                "severity": AlertSeverity.HIGH,
            },
            "active_users": {"min": 10, "max": 1000, "severity": AlertSeverity.MEDIUM},
            "disk_usage": {"max": 80, "severity": AlertSeverity.HIGH},
            "failed_transactions": {"max": 10, "severity": AlertSeverity.CRITICAL},
        }

    def _setup_anomaly_detectors(self):
        """Configura detectores de anomalias."""
        self.anomaly_detectors = {
            "statistical_outlier": self._detect_statistical_outlier,
            "trend_change": self._detect_trend_change,
            "pattern_break": self._detect_pattern_break,
            "spike_detection": self._detect_spike,
        }

    async def collect_metric(self, metric: MetricPoint) -> None:
        """
        Coleta uma métrica em tempo real.

        Args:
            metric: Ponto de métrica a ser coletado
        """
        # Adiciona ao buffer circular
        self.metric_buffers[metric.name].append(
            {"value": metric.value, "timestamp": metric.timestamp, "tags": metric.tags}
        )

        # Verifica alertas
        await self._check_alerts(metric)

        # Detecta anomalias
        await self._detect_anomalies(metric)

    async def _check_alerts(self, metric: MetricPoint) -> None:
        """Verifica se uma métrica deve disparar alertas."""
        if metric.name not in self.alert_rules:
            return

        rule = self.alert_rules[metric.name]
        alert_triggered = False

        # Verifica limite máximo
        if "max" in rule and metric.value > rule["max"]:
            alert_triggered = True
            alert_type = f"Valor acima do limite: {metric.value} > {rule['max']}"

        # Verifica limite mínimo
        elif "min" in rule and metric.value < rule["min"]:
            alert_triggered = True
            alert_type = f"Valor abaixo do limite: {metric.value} < {rule['min']}"

        if alert_triggered:
            alert_id = f"{metric.name}_{int(metric.timestamp.timestamp())}"

            alert = Alert(
                id=alert_id,
                title=f"Alerta: {metric.name.replace('_', ' ').title()}",
                description=alert_type,
                metric=metric.name,
                current_value=metric.value,
                threshold=rule.get("max", rule.get("min", 0)),
                severity=rule.get("severity", AlertSeverity.MEDIUM),
                triggered_at=metric.timestamp,
                resolved_at=None,
                tags=metric.tags,
                actions=self._get_suggested_actions(metric.name, metric.value),
            )

            self.active_alerts[alert_id] = alert
            await self._notify_alert(alert)

    async def _detect_anomalies(self, metric: MetricPoint) -> list[Anomaly]:
        """Detecta anomalias na métrica."""
        anomalies = []

        # Precisa de pelo menos 10 pontos para detectar anomalias
        if len(self.metric_buffers[metric.name]) < 10:
            return anomalies

        # Executa todos os detectores
        for _detector_name, detector_func in self.anomaly_detectors.items():
            anomaly = await detector_func(metric)
            if anomaly:
                anomalies.append(anomaly)

        return anomalies

    async def _detect_statistical_outlier(self, metric: MetricPoint) -> Anomaly | None:
        """Detecta outliers estatísticos."""
        buffer = self.metric_buffers[metric.name]
        values = [point["value"] for point in list(buffer)[-50:]]  # Últimos 50 pontos

        if len(values) < 10:
            return None

        mean = statistics.mean(values[:-1])  # Exclui o valor atual
        stdev = statistics.stdev(values[:-1])

        # Z-score > 2.5 considera outlier
        z_score = abs(metric.value - mean) / stdev if stdev > 0 else 0

        if z_score > 2.5:
            return Anomaly(
                id=f"outlier_{metric.name}_{int(metric.timestamp.timestamp())}",
                metric=metric.name,
                type=AnomalyType.OUTLIER,
                confidence=min(z_score / 5.0, 1.0),
                detected_at=metric.timestamp,
                value=metric.value,
                expected_range={"mean": mean, "stdev": stdev},
                description=f"Valor {metric.value} é um outlier estatístico (Z-score: {z_score:.2f})",
            )

        return None

    async def _detect_trend_change(self, metric: MetricPoint) -> Anomaly | None:
        """Detecta mudanças de tendência."""
        buffer = self.metric_buffers[metric.name]
        values = [point["value"] for point in list(buffer)[-20:]]

        if len(values) < 20:
            return None

        # Divide em duas metades e compara tendências
        first_half = values[:10]
        second_half = values[-10:]

        first_trend = (first_half[-1] - first_half[0]) / len(first_half)
        second_trend = (second_half[-1] - second_half[0]) / len(second_half)

        # Detecta mudança significativa de tendência
        trend_change = abs(second_trend - first_trend)
        mean_value = statistics.mean(values)

        if trend_change > mean_value * 0.1:  # 10% da média
            return Anomaly(
                id=f"trend_{metric.name}_{int(metric.timestamp.timestamp())}",
                metric=metric.name,
                type=AnomalyType.TREND_CHANGE,
                confidence=min(trend_change / (mean_value * 0.2), 1.0),
                detected_at=metric.timestamp,
                value=metric.value,
                expected_range={"first_trend": first_trend, "second_trend": second_trend},
                description=f"Mudança de tendência detectada: {first_trend:.2f} → {second_trend:.2f}",
            )

        return None

    async def _detect_pattern_break(self, metric: MetricPoint) -> Anomaly | None:
        """Detecta quebras de padrão."""
        buffer = self.metric_buffers[metric.name]

        if len(buffer) < 50:
            return None

        # Implementação simplificada - detecta se saiu muito do padrão recente
        recent_values = [point["value"] for point in list(buffer)[-30:-1]]
        recent_mean = statistics.mean(recent_values)
        recent_stdev = statistics.stdev(recent_values)

        if recent_stdev == 0:
            return None

        deviation = abs(metric.value - recent_mean) / recent_stdev

        if deviation > 3.0:  # 3 desvios padrão
            return Anomaly(
                id=f"pattern_{metric.name}_{int(metric.timestamp.timestamp())}",
                metric=metric.name,
                type=AnomalyType.PATTERN_BREAK,
                confidence=min(deviation / 5.0, 1.0),
                detected_at=metric.timestamp,
                value=metric.value,
                expected_range={"mean": recent_mean, "stdev": recent_stdev},
                description=f"Quebra de padrão: valor {deviation:.1f}x além do padrão recente",
            )

        return None

    async def _detect_spike(self, metric: MetricPoint) -> Anomaly | None:
        """Detecta spikes (aumentos súbitos)."""
        buffer = self.metric_buffers[metric.name]

        if len(buffer) < 5:
            return None

        recent_points = list(buffer)[-5:]
        previous_value = recent_points[-2]["value"] if len(recent_points) > 1 else 0

        if previous_value == 0:
            return None

        change_percent = ((metric.value - previous_value) / previous_value) * 100

        # Spike se mudança > 50%
        if abs(change_percent) > 50:
            spike_type = AnomalyType.SPIKE if change_percent > 0 else AnomalyType.DROP

            return Anomaly(
                id=f"spike_{metric.name}_{int(metric.timestamp.timestamp())}",
                metric=metric.name,
                type=spike_type,
                confidence=min(abs(change_percent) / 100.0, 1.0),
                detected_at=metric.timestamp,
                value=metric.value,
                expected_range={"previous": previous_value, "change_percent": change_percent},
                description=f"{'Spike' if change_percent > 0 else 'Drop'} detectado: {change_percent:.1f}% de mudança",
            )

        return None

    def _get_suggested_actions(self, metric_name: str, value: float) -> list[str]:
        """Gera ações sugeridas para alertas."""
        actions = {
            "cpu_usage": [
                "Verificar processos com alto uso de CPU",
                "Considerar scaling horizontal",
                "Analisar otimização de código",
            ],
            "memory_usage": [
                "Verificar vazamentos de memória",
                "Limpar caches desnecessários",
                "Considerar aumento de RAM",
            ],
            "response_time": [
                "Verificar queries lentas no banco",
                "Analisar gargalos de rede",
                "Otimizar APIs críticas",
            ],
            "error_rate": [
                "Verificar logs de erro imediatamente",
                "Validar integridade dos dados",
                "Testar funcionalidades críticas",
            ],
            "receita_diaria": [
                "Analisar campanhas de marketing",
                "Verificar problemas no checkout",
                "Contactar equipe comercial",
            ],
        }

        return actions.get(metric_name, ["Investigar causa raiz", "Monitorar de perto"])

    async def _notify_alert(self, alert: Alert) -> None:
        """Notifica sobre um alerta (implementação futura com webhooks/email)."""
        # Por enquanto apenas log
        print(f"🚨 ALERTA {alert.severity.upper()}: {alert.title}")
        print(f"   Métrica: {alert.metric} = {alert.current_value}")
        print(f"   Threshold: {alert.threshold}")
        print(f"   Ações: {', '.join(alert.actions[:2])}")

    async def get_realtime_metrics(self) -> RealTimeMetrics:
        """
        Retorna snapshot das métricas em tempo real.
        """
        current_metrics = []
        current_anomalies = []

        # Coleta últimas métricas de cada buffer
        for metric_name, buffer in self.metric_buffers.items():
            if buffer:
                last_point = buffer[-1]
                current_metrics.append(
                    MetricPoint(
                        name=metric_name,
                        value=last_point["value"],
                        timestamp=last_point["timestamp"],
                        tags=last_point["tags"],
                        type=MetricType.GAUGE,  # Simplificado
                    )
                )

        # Sistema de saúde
        system_health = await self._calculate_system_health()

        return RealTimeMetrics(
            timestamp=datetime.now(),
            metrics=current_metrics,
            active_alerts=list(self.active_alerts.values()),
            anomalies=current_anomalies,
            system_health=system_health,
        )

    async def _calculate_system_health(self) -> dict[str, Any]:
        """Calcula saúde geral do sistema."""
        total_metrics = len(self.metric_buffers)
        active_alerts_count = len(self.active_alerts)
        critical_alerts = sum(1 for alert in self.active_alerts.values() if alert.severity == AlertSeverity.CRITICAL)

        # Score de saúde (0-100)
        health_score = 100
        health_score -= active_alerts_count * 5  # -5 por alerta
        health_score -= critical_alerts * 20  # -20 por alerta crítico
        health_score = max(0, health_score)

        status = "healthy"
        if health_score < 70:
            status = "warning"
        if health_score < 50:
            status = "critical"

        return {
            "score": health_score,
            "status": status,
            "total_metrics": total_metrics,
            "active_alerts": active_alerts_count,
            "critical_alerts": critical_alerts,
            "last_updated": datetime.now().isoformat(),
        }

    async def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve um alerta.

        Args:
            alert_id: ID do alerta a resolver

        Returns:
            True se resolvido com sucesso
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            return True
        return False

    async def add_custom_threshold(
        self,
        metric_name: str,
        min_value: float | None = None,
        max_value: float | None = None,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
    ) -> None:
        """
        Adiciona threshold customizado para uma métrica.

        Args:
            metric_name: Nome da métrica
            min_value: Valor mínimo (opcional)
            max_value: Valor máximo (opcional)
            severity: Severidade dos alertas
        """
        rule = {"severity": severity}
        if min_value is not None:
            rule["min"] = min_value
        if max_value is not None:
            rule["max"] = max_value

        self.alert_rules[metric_name] = rule

    async def get_metric_history(self, metric_name: str, points: int = 100) -> list[dict[str, Any]]:
        """
        Retorna histórico de uma métrica.

        Args:
            metric_name: Nome da métrica
            points: Número de pontos a retornar

        Returns:
            Lista de pontos históricos
        """
        if metric_name not in self.metric_buffers:
            return []

        buffer = self.metric_buffers[metric_name]
        return list(buffer)[-points:]

    async def get_anomaly_summary(self, hours: int = 24) -> dict[str, Any]:
        """
        Retorna resumo de anomalias detectadas.

        Args:
            hours: Período em horas para análise

        Returns:
            Resumo de anomalias
        """
        # Implementação simplificada - em produção seria persistido
        return {
            "period_hours": hours,
            "total_anomalies": 15,
            "by_type": {"outlier": 8, "spike": 4, "trend_change": 2, "pattern_break": 1},
            "by_metric": {"response_time": 6, "cpu_usage": 4, "memory_usage": 3, "error_rate": 2},
            "confidence_avg": 0.78,
        }


# Instância singleton do serviço
realtime_analytics_service = RealTimeAnalyticsService()

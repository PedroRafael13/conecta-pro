"""Sistema de monitoramento de modelos ML em produção."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

import numpy as np
from scipy import stats
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.ml.registry.model_registry import (
    ModelRegistry,
    ModelStage,
)

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Status de saúde do modelo."""

    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class DriftType(Enum):
    """Tipos de drift detectáveis."""

    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    LABEL_DRIFT = "label_drift"
    FEATURE_DRIFT = "feature_drift"


class AlertSeverity(Enum):
    """Severidade dos alertas."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Métrica de performance do modelo."""

    name: str
    value: float
    baseline: float
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime
    is_healthy: bool
    trend: str  # improving, stable, degrading


@dataclass
class DriftAlert:
    """Alerta de drift detectado."""

    id: UUID
    model_name: str
    drift_type: DriftType
    severity: AlertSeverity
    feature_name: Optional[str]
    drift_score: float
    baseline_distribution: dict[str, Any]
    current_distribution: dict[str, Any]
    description: str
    recommended_action: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False


@dataclass
class ModelHealth:
    """Status de saúde completo do modelo."""

    model_name: str
    model_version: str
    status: HealthStatus
    overall_score: float  # 0-100
    metrics: list[PerformanceMetric]
    drift_alerts: list[DriftAlert]
    last_prediction_time: Optional[datetime]
    predictions_last_hour: int
    avg_latency_ms: float
    error_rate: float
    recommendations: list[str]
    checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MonitoringDashboard:
    """Dashboard de monitoramento."""

    timestamp: datetime
    models_monitored: int
    healthy_models: int
    warning_models: int
    critical_models: int
    active_alerts: int
    models_status: list[dict[str, Any]]
    recent_alerts: list[DriftAlert]
    system_metrics: dict[str, float]


class ModelMonitor:
    """
    Sistema de monitoramento de modelos ML.

    Funcionalidades:
    - Monitoramento de performance
    - Detecção de data drift
    - Detecção de concept drift
    - Alertas automáticos
    - Dashboard de saúde
    - Recomendações de retrain
    """

    # Thresholds padrão
    DEFAULT_THRESHOLDS = {
        "accuracy": {"warning": 0.85, "critical": 0.75},
        "precision": {"warning": 0.80, "critical": 0.70},
        "recall": {"warning": 0.80, "critical": 0.70},
        "f1_score": {"warning": 0.80, "critical": 0.70},
        "auc_roc": {"warning": 0.85, "critical": 0.75},
        "latency_ms": {"warning": 100, "critical": 500},
        "error_rate": {"warning": 0.05, "critical": 0.10},
        "drift_score": {"warning": 0.15, "critical": 0.30},
    }

    def __init__(
        self,
        model_registry: Optional[ModelRegistry] = None,
    ) -> None:
        """
        Inicializa o monitor.

        Args:
            model_registry: Registry de modelos
        """
        self.model_registry = model_registry or ModelRegistry()
        self._alerts: list[DriftAlert] = []
        self._metrics_history: dict[str, list[PerformanceMetric]] = {}
        self._prediction_counts: dict[str, int] = {}
        self._latencies: dict[str, list[float]] = {}
        self._baseline_distributions: dict[str, dict] = {}

    async def check_model_health(
        self,
        db: AsyncSession,
        model_name: str,
    ) -> ModelHealth:
        """
        Verifica saúde de um modelo.

        Args:
            db: Sessão do banco
            model_name: Nome do modelo

        Returns:
            ModelHealth com status completo
        """
        logger.info(f"Verificando saúde do modelo: {model_name}")

        # Obter versão em produção
        model_version = self.model_registry.get_model_version(
            model_name,
            stage=ModelStage.PRODUCTION
        )

        if not model_version:
            return ModelHealth(
                model_name=model_name,
                model_version="unknown",
                status=HealthStatus.UNKNOWN,
                overall_score=0,
                metrics=[],
                drift_alerts=[],
                last_prediction_time=None,
                predictions_last_hour=0,
                avg_latency_ms=0,
                error_rate=0,
                recommendations=["Modelo não encontrado em produção"],
            )

        # Coletar métricas de performance
        metrics = await self._collect_performance_metrics(
            db, model_name, model_version.version
        )

        # Verificar drift
        drift_alerts = await self._check_drift(db, model_name)

        # Métricas operacionais
        predictions = self._prediction_counts.get(model_name, 0)
        latencies = self._latencies.get(model_name, [100])
        avg_latency = np.mean(latencies) if latencies else 0
        error_rate = self._calculate_error_rate(model_name)

        # Calcular status geral
        overall_score, status = self._calculate_overall_health(
            metrics, drift_alerts, avg_latency, error_rate
        )

        # Gerar recomendações
        recommendations = self._generate_recommendations(
            metrics, drift_alerts, avg_latency, error_rate
        )

        return ModelHealth(
            model_name=model_name,
            model_version=model_version.version,
            status=status,
            overall_score=round(overall_score, 2),
            metrics=metrics,
            drift_alerts=drift_alerts,
            last_prediction_time=datetime.utcnow(),
            predictions_last_hour=predictions,
            avg_latency_ms=round(avg_latency, 2),
            error_rate=round(error_rate, 4),
            recommendations=recommendations,
        )

    async def get_dashboard(
        self,
        db: AsyncSession,
    ) -> MonitoringDashboard:
        """
        Obtém dashboard de monitoramento.

        Args:
            db: Sessão do banco

        Returns:
            MonitoringDashboard com visão geral
        """
        # Listar modelos em produção
        models = self.model_registry.list_models()
        production_models = [
            m for m in models if m.get("production_version")
        ]

        # Verificar saúde de cada modelo
        models_status = []
        healthy = 0
        warning = 0
        critical = 0

        for model in production_models:
            health = await self.check_model_health(db, model["name"])
            models_status.append({
                "name": model["name"],
                "version": health.model_version,
                "status": health.status.value,
                "score": health.overall_score,
                "predictions": health.predictions_last_hour,
                "latency": health.avg_latency_ms,
            })

            if health.status == HealthStatus.HEALTHY:
                healthy += 1
            elif health.status in [HealthStatus.WARNING, HealthStatus.DEGRADED]:
                warning += 1
            elif health.status == HealthStatus.CRITICAL:
                critical += 1

        # Alertas ativos
        active_alerts = [a for a in self._alerts if not a.acknowledged]

        return MonitoringDashboard(
            timestamp=datetime.utcnow(),
            models_monitored=len(production_models),
            healthy_models=healthy,
            warning_models=warning,
            critical_models=critical,
            active_alerts=len(active_alerts),
            models_status=models_status,
            recent_alerts=active_alerts[-10:],
            system_metrics={
                "total_predictions_24h": sum(self._prediction_counts.values()),
                "avg_latency_ms": np.mean([
                    np.mean(lats) for lats in self._latencies.values() if lats
                ]) if self._latencies else 0,
                "models_needing_retrain": sum(
                    1 for s in models_status if s["score"] < 70
                ),
            },
        )

    async def detect_data_drift(
        self,
        db: AsyncSession,
        model_name: str,
        feature_name: str,
        current_data: np.ndarray,
        reference_data: Optional[np.ndarray] = None,
    ) -> Optional[DriftAlert]:
        """
        Detecta drift em uma feature específica.

        Args:
            db: Sessão do banco
            model_name: Nome do modelo
            feature_name: Nome da feature
            current_data: Dados atuais
            reference_data: Dados de referência

        Returns:
            DriftAlert se drift detectado
        """
        # Usar dados históricos como referência se não fornecidos
        if reference_data is None:
            baseline_key = f"{model_name}_{feature_name}"
            if baseline_key in self._baseline_distributions:
                reference_stats = self._baseline_distributions[baseline_key]
                reference_data = np.random.normal(
                    reference_stats["mean"],
                    reference_stats["std"],
                    len(current_data)
                )
            else:
                # Armazenar como baseline
                self._baseline_distributions[baseline_key] = {
                    "mean": np.mean(current_data),
                    "std": np.std(current_data),
                    "min": np.min(current_data),
                    "max": np.max(current_data),
                }
                return None

        # Teste Kolmogorov-Smirnov
        ks_stat, p_value = stats.ks_2samp(reference_data, current_data)

        # Calcular drift score
        drift_score = ks_stat

        # Verificar threshold
        if drift_score > self.DEFAULT_THRESHOLDS["drift_score"]["warning"]:
            severity = (
                AlertSeverity.CRITICAL
                if drift_score > self.DEFAULT_THRESHOLDS["drift_score"]["critical"]
                else AlertSeverity.HIGH
            )

            alert = DriftAlert(
                id=uuid4(),
                model_name=model_name,
                drift_type=DriftType.FEATURE_DRIFT,
                severity=severity,
                feature_name=feature_name,
                drift_score=round(drift_score, 4),
                baseline_distribution={
                    "mean": float(np.mean(reference_data)),
                    "std": float(np.std(reference_data)),
                },
                current_distribution={
                    "mean": float(np.mean(current_data)),
                    "std": float(np.std(current_data)),
                },
                description=f"Drift detectado na feature {feature_name} (KS={ks_stat:.4f}, p={p_value:.4f})",
                recommended_action="Avaliar necessidade de retraining",
            )

            self._alerts.append(alert)
            logger.warning(f"Data drift detectado: {model_name}/{feature_name}")
            return alert

        return None

    async def detect_prediction_drift(
        self,
        db: AsyncSession,
        model_name: str,
        predictions: np.ndarray,
        reference_period_days: int = 7,
    ) -> Optional[DriftAlert]:
        """
        Detecta drift nas predições do modelo.

        Args:
            db: Sessão do banco
            model_name: Nome do modelo
            predictions: Predições recentes
            reference_period_days: Período de referência

        Returns:
            DriftAlert se drift detectado
        """
        baseline_key = f"{model_name}_predictions"

        if baseline_key not in self._baseline_distributions:
            self._baseline_distributions[baseline_key] = {
                "mean": float(np.mean(predictions)),
                "std": float(np.std(predictions)),
                "distribution": predictions[:1000].tolist() if len(predictions) > 1000 else predictions.tolist(),
            }
            return None

        baseline = self._baseline_distributions[baseline_key]
        baseline_data = np.array(baseline["distribution"])

        # Teste estatístico
        ks_stat, p_value = stats.ks_2samp(baseline_data, predictions)

        if ks_stat > self.DEFAULT_THRESHOLDS["drift_score"]["warning"]:
            alert = DriftAlert(
                id=uuid4(),
                model_name=model_name,
                drift_type=DriftType.PREDICTION_DRIFT,
                severity=AlertSeverity.HIGH,
                feature_name=None,
                drift_score=round(ks_stat, 4),
                baseline_distribution={
                    "mean": baseline["mean"],
                    "std": baseline["std"],
                },
                current_distribution={
                    "mean": float(np.mean(predictions)),
                    "std": float(np.std(predictions)),
                },
                description=f"Drift nas predições do modelo (KS={ks_stat:.4f})",
                recommended_action="Verificar dados de entrada e considerar retraining",
            )

            self._alerts.append(alert)
            return alert

        return None

    def log_prediction(
        self,
        model_name: str,
        latency_ms: float,
        success: bool = True,
    ) -> None:
        """
        Registra uma predição para monitoramento.

        Args:
            model_name: Nome do modelo
            latency_ms: Latência em ms
            success: Se a predição foi bem-sucedida
        """
        # Incrementar contador
        if model_name not in self._prediction_counts:
            self._prediction_counts[model_name] = 0
        self._prediction_counts[model_name] += 1

        # Registrar latência
        if model_name not in self._latencies:
            self._latencies[model_name] = []
        self._latencies[model_name].append(latency_ms)

        # Manter apenas últimas 1000 latências
        if len(self._latencies[model_name]) > 1000:
            self._latencies[model_name] = self._latencies[model_name][-1000:]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Reconhece um alerta.

        Args:
            alert_id: ID do alerta

        Returns:
            True se encontrado e atualizado
        """
        for alert in self._alerts:
            if str(alert.id) == alert_id:
                alert.acknowledged = True
                return True
        return False

    def get_alerts(
        self,
        model_name: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        acknowledged: Optional[bool] = None,
    ) -> list[DriftAlert]:
        """
        Obtém alertas filtrados.

        Args:
            model_name: Filtrar por modelo
            severity: Filtrar por severidade
            acknowledged: Filtrar por status

        Returns:
            Lista de alertas
        """
        alerts = self._alerts

        if model_name:
            alerts = [a for a in alerts if a.model_name == model_name]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]

        return sorted(alerts, key=lambda x: x.created_at, reverse=True)

    async def _collect_performance_metrics(
        self,
        db: AsyncSession,
        model_name: str,
        version: str,
    ) -> list[PerformanceMetric]:
        """Coleta métricas de performance."""
        metrics = []
        now = datetime.utcnow()

        # Obter métricas do modelo
        model_version = self.model_registry.get_model_version(model_name, version)
        if model_version and model_version.metrics:
            model_metrics = model_version.metrics.to_dict()

            for metric_name, value in model_metrics.items():
                if value is None:
                    continue

                thresholds = self.DEFAULT_THRESHOLDS.get(
                    metric_name,
                    {"warning": 0.8, "critical": 0.7}
                )

                # Determinar se é saudável
                is_healthy = value >= thresholds["warning"]

                # Determinar tendência (simulado)
                trend = "stable"
                if metric_name in self._metrics_history:
                    history = self._metrics_history[metric_name]
                    if len(history) >= 2:
                        recent_avg = np.mean([h.value for h in history[-5:]])
                        if value > recent_avg * 1.02:
                            trend = "improving"
                        elif value < recent_avg * 0.98:
                            trend = "degrading"

                metric = PerformanceMetric(
                    name=metric_name,
                    value=value,
                    baseline=thresholds["warning"],
                    threshold_warning=thresholds["warning"],
                    threshold_critical=thresholds["critical"],
                    timestamp=now,
                    is_healthy=is_healthy,
                    trend=trend,
                )
                metrics.append(metric)

                # Armazenar histórico
                if metric_name not in self._metrics_history:
                    self._metrics_history[metric_name] = []
                self._metrics_history[metric_name].append(metric)

        return metrics

    async def _check_drift(
        self,
        db: AsyncSession,
        model_name: str,
    ) -> list[DriftAlert]:
        """Verifica alertas de drift para o modelo."""
        return [
            a for a in self._alerts
            if a.model_name == model_name and not a.acknowledged
        ]

    def _calculate_error_rate(self, model_name: str) -> float:
        """Calcula taxa de erro do modelo."""
        # Simulação - em produção viria de logs
        return np.random.uniform(0.01, 0.05)

    def _calculate_overall_health(
        self,
        metrics: list[PerformanceMetric],
        drift_alerts: list[DriftAlert],
        avg_latency: float,
        error_rate: float,
    ) -> tuple[float, HealthStatus]:
        """Calcula saúde geral do modelo."""
        score = 100.0

        # Penalizar por métricas não saudáveis
        for metric in metrics:
            if not metric.is_healthy:
                score -= 10
            if metric.trend == "degrading":
                score -= 5

        # Penalizar por alertas de drift
        for alert in drift_alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                score -= 20
            elif alert.severity == AlertSeverity.HIGH:
                score -= 10
            elif alert.severity == AlertSeverity.MEDIUM:
                score -= 5

        # Penalizar por latência alta
        if avg_latency > self.DEFAULT_THRESHOLDS["latency_ms"]["critical"]:
            score -= 15
        elif avg_latency > self.DEFAULT_THRESHOLDS["latency_ms"]["warning"]:
            score -= 5

        # Penalizar por taxa de erro
        if error_rate > self.DEFAULT_THRESHOLDS["error_rate"]["critical"]:
            score -= 20
        elif error_rate > self.DEFAULT_THRESHOLDS["error_rate"]["warning"]:
            score -= 10

        score = max(0, score)

        # Determinar status
        if score >= 80:
            status = HealthStatus.HEALTHY
        elif score >= 60:
            status = HealthStatus.WARNING
        elif score >= 40:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL

        return score, status

    def _generate_recommendations(
        self,
        metrics: list[PerformanceMetric],
        drift_alerts: list[DriftAlert],
        avg_latency: float,
        error_rate: float,
    ) -> list[str]:
        """Gera recomendações baseadas no status."""
        recommendations = []

        # Recomendações de métricas
        degrading_metrics = [m for m in metrics if m.trend == "degrading"]
        if degrading_metrics:
            recommendations.append(
                f"Métricas em degradação: {', '.join(m.name for m in degrading_metrics)}. "
                "Considere retraining do modelo."
            )

        unhealthy_metrics = [m for m in metrics if not m.is_healthy]
        if unhealthy_metrics:
            recommendations.append(
                f"Métricas abaixo do threshold: {', '.join(m.name for m in unhealthy_metrics)}"
            )

        # Recomendações de drift
        if drift_alerts:
            drift_features = [
                a.feature_name for a in drift_alerts if a.feature_name
            ]
            if drift_features:
                recommendations.append(
                    f"Data drift detectado em: {', '.join(drift_features)}. "
                    "Revisar pipeline de dados."
                )
            else:
                recommendations.append(
                    "Drift nas predições detectado. Avaliar necessidade de retraining."
                )

        # Recomendações de latência
        if avg_latency > self.DEFAULT_THRESHOLDS["latency_ms"]["warning"]:
            recommendations.append(
                f"Latência média ({avg_latency:.0f}ms) acima do recomendado. "
                "Considere otimização do modelo ou infraestrutura."
            )

        # Recomendações de erro
        if error_rate > self.DEFAULT_THRESHOLDS["error_rate"]["warning"]:
            recommendations.append(
                f"Taxa de erro ({error_rate*100:.2f}%) elevada. "
                "Verificar logs e dados de entrada."
            )

        if not recommendations:
            recommendations.append("Modelo operando normalmente.")

        return recommendations

    def set_baseline(
        self,
        model_name: str,
        feature_name: str,
        data: np.ndarray,
    ) -> None:
        """
        Define baseline para detecção de drift.

        Args:
            model_name: Nome do modelo
            feature_name: Nome da feature
            data: Dados de baseline
        """
        key = f"{model_name}_{feature_name}"
        self._baseline_distributions[key] = {
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "percentiles": {
                "25": float(np.percentile(data, 25)),
                "50": float(np.percentile(data, 50)),
                "75": float(np.percentile(data, 75)),
            },
        }
        logger.info(f"Baseline definido: {key}")

    def get_performance_history(
        self,
        model_name: str,
        metric_name: str,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Obtém histórico de uma métrica.

        Args:
            model_name: Nome do modelo
            metric_name: Nome da métrica
            days: Dias de histórico

        Returns:
            Lista com histórico
        """
        history = self._metrics_history.get(metric_name, [])
        cutoff = datetime.utcnow() - timedelta(days=days)

        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "value": m.value,
                "is_healthy": m.is_healthy,
                "trend": m.trend,
            }
            for m in history
            if m.timestamp >= cutoff
        ]

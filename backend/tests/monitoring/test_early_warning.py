"""
Testes do Early Warning System.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from modules.monitoring.models.alert import Alert, AlertLevel, AlertStatus
from modules.monitoring.models.metric_threshold import MetricThreshold, ThresholdType


class TestAlertModel:
    """Testes do modelo Alert."""

    def test_alert_creation(self):
        """Testa criacao de alerta."""
        alert = Alert(
            id=uuid4(),
            metric_name="cpu_usage",
            source="system",
            level=AlertLevel.YELLOW,
            status=AlertStatus.ACTIVE,
            current_value=75.0,
            threshold_value=70.0,
            title="CPU Usage em nivel YELLOW",
            message="Teste",
        )

        assert alert.metric_name == "cpu_usage"
        assert alert.level == AlertLevel.YELLOW
        assert alert.status == AlertStatus.ACTIVE
        assert alert.current_value == 75.0

    def test_alert_is_critical(self):
        """Testa verificacao de criticidade."""
        alert_yellow = Alert(
            id=uuid4(),
            metric_name="test",
            level=AlertLevel.YELLOW,
            status=AlertStatus.ACTIVE,
            current_value=50,
            threshold_value=40,
            title="Test",
        )
        assert not alert_yellow.is_critical

        alert_orange = Alert(
            id=uuid4(),
            metric_name="test",
            level=AlertLevel.ORANGE,
            status=AlertStatus.ACTIVE,
            current_value=60,
            threshold_value=50,
            title="Test",
        )
        assert alert_orange.is_critical

        alert_red = Alert(
            id=uuid4(),
            metric_name="test",
            level=AlertLevel.RED,
            status=AlertStatus.ACTIVE,
            current_value=70,
            threshold_value=60,
            title="Test",
        )
        assert alert_red.is_critical

    def test_alert_acknowledge(self):
        """Testa reconhecimento de alerta."""
        alert = Alert(
            id=uuid4(),
            metric_name="test",
            level=AlertLevel.YELLOW,
            status=AlertStatus.ACTIVE,
            current_value=50,
            threshold_value=40,
            title="Test",
        )

        user_id = uuid4()
        alert.acknowledge(user_id)

        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == user_id
        assert alert.acknowledged_at is not None

    def test_alert_resolve(self):
        """Testa resolucao de alerta."""
        alert = Alert(
            id=uuid4(),
            metric_name="test",
            level=AlertLevel.YELLOW,
            status=AlertStatus.ACTIVE,
            current_value=50,
            threshold_value=40,
            title="Test",
        )

        user_id = uuid4()
        alert.resolve(user_id, "Problema corrigido")

        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_by == user_id
        assert alert.resolved_at is not None
        assert alert.resolution_notes == "Problema corrigido"


class TestMetricThreshold:
    """Testes do modelo MetricThreshold."""

    def test_threshold_creation(self):
        """Testa criacao de threshold."""
        threshold = MetricThreshold(
            id=uuid4(),
            metric_name="cpu_usage",
            display_name="CPU Usage",
            category="performance",
            threshold_type=ThresholdType.UPPER,
            yellow_threshold=70,
            orange_threshold=85,
            red_threshold=95,
            unit="%",
        )

        assert threshold.metric_name == "cpu_usage"
        assert threshold.yellow_threshold == 70
        assert threshold.red_threshold == 95

    def test_get_level_for_value_upper(self):
        """Testa determinacao de nivel para UPPER type."""
        threshold = MetricThreshold(
            id=uuid4(),
            metric_name="cpu_usage",
            display_name="CPU Usage",
            threshold_type=ThresholdType.UPPER,
            yellow_threshold=70,
            orange_threshold=85,
            red_threshold=95,
        )

        # Green
        assert threshold.get_level_for_value(50) == "green"
        assert threshold.get_level_for_value(69.9) == "green"

        # Yellow
        assert threshold.get_level_for_value(70) == "yellow"
        assert threshold.get_level_for_value(84.9) == "yellow"

        # Orange
        assert threshold.get_level_for_value(85) == "orange"
        assert threshold.get_level_for_value(94.9) == "orange"

        # Red
        assert threshold.get_level_for_value(95) == "red"
        assert threshold.get_level_for_value(100) == "red"

    def test_get_level_for_value_lower(self):
        """Testa determinacao de nivel para LOWER type."""
        threshold = MetricThreshold(
            id=uuid4(),
            metric_name="cache_hit_rate",
            display_name="Cache Hit Rate",
            threshold_type=ThresholdType.LOWER,
            yellow_threshold=90,
            orange_threshold=80,
            red_threshold=70,
        )

        # Green
        assert threshold.get_level_for_value(95) == "green"
        assert threshold.get_level_for_value(91) == "green"

        # Yellow
        assert threshold.get_level_for_value(90) == "yellow"
        assert threshold.get_level_for_value(81) == "yellow"

        # Orange
        assert threshold.get_level_for_value(80) == "orange"
        assert threshold.get_level_for_value(71) == "orange"

        # Red
        assert threshold.get_level_for_value(70) == "red"
        assert threshold.get_level_for_value(50) == "red"

    def test_should_alert_disabled(self):
        """Testa que threshold desabilitado nao gera alerta."""
        threshold = MetricThreshold(
            id=uuid4(),
            metric_name="test",
            display_name="Test",
            threshold_type=ThresholdType.UPPER,
            yellow_threshold=50,
            orange_threshold=75,
            red_threshold=90,
            enabled=False,
        )

        assert not threshold.should_alert(100)

    def test_should_alert_in_cooldown(self):
        """Testa que cooldown impede novo alerta."""
        threshold = MetricThreshold(
            id=uuid4(),
            metric_name="test",
            display_name="Test",
            threshold_type=ThresholdType.UPPER,
            yellow_threshold=50,
            orange_threshold=75,
            red_threshold=90,
            cooldown_seconds=300,
        )

        # Alerta ha menos de 5 minutos
        last_alert = datetime.utcnow() - timedelta(minutes=2)
        assert not threshold.should_alert(60, last_alert)

        # Alerta ha mais de 5 minutos
        last_alert = datetime.utcnow() - timedelta(minutes=10)
        assert threshold.should_alert(60, last_alert)


class TestAlertLevels:
    """Testes dos niveis de alerta."""

    def test_alert_level_values(self):
        """Testa valores dos niveis de alerta."""
        assert AlertLevel.GREEN.value == "green"
        assert AlertLevel.YELLOW.value == "yellow"
        assert AlertLevel.ORANGE.value == "orange"
        assert AlertLevel.RED.value == "red"

    def test_alert_status_values(self):
        """Testa valores dos status de alerta."""
        assert AlertStatus.ACTIVE.value == "active"
        assert AlertStatus.ACKNOWLEDGED.value == "acknowledged"
        assert AlertStatus.RESOLVED.value == "resolved"
        assert AlertStatus.ESCALATED.value == "escalated"
        assert AlertStatus.SUPPRESSED.value == "suppressed"


class TestMetricCollector:
    """Testes do MetricCollectorService."""

    def test_collector_singleton(self):
        """Testa que coletor e singleton."""
        from modules.monitoring.services.metric_collector import get_metric_collector

        collector1 = get_metric_collector()
        collector2 = get_metric_collector()

        assert collector1 is collector2

    def test_collect_system_metrics(self):
        """Testa coleta de metricas do sistema."""
        from modules.monitoring.services.metric_collector import MetricCollectorService

        collector = MetricCollectorService()
        metrics = collector._collect_system_metrics()

        assert "cpu_usage" in metrics
        assert "memory_usage" in metrics
        assert "disk_usage" in metrics

        assert 0 <= metrics["cpu_usage"] <= 100
        assert 0 <= metrics["memory_usage"] <= 100
        assert 0 <= metrics["disk_usage"] <= 100

    def test_collect_process_metrics(self):
        """Testa coleta de metricas do processo."""
        from modules.monitoring.services.metric_collector import MetricCollectorService

        collector = MetricCollectorService()
        metrics = collector._collect_process_metrics()

        assert "process_cpu_percent" in metrics
        assert "process_memory_rss_mb" in metrics
        assert "process_threads" in metrics
        assert "process_uptime_seconds" in metrics

        assert metrics["process_uptime_seconds"] > 0
        assert metrics["process_threads"] >= 1

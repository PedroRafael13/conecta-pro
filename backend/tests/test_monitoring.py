"""Testes para o sistema de monitoramento."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.monitoring.metrics import (
    MetricsCollector,
    MetricsMiddleware,
    get_metrics,
    increment_counter,
    observe_histogram,
    set_gauge,
    set_info,
)


class TestMetricsCollector:
    """Testes para MetricsCollector."""

    def test_inc_counter(self):
        """Testa incremento de contador."""
        collector = MetricsCollector()

        collector.inc_counter("requests_total", {"method": "GET"})
        collector.inc_counter("requests_total", {"method": "GET"})
        collector.inc_counter("requests_total", {"method": "POST"})

        # Formato: {method="GET"} (não JSON)
        assert collector._counters["requests_total"]['{method="GET"}'] == 2
        assert collector._counters["requests_total"]['{method="POST"}'] == 1

    def test_inc_counter_no_labels(self):
        """Testa contador sem labels."""
        collector = MetricsCollector()

        collector.inc_counter("simple_counter")
        collector.inc_counter("simple_counter", value=5)

        assert collector._counters["simple_counter"][""] == 6

    def test_observe_histogram(self):
        """Testa observação em histograma."""
        collector = MetricsCollector()

        collector.observe_histogram("duration", 0.1)
        collector.observe_histogram("duration", 0.2)
        collector.observe_histogram("duration", 0.3)

        assert len(collector._histograms["duration"]) == 3
        assert 0.1 in collector._histograms["duration"]

    def test_observe_histogram_with_labels(self):
        """Testa histograma com labels."""
        collector = MetricsCollector()

        collector.observe_histogram("duration", 0.1, {"path": "/api"})
        collector.observe_histogram("duration", 0.2, {"path": "/api"})

        # Formato: duration{path="/api"}
        key = 'duration{path="/api"}'
        assert len(collector._histograms[key]) == 2

    def test_histogram_max_observations(self):
        """Testa limite de observações."""
        collector = MetricsCollector()

        for i in range(1500):
            collector.observe_histogram("many", float(i))

        # Deve manter apenas 1000
        assert len(collector._histograms["many"]) == 1000

    def test_set_gauge(self):
        """Testa definição de gauge."""
        collector = MetricsCollector()

        collector.set_gauge("memory_usage", 75.5)
        collector.set_gauge("memory_usage", 80.0)

        assert collector._gauges["memory_usage"][""] == 80.0

    def test_set_gauge_with_labels(self):
        """Testa gauge com labels."""
        collector = MetricsCollector()

        collector.set_gauge("cpu", 50.0, {"core": "0"})
        collector.set_gauge("cpu", 60.0, {"core": "1"})

        # Formato: {core="0"}
        assert collector._gauges["cpu"]['{core="0"}'] == 50.0
        assert collector._gauges["cpu"]['{core="1"}'] == 60.0

    def test_set_info(self):
        """Testa definição de info."""
        collector = MetricsCollector()

        collector.set_info("app_info", {"version": "1.0", "env": "prod"})

        assert collector._info["app_info"]["version"] == "1.0"
        assert collector._info["app_info"]["env"] == "prod"

    def test_labels_to_key(self):
        """Testa conversão de labels para chave."""
        collector = MetricsCollector()

        key = collector._labels_to_key({"b": "2", "a": "1"})

        # Deve ser ordenado e no formato Prometheus
        assert key == '{a="1",b="2"}'

    def test_labels_to_key_empty(self):
        """Testa conversão de labels vazios."""
        collector = MetricsCollector()

        key = collector._labels_to_key({})

        assert key == ""

    def test_calculate_histogram_stats_empty(self):
        """Testa estatísticas de histograma vazio."""
        collector = MetricsCollector()

        stats = collector._calculate_histogram_stats([])

        assert stats["count"] == 0
        assert stats["sum"] == 0

    def test_calculate_histogram_stats(self):
        """Testa estatísticas de histograma."""
        collector = MetricsCollector()

        stats = collector._calculate_histogram_stats([0.1, 0.2, 0.3, 0.4, 0.5])

        assert stats["count"] == 5
        assert stats["sum"] == 1.5
        assert stats["avg"] == 0.3
        assert stats["p50"] == 0.3

    def test_format_prometheus_counters(self):
        """Testa formatação Prometheus de contadores."""
        collector = MetricsCollector()

        collector.inc_counter("requests", {"method": "GET"})

        output = collector.format_prometheus()

        assert "# TYPE requests counter" in output
        assert 'requests{method="GET"} 1' in output

    def test_format_prometheus_gauges(self):
        """Testa formatação Prometheus de gauges."""
        collector = MetricsCollector()

        collector.set_gauge("memory", 75.5)

        output = collector.format_prometheus()

        assert "# TYPE memory gauge" in output
        assert "memory 75.5" in output

    def test_format_prometheus_info(self):
        """Testa formatação Prometheus de info."""
        collector = MetricsCollector()

        collector.set_info("app", {"version": "1.0"})

        output = collector.format_prometheus()

        assert 'app{version="1.0"} 1' in output


class TestGlobalFunctions:
    """Testes para funções globais."""

    def test_increment_counter(self):
        """Testa função increment_counter."""
        # Reset collector
        import core.monitoring.metrics as m

        m._collector = MetricsCollector()

        increment_counter("test_counter")
        increment_counter("test_counter")

        output = get_metrics()
        assert "test_counter" in output

    def test_observe_histogram(self):
        """Testa função observe_histogram."""
        import core.monitoring.metrics as m

        m._collector = MetricsCollector()

        observe_histogram("test_duration", 0.5)

        output = get_metrics()
        assert "test_duration" in output

    def test_set_gauge(self):
        """Testa função set_gauge."""
        import core.monitoring.metrics as m

        m._collector = MetricsCollector()

        set_gauge("test_gauge", 42.0)

        output = get_metrics()
        assert "test_gauge" in output
        assert "42" in output

    def test_set_info(self):
        """Testa função set_info."""
        import core.monitoring.metrics as m

        m._collector = MetricsCollector()

        set_info("test_info", {"key": "value"})

        output = get_metrics()
        assert "test_info" in output


class TestMetricsMiddleware:
    """Testes para MetricsMiddleware."""

    @pytest.mark.asyncio
    async def test_middleware_skips_metrics_path(self):
        """Testa que middleware pula /metrics."""
        mock_app = MagicMock()
        mock_request = MagicMock()
        mock_request.url.path = "/metrics"

        call_next = AsyncMock(return_value=MagicMock(status_code=200))

        with patch("core.monitoring.metrics.set_info"):
            with patch("core.config.settings") as mock_settings:
                mock_settings.app_version = "1.0"
                mock_settings.environment = "test"

                middleware = MetricsMiddleware(mock_app)
                response = await middleware.dispatch(mock_request, call_next)

                call_next.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_records_request(self):
        """Testa que middleware registra request."""
        mock_app = MagicMock()
        mock_app.routes = []

        mock_request = MagicMock()
        mock_request.url.path = "/api/users"
        mock_request.method = "GET"
        mock_request.scope = {}

        mock_response = MagicMock()
        mock_response.status_code = 200

        call_next = AsyncMock(return_value=mock_response)

        with patch("core.monitoring.metrics.set_info"):
            with patch("core.config.settings") as mock_settings:
                mock_settings.app_version = "1.0"
                mock_settings.environment = "test"

                import core.monitoring.metrics as m

                m._collector = MetricsCollector()

                middleware = MetricsMiddleware(mock_app)
                response = await middleware.dispatch(mock_request, call_next)

                assert response == mock_response

                # Verifica métricas
                output = m._collector.format_prometheus()
                assert "http_requests_total" in output

    @pytest.mark.asyncio
    async def test_middleware_records_error(self):
        """Testa que middleware registra erro."""
        mock_app = MagicMock()
        mock_app.routes = []

        mock_request = MagicMock()
        mock_request.url.path = "/api/error"
        mock_request.method = "POST"
        mock_request.scope = {}

        mock_response = MagicMock()
        mock_response.status_code = 500

        call_next = AsyncMock(return_value=mock_response)

        with patch("core.monitoring.metrics.set_info"):
            with patch("core.config.settings") as mock_settings:
                mock_settings.app_version = "1.0"
                mock_settings.environment = "test"

                import core.monitoring.metrics as m

                m._collector = MetricsCollector()

                middleware = MetricsMiddleware(mock_app)
                response = await middleware.dispatch(mock_request, call_next)

                output = m._collector.format_prometheus()
                assert 'status="500"' in output

    def test_get_route_path(self):
        """Testa extração de path da rota."""
        mock_app = MagicMock()
        mock_app.routes = []

        mock_request = MagicMock()
        mock_request.url.path = "/api/users/123"
        mock_request.scope = {}

        with patch("core.monitoring.metrics.set_info"):
            with patch("core.config.settings") as mock_settings:
                mock_settings.app_version = "1.0"
                mock_settings.environment = "test"

                middleware = MetricsMiddleware(mock_app)
                path = middleware._get_route_path(mock_request)

                # Sem rotas definidas, retorna url.path
                assert path == "/api/users/123"

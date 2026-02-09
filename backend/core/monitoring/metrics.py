"""
Sistema de metricas Prometheus para ERP Conecta Mais.
Expoe metricas em formato Prometheus no endpoint /metrics.
"""

import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

from core.logging import logger


class MetricsCollector:
    """Coletor de metricas em memoria."""

    def __init__(self):
        # Contadores
        self._counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Histogramas (latencia)
        self._histograms: dict[str, list[float]] = defaultdict(list)

        # Gauges (valores atuais)
        self._gauges: dict[str, dict[str, float]] = defaultdict(dict)

        # Info
        self._info: dict[str, dict[str, str]] = {}

    def inc_counter(self, name: str, labels: dict[str, str] | None = None, value: int = 1):
        """Incrementa contador."""
        label_key = self._labels_to_key(labels or {})
        self._counters[name][label_key] += value

    def observe_histogram(self, name: str, value: float, labels: dict[str, str] | None = None):
        """Registra valor em histograma."""
        label_key = self._labels_to_key(labels or {})
        key = f"{name}{label_key}"
        self._histograms[key].append(value)

        # Manter apenas ultimas 1000 observacoes
        if len(self._histograms[key]) > 1000:
            self._histograms[key] = self._histograms[key][-1000:]

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None):
        """Define valor de gauge."""
        label_key = self._labels_to_key(labels or {})
        self._gauges[name][label_key] = value

    def set_info(self, name: str, labels: dict[str, str]):
        """Define info metric."""
        self._info[name] = labels

    def _labels_to_key(self, labels: dict[str, str]) -> str:
        """Converte labels para chave unica."""
        if not labels:
            return ""
        sorted_items = sorted(labels.items())
        return "{" + ",".join(f'{k}="{v}"' for k, v in sorted_items) + "}"

    def _calculate_histogram_stats(self, values: list[float]) -> dict[str, float]:
        """Calcula estatisticas do histograma."""
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "p50": 0, "p90": 0, "p99": 0}

        sorted_vals = sorted(values)
        count = len(sorted_vals)

        def percentile(p: float) -> float:
            idx = int(count * p)
            return sorted_vals[min(idx, count - 1)]

        return {
            "count": count,
            "sum": sum(sorted_vals),
            "avg": sum(sorted_vals) / count,
            "p50": percentile(0.5),
            "p90": percentile(0.9),
            "p99": percentile(0.99),
        }

    def _format_info_metrics(self) -> list:
        """Formata metricas de info."""
        lines = []
        for name, labels in self._info.items():
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            lines.extend(
                [
                    f"# HELP {name} Application information",
                    f"# TYPE {name} gauge",
                    f"{name}{{{label_str}}} 1",
                    "",
                ]
            )
        return lines

    def _format_counter_metrics(self) -> list:
        """Formata metricas de counter."""
        lines = []
        for name, values in self._counters.items():
            lines.extend([f"# HELP {name} Counter metric", f"# TYPE {name} counter"])
            lines.extend(f"{name}{label} {value}" for label, value in values.items())
            lines.append("")
        return lines

    def _format_gauge_metrics(self) -> list:
        """Formata metricas de gauge."""
        lines = []
        for name, values in self._gauges.items():
            lines.extend([f"# HELP {name} Gauge metric", f"# TYPE {name} gauge"])
            lines.extend(f"{name}{label} {value}" for label, value in values.items())
            lines.append("")
        return lines

    def _format_bucket_label(self, label_part: str, bucket: float | str) -> str:
        """Formata label de bucket."""
        if label_part:
            return label_part[:-1] + f',le="{bucket}"' + "}"
        return f'{{le="{bucket}"}}'

    def _format_histogram_metrics(self) -> list:
        """Formata metricas de histogram."""
        lines = []
        buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        histogram_names = {key.split("{")[0] for key in self._histograms.keys()}

        for name in histogram_names:
            lines.extend([f"# HELP {name} Histogram metric", f"# TYPE {name} histogram"])

            for key, values in self._histograms.items():
                if not key.startswith(name):
                    continue

                label_part = key[len(name) :]
                stats = self._calculate_histogram_stats(values)

                for bucket in buckets:
                    count = sum(1 for v in values if v <= bucket)
                    bucket_label = self._format_bucket_label(label_part, bucket)
                    lines.append(f"{name}_bucket{bucket_label} {count}")

                inf_label = self._format_bucket_label(label_part, "+Inf")
                lines.extend(
                    [
                        f"{name}_bucket{inf_label} {len(values)}",
                        f"{name}_sum{label_part} {stats['sum']:.6f}",
                        f"{name}_count{label_part} {stats['count']}",
                    ]
                )
            lines.append("")
        return lines

    def format_prometheus(self) -> str:
        """Formata metricas no formato Prometheus."""
        lines = []
        lines.extend(self._format_info_metrics())
        lines.extend(self._format_counter_metrics())
        lines.extend(self._format_gauge_metrics())
        lines.extend(self._format_histogram_metrics())
        return "\n".join(lines)


# Instancia global
_collector = MetricsCollector()


def get_metrics() -> str:
    """Retorna metricas no formato Prometheus."""
    return _collector.format_prometheus()


def increment_counter(name: str, labels: dict[str, str] | None = None, value: int = 1):
    """Incrementa contador."""
    _collector.inc_counter(name, labels, value)


def observe_histogram(name: str, value: float, labels: dict[str, str] | None = None):
    """Registra valor em histograma."""
    _collector.observe_histogram(name, value, labels)


def set_gauge(name: str, value: float, labels: dict[str, str] | None = None):
    """Define valor de gauge."""
    _collector.set_gauge(name, value, labels)


def set_info(name: str, labels: dict[str, str]):
    """Define info metric."""
    _collector.set_info(name, labels)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coletar metricas HTTP."""

    def __init__(self, app, app_name: str = "erp_conecta_mais"):
        super().__init__(app)
        self.app_name = app_name

        # Registrar info da aplicacao
        from core.config import settings

        set_info(
            "app_info",
            {
                "app": app_name,
                "version": settings.app_version,
                "environment": settings.environment,
            },
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processa request e coleta metricas."""
        # Pular endpoint de metricas
        if request.url.path == "/metrics":
            return await call_next(request)

        # Encontrar rota correspondente
        route_path = self._get_route_path(request)

        # Medir tempo
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time

            # Labels comuns
            labels = {
                "method": request.method,
                "path": route_path,
                "status": str(status_code),
            }

            # Incrementar contador de requests
            increment_counter("http_requests_total", labels)

            # Registrar duracao
            observe_histogram(
                "http_request_duration_seconds",
                duration,
                {"method": request.method, "path": route_path},
            )

            # Log lento
            if duration > 1.0:
                logger.warning(f"Request lenta: {request.method} {route_path} - {duration:.2f}s")

        return response

    def _get_route_path(self, request: Request) -> str:
        """Extrai path da rota (com parametros genericos)."""
        # Tentar match com rotas definidas
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path

        return request.url.path

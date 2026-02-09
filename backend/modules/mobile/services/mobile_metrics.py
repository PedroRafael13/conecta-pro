"""Serviço de métricas mobile."""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RequestMetric:
    """Métrica de requisição."""

    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    response_size_bytes: int
    compressed: bool
    device_type: str
    platform: str
    connection_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SyncMetric:
    """Métrica de sincronização."""

    user_id: int
    device_id: str
    operations_sent: int
    operations_received: int
    conflicts: int
    duration_ms: float
    data_size_bytes: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PushMetric:
    """Métrica de notificação push."""

    notification_id: str
    user_id: int
    platform: str
    sent_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    delivery_time_ms: float | None = None


class MobileMetrics:
    """
    Serviço de métricas para API mobile.

    Coleta:
    - Métricas de requisições (tempo, tamanho, compressão)
    - Métricas de sync (operações, conflitos)
    - Métricas de push (entrega, leitura)
    - Métricas de performance por dispositivo/conexão
    """

    def __init__(
        self,
        flush_interval_seconds: int = 60,
        max_buffer_size: int = 1000,
    ) -> None:
        """
        Inicializa o serviço de métricas.

        Args:
            flush_interval_seconds: Intervalo para persistir métricas
            max_buffer_size: Tamanho máximo do buffer antes de flush
        """
        self.flush_interval = flush_interval_seconds
        self.max_buffer = max_buffer_size

        # Buffers de métricas
        self._request_metrics: list[RequestMetric] = []
        self._sync_metrics: list[SyncMetric] = []
        self._push_metrics: list[PushMetric] = []

        # Agregações em memória
        self._endpoint_stats: dict[str, dict] = defaultdict(
            lambda: {
                "count": 0,
                "total_time_ms": 0,
                "total_size_bytes": 0,
                "errors": 0,
                "compressed_count": 0,
            }
        )

        self._device_stats: dict[str, dict] = defaultdict(
            lambda: {
                "requests": 0,
                "syncs": 0,
                "push_sent": 0,
                "push_delivered": 0,
            }
        )

        self._connection_stats: dict[str, dict] = defaultdict(
            lambda: {
                "requests": 0,
                "avg_response_time_ms": 0,
                "total_time_ms": 0,
            }
        )

        self._last_flush = time.time()

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        response_size_bytes: int,
        compressed: bool = False,
        device_type: str = "unknown",
        platform: str = "unknown",
        connection_type: str = "unknown",
    ) -> None:
        """
        Registra métrica de requisição.

        Args:
            endpoint: Endpoint da API
            method: Método HTTP
            status_code: Código de status
            response_time_ms: Tempo de resposta em ms
            response_size_bytes: Tamanho da resposta
            compressed: Se resposta foi comprimida
            device_type: Tipo de dispositivo
            platform: Plataforma (android, ios)
            connection_type: Tipo de conexão
        """
        metric = RequestMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            response_size_bytes=response_size_bytes,
            compressed=compressed,
            device_type=device_type,
            platform=platform,
            connection_type=connection_type,
        )

        self._request_metrics.append(metric)

        # Atualizar agregações
        key = f"{method}:{endpoint}"
        stats = self._endpoint_stats[key]
        stats["count"] += 1
        stats["total_time_ms"] += response_time_ms
        stats["total_size_bytes"] += response_size_bytes
        if status_code >= 400:
            stats["errors"] += 1
        if compressed:
            stats["compressed_count"] += 1

        # Stats por conexão
        conn_stats = self._connection_stats[connection_type]
        conn_stats["requests"] += 1
        conn_stats["total_time_ms"] += response_time_ms
        conn_stats["avg_response_time_ms"] = conn_stats["total_time_ms"] / conn_stats["requests"]

        # Stats por dispositivo
        self._device_stats[device_type]["requests"] += 1

        # Flush se necessário
        self._check_flush()

    def record_sync(
        self,
        user_id: int,
        device_id: str,
        operations_sent: int,
        operations_received: int,
        conflicts: int,
        duration_ms: float,
        data_size_bytes: int,
    ) -> None:
        """
        Registra métrica de sincronização.

        Args:
            user_id: ID do usuário
            device_id: ID do dispositivo
            operations_sent: Operações enviadas pelo cliente
            operations_received: Mudanças do servidor
            conflicts: Número de conflitos
            duration_ms: Duração da sync
            data_size_bytes: Tamanho dos dados
        """
        metric = SyncMetric(
            user_id=user_id,
            device_id=device_id,
            operations_sent=operations_sent,
            operations_received=operations_received,
            conflicts=conflicts,
            duration_ms=duration_ms,
            data_size_bytes=data_size_bytes,
        )

        self._sync_metrics.append(metric)

        # Atualizar agregações
        device_key = f"{device_id[:8]}..."
        self._device_stats[device_key]["syncs"] += 1

        self._check_flush()

    def record_push_sent(
        self,
        notification_id: str,
        user_id: int,
        platform: str,
    ) -> None:
        """Registra envio de notificação push."""
        metric = PushMetric(
            notification_id=notification_id,
            user_id=user_id,
            platform=platform,
            sent_at=datetime.utcnow(),
        )

        self._push_metrics.append(metric)
        self._device_stats[platform]["push_sent"] += 1

    def record_push_delivered(
        self,
        notification_id: str,
        delivery_time_ms: float,
    ) -> None:
        """Registra entrega de notificação push."""
        # Encontrar métrica existente
        for metric in self._push_metrics:
            if metric.notification_id == notification_id:
                metric.delivered_at = datetime.utcnow()
                metric.delivery_time_ms = delivery_time_ms
                self._device_stats[metric.platform]["push_delivered"] += 1
                break

    def record_push_read(
        self,
        notification_id: str,
    ) -> None:
        """Registra leitura de notificação push."""
        for metric in self._push_metrics:
            if metric.notification_id == notification_id:
                metric.read_at = datetime.utcnow()
                break

    def _check_flush(self) -> None:
        """Verifica se deve fazer flush das métricas."""
        should_flush = (
            time.time() - self._last_flush > self.flush_interval or len(self._request_metrics) >= self.max_buffer
        )

        if should_flush:
            self._flush_metrics()

    def _flush_metrics(self) -> None:
        """Persiste métricas em storage."""
        # TODO: Implementar persistência real (Prometheus, InfluxDB, etc)

        if self._request_metrics:
            logger.info(f"Flushing {len(self._request_metrics)} request metrics")
            self._request_metrics.clear()

        if self._sync_metrics:
            logger.info(f"Flushing {len(self._sync_metrics)} sync metrics")
            self._sync_metrics.clear()

        if self._push_metrics:
            # Manter apenas métricas recentes (últimas 24h)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self._push_metrics = [m for m in self._push_metrics if m.sent_at > cutoff]

        self._last_flush = time.time()

    def get_endpoint_stats(self) -> dict[str, dict]:
        """Obtém estatísticas por endpoint."""
        result = {}
        for key, stats in self._endpoint_stats.items():
            count = stats["count"]
            result[key] = {
                "count": count,
                "avg_response_time_ms": stats["total_time_ms"] / count if count > 0 else 0,
                "avg_response_size_bytes": stats["total_size_bytes"] / count if count > 0 else 0,
                "error_rate": stats["errors"] / count * 100 if count > 0 else 0,
                "compression_rate": stats["compressed_count"] / count * 100 if count > 0 else 0,
            }
        return result

    def get_connection_stats(self) -> dict[str, dict]:
        """Obtém estatísticas por tipo de conexão."""
        return dict(self._connection_stats)

    def get_device_stats(self) -> dict[str, dict]:
        """Obtém estatísticas por tipo de dispositivo."""
        return dict(self._device_stats)

    def get_push_stats(self) -> dict[str, Any]:
        """Obtém estatísticas de notificações push."""
        total_sent = len(self._push_metrics)
        total_delivered = sum(1 for m in self._push_metrics if m.delivered_at)
        total_read = sum(1 for m in self._push_metrics if m.read_at)

        delivery_times = [m.delivery_time_ms for m in self._push_metrics if m.delivery_time_ms is not None]

        return {
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_read": total_read,
            "delivery_rate": total_delivered / total_sent * 100 if total_sent > 0 else 0,
            "read_rate": total_read / total_delivered * 100 if total_delivered > 0 else 0,
            "avg_delivery_time_ms": sum(delivery_times) / len(delivery_times) if delivery_times else 0,
        }

    def get_summary(self) -> dict[str, Any]:
        """Obtém resumo geral de métricas."""
        endpoint_stats = self.get_endpoint_stats()
        total_requests = sum(s["count"] for s in endpoint_stats.values())

        all_times = []
        for _key, stats in self._endpoint_stats.items():
            if stats["count"] > 0:
                all_times.append(stats["total_time_ms"] / stats["count"])

        return {
            "total_requests": total_requests,
            "avg_response_time_ms": sum(all_times) / len(all_times) if all_times else 0,
            "endpoints_count": len(endpoint_stats),
            "device_types": list(self._device_stats.keys()),
            "connection_types": list(self._connection_stats.keys()),
            "push_stats": self.get_push_stats(),
        }

    def reset(self) -> None:
        """Reseta todas as métricas (para testes)."""
        self._request_metrics.clear()
        self._sync_metrics.clear()
        self._push_metrics.clear()
        self._endpoint_stats.clear()
        self._device_stats.clear()
        self._connection_stats.clear()
        self._last_flush = time.time()


# Instância global para métricas
mobile_metrics = MobileMetrics()


def get_metrics() -> MobileMetrics:
    """Retorna instância global de métricas."""
    return mobile_metrics

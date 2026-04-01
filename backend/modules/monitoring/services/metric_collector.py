"""
Metric Collector Service.

Coleta metricas do sistema de forma periodica.
"""

import asyncio
import os
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

import psutil

from core.logging import logger
from core.monitoring import observe_histogram, set_gauge


class MetricCollectorService:
    """
    Servico de coleta de metricas.

    Coleta metricas de:
    - Sistema (CPU, memoria, disco)
    - Aplicacao (requests, latencia)
    - Banco de dados (conexoes, queries)
    - Cache (Redis hit rate, memoria)
    """

    def __init__(self):
        self._running = False
        self._collectors: list[Callable] = []
        self._metrics: dict[str, Any] = {}
        self._last_collection: datetime | None = None
        self._collection_interval = 15  # segundos

        # Registrar coletores padrao
        self._register_default_collectors()

    def _register_default_collectors(self) -> None:
        """Registra coletores padrao."""
        self._collectors.extend(
            [
                self._collect_system_metrics,
                self._collect_process_metrics,
            ]
        )

    def register_collector(self, collector: Callable) -> None:
        """Registra um novo coletor de metricas."""
        self._collectors.append(collector)
        logger.debug(f"Coletor registrado: {collector.__name__}")

    async def collect_all(self) -> dict[str, Any]:
        """
        Executa todos os coletores e retorna metricas.

        Returns:
            Dicionario com todas as metricas coletadas
        """
        metrics = {}
        collection_start = time.time()

        for collector in self._collectors:
            try:
                if asyncio.iscoroutinefunction(collector):
                    result = await collector()
                else:
                    result = collector()

                if result:
                    metrics.update(result)
            except Exception as e:
                logger.error(f"Erro no coletor {collector.__name__}: {e}")

        collection_time = time.time() - collection_start
        metrics["collection_time_ms"] = collection_time * 1000

        self._metrics = metrics
        self._last_collection = datetime.utcnow()

        # Registrar tempo de coleta
        observe_histogram("metric_collection_duration_seconds", collection_time)

        return metrics

    def _collect_system_metrics(self) -> dict[str, float]:
        """Coleta metricas do sistema operacional."""
        metrics = {}

        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics["cpu_usage"] = cpu_percent
            set_gauge("system_cpu_usage_percent", cpu_percent)

            # Memoria
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = memory.percent
            metrics["memory_available_mb"] = memory.available / (1024 * 1024)
            metrics["memory_total_mb"] = memory.total / (1024 * 1024)
            set_gauge("system_memory_usage_percent", memory.percent)
            set_gauge("system_memory_available_bytes", memory.available)

            # Disco
            disk = psutil.disk_usage("/")
            metrics["disk_usage"] = disk.percent
            metrics["disk_free_gb"] = disk.free / (1024 * 1024 * 1024)
            set_gauge("system_disk_usage_percent", disk.percent)

            # Load average (Unix only)
            try:
                load1, load5, load15 = os.getloadavg()
                metrics["load_avg_1m"] = load1
                metrics["load_avg_5m"] = load5
                metrics["load_avg_15m"] = load15
                set_gauge("system_load_1m", load1)
            except (OSError, AttributeError):
                pass

            # Network I/O
            try:
                net_io = psutil.net_io_counters()
                metrics["network_bytes_sent"] = net_io.bytes_sent
                metrics["network_bytes_recv"] = net_io.bytes_recv
            except Exception as e:
                logger.debug(f"Erro ao coletar métricas de rede: {e}")

        except Exception as e:
            logger.error(f"Erro coletando metricas do sistema: {e}")

        return metrics

    def _collect_process_metrics(self) -> dict[str, float]:
        """Coleta metricas do processo atual."""
        metrics = {}

        try:
            process = psutil.Process()

            # CPU do processo
            cpu_percent = process.cpu_percent(interval=0.1)
            metrics["process_cpu_percent"] = cpu_percent
            set_gauge("process_cpu_percent", cpu_percent)

            # Memoria do processo
            memory_info = process.memory_info()
            metrics["process_memory_rss_mb"] = memory_info.rss / (1024 * 1024)
            metrics["process_memory_vms_mb"] = memory_info.vms / (1024 * 1024)
            set_gauge("process_memory_rss_bytes", memory_info.rss)

            # Threads
            metrics["process_threads"] = process.num_threads()
            set_gauge("process_num_threads", process.num_threads())

            # File descriptors (Unix only)
            try:
                metrics["process_open_fds"] = process.num_fds()
                set_gauge("process_open_fds", process.num_fds())
            except AttributeError:
                pass

            # Uptime
            create_time = process.create_time()
            uptime = time.time() - create_time
            metrics["process_uptime_seconds"] = uptime
            set_gauge("process_uptime_seconds", uptime)

        except Exception as e:
            logger.error(f"Erro coletando metricas do processo: {e}")

        return metrics

    async def start_background_collection(self) -> None:
        """Inicia coleta em background."""
        if self._running:
            logger.warning("Coleta em background ja esta rodando")
            return

        self._running = True
        logger.info(f"Iniciando coleta de metricas (intervalo: {self._collection_interval}s)")

        while self._running:
            try:
                await self.collect_all()
            except Exception as e:
                logger.error(f"Erro na coleta de metricas: {e}")

            await asyncio.sleep(self._collection_interval)

    def stop_background_collection(self) -> None:
        """Para coleta em background."""
        self._running = False
        logger.info("Coleta de metricas parada")

    def get_latest_metrics(self) -> dict[str, Any]:
        """Retorna metricas mais recentes."""
        return {
            "metrics": self._metrics,
            "last_collection": self._last_collection.isoformat() if self._last_collection else None,
        }

    def get_metric(self, name: str) -> float | None:
        """Retorna valor de uma metrica especifica."""
        return self._metrics.get(name)


# Instancia global
_collector: MetricCollectorService | None = None


def get_metric_collector() -> MetricCollectorService:
    """Retorna instancia global do coletor."""
    global _collector
    if _collector is None:
        _collector = MetricCollectorService()
    return _collector

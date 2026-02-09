"""
Health Check System - Verifica status de componentes críticos.

Monitora: Database, Redis, Integrações Externas, Filesystem.
"""

import asyncio
from datetime import datetime
from enum import StrEnum
from typing import Any

import httpx
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger


class HealthStatus(StrEnum):
    """Status de saúde do componente."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth:
    """Representa saúde de um componente."""

    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: str,
        latency_ms: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.name = name
        self.status = status
        self.message = message
        self.latency_ms = latency_ms
        self.details = details or {}
        self.checked_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }


class HealthChecker:
    """
    Sistema de Health Check.

    Verifica saúde de componentes críticos da aplicação.
    """

    def __init__(self):
        self.checks: dict[str, ComponentHealth] = {}

    async def check_database(self, db: AsyncSession) -> ComponentHealth:
        """
        Verifica conexão e performance do banco de dados.

        Args:
            db: Sessão do banco de dados

        Returns:
            ComponentHealth com status do banco
        """
        import time

        start = time.monotonic()

        try:
            # Query simples para testar conexão
            result = await db.execute(text("SELECT 1"))
            result.scalar()

            latency = int((time.monotonic() - start) * 1000)

            # Verifica pool de conexões
            pool_size = db.bind.pool.size() if hasattr(db.bind, "pool") else None
            pool_overflow = db.bind.pool.overflow() if hasattr(db.bind, "pool") else None

            details = {}
            if pool_size is not None:
                details["pool_size"] = pool_size
            if pool_overflow is not None:
                details["pool_overflow"] = pool_overflow

            # Define status baseado em latência
            if latency < 100:
                status = HealthStatus.HEALTHY
                message = "Database online e responsivo"
            elif latency < 500:
                status = HealthStatus.DEGRADED
                message = f"Database lento ({latency}ms)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Database muito lento ({latency}ms)"

            return ComponentHealth(
                name="database",
                status=status,
                message=message,
                latency_ms=latency,
                details=details,
            )

        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            logger.error(f"Database health check falhou: {e}")

            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database offline: {str(e)[:100]}",
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_redis(self, redis: Redis | None = None) -> ComponentHealth:
        """
        Verifica conexão com Redis.

        Args:
            redis: Cliente Redis (opcional)

        Returns:
            ComponentHealth com status do Redis
        """
        import time

        if redis is None:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.DEGRADED,
                message="Redis não configurado",
                details={"configured": False},
            )

        start = time.monotonic()

        try:
            # Ping no Redis
            await redis.ping()

            latency = int((time.monotonic() - start) * 1000)

            # Verifica info
            info = await redis.info()
            connected_clients = info.get("connected_clients", 0)
            used_memory_mb = info.get("used_memory", 0) / (1024 * 1024)

            details = {
                "connected_clients": connected_clients,
                "used_memory_mb": round(used_memory_mb, 2),
            }

            if latency < 50:
                status = HealthStatus.HEALTHY
                message = "Redis online e responsivo"
            elif latency < 200:
                status = HealthStatus.DEGRADED
                message = f"Redis lento ({latency}ms)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Redis muito lento ({latency}ms)"

            return ComponentHealth(
                name="redis",
                status=status,
                message=message,
                latency_ms=latency,
                details=details,
            )

        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            logger.error(f"Redis health check falhou: {e}")

            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis offline: {str(e)[:100]}",
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_external_integration(
        self,
        name: str,
        url: str,
        timeout: int = 5,
    ) -> ComponentHealth:
        """
        Verifica integração externa via HTTP.

        Args:
            name: Nome da integração
            url: URL para testar
            timeout: Timeout em segundos

        Returns:
            ComponentHealth com status da integração
        """
        import time

        start = time.monotonic()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)

            latency = int((time.monotonic() - start) * 1000)

            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                message = f"Integração {name} online"
            elif 200 <= response.status_code < 500:
                status = HealthStatus.DEGRADED
                message = f"Integração {name} com problemas (HTTP {response.status_code})"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Integração {name} offline (HTTP {response.status_code})"

            return ComponentHealth(
                name=name,
                status=status,
                message=message,
                latency_ms=latency,
                details={"status_code": response.status_code},
            )

        except httpx.TimeoutException:
            latency = int((time.monotonic() - start) * 1000)
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Integração {name} timeout ({timeout}s)",
                latency_ms=latency,
                details={"error": "timeout"},
            )

        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            logger.error(f"Integration {name} health check falhou: {e}")

            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Integração {name} offline: {str(e)[:100]}",
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_all(
        self,
        db: AsyncSession,
        redis: Redis | None = None,
        external_integrations: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Executa todos os health checks em paralelo.

        Args:
            db: Sessão do banco de dados
            redis: Cliente Redis (opcional)
            external_integrations: Dict de {nome: url} para integra��ões

        Returns:
            Dict com status geral e detalhes de cada componente
        """
        checks = []

        # Database check
        checks.append(self.check_database(db))

        # Redis check
        if redis:
            checks.append(self.check_redis(redis))

        # External integrations
        if external_integrations:
            for name, url in external_integrations.items():
                checks.append(self.check_external_integration(name, url))

        # Executa todos em paralelo
        results = await asyncio.gather(*checks, return_exceptions=True)

        # Processa resultados
        components = {}
        overall_status = HealthStatus.HEALTHY

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check exception: {result}")
                continue

            components[result.name] = result.to_dict()

            # Atualiza status geral (pior status prevalece)
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "healthy_count": sum(1 for c in components.values() if c["status"] == "healthy"),
            "total_count": len(components),
        }

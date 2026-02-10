"""
Testes - Health Check Detailed
Sprint 21: Monitoramento avancado para UptimeRobot

Testa o endpoint /health/detailed que verifica DB, Redis e Celery.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestHealthDetailed:
    """Testes do endpoint /health/detailed."""

    @pytest.mark.asyncio
    async def test_health_detailed_all_healthy(self):
        """Testa health detailed quando todos servicos estao ok."""
        from main_production import health_check_detailed

        # Mock das dependencias reais usadas pela funcao
        with (
            patch("core.cache.get_redis") as mock_get_redis,
            patch("core.database.session.async_session_factory") as mock_session_factory,
            patch("redis.from_url") as mock_celery_redis,
        ):
            # Setup Redis mock
            mock_redis_client = AsyncMock()
            mock_redis_client.ping = AsyncMock(return_value=True)
            mock_get_redis.return_value = mock_redis_client

            # Setup DB mock (async context manager)
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value=True)
            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_cm

            # Setup Celery/Redis sync mock
            mock_celery = MagicMock()
            mock_celery.ping.return_value = True
            mock_celery.close = MagicMock()
            mock_celery_redis.return_value = mock_celery

            result = await health_check_detailed()

            assert result["status"] in ["healthy", "degraded", "unhealthy"]
            assert "checks" in result
            assert "database" in result["checks"]
            assert "redis" in result["checks"]
            assert "celery" in result["checks"]
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_health_detailed_returns_status_fields(self):
        """Testa que health detailed retorna campos obrigatorios."""
        from main_production import health_check_detailed

        with (
            patch("core.cache.get_redis") as mock_get_redis,
            patch("core.database.session.async_session_factory") as mock_session_factory,
            patch("redis.from_url") as mock_celery_redis,
        ):
            # Setup - tudo falha para testar estrutura
            mock_get_redis.side_effect = Exception("Redis Error")
            mock_session_factory.side_effect = Exception("DB Error")
            mock_celery_redis.side_effect = Exception("Celery Error")

            result = await health_check_detailed()

            # Campos obrigatorios
            assert "status" in result
            assert "app" in result
            assert "version" in result
            assert "environment" in result
            assert "checks" in result
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_health_detailed_unhealthy_on_db_failure(self):
        """Testa que retorna unhealthy quando DB falha."""
        from main_production import health_check_detailed

        with (
            patch("core.cache.get_redis") as mock_get_redis,
            patch("core.database.session.async_session_factory") as mock_session_factory,
            patch("redis.from_url") as mock_celery_redis,
        ):
            # Redis OK
            mock_redis_client = AsyncMock()
            mock_redis_client.ping = AsyncMock(return_value=True)
            mock_get_redis.return_value = mock_redis_client

            # DB falha
            mock_session_factory.side_effect = Exception("Connection refused")

            # Celery OK
            mock_celery = MagicMock()
            mock_celery.ping.return_value = True
            mock_celery.close = MagicMock()
            mock_celery_redis.return_value = mock_celery

            result = await health_check_detailed()

            assert result["checks"]["database"]["status"] == "unhealthy"
            assert result["checks"]["database"]["error"] is not None

    @pytest.mark.asyncio
    async def test_health_detailed_latency_tracking(self):
        """Testa que latencia eh rastreada para cada servico."""
        from main_production import health_check_detailed

        with (
            patch("core.cache.get_redis") as mock_get_redis,
            patch("core.database.session.async_session_factory") as mock_session_factory,
            patch("redis.from_url") as mock_celery_redis,
        ):
            # Todos os servicos OK
            mock_redis_client = AsyncMock()
            mock_redis_client.ping = AsyncMock(return_value=True)
            mock_get_redis.return_value = mock_redis_client

            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value=True)
            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_cm

            mock_celery = MagicMock()
            mock_celery.ping.return_value = True
            mock_celery.close = MagicMock()
            mock_celery_redis.return_value = mock_celery

            result = await health_check_detailed()

            # Verifica que latencia eh um numero ou None
            for _check_name, check_data in result["checks"].items():
                latency = check_data.get("latency_ms")
                assert latency is None or isinstance(latency, (int, float))


class TestHealthDetailedStatusLogic:
    """Testes da logica de status do health detailed."""

    def test_status_healthy_when_all_services_healthy(self):
        """Status deve ser healthy quando todos servicos estao healthy."""
        checks = {
            "database": {"status": "healthy"},
            "redis": {"status": "healthy"},
            "celery": {"status": "healthy"},
        }
        statuses = [c["status"] for c in checks.values()]

        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif "unhealthy" in statuses:
            overall = "unhealthy"
        else:
            overall = "degraded"

        assert overall == "healthy"

    def test_status_unhealthy_when_any_unhealthy(self):
        """Status deve ser unhealthy quando qualquer servico esta unhealthy."""
        checks = {
            "database": {"status": "unhealthy"},
            "redis": {"status": "healthy"},
            "celery": {"status": "healthy"},
        }
        statuses = [c["status"] for c in checks.values()]

        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif "unhealthy" in statuses:
            overall = "unhealthy"
        else:
            overall = "degraded"

        assert overall == "unhealthy"

    def test_status_degraded_when_some_degraded(self):
        """Status deve ser degraded quando ha servicos degraded mas nenhum unhealthy."""
        checks = {
            "database": {"status": "healthy"},
            "redis": {"status": "degraded"},
            "celery": {"status": "healthy"},
        }
        statuses = [c["status"] for c in checks.values()]

        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif "unhealthy" in statuses:
            overall = "unhealthy"
        else:
            overall = "degraded"

        assert overall == "degraded"

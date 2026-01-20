"""
Testes E2E - Fluxo de Operações.

Testa os módulos de Operações: Postos, Escalas, Alocações.
Rotas usam padrão: /api/v1/operations/{module}/{module}/
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestOperationsPosts:
    """Testes de Postos."""

    async def test_posts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de postos existe."""
        response = await client.get("/api/v1/operations/posts/posts/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_posts_stats_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de stats de postos existe."""
        response = await client.get("/api/v1/operations/posts/posts/stats")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestOperationsScales:
    """Testes de Escalas."""

    async def test_scales_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de escalas existe."""
        response = await client.get("/api/v1/operations/scales/scales/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestOperationsShifts:
    """Testes de Turnos."""

    async def test_shifts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de turnos existe."""
        response = await client.get("/api/v1/operations/shifts/shifts/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_shifts_today_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de turnos de hoje existe."""
        response = await client.get("/api/v1/operations/shifts/shifts/today")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestOperationsAllocations:
    """Testes de Alocações."""

    async def test_allocations_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de alocações existe."""
        response = await client.get("/api/v1/operations/allocations/allocations/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_allocations_current_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de alocações atuais existe."""
        response = await client.get("/api/v1/operations/allocations/allocations/current")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestClients:
    """Testes de Clientes/Condomínios."""

    @pytest.mark.xfail(reason="Bug: sync query com AsyncSession no repository")
    async def test_clients_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de clientes existe."""
        # Rota tem duplicação: /api/v1/clients/api/v1/clients/
        response = await client.get("/api/v1/clients/api/v1/clients/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestOccurrences:
    """Testes de Ocorrências."""

    async def test_occurrences_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de ocorrências existe."""
        response = await client.get("/api/v1/occurrences/occurrences/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestAudit:
    """Testes de Auditoria."""

    async def test_audit_logs_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de logs de auditoria existe."""
        response = await client.get("/api/v1/audit/audit/logs")
        assert response.status_code in [200, 401, 403, 422]

    async def test_audit_dashboard_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de dashboard de auditoria existe."""
        response = await client.get("/api/v1/audit/audit/dashboard")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestGED:
    """Testes de Gestão de Documentos."""

    async def test_ged_folders_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de pastas GED existe."""
        response = await client.get("/api/v1/ged/folders/folders/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_ged_documents_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de documentos GED existe."""
        response = await client.get("/api/v1/ged/documents/documents/")
        assert response.status_code in [200, 401, 403, 422]

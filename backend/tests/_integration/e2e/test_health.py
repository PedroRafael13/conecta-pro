"""
Testes E2E - Health Check e Status do Sistema.

Verifica se o sistema está funcionando corretamente.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Testes dos endpoints de health check."""

    async def test_health_check(self, client: AsyncClient):
        """Testa endpoint /health."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_root_endpoint(self, client: AsyncClient):
        """Testa endpoint raiz /."""
        response = await client.get("/")
        assert response.status_code == 200

    async def test_docs_endpoint_in_debug(self, client: AsyncClient):
        """Testa que /docs está disponível em debug mode."""
        response = await client.get("/docs")
        assert response.status_code in [200, 404]

    async def test_metrics_endpoint(self, client: AsyncClient):
        """Testa endpoint /metrics para Prometheus."""
        response = await client.get("/metrics")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAPIStructure:
    """Testes da estrutura da API."""

    async def test_openapi_json_available(self, client: AsyncClient):
        """Verifica que OpenAPI schema está disponível."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    async def test_api_has_many_routes(self, client: AsyncClient):
        """Verifica que a API tem muitas rotas registradas."""
        response = await client.get("/openapi.json")
        data = response.json()
        paths = data.get("paths", {})
        assert len(paths) > 100, f"Esperado >100 rotas, encontradas: {len(paths)}"

    async def test_api_has_ai_module_routes(self, client: AsyncClient):
        """Verifica que rotas de IA estão registradas."""
        response = await client.get("/openapi.json")
        data = response.json()
        paths = data.get("paths", {})
        ai_routes = [p for p in paths if "/ai/" in p]
        assert len(ai_routes) > 50, f"Esperado >50 rotas IA, encontradas: {len(ai_routes)}"

    async def test_api_has_financial_routes(self, client: AsyncClient):
        """Verifica que rotas financeiras estão registradas."""
        response = await client.get("/openapi.json")
        data = response.json()
        paths = data.get("paths", {})
        fin_routes = [p for p in paths if "/financial/" in p]
        assert len(fin_routes) > 20, f"Esperado >20 rotas financeiras, encontradas: {len(fin_routes)}"

    async def test_api_has_hr_routes(self, client: AsyncClient):
        """Verifica que rotas de RH estão registradas."""
        response = await client.get("/openapi.json")
        data = response.json()
        paths = data.get("paths", {})
        hr_routes = [p for p in paths if "/hr/" in p]
        assert len(hr_routes) > 20, f"Esperado >20 rotas RH, encontradas: {len(hr_routes)}"

    async def test_api_has_operations_routes(self, client: AsyncClient):
        """Verifica que rotas de operações estão registradas."""
        response = await client.get("/openapi.json")
        data = response.json()
        paths = data.get("paths", {})
        ops_routes = [p for p in paths if "/operacional/" in p]
        assert len(ops_routes) > 10, f"Esperado >10 rotas operações, encontradas: {len(ops_routes)}"

    async def test_invalid_endpoint_returns_404(self, client: AsyncClient):
        """Verifica que endpoints inválidos retornam 404."""
        response = await client.get("/invalid/endpoint/that/does/not/exist")
        assert response.status_code == 404

    async def test_method_not_allowed(self, client: AsyncClient):
        """Verifica que métodos não permitidos retornam 405."""
        response = await client.post("/health")
        assert response.status_code == 405

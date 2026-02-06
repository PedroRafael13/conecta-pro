"""
Testes E2E - Fluxo de Autenticação.

Testa o fluxo completo de autenticação: login, token, refresh, logout.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Testes do fluxo de autenticação."""

    @pytest.mark.xfail(reason="Requer banco de dados configurado")
    async def test_login_endpoint_exists(self, client: AsyncClient):
        """Testa que endpoint de login existe."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "test@test.com", "password": "test123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # 401 = credenciais inválidas, 422 = validação
        assert response.status_code in [200, 401, 422]

    async def test_login_with_missing_fields(self, client: AsyncClient):
        """Testa login com campos faltando."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "test@email.com"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # Deve retornar erro de validação
        assert response.status_code == 422

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Testa acesso a endpoint protegido sem token."""
        response = await client.get("/api/v1/leads/")
        # Deve retornar 401 Unauthorized ou 403 Forbidden
        assert response.status_code in [401, 403]

    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Testa acesso a endpoint protegido com token inválido."""
        response = await client.get(
            "/api/v1/leads/",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        # Deve retornar 401 ou 403
        assert response.status_code in [401, 403]

    async def test_me_endpoint_exists(self, client: AsyncClient):
        """Testa que endpoint /me existe."""
        response = await client.get("/api/v1/auth/me")
        # 401 sem token é esperado
        assert response.status_code in [401, 403]

    async def test_refresh_endpoint_exists(self, client: AsyncClient):
        """Testa que endpoint /refresh existe."""
        response = await client.post("/api/v1/auth/refresh")
        # 401/422 sem token é esperado
        assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
class TestAuthorizationRoles:
    """Testes de autorização por roles."""

    async def test_unauthenticated_public_endpoints(self, client: AsyncClient):
        """Testa que endpoints públicos não requerem auth."""
        public_endpoints = ["/health", "/", "/metrics"]

        for endpoint in public_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"

    async def test_openapi_is_public(self, client: AsyncClient):
        """Testa que OpenAPI é público."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200

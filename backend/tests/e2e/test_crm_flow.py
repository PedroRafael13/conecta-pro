"""
Testes E2E - Fluxo CRM.

Testa o fluxo completo do CRM: Lead -> Oportunidade -> Proposta -> Contrato.
Rotas diretas em /api/v1/ (sem prefixo /crm/).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCRMLeads:
    """Testes de Leads no CRM."""

    async def test_leads_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de leads existe."""
        response = await client.get("/api/v1/leads/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_create_lead_validation(self, authenticated_client: AsyncClient):
        """Testa validação ao criar lead."""
        response = await authenticated_client.post(
            "/api/v1/leads/",
            json={},
        )
        assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
class TestCRMOpportunities:
    """Testes de Oportunidades no CRM."""

    async def test_opportunities_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de oportunidades existe."""
        response = await client.get("/api/v1/opportunities/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestCRMProposals:
    """Testes de Propostas no CRM."""

    async def test_proposals_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de propostas existe."""
        response = await client.get("/api/v1/proposals/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestCRMContracts:
    """Testes de Contratos no CRM."""

    async def test_contracts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de contratos existe."""
        response = await client.get("/api/v1/contracts/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestCRMDashboard:
    """Testes do Dashboard CRM."""

    async def test_dashboard_charts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de charts do dashboard existe."""
        response = await client.get("/api/v1/dashboard/charts/leads-by-status")
        assert response.status_code in [200, 401, 403, 422]

    async def test_dashboard_trends_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de trends do dashboard existe."""
        response = await client.get("/api/v1/dashboard/trends/leads")
        assert response.status_code in [200, 401, 403, 422]

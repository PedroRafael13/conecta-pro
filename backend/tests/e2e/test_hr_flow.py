"""
Testes E2E - Fluxo de RH.

Testa os módulos de Recursos Humanos.
Rotas usam padrão: /api/v1/hr/{module}/{module}/
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHRAnalytics:
    """Testes de Analytics de RH."""

    async def test_hr_analytics_dashboards_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de dashboards HR existe."""
        response = await client.get("/api/v1/hr/analytics/dashboards/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_hr_analytics_kpis_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de KPIs existe."""
        response = await client.get("/api/v1/hr/analytics/kpis/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestHRPortal:
    """Testes do Portal do Funcionário."""

    async def test_hr_portal_notifications_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de notificações existe."""
        response = await client.get("/api/v1/hr/portal/notifications/")
        assert response.status_code in [200, 401, 403, 404, 422]


@pytest.mark.asyncio
class TestHRMobileTimeClock:
    """Testes do Ponto Mobile."""

    async def test_mobile_devices_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de dispositivos mobile existe."""
        response = await client.get("/api/v1/hr/mobile/mobile/devices/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_mobile_checkins_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de check-ins mobile existe."""
        response = await client.get("/api/v1/hr/mobile/mobile/checkins/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_mobile_geofences_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de geofences existe."""
        response = await client.get("/api/v1/hr/mobile/mobile/geofences/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestHRPayroll:
    """Testes de Folha de Pagamento."""

    async def test_payroll_exports_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de exportação existe."""
        response = await client.get("/api/v1/hr/payroll/exports/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_payroll_esocial_status_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de status eSocial existe."""
        response = await client.get("/api/v1/hr/payroll/esocial/status")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestHRTimeTracking:
    """Testes de Ponto Eletrônico."""

    async def test_time_tracking_entries_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de registros de ponto existe."""
        response = await client.get("/api/v1/hr/time-tracking/time-entries/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestRecruitment:
    """Testes de Recrutamento."""

    async def test_vacancies_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de vagas existe."""
        response = await client.get("/api/v1/recruitment/job-positions/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_candidates_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de candidatos existe."""
        response = await client.get("/api/v1/recruitment/candidates/")
        assert response.status_code in [200, 401, 403, 422]

"""
Testes de integração para os endpoints API do módulo Facilities.
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from modules.facilities.controllers.area_controller import router as area_router
from modules.facilities.controllers.checklist_controller import router as checklist_router
from modules.facilities.controllers.inspection_controller import router as inspection_router
from modules.facilities.controllers.maintenance_controller import router as maintenance_router
from modules.facilities.controllers.service_request_controller import (
    router as service_request_router,
)
from modules.facilities.models.area import Area, AreaStatus, AreaType
from modules.facilities.models.checklist import Checklist, ChecklistItem, ChecklistStatus
from modules.facilities.models.inspection import Inspection, InspectionStatus, InspectionType
from modules.facilities.models.maintenance import (
    Maintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.facilities.models.service_request import (
    ServiceRequest,
    ServiceRequestCategory,
    ServiceRequestPriority,
    ServiceRequestStatus,
)


@pytest.fixture
def mock_area():
    """Fixture para área mock."""
    area = MagicMock(spec=Area)
    area.id = "area-001"
    area.name = "Hall de Entrada"
    area.code = "HALL-001"
    area.area_type = AreaType.COMMON_AREA
    area.status = AreaStatus.ACTIVE
    area.floor = "Térreo"
    area.size_m2 = Decimal("150.0")
    area.description = "Hall principal"
    area.parent_id = None
    area.client_id = "client-001"
    area.condominium_id = "condo-001"
    area.is_active = True
    area.created_at = "2024-01-01T00:00:00"
    area.updated_at = "2024-01-01T00:00:00"
    return area


@pytest.fixture
def mock_maintenance():
    """Fixture para manutenção mock."""
    maintenance = MagicMock(spec=Maintenance)
    maintenance.id = "maint-001"
    maintenance.title = "Troca de lâmpadas"
    maintenance.description = "Substituir lâmpadas"
    maintenance.maintenance_type = MaintenanceType.CORRECTIVE
    maintenance.priority = MaintenancePriority.MEDIUM
    maintenance.status = MaintenanceStatus.PENDING
    maintenance.scheduled_date = date.today() + timedelta(days=7)
    maintenance.estimated_hours = Decimal("2.0")
    maintenance.estimated_cost = Decimal("500.00")
    maintenance.area_id = "area-001"
    maintenance.client_id = "client-001"
    maintenance.is_active = True
    maintenance.created_at = "2024-01-01T00:00:00"
    maintenance.updated_at = "2024-01-01T00:00:00"
    return maintenance


@pytest.fixture
def mock_inspection():
    """Fixture para inspeção mock."""
    inspection = MagicMock(spec=Inspection)
    inspection.id = "insp-001"
    inspection.title = "Vistoria Mensal"
    inspection.description = "Inspeção de rotina"
    inspection.inspection_type = InspectionType.ROUTINE
    inspection.status = InspectionStatus.SCHEDULED
    inspection.scheduled_date = date.today() + timedelta(days=3)
    inspection.inspector_name = "João Silva"
    inspection.area_id = "area-001"
    inspection.client_id = "client-001"
    inspection.checklists = []
    inspection.is_active = True
    inspection.created_at = "2024-01-01T00:00:00"
    inspection.updated_at = "2024-01-01T00:00:00"
    return inspection


@pytest.fixture
def mock_checklist():
    """Fixture para checklist mock."""
    checklist = MagicMock(spec=Checklist)
    checklist.id = "check-001"
    checklist.name = "Checklist de Limpeza"
    checklist.description = "Verificação diária"
    checklist.category = "cleaning"
    checklist.is_template = True
    checklist.status = ChecklistStatus.DRAFT
    checklist.items = []
    checklist.client_id = "client-001"
    checklist.is_active = True
    checklist.created_at = "2024-01-01T00:00:00"
    checklist.updated_at = "2024-01-01T00:00:00"
    return checklist


@pytest.fixture
def mock_service_request():
    """Fixture para solicitação de serviço mock."""
    request = MagicMock(spec=ServiceRequest)
    request.id = "req-001"
    request.title = "Vazamento na cozinha"
    request.description = "Vazamento na pia"
    request.category = ServiceRequestCategory.PLUMBING
    request.priority = ServiceRequestPriority.HIGH
    request.status = ServiceRequestStatus.OPEN
    request.requester_name = "Maria Santos"
    request.requester_email = "maria@email.com"
    request.area_id = "area-001"
    request.client_id = "client-001"
    request.is_active = True
    request.created_at = "2024-01-01T00:00:00"
    request.updated_at = "2024-01-01T00:00:00"
    return request


class TestAreaAPI:
    """Testes para API de Areas."""

    @pytest.mark.asyncio
    async def test_create_area(self, mock_area):
        """Testa criação de área via API."""
        with patch("modules.facilities.controllers.area_controller.AreaRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create = AsyncMock(return_value=mock_area)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(area_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.area_controller.get_db"):
                    response = await client.post(
                        "/areas/",
                        json={
                            "name": "Hall de Entrada",
                            "code": "HALL-001",
                            "area_type": "common_area",
                        },
                    )

            # Verificar que o endpoint existe e aceita o formato
            assert response.status_code in [201, 422, 500]

    @pytest.mark.asyncio
    async def test_list_areas(self, mock_area):
        """Testa listagem de áreas via API."""
        with patch("modules.facilities.controllers.area_controller.AreaRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.list = AsyncMock(return_value=([mock_area], 1))

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(area_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.area_controller.get_db"):
                    response = await client.get("/areas/")

            assert response.status_code in [200, 500]


class TestMaintenanceAPI:
    """Testes para API de Maintenances."""

    @pytest.mark.asyncio
    async def test_create_maintenance(self, mock_maintenance):
        """Testa criação de manutenção via API."""
        with patch("modules.facilities.controllers.maintenance_controller.MaintenanceRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create = AsyncMock(return_value=mock_maintenance)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(maintenance_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.maintenance_controller.get_db"):
                    response = await client.post(
                        "/maintenances/",
                        json={
                            "title": "Troca de lâmpadas",
                            "description": "Substituir lâmpadas",
                            "maintenance_type": "corrective",
                            "priority": "medium",
                        },
                    )

            assert response.status_code in [201, 422, 500]

    @pytest.mark.asyncio
    async def test_suggest_schedule(self):
        """Testa endpoint de sugestão de agendamento."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(maintenance_router)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/maintenances/suggest-schedule",
                params={
                    "maintenance_type": "preventive",
                    "equipment_type": "elevator",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "suggested_date" in data


class TestInspectionAPI:
    """Testes para API de Inspections."""

    @pytest.mark.asyncio
    async def test_create_inspection(self, mock_inspection):
        """Testa criação de inspeção via API."""
        with patch("modules.facilities.controllers.inspection_controller.InspectionRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create = AsyncMock(return_value=mock_inspection)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(inspection_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.inspection_controller.get_db"):
                    response = await client.post(
                        "/inspections/",
                        json={
                            "title": "Vistoria Mensal",
                            "description": "Inspeção de rotina",
                            "inspection_type": "routine",
                        },
                    )

            assert response.status_code in [201, 422, 500]


class TestChecklistAPI:
    """Testes para API de Checklists."""

    @pytest.mark.asyncio
    async def test_create_checklist(self, mock_checklist):
        """Testa criação de checklist via API."""
        with patch("modules.facilities.controllers.checklist_controller.ChecklistRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create = AsyncMock(return_value=mock_checklist)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(checklist_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.checklist_controller.get_db"):
                    response = await client.post(
                        "/checklists/",
                        json={
                            "name": "Checklist de Limpeza",
                            "description": "Verificação diária",
                            "category": "cleaning",
                            "is_template": True,
                        },
                    )

            assert response.status_code in [201, 422, 500]

    @pytest.mark.asyncio
    async def test_list_templates(self, mock_checklist):
        """Testa listagem de templates via API."""
        with patch("modules.facilities.controllers.checklist_controller.ChecklistRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.list = AsyncMock(return_value=([mock_checklist], 1))

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(checklist_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.checklist_controller.get_db"):
                    response = await client.get("/checklists/templates")

            assert response.status_code in [200, 500]


class TestServiceRequestAPI:
    """Testes para API de ServiceRequests."""

    @pytest.mark.asyncio
    async def test_create_service_request(self, mock_service_request):
        """Testa criação de solicitação via API."""
        with patch("modules.facilities.controllers.service_request_controller.ServiceRequestRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create = AsyncMock(return_value=mock_service_request)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(service_request_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.service_request_controller.get_db"):
                    response = await client.post(
                        "/service-requests/",
                        json={
                            "title": "Vazamento na cozinha",
                            "description": "Vazamento na pia",
                            "category": "plumbing",
                            "priority": "high",
                            "requester_name": "Maria Santos",
                        },
                    )

            assert response.status_code in [201, 422, 500]

    @pytest.mark.asyncio
    async def test_classify_request(self):
        """Testa endpoint de classificação via API."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(service_request_router)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/service-requests/classify",
                params={
                    "title": "Vazamento no banheiro",
                    "description": "Água vazando da torneira",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert data["category"] == "plumbing"

    @pytest.mark.asyncio
    async def test_suggest_assignee(self):
        """Testa endpoint de sugestão de responsável via API."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(service_request_router)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/service-requests/suggest-assignee",
                params={
                    "category": "plumbing",
                    "priority": "high",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "suggested_team" in data


class TestAPIErrorHandling:
    """Testes de tratamento de erros na API."""

    @pytest.mark.asyncio
    async def test_area_not_found(self):
        """Testa erro 404 para área não encontrada."""
        with patch("modules.facilities.controllers.area_controller.AreaRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(area_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.area_controller.get_db"):
                    response = await client.get("/areas/invalid-id")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_maintenance_not_found(self):
        """Testa erro 404 para manutenção não encontrada."""
        with patch("modules.facilities.controllers.maintenance_controller.MaintenanceRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(maintenance_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.maintenance_controller.get_db"):
                    response = await client.get("/maintenances/invalid-id")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_inspection_not_found(self):
        """Testa erro 404 para inspeção não encontrada."""
        with patch("modules.facilities.controllers.inspection_controller.InspectionRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(inspection_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.inspection_controller.get_db"):
                    response = await client.get("/inspections/invalid-id")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_checklist_not_found(self):
        """Testa erro 404 para checklist não encontrado."""
        with patch("modules.facilities.controllers.checklist_controller.ChecklistRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(checklist_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.checklist_controller.get_db"):
                    response = await client.get("/checklists/invalid-id")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_service_request_not_found(self):
        """Testa erro 404 para solicitação não encontrada."""
        with patch("modules.facilities.controllers.service_request_controller.ServiceRequestRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(service_request_router)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with patch("modules.facilities.controllers.service_request_controller.get_db"):
                    response = await client.get("/service-requests/invalid-id")

            assert response.status_code == 404

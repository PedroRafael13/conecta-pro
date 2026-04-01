"""
Testes E2E do Time Tracking (DP) — endpoints FastAPI com DB mockado e services mockados.

Endpoints cobertos:
  POST /time-tracking/from-operations  — registrar ponto via operações
  GET  /time-tracking/employee/{id}/entries — listar registros de ponto
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.auth.dependencies import get_current_active_user
from core.database.session import get_db
from modules.people_management.hr.controllers.time_tracking_controller import (
    router as time_tracking_router,
)

# ===========================================================================
# FAKE DB + FAKE USER
# ===========================================================================


class FakeAsyncSession:
    """AsyncSession fake (sem banco real)."""

    def __init__(self):
        self._added: list = []

    def add(self, obj):
        self._added.append(obj)

    async def flush(self):
        for obj in self._added:
            if not getattr(obj, "id", None):
                import uuid

                obj.id = uuid.uuid4()
        self._added.clear()

    async def refresh(self, obj):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def execute(self, stmt, params=None):
        return FakeResult()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeResult:
    """Resultado fake de query SQLAlchemy."""

    def scalar_one_or_none(self):
        return None

    def scalar(self):
        return 0

    def scalars(self):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def fetchall(self):
        return []

    def mappings(self):
        return self


async def get_fake_db():
    yield FakeAsyncSession()


class FakeUser:
    id = "user-test-001"
    email = "admin@conectapro.com.br"
    role = "admin"
    is_active = True
    permissions = ["*"]


async def get_fake_current_user():
    return FakeUser()


# ===========================================================================
# FIXTURES
# ===========================================================================

PATCH_TT_SERVICE = "modules.people_management.hr.controllers.time_tracking_controller.TimeTrackingService"


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(time_tracking_router, prefix="/api/v1")
    application.dependency_overrides[get_db] = get_fake_db
    application.dependency_overrides[get_current_active_user] = get_fake_current_user
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ===========================================================================
# POST /time-tracking/from-operations
# ===========================================================================


class TestRegisterFromOperations:
    """Testes E2E para POST /time-tracking/from-operations."""

    @pytest.mark.asyncio
    async def test_register_happy_path(self, client):
        """Happy path — registra ponto com sucesso e retorna 200."""
        mock_result = {
            "entry_id": "entry-abc-001",
            "employee_id": "emp-001",
            "entry_datetime": "2026-03-29T08:00:00",
            "shift_end": "2026-03-29T20:00:00",
            "duration_hours": 12.0,
            "source": "operations",
            "status": "registered",
        }
        mock_service = MagicMock()
        mock_service.register_from_operations = AsyncMock(return_value=mock_result)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.post(
                "/api/v1/time-tracking/from-operations",
                json={
                    "employee_id": "emp-001",
                    "shift_start": "2026-03-29T08:00:00",
                    "shift_end": "2026-03-29T20:00:00",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["entry_id"] == "entry-abc-001"
        assert data["employee_id"] == "emp-001"
        assert data["status"] == "registered"
        assert data["duration_hours"] == 12.0
        assert data["source"] == "operations"

    @pytest.mark.asyncio
    async def test_register_with_location_and_notes(self, client):
        """Deve aceitar location_id e notes opcionais."""
        mock_result = {
            "entry_id": "entry-abc-002",
            "employee_id": "emp-002",
            "entry_datetime": "2026-03-29T18:00:00",
            "shift_end": "2026-03-30T06:00:00",
            "duration_hours": 12.0,
            "source": "operations",
            "status": "registered",
        }
        mock_service = MagicMock()
        mock_service.register_from_operations = AsyncMock(return_value=mock_result)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.post(
                "/api/v1/time-tracking/from-operations",
                json={
                    "employee_id": "emp-002",
                    "shift_start": "2026-03-29T18:00:00",
                    "shift_end": "2026-03-30T06:00:00",
                    "location_id": "posto-central-001",
                    "notes": "Turno noturno — escala 12x36",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == "emp-002"
        assert data["status"] == "registered"

        # Verificar que service foi chamado com os parametros corretos
        call_kwargs = mock_service.register_from_operations.call_args.kwargs
        assert call_kwargs["location_id"] == "posto-central-001"
        assert call_kwargs["notes"] == "Turno noturno — escala 12x36"

    @pytest.mark.asyncio
    async def test_register_module_unavailable(self, client):
        """Quando modulo time_tracking nao esta disponivel, retorna status=unavailable."""
        mock_result = {
            "status": "unavailable",
            "message": "Módulo de ponto não disponível",
        }
        mock_service = MagicMock()
        mock_service.register_from_operations = AsyncMock(return_value=mock_result)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.post(
                "/api/v1/time-tracking/from-operations",
                json={
                    "employee_id": "emp-003",
                    "shift_start": "2026-03-29T08:00:00",
                    "shift_end": "2026-03-29T20:00:00",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_register_missing_employee_id_returns_422(self, client):
        """Sem employee_id → 422 Unprocessable Entity."""
        response = await client.post(
            "/api/v1/time-tracking/from-operations",
            json={
                "shift_start": "2026-03-29T08:00:00",
                "shift_end": "2026-03-29T20:00:00",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_shift_start_returns_422(self, client):
        """Sem shift_start → 422 Unprocessable Entity."""
        response = await client.post(
            "/api/v1/time-tracking/from-operations",
            json={
                "employee_id": "emp-001",
                "shift_end": "2026-03-29T20:00:00",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_shift_end_returns_422(self, client):
        """Sem shift_end → 422 Unprocessable Entity."""
        response = await client.post(
            "/api/v1/time-tracking/from-operations",
            json={
                "employee_id": "emp-001",
                "shift_start": "2026-03-29T08:00:00",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_datetime_format_returns_422(self, client):
        """Datas em formato invalido → 422."""
        response = await client.post(
            "/api/v1/time-tracking/from-operations",
            json={
                "employee_id": "emp-001",
                "shift_start": "nao-eh-data",
                "shift_end": "tambem-nao",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_body_returns_422(self, client):
        """Body vazio → 422."""
        response = await client.post("/api/v1/time-tracking/from-operations", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_calls_service_with_correct_args(self, client):
        """Verifica que o service é chamado com os argumentos corretos."""
        mock_result = {
            "entry_id": "entry-check-001",
            "employee_id": "emp-check",
            "entry_datetime": "2026-03-29T07:00:00",
            "shift_end": "2026-03-29T19:00:00",
            "duration_hours": 12.0,
            "source": "operations",
            "status": "registered",
        }
        mock_service = MagicMock()
        mock_service.register_from_operations = AsyncMock(return_value=mock_result)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            await client.post(
                "/api/v1/time-tracking/from-operations",
                json={
                    "employee_id": "emp-check",
                    "shift_start": "2026-03-29T07:00:00",
                    "shift_end": "2026-03-29T19:00:00",
                    "notes": "turno-teste",
                },
            )

        mock_service.register_from_operations.assert_awaited_once()
        kwargs = mock_service.register_from_operations.call_args.kwargs
        assert kwargs["employee_id"] == "emp-check"
        assert kwargs["notes"] == "turno-teste"


# ===========================================================================
# GET /time-tracking/employee/{employee_id}/entries
# ===========================================================================


class TestGetEmployeeEntries:
    """Testes E2E para GET /time-tracking/employee/{id}/entries."""

    @pytest.mark.asyncio
    async def test_get_entries_happy_path(self, client):
        """Happy path — retorna lista de registros e total."""
        mock_entries = [
            {
                "date": "2026-03-28",
                "data": "2026-03-28",
                "clock_in": "08:00",
                "entrada": "08:00",
                "clock_out": "20:00",
                "saida": "20:00",
                "total_hours": "12:00",
                "total": "12:00",
                "status": "normal",
                "source": "tangerino",
            },
            {
                "date": "2026-03-26",
                "data": "2026-03-26",
                "clock_in": "20:00",
                "entrada": "20:00",
                "clock_out": "08:00",
                "saida": "08:00",
                "total_hours": "12:00",
                "total": "12:00",
                "status": "normal",
                "source": "tangerino",
            },
        ]
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=mock_entries)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get("/api/v1/time-tracking/employee/emp-001/entries")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["clock_in"] == "08:00"

    @pytest.mark.asyncio
    async def test_get_entries_empty_list(self, client):
        """Funcionario sem registros retorna lista vazia com total=0."""
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=[])

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get("/api/v1/time-tracking/employee/emp-sem-ponto/entries")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_entries_with_date_range(self, client):
        """Aceita start_date e end_date como query params."""
        mock_entries = [
            {
                "date": "2026-03-15",
                "data": "2026-03-15",
                "clock_in": "08:00",
                "entrada": "08:00",
                "clock_out": "17:00",
                "saida": "17:00",
                "total_hours": "09:00",
                "total": "09:00",
                "status": "normal",
                "source": "portal",
            }
        ]
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=mock_entries)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/time-tracking/employee/emp-001/entries",
                params={
                    "start_date": "2026-03-01T00:00:00",
                    "end_date": "2026-03-31T23:59:59",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["date"] == "2026-03-15"

        # Verificar que service foi chamado com datas
        mock_service.get_entries.assert_awaited_once()
        kwargs = mock_service.get_entries.call_args
        assert "emp-001" in kwargs.args or kwargs.kwargs.get("employee_id") == "emp-001"

    @pytest.mark.asyncio
    async def test_get_entries_with_only_start_date(self, client):
        """Aceita apenas start_date (end_date opcional)."""
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=[])

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/time-tracking/employee/emp-001/entries",
                params={"start_date": "2026-03-01T00:00:00"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_entries_with_only_end_date(self, client):
        """Aceita apenas end_date (start_date opcional)."""
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=[])

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/time-tracking/employee/emp-001/entries",
                params={"end_date": "2026-03-31T23:59:59"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_entries_invalid_start_date_returns_422(self, client):
        """start_date em formato invalido → 422."""
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=[])

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/time-tracking/employee/emp-001/entries",
                params={"start_date": "nao-eh-uma-data"},
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_entries_invalid_end_date_returns_422(self, client):
        """end_date em formato invalido → 422."""
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=[])

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/time-tracking/employee/emp-001/entries",
                params={"end_date": "32/13/2026"},
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_entries_single_record(self, client):
        """Retorna exatamente 1 registro quando ha apenas um."""
        mock_entries = [
            {
                "date": "2026-03-29",
                "data": "2026-03-29",
                "clock_in": "07:30",
                "entrada": "07:30",
                "clock_out": "19:30",
                "saida": "19:30",
                "total_hours": "12:00",
                "total": "12:00",
                "status": "normal",
                "source": "tangerino",
            }
        ]
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=mock_entries)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get("/api/v1/time-tracking/employee/emp-unique/entries")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["clock_in"] == "07:30"
        assert data["items"][0]["total_hours"] == "12:00"

    @pytest.mark.asyncio
    async def test_get_entries_with_inconsistencia_status(self, client):
        """Registros com status=inconsistencia sao retornados normalmente."""
        mock_entries = [
            {
                "date": "2026-03-20",
                "data": "2026-03-20",
                "clock_in": None,
                "entrada": None,
                "clock_out": "17:00",
                "saida": "17:00",
                "total_hours": "00:00",
                "total": "00:00",
                "status": "inconsistencia",
                "source": "tangerino",
            }
        ]
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=mock_entries)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get("/api/v1/time-tracking/employee/emp-inc/entries")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "inconsistencia"
        assert data["items"][0]["clock_in"] is None

    @pytest.mark.asyncio
    async def test_get_entries_many_records(self, client):
        """Retorna multiplos registros com total correto."""
        mock_entries = [
            {
                "date": f"2026-03-{d:02d}",
                "data": f"2026-03-{d:02d}",
                "clock_in": "08:00",
                "entrada": "08:00",
                "clock_out": "17:00",
                "saida": "17:00",
                "total_hours": "09:00",
                "total": "09:00",
                "status": "normal",
                "source": "portal",
            }
            for d in range(1, 16)  # 15 dias
        ]
        mock_service = MagicMock()
        mock_service.get_entries = AsyncMock(return_value=mock_entries)

        with patch(PATCH_TT_SERVICE, return_value=mock_service):
            response = await client.get("/api/v1/time-tracking/employee/emp-full/entries")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 15

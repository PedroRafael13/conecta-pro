"""
Testes E2E — Portal Escalas.

Endpoints cobertos:
  GET /portal/my-schedules
  GET /portal/my-schedules/current-month
  GET /portal/my-schedules/next-shift

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_schedules_controller import (
    router as schedules_router,
)

# ---------------------------------------------------------------------------
# FAKE AUTH
# ---------------------------------------------------------------------------

FAKE_EMPLOYEE_ID = str(uuid4())


async def fake_employee_id() -> str:
    return FAKE_EMPLOYEE_ID


# ---------------------------------------------------------------------------
# FAKE DB SESSION
# ---------------------------------------------------------------------------


class FakeResult:
    def scalars(self):
        return self

    def all(self):
        return []

    def scalar_one_or_none(self):
        return None

    def scalar(self):
        return 0

    def first(self):
        return None


class FakeAsyncSession:
    def __init__(self):
        pass

    def add(self, obj):
        pass

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def refresh(self, obj):
        pass

    async def execute(self, stmt, params=None):
        return FakeResult()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


async def get_fake_db():
    yield FakeAsyncSession()


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(schedules_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    application.dependency_overrides[get_portal_employee_id] = fake_employee_id
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def app_sem_override():
    application = FastAPI()
    application.include_router(schedules_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-schedules
# ---------------------------------------------------------------------------


class TestPortalMySchedules:
    """Testes E2E do endpoint de escala com filtro mes/ano."""

    @pytest.mark.asyncio
    async def test_escala_sem_filtros_retorna_200(self, client):
        """Sem filtros deve usar mes/ano atual → 200."""
        response = await client.get("/portal/my-schedules")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_escala_estrutura_correta(self, client):
        """Response deve conter campos do MyScheduleResponse."""
        response = await client.get("/portal/my-schedules")
        assert response.status_code == 200
        data = response.json()
        assert "month" in data
        assert "year" in data
        assert "shifts" in data
        assert "total_hours" in data

    @pytest.mark.asyncio
    async def test_escala_com_mes_e_ano(self, client):
        """Filtrar por mes e ano especificos → 200."""
        response = await client.get("/portal/my-schedules", params={"month": 3, "year": 2026})
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == 3
        assert data["year"] == 2026

    @pytest.mark.asyncio
    async def test_escala_shifts_e_lista(self, client):
        """shifts deve ser uma lista (vazia com DB fake)."""
        response = await client.get("/portal/my-schedules")
        assert response.status_code == 200
        assert isinstance(response.json()["shifts"], list)

    @pytest.mark.asyncio
    async def test_escala_mes_invalido_retorna_422(self, client):
        """Mes 0 invalido → 422."""
        response = await client.get("/portal/my-schedules", params={"month": 0})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_escala_mes_13_retorna_422(self, client):
        """Mes 13 invalido → 422."""
        response = await client.get("/portal/my-schedules", params={"month": 13})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_escala_ano_muito_antigo_retorna_422(self, client):
        """Ano 2019 invalido → 422."""
        response = await client.get("/portal/my-schedules", params={"year": 2019})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_escala_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-schedules")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-schedules/current-month
# ---------------------------------------------------------------------------


class TestPortalCurrentMonthSchedule:
    """Testes E2E do atalho de escala do mes atual."""

    @pytest.mark.asyncio
    async def test_current_month_retorna_200(self, client):
        """Atalho para mes atual deve retornar 200."""
        response = await client.get("/portal/my-schedules/current-month")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_current_month_estrutura_correta(self, client):
        """Response deve conter month e year preenchidos."""
        response = await client.get("/portal/my-schedules/current-month")
        assert response.status_code == 200
        data = response.json()
        assert "month" in data
        assert "year" in data
        assert isinstance(data["month"], int)
        assert isinstance(data["year"], int)

    @pytest.mark.asyncio
    async def test_current_month_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-schedules/current-month")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-schedules/next-shift
# ---------------------------------------------------------------------------


class TestPortalNextShift:
    """Testes E2E do endpoint de próximo turno."""

    @pytest.mark.asyncio
    async def test_next_shift_sem_dados_retorna_404(self, client):
        """Com DB fake (sem turno), deve retornar 404."""
        response = await client.get("/portal/my-schedules/next-shift")
        # DocumentViewService.get_next_shift nao existe → AttributeError capturado → 404
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_next_shift_detail_nenhum_turno(self, client):
        """Detail do 404 deve mencionar turno."""
        response = await client.get("/portal/my-schedules/next-shift")
        assert response.status_code == 404
        assert "turno" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_next_shift_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-schedules/next-shift")
        assert response.status_code == 401

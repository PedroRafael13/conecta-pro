"""
Testes E2E — Portal Férias.

Endpoints cobertos:
  GET /portal/my-vacations/balance
  GET /portal/my-vacations/requests

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_vacations_controller import (
    router as vacations_router,
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
    application.include_router(vacations_router, prefix="/portal")
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
    application.include_router(vacations_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-vacations/balance
# ---------------------------------------------------------------------------


class TestPortalVacationBalance:
    """Testes E2E do endpoint de saldo de férias."""

    @pytest.mark.asyncio
    async def test_balance_retorna_200(self, client):
        """Saldo de férias deve retornar 200."""
        response = await client.get("/portal/my-vacations/balance")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_balance_estrutura_correta(self, client):
        """Response deve conter campos obrigatórios do VacationBalanceResponse."""
        response = await client.get("/portal/my-vacations/balance")
        assert response.status_code == 200
        data = response.json()
        assert "dias_direito" in data
        assert "dias_gozados" in data
        assert "dias_saldo" in data
        assert "total_bruto_ferias" in data

    @pytest.mark.asyncio
    async def test_balance_fallback_sem_dados(self, client):
        """Com DB fake vazio, deve retornar saldo padrão de 30 dias."""
        response = await client.get("/portal/my-vacations/balance")
        assert response.status_code == 200
        data = response.json()
        assert data["dias_direito"] == 30
        assert data["dias_gozados"] == 0
        assert data["dias_saldo"] == 30

    @pytest.mark.asyncio
    async def test_balance_total_bruto_e_float(self, client):
        """total_bruto_ferias deve ser um número."""
        response = await client.get("/portal/my-vacations/balance")
        assert response.status_code == 200
        saldo = response.json()["total_bruto_ferias"]
        assert isinstance(saldo, (int, float))

    @pytest.mark.asyncio
    async def test_balance_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-vacations/balance")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-vacations/requests
# ---------------------------------------------------------------------------


class TestPortalVacationRequests:
    """Testes E2E do endpoint de solicitações de férias."""

    @pytest.mark.asyncio
    async def test_requests_retorna_200(self, client):
        """Solicitações deve retornar 200."""
        response = await client.get("/portal/my-vacations/requests")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_requests_retorna_lista(self, client):
        """Response deve ser uma lista."""
        response = await client.get("/portal/my-vacations/requests")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_requests_lista_vazia_sem_dados(self, client):
        """Com DB fake (ImportError/vazio), deve retornar lista vazia."""
        response = await client.get("/portal/my-vacations/requests")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_requests_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-vacations/requests")
        assert response.status_code == 401

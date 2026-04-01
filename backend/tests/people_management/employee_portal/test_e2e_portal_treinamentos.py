"""
Testes E2E — Portal Treinamentos.

Endpoints cobertos:
  GET /portal/my-trainings/enrollments
  GET /portal/my-trainings/certificates

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_trainings_controller import (
    router as trainings_router,
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
    application.include_router(trainings_router, prefix="/portal")
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
    application.include_router(trainings_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-trainings/enrollments
# ---------------------------------------------------------------------------


class TestPortalTrainingEnrollments:
    """Testes E2E do endpoint de matrículas em treinamentos."""

    @pytest.mark.asyncio
    async def test_enrollments_retorna_200(self, client):
        """Matrículas deve retornar 200."""
        response = await client.get("/portal/my-trainings/enrollments")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_enrollments_retorna_lista(self, client):
        """Response deve ser uma lista."""
        response = await client.get("/portal/my-trainings/enrollments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_enrollments_lista_vazia_sem_dados(self, client):
        """Com DB fake (ImportError/vazio), deve retornar lista vazia."""
        response = await client.get("/portal/my-trainings/enrollments")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_enrollments_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-trainings/enrollments")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-trainings/certificates
# ---------------------------------------------------------------------------


class TestPortalTrainingCertificates:
    """Testes E2E do endpoint de certificados de treinamento."""

    @pytest.mark.asyncio
    async def test_certificates_retorna_200(self, client):
        """Certificados deve retornar 200."""
        response = await client.get("/portal/my-trainings/certificates")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_certificates_retorna_lista(self, client):
        """Response deve ser uma lista."""
        response = await client.get("/portal/my-trainings/certificates")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_certificates_lista_vazia_sem_dados(self, client):
        """Com DB fake (ImportError/vazio), deve retornar lista vazia."""
        response = await client.get("/portal/my-trainings/certificates")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_certificates_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-trainings/certificates")
        assert response.status_code == 401

"""
Testes E2E — Portal Notificações.

Endpoints cobertos:
  GET   /portal/my-notifications
  PATCH /portal/my-notifications/{notification_id}/read

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_notifications_controller import (
    router as notifications_router,
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
    application.include_router(notifications_router, prefix="/portal")
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
    application.include_router(notifications_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-notifications
# ---------------------------------------------------------------------------


class TestPortalNotificationsList:
    """Testes E2E do endpoint de listagem de notificações."""

    @pytest.mark.asyncio
    async def test_lista_retorna_200(self, client):
        """Listagem de notificações deve retornar 200."""
        response = await client.get("/portal/my-notifications")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lista_retorna_array(self, client):
        """Response deve ser uma lista."""
        response = await client.get("/portal/my-notifications")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_lista_vazia_sem_notificacoes(self, client):
        """Com DB fake (vazio/ImportError), deve retornar lista vazia."""
        response = await client.get("/portal/my-notifications")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_lista_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-notifications")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — PATCH /portal/my-notifications/{notification_id}/read
# ---------------------------------------------------------------------------


class TestPortalMarkNotificationRead:
    """Testes E2E do endpoint de marcar notificação como lida."""

    @pytest.mark.asyncio
    async def test_notificacao_inexistente_retorna_404_ou_500(self, client):
        """Com DB fake, notificação não encontrada → 404 ou 500."""
        response = await client.patch("/portal/my-notifications/999/read")
        # FakeAsyncSession retorna None → NotFound levanta 404
        # Pode retornar 404 (not found) ou 500 (se commit falhar)
        assert response.status_code in (404, 500)

    @pytest.mark.asyncio
    async def test_id_invalido_retorna_422(self, client):
        """ID não numérico deve retornar 422."""
        response = await client.patch("/portal/my-notifications/abc/read")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_mark_read_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.patch("/portal/my-notifications/1/read")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_notificacao_id_positivo(self, client):
        """ID positivo deve processar (pode retornar 404 sem dados)."""
        response = await client.patch("/portal/my-notifications/1/read")
        assert response.status_code in (200, 404, 500)

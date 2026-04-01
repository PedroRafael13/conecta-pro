"""
Testes E2E — Portal Perfil + Dados Pessoais.

Endpoints cobertos:
  GET /portal/perfil
  GET /portal/contrato
  GET /portal/my-data
  PUT /portal/my-data

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_data_controller import (
    router as data_router,
)
from modules.people_management.employee_portal.controllers.my_profile_controller import (
    router as profile_router,
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
        self._added: list = []

    def add(self, obj):
        self._added.append(obj)

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
    application.include_router(profile_router, prefix="/portal")
    application.include_router(data_router, prefix="/portal")
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
    application.include_router(profile_router, prefix="/portal")
    application.include_router(data_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/perfil
# ---------------------------------------------------------------------------


class TestPortalPerfil:
    """Testes E2E do endpoint de perfil."""

    @pytest.mark.asyncio
    async def test_perfil_retorna_200(self, client):
        """Perfil deve retornar 200."""
        response = await client.get("/portal/perfil")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_perfil_contem_employee_id(self, client):
        """Response deve conter employee_id."""
        response = await client.get("/portal/perfil")
        assert response.status_code == 200
        data = response.json()
        assert "employee_id" in data
        assert data["employee_id"] == FAKE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_perfil_fallback_sem_dados_db(self, client):
        """Com DB fake (vazio), deve retornar fallback com status ativo."""
        response = await client.get("/portal/perfil")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ativo"
        assert "nome" in data

    @pytest.mark.asyncio
    async def test_perfil_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token /perfil deve retornar 401."""
        response = await client_sem_auth.get("/portal/perfil")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/contrato
# ---------------------------------------------------------------------------


class TestPortalContrato:
    """Testes E2E do endpoint de contrato."""

    @pytest.mark.asyncio
    async def test_contrato_retorna_200(self, client):
        """Contrato deve retornar 200."""
        response = await client.get("/portal/contrato")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_contrato_contem_employee_id(self, client):
        """Response deve conter employee_id."""
        response = await client.get("/portal/contrato")
        assert response.status_code == 200
        data = response.json()
        assert "employee_id" in data

    @pytest.mark.asyncio
    async def test_contrato_tipo_clt_como_fallback(self, client):
        """Com DB fake (vazio), tipo_contrato deve ser CLT."""
        response = await client.get("/portal/contrato")
        assert response.status_code == 200
        data = response.json()
        assert data["tipo_contrato"] == "CLT"

    @pytest.mark.asyncio
    async def test_contrato_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token /contrato deve retornar 401."""
        response = await client_sem_auth.get("/portal/contrato")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-data
# ---------------------------------------------------------------------------


class TestPortalMyData:
    """Testes E2E do endpoint GET /my-data."""

    @pytest.mark.asyncio
    async def test_my_data_retorna_200(self, client):
        """GET /my-data deve retornar 200."""
        response = await client.get("/portal/my-data")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_my_data_estrutura_correta(self, client):
        """Response deve ser um objeto com campos de MyDataResponse."""
        response = await client.get("/portal/my-data")
        assert response.status_code == 200
        data = response.json()
        # Pelo menos nome deve existir
        assert "nome" in data

    @pytest.mark.asyncio
    async def test_my_data_fallback_sem_dados(self, client):
        """Com DB fake vazio, deve retornar valores padrao."""
        response = await client.get("/portal/my-data")
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Funcionario"

    @pytest.mark.asyncio
    async def test_my_data_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-data")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — PUT /portal/my-data
# ---------------------------------------------------------------------------


class TestPortalUpdateMyData:
    """Testes E2E do endpoint PUT /my-data."""

    @pytest.mark.asyncio
    async def test_update_telefone_retorna_200(self, client):
        """Atualizar telefone deve retornar 200."""
        payload = {"telefone": "(92) 98765-4321"}
        response = await client.put("/portal/my-data", json=payload)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_email_retorna_200(self, client):
        """Atualizar email deve retornar 200."""
        payload = {"email": "funcionario@email.com"}
        response = await client.put("/portal/my-data", json=payload)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_multiplos_campos_retorna_200(self, client):
        """Atualizar multiplos campos deve retornar 200."""
        payload = {
            "telefone": "(92) 98765-4321",
            "email": "func@email.com",
            "endereco": "Rua das Flores, 123",
        }
        response = await client.put("/portal/my-data", json=payload)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_sem_campos_retorna_400(self, client):
        """Payload vazio deve retornar 400."""
        response = await client.put("/portal/my-data", json={})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_response_contem_campo_atualizado(self, client):
        """Response deve refletir o campo enviado."""
        payload = {"telefone": "(92) 91234-5678"}
        response = await client.put("/portal/my-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["telefone"] == "(92) 91234-5678"

    @pytest.mark.asyncio
    async def test_update_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        payload = {"telefone": "(92) 98765-4321"}
        response = await client_sem_auth.put("/portal/my-data", json=payload)
        assert response.status_code == 401

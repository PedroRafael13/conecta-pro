"""
Testes E2E — Portal Contracheques (Payslips).

Endpoints cobertos:
  GET /portal/my-payslips
  GET /portal/my-payslips/{month}/{year}
  GET /portal/my-payslips/{month}/{year}/pdf

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_payslips_controller import (
    router as payslips_router,
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
    application.include_router(payslips_router, prefix="/portal")
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
    application.include_router(payslips_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-payslips
# ---------------------------------------------------------------------------


class TestPortalPayslipsList:
    """Testes E2E do endpoint de listagem de contracheques."""

    @pytest.mark.asyncio
    async def test_lista_retorna_200(self, client):
        """Listagem deve retornar 200."""
        response = await client.get("/portal/my-payslips")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lista_retorna_array(self, client):
        """Response deve ser uma lista."""
        response = await client.get("/portal/my-payslips")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_lista_vazia_sem_funcionario(self, client):
        """Com DB fake (employee nao encontrado), lista deve ser vazia."""
        response = await client.get("/portal/my-payslips")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_lista_com_ano_valido(self, client):
        """Filtrar por ano valido deve retornar 200."""
        response = await client.get("/portal/my-payslips", params={"year": 2025})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lista_ano_invalido_retorna_422(self, client):
        """Ano fora do range deve retornar 422."""
        response = await client.get("/portal/my-payslips", params={"year": 2019})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_lista_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-payslips")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-payslips/{month}/{year}
# ---------------------------------------------------------------------------


class TestPortalPayslipByMonth:
    """Testes E2E do endpoint de contracheque especifico."""

    @pytest.mark.asyncio
    async def test_contracheque_nao_encontrado_retorna_404(self, client):
        """Com DB fake vazio, contracheque especifico → 404."""
        response = await client.get("/portal/my-payslips/3/2026")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_mes_invalido_retorna_422(self, client):
        """Mes 0 invalido → 422."""
        response = await client.get("/portal/my-payslips/0/2026")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_mes_13_retorna_422(self, client):
        """Mes 13 invalido → 422."""
        response = await client.get("/portal/my-payslips/13/2026")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ano_invalido_retorna_422(self, client):
        """Ano 2019 invalido → 422."""
        response = await client.get("/portal/my-payslips/3/2019")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_mes_e_ano_validos_retornam_404_sem_dados(self, client):
        """Mes e ano validos mas sem dados → 404."""
        response = await client.get("/portal/my-payslips/1/2025")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-payslips/3/2026")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-payslips/{month}/{year}/pdf
# ---------------------------------------------------------------------------


class TestPortalPayslipPdf:
    """Testes E2E do endpoint de PDF do contracheque."""

    @pytest.mark.asyncio
    async def test_pdf_nao_encontrado_retorna_404(self, client):
        """Com DB fake vazio, PDF do contracheque → 404."""
        response = await client.get("/portal/my-payslips/3/2026/pdf")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_pdf_mes_invalido_retorna_422(self, client):
        """Mes 0 invalido → 422."""
        response = await client.get("/portal/my-payslips/0/2026/pdf")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pdf_ano_invalido_retorna_422(self, client):
        """Ano 2019 invalido → 422."""
        response = await client.get("/portal/my-payslips/3/2019/pdf")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pdf_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-payslips/3/2026/pdf")
        assert response.status_code == 401

"""Testes E2E do SST - endpoints FastAPI com auth e DB override."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.auth.dependencies import get_current_active_user
from core.database import get_db
from modules.people_management.sst.controllers.sst_controller import router as sst_router


class _FakeResult:
    """Fake DB result for SST tests."""

    def __init__(self):
        self._rows = []

    def scalars(self):
        return self

    def all(self):
        return []

    def scalar(self):
        return 0

    def scalar_one_or_none(self):
        return None

    def fetchall(self):
        return []

    def keys(self):
        return []


class _FakeDB:
    """Fake async DB session for SST E2E tests."""

    async def execute(self, *args, **kwargs):
        return _FakeResult()

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

    def add(self, obj):
        pass


@pytest.fixture
def app():
    """App com auth + DB override para testes."""
    test_app = FastAPI()

    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    mock_user.email = "test@test.com"
    mock_user.is_active = True
    mock_user.role = "admin"

    test_app.dependency_overrides[get_current_active_user] = lambda: mock_user
    test_app.dependency_overrides[get_db] = lambda: _FakeDB()
    test_app.include_router(sst_router, prefix="/api/v1")
    return test_app


@pytest.fixture
async def client(app):
    """Client HTTP com auth e DB mockadas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestSSTDashboardE2E:
    """Testes E2E do dashboard SST."""

    @pytest.mark.asyncio
    async def test_dashboard(self, client):
        response = await client.get("/api/v1/sst/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_colaboradores" in data
        assert "risco_nr1" in data

    @pytest.mark.asyncio
    async def test_nr1_dashboard(self, client):
        response = await client.get("/api/v1/sst/nr1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "%" in data["indice_risco_geral"]  # Calculado dinamicamente

    @pytest.mark.asyncio
    async def test_pcmso_status(self, client):
        response = await client.get("/api/v1/sst/pcmso/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_colaboradores" in data
        assert "exames_realizados" in data

    @pytest.mark.asyncio
    async def test_ppra_status(self, client):
        response = await client.get("/api/v1/sst/ppra/status")
        assert response.status_code == 200
        data = response.json()
        assert "riscos_mapeados" in data
        assert "medidas_implementadas" in data


class TestSSTAfastamentosE2E:
    """Testes E2E de afastamentos."""

    @pytest.mark.asyncio
    async def test_listar_afastamentos(self, client):
        response = await client.get("/api/v1/sst/afastamentos")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "afastamentos" in data

    @pytest.mark.asyncio
    async def test_estabilidade_ativos(self, client):
        response = await client.get("/api/v1/sst/estabilidade/ativos")
        assert response.status_code == 200
        assert "total" in response.json()

    @pytest.mark.asyncio
    async def test_ajuda_medicamento_ativos(self, client):
        response = await client.get("/api/v1/sst/ajuda-medicamento/ativos")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "clausula_cct" in data


class TestSSTASOE2E:
    """Testes E2E de ASO."""

    @pytest.mark.asyncio
    async def test_listar_asos(self, client):
        response = await client.get("/api/v1/sst/aso")
        assert response.status_code == 200
        assert "total" in response.json()

    @pytest.mark.asyncio
    async def test_asos_vencendo(self, client):
        response = await client.get("/api/v1/sst/asos/vencendo?dias=30")
        assert response.status_code == 200


class TestSSTEPIE2E:
    """Testes E2E de EPI."""

    @pytest.mark.asyncio
    async def test_listar_epis(self, client):
        response = await client.get("/api/v1/sst/epi")
        assert response.status_code == 200
        assert "total" in response.json()


class TestSSTCatE2E:
    """Testes E2E de CAT."""

    @pytest.mark.asyncio
    async def test_listar_cats(self, client):
        response = await client.get("/api/v1/sst/cat")
        assert response.status_code == 200
        assert "total" in response.json()

    @pytest.mark.asyncio
    async def test_taxa_acidente(self, client):
        response = await client.get("/api/v1/sst/cat/taxa-acidente")
        assert response.status_code == 200
        assert "taxa_acidente_percentual" in response.json()


class TestSSTRiscoE2E:
    """Testes E2E de mapeamento de riscos."""

    @pytest.mark.asyncio
    async def test_listar_todos_riscos(self, client):
        response = await client.get("/api/v1/sst/riscos")
        assert response.status_code == 200
        assert "total" in response.json()

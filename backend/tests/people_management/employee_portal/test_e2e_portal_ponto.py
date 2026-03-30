"""
Testes E2E — Employee Portal Ponto e Banco de Horas.

Endpoints cobertos:
  GET /portal/ponto/historico  (mes, ano query params)
  GET /portal/banco-horas

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_ponto_controller import router as ponto_router

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
    """Resultado fake de SELECT — retorna lista vazia."""

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
    """AsyncSession minima que responde a execute() com lista vazia."""

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
    # The ponto router has no prefix — the aggregator mounts it under /portal
    application.include_router(ponto_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    application.dependency_overrides[get_portal_employee_id] = fake_employee_id
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/ponto/historico
# ---------------------------------------------------------------------------


class TestPortalPontoHistorico:
    """Testes E2E do endpoint de historico de ponto do portal."""

    @pytest.mark.asyncio
    async def test_historico_sem_params_retorna_200(self, client):
        """Happy path: sem filtros → usa mes/ano atual."""
        response = await client.get("/portal/ponto/historico")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_historico_retorna_estrutura_correta(self, client):
        """Verifica campos obrigatórios na resposta."""
        response = await client.get("/portal/ponto/historico")
        assert response.status_code == 200
        data = response.json()
        assert "employee_id" in data
        assert data["employee_id"] == FAKE_EMPLOYEE_ID
        assert "mes" in data
        assert "ano" in data
        assert "total_registros" in data
        assert "registros" in data
        assert isinstance(data["registros"], list)

    @pytest.mark.asyncio
    async def test_historico_com_mes_e_ano(self, client):
        """Happy path: filtrar por mes e ano específicos."""
        response = await client.get("/portal/ponto/historico", params={"mes": 3, "ano": 2026})
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == 3
        assert data["ano"] == 2026

    @pytest.mark.asyncio
    async def test_historico_com_mes_1_extremo_inferior(self, client):
        """Limite inferior do mes (1 = Janeiro)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 1, "ano": 2026})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_historico_com_mes_12_extremo_superior(self, client):
        """Limite superior do mes (12 = Dezembro)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 12, "ano": 2026})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_historico_registros_vazios_quando_sem_dados(self, client):
        """Com DB fake (vazio), total_registros deve ser 0."""
        response = await client.get("/portal/ponto/historico", params={"mes": 3, "ano": 2026})
        assert response.status_code == 200
        data = response.json()
        assert data["total_registros"] == 0
        assert data["registros"] == []

    @pytest.mark.asyncio
    async def test_historico_mes_invalido_retorna_422(self, client):
        """Mes 0 é inválido (ge=1)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 0, "ano": 2026})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_historico_mes_13_retorna_422(self, client):
        """Mes 13 é inválido (le=12)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 13, "ano": 2026})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_historico_ano_muito_antigo_retorna_422(self, client):
        """Ano 2019 é inválido (ge=2020)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 3, "ano": 2019})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_historico_ano_muito_futuro_retorna_422(self, client):
        """Ano 2031 é inválido (le=2030)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 3, "ano": 2031})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_historico_apenas_mes_sem_ano(self, client):
        """Só o mes informado: ano usa padrão (ano atual)."""
        response = await client.get("/portal/ponto/historico", params={"mes": 6})
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == 6

    @pytest.mark.asyncio
    async def test_historico_apenas_ano_sem_mes(self, client):
        """Só o ano informado: mes usa padrão (mes atual)."""
        response = await client.get("/portal/ponto/historico", params={"ano": 2026})
        assert response.status_code == 200
        data = response.json()
        assert data["ano"] == 2026

    @pytest.mark.asyncio
    async def test_historico_employee_id_corresponde_ao_autenticado(self, client):
        """O employee_id retornado deve ser o do token (fake)."""
        response = await client.get("/portal/ponto/historico")
        assert response.status_code == 200
        assert response.json()["employee_id"] == FAKE_EMPLOYEE_ID


# ---------------------------------------------------------------------------
# TESTES — GET /portal/banco-horas
# ---------------------------------------------------------------------------


class TestPortalBancoHoras:
    """Testes E2E do endpoint de banco de horas do portal."""

    @pytest.mark.asyncio
    async def test_banco_horas_retorna_200(self, client):
        """Happy path: endpoint responde com sucesso."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_banco_horas_estrutura_correta(self, client):
        """Verifica campos obrigatórios na resposta."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200
        data = response.json()
        assert "employee_id" in data
        assert "saldo_horas" in data
        assert "total_entradas" in data
        assert "ultimas_entradas" in data

    @pytest.mark.asyncio
    async def test_banco_horas_employee_id_correto(self, client):
        """O employee_id retornado deve ser o do token autenticado."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200
        assert response.json()["employee_id"] == FAKE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_banco_horas_saldo_zero_sem_dados(self, client):
        """Com DB fake (vazio), saldo deve ser 0.0."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200
        data = response.json()
        assert data["saldo_horas"] == 0.0
        assert data["total_entradas"] == 0
        assert data["ultimas_entradas"] == []

    @pytest.mark.asyncio
    async def test_banco_horas_ultimas_entradas_e_lista(self, client):
        """ultimas_entradas deve ser uma lista."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200
        assert isinstance(response.json()["ultimas_entradas"], list)

    @pytest.mark.asyncio
    async def test_banco_horas_sem_query_params(self, client):
        """Endpoint não aceita nenhum query param obrigatório."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_banco_horas_saldo_e_float(self, client):
        """saldo_horas deve ser um número (float/int)."""
        response = await client.get("/portal/banco-horas")
        assert response.status_code == 200
        saldo = response.json()["saldo_horas"]
        assert isinstance(saldo, (int, float))


# ---------------------------------------------------------------------------
# TESTES — SEM AUTH (override removido)
# ---------------------------------------------------------------------------


class TestPortalPontoSemAuth:
    """Valida que sem token o portal retorna 401."""

    @pytest.fixture
    def app_sem_override(self):
        """App sem override de autenticação — usa auth real."""
        application = FastAPI()
        application.include_router(ponto_router, prefix="/portal")
        application.dependency_overrides[get_db] = get_fake_db
        # NÃO sobrescreve get_portal_employee_id
        return application

    @pytest.fixture
    async def client_sem_auth(self, app_sem_override):
        transport = ASGITransport(app=app_sem_override)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_historico_sem_token_retorna_401(self, client_sem_auth):
        """Sem Bearer token o portal deve retornar 401."""
        response = await client_sem_auth.get("/portal/ponto/historico")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_banco_horas_sem_token_retorna_401(self, client_sem_auth):
        """Sem Bearer token o portal deve retornar 401."""
        response = await client_sem_auth.get("/portal/banco-horas")
        assert response.status_code == 401

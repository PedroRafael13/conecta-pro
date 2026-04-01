"""
Testes E2E — Portal CCT Direitos + Benefícios + Comunicados.

Endpoints cobertos:
  GET  /portal/my-benefits
  GET  /portal/comunicados
  GET  /portal/cct/direitos
  POST /portal/cct/calculadora
  GET  /portal/cct/feriados
  GET  /portal/cct/adicional-noturno

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_benefits_controller import (
    router as benefits_router,
)
from modules.people_management.employee_portal.controllers.my_cct_controller import (
    router as cct_router,
)
from modules.people_management.employee_portal.controllers.my_comunicados_controller import (
    router as comunicados_router,
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
    application.include_router(benefits_router, prefix="/portal")
    application.include_router(comunicados_router, prefix="/portal")
    application.include_router(cct_router, prefix="/portal")
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
    application.include_router(benefits_router, prefix="/portal")
    application.include_router(comunicados_router, prefix="/portal")
    application.include_router(cct_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-benefits
# ---------------------------------------------------------------------------


class TestPortalBeneficios:
    """Testes E2E do endpoint de benefícios."""

    @pytest.mark.asyncio
    async def test_beneficios_retorna_200(self, client):
        """Benefícios deve retornar 200."""
        response = await client.get("/portal/my-benefits")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_beneficios_estrutura_correta(self, client):
        """Response deve conter campos obrigatórios."""
        response = await client.get("/portal/my-benefits")
        assert response.status_code == 200
        data = response.json()
        assert "employee_id" in data
        assert "beneficios_ativos" in data
        assert "beneficios_cct" in data
        assert "cct" in data

    @pytest.mark.asyncio
    async def test_beneficios_employee_id_correto(self, client):
        """employee_id deve ser o do funcionário autenticado."""
        response = await client.get("/portal/my-benefits")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == FAKE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_beneficios_cct_e_lista(self, client):
        """beneficios_cct deve ser uma lista."""
        response = await client.get("/portal/my-benefits")
        assert response.status_code == 200
        assert isinstance(response.json()["beneficios_cct"], list)

    @pytest.mark.asyncio
    async def test_beneficios_cct_vigente(self, client):
        """cct deve mencionar SINDECOMPRESTS."""
        response = await client.get("/portal/my-benefits")
        assert response.status_code == 200
        assert "SINDECOMPRESTS" in response.json()["cct"]

    @pytest.mark.asyncio
    async def test_beneficios_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-benefits")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/comunicados
# ---------------------------------------------------------------------------


class TestPortalComunicados:
    """Testes E2E do endpoint de comunicados."""

    @pytest.mark.asyncio
    async def test_comunicados_retorna_200(self, client):
        """Comunicados deve retornar 200."""
        response = await client.get("/portal/comunicados")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_comunicados_estrutura_correta(self, client):
        """Response deve conter total e lista de comunicados."""
        response = await client.get("/portal/comunicados")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "comunicados" in data
        assert isinstance(data["comunicados"], list)

    @pytest.mark.asyncio
    async def test_comunicados_fallback_boas_vindas(self, client):
        """Sem notificações no DB, deve retornar mensagem de boas-vindas."""
        response = await client.get("/portal/comunicados")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["comunicados"]) >= 1

    @pytest.mark.asyncio
    async def test_comunicados_total_consistente(self, client):
        """total deve ser igual ao len(comunicados)."""
        response = await client.get("/portal/comunicados")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(data["comunicados"])

    @pytest.mark.asyncio
    async def test_comunicados_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/comunicados")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/cct/direitos
# ---------------------------------------------------------------------------


class TestPortalCctDireitos:
    """Testes E2E do endpoint de direitos CCT."""

    @pytest.mark.asyncio
    async def test_direitos_retorna_200(self, client):
        """Direitos CCT deve retornar 200."""
        response = await client.get("/portal/cct/direitos")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_direitos_estrutura_correta(self, client):
        """Response deve conter cct, funcionario, beneficios_garantidos, adicionais."""
        response = await client.get("/portal/cct/direitos")
        assert response.status_code == 200
        data = response.json()
        assert "cct" in data
        assert "funcionario" in data
        assert "beneficios_garantidos" in data
        assert "adicionais" in data

    @pytest.mark.asyncio
    async def test_direitos_cct_vigencia(self, client):
        """cct deve conter informações de vigência."""
        response = await client.get("/portal/cct/direitos")
        assert response.status_code == 200
        cct = response.json()["cct"]
        assert "nome" in cct
        assert "vigencia" in cct

    @pytest.mark.asyncio
    async def test_direitos_escala_proibida(self, client):
        """Response deve informar sobre escala proibida (2x1 TAC MPT)."""
        response = await client.get("/portal/cct/direitos")
        assert response.status_code == 200
        data = response.json()
        assert "escala_proibida" in data

    @pytest.mark.asyncio
    async def test_direitos_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/cct/direitos")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — POST /portal/cct/calculadora
# ---------------------------------------------------------------------------


class TestPortalCctCalculadora:
    """Testes E2E do endpoint de calculadora rescisória."""

    @pytest.mark.asyncio
    async def test_calculadora_sem_justa_causa_retorna_200(self, client):
        """Motivo sem_justa_causa (default) → 200."""
        response = await client.post("/portal/cct/calculadora")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_calculadora_justa_causa_retorna_200(self, client):
        """Motivo justa_causa → 200."""
        response = await client.post("/portal/cct/calculadora", params={"motivo": "justa_causa"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_calculadora_pedido_demissao_retorna_200(self, client):
        """Motivo pedido_demissao → 200."""
        response = await client.post("/portal/cct/calculadora", params={"motivo": "pedido_demissao"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_calculadora_estrutura_correta(self, client):
        """Response deve conter campos da simulação."""
        response = await client.post("/portal/cct/calculadora")
        assert response.status_code == 200
        data = response.json()
        assert "simulacao_data" in data
        assert "motivo" in data
        assert "salario_base" in data
        assert "rescisao" in data

    @pytest.mark.asyncio
    async def test_calculadora_aviso_presente(self, client):
        """Response deve conter aviso de simulação."""
        response = await client.post("/portal/cct/calculadora")
        assert response.status_code == 200
        assert "aviso" in response.json()

    @pytest.mark.asyncio
    async def test_calculadora_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.post("/portal/cct/calculadora")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/cct/feriados
# ---------------------------------------------------------------------------


class TestPortalCctFeriados:
    """Testes E2E do endpoint de feriados 2026."""

    @pytest.mark.asyncio
    async def test_feriados_retorna_200(self, client):
        """Feriados deve retornar 200."""
        response = await client.get("/portal/cct/feriados")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_feriados_estrutura_correta(self, client):
        """Response deve conter total, ano, municipio e lista de feriados."""
        response = await client.get("/portal/cct/feriados")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "ano" in data
        assert "municipio" in data
        assert "feriados" in data
        assert isinstance(data["feriados"], list)

    @pytest.mark.asyncio
    async def test_feriados_ano_2026(self, client):
        """Ano deve ser 2026."""
        response = await client.get("/portal/cct/feriados")
        assert response.status_code == 200
        assert response.json()["ano"] == 2026

    @pytest.mark.asyncio
    async def test_feriados_municipio_manaus(self, client):
        """Municipio deve ser Manaus/AM."""
        response = await client.get("/portal/cct/feriados")
        assert response.status_code == 200
        assert "Manaus" in response.json()["municipio"]

    @pytest.mark.asyncio
    async def test_feriados_com_filtro_mes(self, client):
        """Filtro por mes deve retornar apenas feriados do mes."""
        response = await client.get("/portal/cct/feriados", params={"mes": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(data["feriados"])

    @pytest.mark.asyncio
    async def test_feriados_mes_invalido_retorna_422(self, client):
        """Mes 0 invalido → 422."""
        response = await client.get("/portal/cct/feriados", params={"mes": 0})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_feriados_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/cct/feriados")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/cct/adicional-noturno
# ---------------------------------------------------------------------------


class TestPortalCctAdicionalNoturno:
    """Testes E2E do endpoint de adicional noturno."""

    @pytest.mark.asyncio
    async def test_adicional_noturno_retorna_200(self, client):
        """Adicional noturno deve retornar 200."""
        response = await client.get("/portal/cct/adicional-noturno")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_adicional_noturno_estrutura_correta(self, client):
        """Response deve conter campo explicacao."""
        response = await client.get("/portal/cct/adicional-noturno")
        assert response.status_code == 200
        data = response.json()
        assert "explicacao" in data

    @pytest.mark.asyncio
    async def test_adicional_noturno_com_horas_personalizadas(self, client):
        """Parametro horas_noturnas deve ser aceito."""
        response = await client.get("/portal/cct/adicional-noturno", params={"horas_noturnas": 12})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_adicional_noturno_horas_zero(self, client):
        """horas_noturnas=0 deve retornar 200."""
        response = await client.get("/portal/cct/adicional-noturno", params={"horas_noturnas": 0})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_adicional_noturno_horas_negativas_retorna_422(self, client):
        """horas_noturnas negativo invalido → 422 (ge=0)."""
        response = await client.get("/portal/cct/adicional-noturno", params={"horas_noturnas": -1})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_adicional_noturno_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/cct/adicional-noturno")
        assert response.status_code == 401

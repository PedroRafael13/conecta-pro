"""
Testes E2E — Portal Auth Controller.

Endpoints cobertos:
  POST /portal/auth/login
  POST /portal/auth/primeiro-acesso
  POST /portal/auth/reset-senha
  POST /portal/auth/refresh
  POST /portal/auth/logout
  GET  /portal/auth/me
  GET  /portal/dashboard

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import (
    create_portal_access_token,
    create_portal_refresh_token,
    get_portal_employee_id,
)
from modules.people_management.employee_portal.controllers.portal_controller import (
    router as portal_router,
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
    application.include_router(portal_router, prefix="/portal")
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
    application.include_router(portal_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — POST /portal/auth/login
# ---------------------------------------------------------------------------


class TestPortalLogin:
    """Testes E2E do endpoint de login do portal."""

    @pytest.mark.asyncio
    async def test_login_sem_credenciais_retorna_400(self, client):
        """Sem senha e sem data_nascimento deve retornar 400."""
        payload = {"cpf": "12345678901"}
        response = await client.post("/portal/auth/login", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_cpf_curto_retorna_422(self, client):
        """CPF com menos de 11 caracteres deve retornar 422."""
        payload = {"cpf": "1234567", "password": "senha123"}  # pragma: allowlist secret
        response = await client.post("/portal/auth/login", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_credenciais_invalidas_retorna_401(self, client):
        """Service retorna None (funcionario nao encontrado) → 401."""
        with patch(
            "modules.people_management.employee_portal.controllers.portal_controller.PortalService"
        ) as mock_svc_cls:
            mock_svc = AsyncMock()
            mock_svc.authenticate_employee.return_value = None
            mock_svc_cls.return_value = mock_svc

            payload = {"cpf": "12345678901", "password": "senhaerrada"}  # pragma: allowlist secret
            response = await client.post("/portal/auth/login", json=payload)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_valido_retorna_200(self, client):
        """Credenciais validas → 200 com access_token."""
        with patch(
            "modules.people_management.employee_portal.controllers.portal_controller.PortalService"
        ) as mock_svc_cls:
            mock_svc = AsyncMock()
            mock_svc.authenticate_employee.return_value = {
                "employee_id": FAKE_EMPLOYEE_ID,
                "nome": "Joao Silva",
                "cargo": "Vigilante",
                "cpf": "12345678901",
                "escala": "12x36",
            }
            mock_svc_cls.return_value = mock_svc

            payload = {"cpf": "12345678901", "password": "senha123"}  # pragma: allowlist secret
            response = await client.post("/portal/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "employee_id" in data

    @pytest.mark.asyncio
    async def test_login_com_data_nascimento_retorna_200(self, client):
        """Login via CPF + data_nascimento deve funcionar."""
        with patch(
            "modules.people_management.employee_portal.controllers.portal_controller.PortalService"
        ) as mock_svc_cls:
            mock_svc = AsyncMock()
            mock_svc.authenticate_employee.return_value = {
                "employee_id": FAKE_EMPLOYEE_ID,
                "nome": "Maria Souza",
                "cargo": "Vigilante",
                "cpf": "98765432109",
                "escala": "12x36",
            }
            mock_svc_cls.return_value = mock_svc

            payload = {"cpf": "98765432109", "data_nascimento": "1990-05-15"}
            response = await client.post("/portal/auth/login", json=payload)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_resposta_contem_campos_obrigatorios(self, client):
        """Response deve conter access_token, employee_id e employee_name."""
        with patch(
            "modules.people_management.employee_portal.controllers.portal_controller.PortalService"
        ) as mock_svc_cls:
            mock_svc = AsyncMock()
            mock_svc.authenticate_employee.return_value = {
                "employee_id": FAKE_EMPLOYEE_ID,
                "nome": "Carlos Lima",
                "cargo": "Supervisor",
                "cpf": "11122233344",
                "escala": "12x36",
            }
            mock_svc_cls.return_value = mock_svc

            payload = {"cpf": "11122233344", "password": "senha123"}  # pragma: allowlist secret
            response = await client.post("/portal/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "employee_id" in data
        assert "employee_name" in data
        assert "expires_in" in data


# ---------------------------------------------------------------------------
# TESTES — POST /portal/auth/primeiro-acesso
# ---------------------------------------------------------------------------


class TestPortalPrimeiroAcesso:
    """Testes E2E do endpoint de primeiro acesso."""

    @pytest.mark.asyncio
    async def test_sem_cpf_retorna_400(self, client):
        """CPF ausente deve retornar 400."""
        payload = {"nova_senha": "senha123", "confirmar_senha": "senha123"}  # pragma: allowlist secret
        response = await client.post("/portal/auth/primeiro-acesso", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_sem_nova_senha_retorna_400(self, client):
        """nova_senha ausente deve retornar 400."""
        payload = {"cpf": "12345678901"}
        response = await client.post("/portal/auth/primeiro-acesso", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_senha_curta_retorna_400(self, client):
        """Senha com menos de 6 caracteres deve retornar 400."""
        payload = {"cpf": "12345678901", "nova_senha": "abc", "confirmar_senha": "abc"}  # pragma: allowlist secret
        response = await client.post("/portal/auth/primeiro-acesso", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_senhas_diferentes_retorna_400(self, client):
        """nova_senha diferente de confirmar_senha deve retornar 400."""
        payload = {
            "cpf": "12345678901",
            "nova_senha": "senha123",  # pragma: allowlist secret
            "confirmar_senha": "outrasenha",  # pragma: allowlist secret
        }
        response = await client.post("/portal/auth/primeiro-acesso", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_funcionario_nao_encontrado_retorna_404(self, client):
        """CPF sem funcionario ativo no DB fake → 404."""
        payload = {
            "cpf": "12345678901",
            "nova_senha": "senha123",  # pragma: allowlist secret
            "confirmar_senha": "senha123",  # pragma: allowlist secret
        }
        response = await client.post("/portal/auth/primeiro-acesso", json=payload)
        # FakeAsyncSession retorna None para employee → 404
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# TESTES — POST /portal/auth/reset-senha
# ---------------------------------------------------------------------------


class TestPortalResetSenha:
    """Testes E2E do endpoint de reset de senha."""

    @pytest.mark.asyncio
    async def test_sem_cpf_retorna_400(self, client):
        payload = {"nova_senha": "senha123", "confirmar_senha": "senha123"}  # pragma: allowlist secret
        response = await client.post("/portal/auth/reset-senha", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_sem_nova_senha_retorna_400(self, client):
        payload = {"cpf": "12345678901"}
        response = await client.post("/portal/auth/reset-senha", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_senha_curta_retorna_400(self, client):
        payload = {"cpf": "12345678901", "nova_senha": "12", "confirmar_senha": "12"}  # pragma: allowlist secret
        response = await client.post("/portal/auth/reset-senha", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_senhas_diferentes_retorna_400(self, client):
        payload = {
            "cpf": "12345678901",
            "nova_senha": "senha123",  # pragma: allowlist secret
            "confirmar_senha": "diferente",  # pragma: allowlist secret
        }
        response = await client.post("/portal/auth/reset-senha", json=payload)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_funcionario_nao_encontrado_retorna_404(self, client):
        payload = {
            "cpf": "12345678901",
            "nova_senha": "senha123",  # pragma: allowlist secret
            "confirmar_senha": "senha123",  # pragma: allowlist secret
        }
        response = await client.post("/portal/auth/reset-senha", json=payload)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# TESTES — POST /portal/auth/refresh
# ---------------------------------------------------------------------------


class TestPortalRefresh:
    """Testes E2E do endpoint de refresh de token."""

    @pytest.mark.asyncio
    async def test_sem_token_retorna_401(self, client):
        """Sem Authorization header deve retornar 401."""
        response = await client.post("/portal/auth/refresh")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_invalido_retorna_401(self, client):
        """Token invalido deve retornar 401."""
        response = await client.post(
            "/portal/auth/refresh",
            headers={"Authorization": "Bearer token.invalido.aqui"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_valido_retorna_200(self, client):
        """Refresh token valido deve retornar novos tokens."""
        refresh_token = create_portal_refresh_token(FAKE_EMPLOYEE_ID)
        response = await client.post(
            "/portal/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 8 * 3600

    @pytest.mark.asyncio
    async def test_refresh_com_access_token_retorna_401(self, client):
        """Access token nao pode ser usado no refresh (tipo errado)."""
        access_token = create_portal_access_token(FAKE_EMPLOYEE_ID, "Joao", "Vigilante")
        response = await client.post(
            "/portal/auth/refresh",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — POST /portal/auth/logout
# ---------------------------------------------------------------------------


class TestPortalLogout:
    """Testes E2E do endpoint de logout."""

    @pytest.mark.asyncio
    async def test_logout_autenticado_retorna_200(self, client):
        """Logout com auth override → 200."""
        response = await client.post("/portal/auth/logout")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_mensagem_sucesso(self, client):
        """Response deve conter mensagem de sucesso."""
        response = await client.post("/portal/auth/logout")
        assert response.status_code == 200
        assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_logout_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token o logout deve retornar 401."""
        response = await client_sem_auth.post("/portal/auth/logout")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/auth/me
# ---------------------------------------------------------------------------


class TestPortalMe:
    """Testes E2E do endpoint /auth/me."""

    @pytest.mark.asyncio
    async def test_me_retorna_200(self, client):
        """Endpoint /auth/me deve retornar 200."""
        response = await client.get("/portal/auth/me")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_me_retorna_employee_id(self, client):
        """Response deve conter employee_id do token."""
        response = await client.get("/portal/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "employee_id" in data
        assert data["employee_id"] == FAKE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_me_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token /auth/me deve retornar 401."""
        response = await client_sem_auth.get("/portal/auth/me")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/dashboard
# ---------------------------------------------------------------------------


class TestPortalDashboard:
    """Testes E2E do endpoint de dashboard."""

    @pytest.mark.asyncio
    async def test_dashboard_retorna_200(self, client):
        """Dashboard deve retornar 200."""
        response = await client.get("/portal/dashboard")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dashboard_estrutura_correta(self, client):
        """Response deve conter campos do PortalDashboard."""
        response = await client.get("/portal/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "pending_documents" in data
        assert "unread_notifications" in data

    @pytest.mark.asyncio
    async def test_dashboard_valores_padrao_sem_dados(self, client):
        """Com DB fake (vazio), campos numericos devem ser 0."""
        response = await client.get("/portal/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["pending_documents"] == 0
        assert data["unread_notifications"] == 0

    @pytest.mark.asyncio
    async def test_dashboard_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token o dashboard deve retornar 401."""
        response = await client_sem_auth.get("/portal/dashboard")
        assert response.status_code == 401

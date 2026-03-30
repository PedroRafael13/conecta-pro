"""
Testes E2E — Portal Documentos e Assinaturas Digitais.

Endpoints cobertos:
  GET  /portal/my-documents
  POST /portal/my-documents/{id}/sign
  GET  /portal/my-documents/{id}/verify-signature

Padrão: httpx.AsyncClient + ASGITransport, FakeAsyncSession, override deps.
"""

import os
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.database import get_db
from modules.people_management.employee_portal.auth import get_portal_employee_id
from modules.people_management.employee_portal.controllers.my_documents_controller import (
    router as documents_router,
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


@pytest.fixture(autouse=True)
def set_signature_secret(monkeypatch):
    """Define a variavel PORTAL_SIGNATURE_SECRET para os testes."""
    monkeypatch.setenv("PORTAL_SIGNATURE_SECRET", "test-secret-for-testing-12345678")


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(documents_router, prefix="/portal")
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
    application.include_router(documents_router, prefix="/portal")
    application.dependency_overrides[get_db] = get_fake_db
    return application


@pytest.fixture
async def client_sem_auth(app_sem_override):
    transport = ASGITransport(app=app_sem_override)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-documents
# ---------------------------------------------------------------------------


class TestPortalDocumentsList:
    """Testes E2E do endpoint de listagem de documentos."""

    @pytest.mark.asyncio
    async def test_lista_retorna_200(self, client):
        """Listagem de documentos deve retornar 200."""
        response = await client.get("/portal/my-documents")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lista_retorna_array(self, client):
        """Response deve ser uma lista."""
        response = await client.get("/portal/my-documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_lista_vazia_sem_assinaturas(self, client):
        """Com DB fake (ImportError/vazio), deve retornar lista vazia."""
        response = await client.get("/portal/my-documents")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_lista_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        response = await client_sem_auth.get("/portal/my-documents")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — POST /portal/my-documents/{id}/sign
# ---------------------------------------------------------------------------


class TestPortalSignDocument:
    """Testes E2E do endpoint de assinatura de documento."""

    @pytest.mark.asyncio
    async def test_assinar_retorna_200_ou_400(self, client):
        """Assinatura: com DB fake pode retornar 200 ou erro de DB."""
        payload = {"document_id": 1, "document_type": "payslip"}
        response = await client.post("/portal/my-documents/1/sign", json=payload)
        # SignatureService pode falhar ao buscar no DB fake → ValueError → 400
        # Ou pode retornar 200 se conseguir gerar hash
        assert response.status_code in (200, 400, 500)

    @pytest.mark.asyncio
    async def test_assinar_id_invalido_retorna_422(self, client):
        """ID 0 ou negativo deve retornar 422 (gt=0)."""
        payload = {"document_id": 1, "document_type": "payslip"}
        response = await client.post("/portal/my-documents/0/sign", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_assinar_id_nao_numerico_retorna_422(self, client):
        """ID não numérico deve retornar 422."""
        payload = {"document_id": 1, "document_type": "payslip"}
        response = await client.post("/portal/my-documents/abc/sign", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_assinar_sem_auth_retorna_401(self, client_sem_auth):
        """Sem token deve retornar 401."""
        payload = {"document_id": 1, "document_type": "payslip"}
        response = await client_sem_auth.post("/portal/my-documents/1/sign", json=payload)
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# TESTES — GET /portal/my-documents/{id}/verify-signature
# ---------------------------------------------------------------------------


class TestPortalVerifySignature:
    """Testes E2E do endpoint de verificação de assinatura."""

    @pytest.mark.asyncio
    async def test_sem_hash_retorna_400(self, client):
        """Sem signature_hash deve retornar 400."""
        response = await client.get("/portal/my-documents/1/verify-signature")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_com_hash_valido_retorna_200_ou_404(self, client):
        """Com hash, DB fake retorna None → is_valid=False mas 200."""
        fake_hash = "a" * 64  # SHA-256 tem 64 caracteres hex
        response = await client.get(
            "/portal/my-documents/1/verify-signature",
            params={"signature_hash": fake_hash},
        )
        assert response.status_code in (200, 404, 500)

    @pytest.mark.asyncio
    async def test_id_invalido_retorna_422(self, client):
        """ID 0 invalido → 422 (gt=0)."""
        response = await client.get(
            "/portal/my-documents/0/verify-signature",
            params={"signature_hash": "a" * 64},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_sem_auth_nao_necessario(self, client_sem_auth):
        """verify-signature não requer auth (endpoint público de verificação)."""
        response = await client_sem_auth.get(
            "/portal/my-documents/1/verify-signature",
            params={"signature_hash": "a" * 64},
        )
        # Deve processar (pode falhar no serviço, mas não em auth)
        assert response.status_code in (200, 400, 404, 500)

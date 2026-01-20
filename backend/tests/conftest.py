"""
Configuração global de testes - Conecta PRO.

Fixtures compartilhadas para todos os testes.
Usa mocks para evitar dependência de banco de dados real.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Importa app apenas se disponivel (evita erros de dependencia)
try:
    from main import app
    _main_app_available = True
except ImportError:
    app = None
    _main_app_available = False


# ==========================================================================
# Event Loop
# ==========================================================================
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==========================================================================
# Mock Database Session
# ==========================================================================
@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


# ==========================================================================
# HTTP Client Fixtures
# ==========================================================================
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    if not _main_app_available or app is None:
        pytest.skip("main app not available")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """Create authenticated client with test token."""
    # Token JWT válido para testes (expira em 2099)
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAZXJwLmNvbS5iciIsInJvbGUiOiJhZG1pbiIsImV4cCI6NDA3MDkwODgwMH0.test-signature"
    client.headers["Authorization"] = f"Bearer {test_token}"
    return client


# ==========================================================================
# Mock Fixtures
# ==========================================================================
@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    service = MagicMock()
    service.send_email = AsyncMock(return_value=True)
    return service


# ==========================================================================
# Test Data Fixtures
# ==========================================================================
@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "id": str(uuid4()),
        "email": "test@erp.com.br",
        "nome": "Test User",
        "role": "admin",
        "ativo": True,
    }


@pytest.fixture
def test_lead_data():
    """Test lead data."""
    return {
        "nome": "Lead Teste",
        "email": "lead@teste.com.br",
        "telefone": "11999999999",
        "empresa": "Empresa Teste",
        "origem": "website",
        "status": "novo",
    }


@pytest.fixture
def test_client_data():
    """Test client/condominium data."""
    return {
        "id": str(uuid4()),
        "nome": "Condomínio Teste",
        "cnpj": "12345678000190",
        "endereco": "Rua Teste, 123",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234567",
        "ativo": True,
    }


# ==========================================================================
# Utility Functions
# ==========================================================================
def assert_response_ok(response, expected_status=200):
    """Assert response is successful."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"


def assert_response_error(response, expected_status=400):
    """Assert response is an error."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"

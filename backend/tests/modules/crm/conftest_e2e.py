"""
Fixtures compartilhadas para testes E2E do módulo CRM.

Padrão de uso:
    - crm_client: AsyncClient autenticado + dependency_overrides para auth
    - _make_lead() / _make_opportunity() / etc: objetos mock com atributos reais
    - Mockar repositório no nível do controller: patch("modules.crm.controllers.X.XRepository")
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime(2026, 3, 30, 12, 0, 0)


def _make_mock_user() -> MagicMock:
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@erp.com.br"
    user.role = "admin"
    user.is_active = True
    return user


# ---------------------------------------------------------------------------
# Mock builders — objetos com atributos tipados para model_validate()
# ---------------------------------------------------------------------------


def make_lead_mock(**kwargs) -> MagicMock:
    """Retorna mock de Lead com todos os atributos obrigatórios."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.name = kwargs.get("name", "João Silva")
    m.email = kwargs.get("email", "joao@empresa.com.br")
    m.phone = kwargs.get("phone")
    m.company = kwargs.get("company", "Empresa Teste")
    m.position = kwargs.get("position")
    m.company_size = kwargs.get("company_size")
    m.industry = kwargs.get("industry")
    m.source = kwargs.get("source", "website")
    m.status = kwargs.get("status", "new")
    m.score = kwargs.get("score", 40)
    m.probability = kwargs.get("probability", 0.4)
    m.expected_value = kwargs.get("expected_value", 10000.0)
    m.notes = kwargs.get("notes")
    m.assigned_to_id = kwargs.get("assigned_to_id")
    m.assigned_to = kwargs.get("assigned_to")
    m.last_contact_at = kwargs.get("last_contact_at")
    m.next_contact_at = kwargs.get("next_contact_at")
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    # Computed properties
    m.is_hot = kwargs.get("is_hot", False)
    m.is_qualified = kwargs.get("is_qualified", False)
    m.weighted_value = kwargs.get("weighted_value", 4000.0)
    return m


def make_opportunity_mock(**kwargs) -> MagicMock:
    """Retorna mock de Opportunity com todos os atributos obrigatórios."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.title = kwargs.get("title", "Oportunidade Teste")
    m.description = kwargs.get("description")
    m.lead_id = kwargs.get("lead_id")
    m.contact_name = kwargs.get("contact_name", "Maria Santos")
    m.contact_email = kwargs.get("contact_email", "maria@empresa.com.br")
    m.contact_phone = kwargs.get("contact_phone")
    m.company_name = kwargs.get("company_name", "Empresa Segurança")
    m.stage = kwargs.get("stage", "qualification")
    m.priority = kwargs.get("priority", "medium")
    m.value = kwargs.get("value", 50000.0)
    m.probability = kwargs.get("probability", 25)
    m.expected_close_date = kwargs.get("expected_close_date")
    m.actual_close_date = kwargs.get("actual_close_date")
    m.owner_id = kwargs.get("owner_id")
    m.owner = kwargs.get("owner")
    m.lead = kwargs.get("lead")
    m.loss_reason = kwargs.get("loss_reason")
    m.competitor = kwargs.get("competitor")
    m.win_notes = kwargs.get("win_notes")
    m.loss_notes = kwargs.get("loss_notes")
    m.notes = kwargs.get("notes")
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    # Computed properties
    m.is_open = kwargs.get("is_open", True)
    m.is_won = kwargs.get("is_won", False)
    m.is_lost = kwargs.get("is_lost", False)
    m.weighted_value = kwargs.get("weighted_value", 12500.0)
    m.days_in_pipeline = kwargs.get("days_in_pipeline", 5)
    m.is_overdue = kwargs.get("is_overdue", False)
    return m


# ---------------------------------------------------------------------------
# Fixture principal: cliente HTTP autenticado
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def crm_client():
    """
    AsyncClient autenticado para testes E2E do CRM.

    Injeta:
    - Override de get_current_active_user → mock user (admin)
    - Header Authorization Bearer (necessário para HTTPBearer security scheme)

    Uso:
        async def test_something(crm_client):
            with patch("modules.crm.controllers.lead_controller.LeadRepository") as R:
                R.return_value.create = AsyncMock(return_value=make_lead_mock())
                resp = await crm_client.post("/api/v1/crm/leads", json={...})
            assert resp.status_code == 201
    """
    from core.auth.dependencies import get_current_active_user
    from main import app

    mock_user = _make_mock_user()

    async def override_auth():
        return mock_user

    app.dependency_overrides[get_current_active_user] = override_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Necessário para satisfazer HTTPBearer antes do override de auth ser resolvido
        client.headers["Authorization"] = "Bearer test-token-valid"
        yield client

    app.dependency_overrides.pop(get_current_active_user, None)


@pytest.fixture
def mock_crm_user() -> MagicMock:
    """Mock user para uso direto em testes."""
    return _make_mock_user()

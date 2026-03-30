"""
Testes E2E para os submodulos Leads e Opportunities do CRM.

Cobre todos os endpoints via HTTP usando AsyncClient + ASGITransport,
com repositorios mockados no nivel do controller.

Endpoints testados:
    LEADS (10 endpoints, 19 testes):
        POST   /api/v1/crm/leads                           → 201 / 400
        GET    /api/v1/crm/leads                           → 200
        GET    /api/v1/crm/leads/stats                     → 200
        GET    /api/v1/crm/leads/{id}                      → 200 / 404
        PUT    /api/v1/crm/leads/{id}                      → 200 / 404
        PATCH  /api/v1/crm/leads/{id}/status               → 200 / 404
        POST   /api/v1/crm/leads/{id}/recalculate-score    → 200 / 404
        GET    /api/v1/crm/leads/{id}/recommended-action   → 200 / 404
        DELETE /api/v1/crm/leads/{id}                      → 204 / 404

    OPPORTUNITIES (9 endpoints, 18 testes):
        POST   /api/v1/crm/opportunities                   → 201
        POST   /api/v1/crm/opportunities/from-lead         → 201 / 404
        GET    /api/v1/crm/opportunities                   → 200
        GET    /api/v1/crm/opportunities/pipeline/stats    → 200
        GET    /api/v1/crm/opportunities/{id}              → 200 / 404
        PUT    /api/v1/crm/opportunities/{id}              → 200 / 404
        PATCH  /api/v1/crm/opportunities/{id}/stage        → 200 / 404
        POST   /api/v1/crm/opportunities/{id}/close        → 200 / 404
        DELETE /api/v1/crm/opportunities/{id}              → 204 / 404
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from modules.crm.schemas.lead import LeadStats
from modules.crm.schemas.opportunity import PipelineStats

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
# Mock builders
# ---------------------------------------------------------------------------


def _make_lead(**kwargs) -> MagicMock:
    """Retorna mock de Lead com todos os atributos necessarios para model_validate."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.name = kwargs.get("name", "Joao Silva")
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
    m.is_hot = kwargs.get("is_hot", False)
    m.is_qualified = kwargs.get("is_qualified", False)
    m.weighted_value = kwargs.get("weighted_value", 4000.0)
    return m


def _make_opportunity(**kwargs) -> MagicMock:
    """Retorna mock de Opportunity com todos os atributos necessarios para model_validate."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.title = kwargs.get("title", "Oportunidade Teste")
    m.description = kwargs.get("description")
    m.lead_id = kwargs.get("lead_id")
    m.contact_name = kwargs.get("contact_name", "Maria Santos")
    m.contact_email = kwargs.get("contact_email", "maria@empresa.com.br")
    m.contact_phone = kwargs.get("contact_phone")
    m.company_name = kwargs.get("company_name", "Empresa Seguranca")
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
    m.is_open = kwargs.get("is_open", True)
    m.is_won = kwargs.get("is_won", False)
    m.is_lost = kwargs.get("is_lost", False)
    m.weighted_value = kwargs.get("weighted_value", 12500.0)
    m.days_in_pipeline = kwargs.get("days_in_pipeline", 5)
    m.is_overdue = kwargs.get("is_overdue", False)
    return m


def _make_lead_stats() -> LeadStats:
    return LeadStats(
        total=10,
        by_status={"new": 3, "contacted": 2, "qualified": 2, "proposal": 1, "negotiation": 1, "won": 1, "lost": 0},
        by_source={"website": 5, "referral": 3, "other": 2},
        hot_leads=2,
        avg_score=55.0,
        total_expected_value=100000.0,
        total_weighted_value=45000.0,
    )


def _make_pipeline_stats() -> PipelineStats:
    return PipelineStats(
        total_opportunities=5,
        open_opportunities=3,
        won_opportunities=1,
        lost_opportunities=1,
        total_value=250000.0,
        weighted_value=62500.0,
        won_value=50000.0,
        lost_value=30000.0,
        win_rate=50.0,
        avg_deal_size=50000.0,
        avg_days_to_close=15.0,
        by_stage={"qualification": 2, "needs_analysis": 1},
        by_priority={"high": 1, "medium": 2, "low": 0},
        overdue_count=1,
    )


# ---------------------------------------------------------------------------
# Fixture: cliente HTTP autenticado
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def crm_client():
    """
    AsyncClient autenticado para testes E2E do CRM.
    Injeta override de get_current_active_user e header Authorization.
    """
    from core.auth.dependencies import get_current_active_user
    from main import app

    mock_user = _make_mock_user()

    async def override_auth():
        return mock_user

    app.dependency_overrides[get_current_active_user] = override_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "Bearer test-token-valid"
        yield client

    app.dependency_overrides.pop(get_current_active_user, None)


# ===========================================================================
# TESTES — LEADS
# ===========================================================================

_LEAD_PATCHER = "modules.crm.controllers.lead_controller.LeadRepository"
_OPP_PATCHER = "modules.crm.controllers.opportunity_controller.OpportunityRepository"
_LEAD_SERVICE_PATCHER = "modules.crm.controllers.lead_controller.lead_service"


class TestCreateLead:
    """POST /api/v1/crm/leads"""

    @pytest.mark.asyncio
    async def test_create_lead_success(self, crm_client):
        """Cria lead com email novo — retorna 201 com dados do lead."""
        mock_lead = _make_lead(name="Joao Silva", email="joao@empresa.com.br")

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_email = AsyncMock(return_value=None)
            instance.create = AsyncMock(return_value=mock_lead)

            response = await crm_client.post(
                "/api/v1/crm/leads",
                json={"name": "Joao Silva", "email": "joao@empresa.com.br", "source": "website"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == mock_lead.id
        assert data["name"] == mock_lead.name
        assert data["email"] == mock_lead.email
        assert data["source"] == "website"
        assert data["status"] == "new"

    @pytest.mark.asyncio
    async def test_create_lead_duplicate_email(self, crm_client):
        """Tenta criar lead com email ja existente — retorna 400."""
        existing_lead = _make_lead(email="joao@empresa.com.br")

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_email = AsyncMock(return_value=existing_lead)

            response = await crm_client.post(
                "/api/v1/crm/leads",
                json={"name": "Joao Silva", "email": "joao@empresa.com.br", "source": "website"},
            )

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_lead_with_all_fields(self, crm_client):
        """Cria lead com todos os campos opcionais preenchidos — retorna 201."""
        mock_lead = _make_lead(
            name="Ana Oliveira",
            email="ana@empresa.com.br",
            company="Tech Corp",
            position="CEO",
            expected_value=50000.0,
        )

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_email = AsyncMock(return_value=None)
            instance.create = AsyncMock(return_value=mock_lead)

            response = await crm_client.post(
                "/api/v1/crm/leads",
                json={
                    "name": "Ana Oliveira",
                    "email": "ana@empresa.com.br",
                    "source": "referral",
                    "company": "Tech Corp",
                    "position": "CEO",
                    "expected_value": 50000.0,
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["company"] == mock_lead.company
        assert data["position"] == mock_lead.position


class TestListLeads:
    """GET /api/v1/crm/leads"""

    @pytest.mark.asyncio
    async def test_list_leads_default(self, crm_client):
        """Lista leads sem filtros — retorna 200 com paginacao padrao."""
        mock_lead = _make_lead()

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([mock_lead], 1))

            response = await crm_client.get("/api/v1/crm/leads")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total_pages"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == mock_lead.id

    @pytest.mark.asyncio
    async def test_list_leads_with_filters(self, crm_client):
        """Lista leads com filtros de status, score e busca — retorna 200."""
        mock_lead = _make_lead(status="contacted", score=70, is_hot=True)

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([mock_lead], 1))

            response = await crm_client.get(
                "/api/v1/crm/leads",
                params={
                    "status": "contacted",
                    "min_score": 60,
                    "is_hot": True,
                    "search": "Joao",
                    "page": 1,
                    "page_size": 10,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 10
        assert len(data["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_leads_empty(self, crm_client):
        """Lista leads sem resultados — retorna 200 com lista vazia."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))

            response = await crm_client.get("/api/v1/crm/leads")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["total_pages"] == 0
        assert data["items"] == []


class TestGetLeadStats:
    """GET /api/v1/crm/leads/stats"""

    @pytest.mark.asyncio
    async def test_get_lead_stats(self, crm_client):
        """Retorna estatisticas de todos os leads — retorna 200."""
        mock_stats = _make_lead_stats()

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_stats = AsyncMock(return_value=mock_stats)

            response = await crm_client.get("/api/v1/crm/leads/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert data["hot_leads"] == 2
        assert data["avg_score"] == 55.0
        assert data["total_expected_value"] == 100000.0
        assert "by_status" in data
        assert "by_source" in data

    @pytest.mark.asyncio
    async def test_get_lead_stats_filtered_by_user(self, crm_client):
        """Retorna estatisticas filtradas por assigned_to_id — retorna 200."""
        user_id = _uid()
        mock_stats = _make_lead_stats()

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_stats = AsyncMock(return_value=mock_stats)

            response = await crm_client.get(
                "/api/v1/crm/leads/stats",
                params={"assigned_to_id": user_id},
            )

        assert response.status_code == 200
        instance.get_stats.assert_awaited_once_with(assigned_to_id=user_id)


class TestGetLead:
    """GET /api/v1/crm/leads/{id}"""

    @pytest.mark.asyncio
    async def test_get_lead_found(self, crm_client):
        """Busca lead existente pelo ID — retorna 200 com dados completos."""
        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id)

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_lead)

            response = await crm_client.get(f"/api/v1/crm/leads/{lead_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lead_id
        assert data["name"] == mock_lead.name

    @pytest.mark.asyncio
    async def test_get_lead_not_found(self, crm_client):
        """Busca lead inexistente — retorna 404."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)

            response = await crm_client.get(f"/api/v1/crm/leads/{_uid()}")

        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]


class TestUpdateLead:
    """PUT /api/v1/crm/leads/{id}"""

    @pytest.mark.asyncio
    async def test_update_lead_success(self, crm_client):
        """Atualiza lead existente — retorna 200 com dados atualizados."""
        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id, name="Joao Atualizado", company="Nova Empresa")

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=mock_lead)

            response = await crm_client.put(
                f"/api/v1/crm/leads/{lead_id}",
                json={"name": "Joao Atualizado", "company": "Nova Empresa"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lead_id
        assert data["name"] == "Joao Atualizado"

    @pytest.mark.asyncio
    async def test_update_lead_not_found(self, crm_client):
        """Tenta atualizar lead inexistente — retorna 404."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=None)

            response = await crm_client.put(
                f"/api/v1/crm/leads/{_uid()}",
                json={"name": "Nao Existe"},
            )

        assert response.status_code == 404


class TestUpdateLeadStatus:
    """PATCH /api/v1/crm/leads/{id}/status"""

    @pytest.mark.asyncio
    async def test_update_lead_status_success(self, crm_client):
        """Atualiza status de lead existente — retorna 200."""
        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id, status="contacted")

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_lead)

            response = await crm_client.patch(
                f"/api/v1/crm/leads/{lead_id}/status",
                json={"status": "contacted"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "contacted"

    @pytest.mark.asyncio
    async def test_update_lead_status_with_notes(self, crm_client):
        """Atualiza status com nota — retorna 200."""
        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id, status="qualified")

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_lead)

            response = await crm_client.patch(
                f"/api/v1/crm/leads/{lead_id}/status",
                json={"status": "qualified", "notes": "Lead qualificado apos reuniao"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_lead_status_not_found(self, crm_client):
        """Tenta alterar status de lead inexistente — retorna 404."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=None)

            response = await crm_client.patch(
                f"/api/v1/crm/leads/{_uid()}/status",
                json={"status": "contacted"},
            )

        assert response.status_code == 404


class TestRecalculateLeadScore:
    """POST /api/v1/crm/leads/{id}/recalculate-score"""

    @pytest.mark.asyncio
    async def test_recalculate_score_success(self, crm_client):
        """Recalcula score de lead existente — retorna 200 com novo score."""
        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id, score=75)

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_score = AsyncMock(return_value=mock_lead)

            response = await crm_client.post(f"/api/v1/crm/leads/{lead_id}/recalculate-score")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lead_id
        assert data["score"] == 75

    @pytest.mark.asyncio
    async def test_recalculate_score_not_found(self, crm_client):
        """Tenta recalcular score de lead inexistente — retorna 404."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_score = AsyncMock(return_value=None)

            response = await crm_client.post(f"/api/v1/crm/leads/{_uid()}/recalculate-score")

        assert response.status_code == 404


class TestGetRecommendedAction:
    """GET /api/v1/crm/leads/{id}/recommended-action"""

    @pytest.mark.asyncio
    async def test_get_recommended_action_success(self, crm_client):
        """Retorna acao recomendada para lead existente — retorna 200."""
        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id, score=65, status="contacted")

        with patch(_LEAD_PATCHER) as MockRepo, patch(_LEAD_SERVICE_PATCHER) as mock_service:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_lead)
            mock_service.get_recommended_action = MagicMock(return_value="CALL")
            mock_service.get_next_contact_date = MagicMock(return_value=None)

            response = await crm_client.get(f"/api/v1/crm/leads/{lead_id}/recommended-action")

        assert response.status_code == 200
        data = response.json()
        assert data["lead_id"] == lead_id
        assert data["recommended_action"] == "CALL"
        assert data["next_contact_date"] is None

    @pytest.mark.asyncio
    async def test_get_recommended_action_with_next_contact(self, crm_client):
        """Retorna acao recomendada com data de proximo contato — retorna 200."""
        from datetime import date

        lead_id = _uid()
        mock_lead = _make_lead(id=lead_id, score=80, status="qualified")
        next_contact = date(2026, 4, 5)

        with patch(_LEAD_PATCHER) as MockRepo, patch(_LEAD_SERVICE_PATCHER) as mock_service:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_lead)
            mock_service.get_recommended_action = MagicMock(return_value="SEND_PROPOSAL")
            mock_service.get_next_contact_date = MagicMock(return_value=next_contact)

            response = await crm_client.get(f"/api/v1/crm/leads/{lead_id}/recommended-action")

        assert response.status_code == 200
        data = response.json()
        assert data["recommended_action"] == "SEND_PROPOSAL"
        assert data["next_contact_date"] == "2026-04-05"

    @pytest.mark.asyncio
    async def test_get_recommended_action_not_found(self, crm_client):
        """Tenta obter acao para lead inexistente — retorna 404."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)

            response = await crm_client.get(f"/api/v1/crm/leads/{_uid()}/recommended-action")

        assert response.status_code == 404


class TestDeleteLead:
    """DELETE /api/v1/crm/leads/{id}"""

    @pytest.mark.asyncio
    async def test_delete_lead_success(self, crm_client):
        """Remove lead existente — retorna 204 sem corpo."""
        lead_id = _uid()

        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=True)

            response = await crm_client.delete(f"/api/v1/crm/leads/{lead_id}")

        assert response.status_code == 204
        assert response.content == b""

    @pytest.mark.asyncio
    async def test_delete_lead_not_found(self, crm_client):
        """Tenta remover lead inexistente — retorna 404."""
        with patch(_LEAD_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=False)

            response = await crm_client.delete(f"/api/v1/crm/leads/{_uid()}")

        assert response.status_code == 404


# ===========================================================================
# TESTES — OPPORTUNITIES
# ===========================================================================


class TestCreateOpportunity:
    """POST /api/v1/crm/opportunities"""

    @pytest.mark.asyncio
    async def test_create_opportunity_success(self, crm_client):
        """Cria oportunidade nova — retorna 201 com dados."""
        mock_opp = _make_opportunity(
            title="Seguranca Patrimonial",
            contact_name="Maria Santos",
            value=50000.0,
        )

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=mock_opp)

            response = await crm_client.post(
                "/api/v1/crm/opportunities",
                json={
                    "title": "Seguranca Patrimonial",
                    "contact_name": "Maria Santos",
                    "contact_email": "maria@empresa.com.br",
                    "value": 50000.0,
                    "probability": 25,
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == mock_opp.id
        assert data["title"] == mock_opp.title
        assert data["value"] == 50000.0

    @pytest.mark.asyncio
    async def test_create_opportunity_with_all_fields(self, crm_client):
        """Cria oportunidade com todos os campos opcionais — retorna 201."""
        lead_id = _uid()
        mock_opp = _make_opportunity(
            title="Portaria Remota",
            lead_id=lead_id,
            stage="needs_analysis",
            priority="high",
        )

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=mock_opp)

            response = await crm_client.post(
                "/api/v1/crm/opportunities",
                json={
                    "title": "Portaria Remota",
                    "contact_name": "Carlos Pereira",
                    "contact_email": "carlos@empresa.com.br",
                    "value": 80000.0,
                    "probability": 40,
                    "lead_id": lead_id,
                    "stage": "needs_analysis",
                    "priority": "high",
                    "company_name": "Empresa Grande",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["lead_id"] == lead_id


class TestCreateOpportunityFromLead:
    """POST /api/v1/crm/opportunities/from-lead"""

    @pytest.mark.asyncio
    async def test_create_from_lead_success(self, crm_client):
        """Converte lead em oportunidade — retorna 201."""
        lead_id = _uid()
        mock_opp = _make_opportunity(lead_id=lead_id, title="Oportunidade do Lead")

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.create_from_lead = AsyncMock(return_value=mock_opp)

            response = await crm_client.post(
                "/api/v1/crm/opportunities/from-lead",
                json={"lead_id": lead_id, "title": "Oportunidade do Lead"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == mock_opp.id
        assert data["lead_id"] == lead_id

    @pytest.mark.asyncio
    async def test_create_from_lead_not_found(self, crm_client):
        """Tenta converter lead inexistente — retorna 404."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.create_from_lead = AsyncMock(return_value=None)

            response = await crm_client.post(
                "/api/v1/crm/opportunities/from-lead",
                json={"lead_id": _uid(), "title": "Oportunidade Inexistente"},
            )

        assert response.status_code == 404
        assert (
            "não encontrado" in response.json()["detail"].lower()
            or "nao encontrado" in response.json()["detail"].lower()
        )


class TestListOpportunities:
    """GET /api/v1/crm/opportunities"""

    @pytest.mark.asyncio
    async def test_list_opportunities_default(self, crm_client):
        """Lista oportunidades sem filtros — retorna 200 paginado."""
        mock_opp = _make_opportunity()

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([mock_opp], 1))

            response = await crm_client.get("/api/v1/crm/opportunities")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == mock_opp.id

    @pytest.mark.asyncio
    async def test_list_opportunities_with_filters(self, crm_client):
        """Lista oportunidades com filtros de stage e valor — retorna 200."""
        mock_opp = _make_opportunity(stage="proposal", value=100000.0)

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([mock_opp], 1))

            response = await crm_client.get(
                "/api/v1/crm/opportunities",
                params={
                    "stage": "proposal",
                    "min_value": 50000,
                    "is_open": True,
                    "search": "Seguranca",
                    "page_size": 5,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 5
        assert len(data["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_opportunities_empty(self, crm_client):
        """Lista oportunidades sem resultados — retorna 200 lista vazia."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))

            response = await crm_client.get("/api/v1/crm/opportunities")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestGetPipelineStats:
    """GET /api/v1/crm/opportunities/pipeline/stats"""

    @pytest.mark.asyncio
    async def test_get_pipeline_stats(self, crm_client):
        """Retorna estatisticas do pipeline — retorna 200."""
        mock_stats = _make_pipeline_stats()

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_pipeline_stats = AsyncMock(return_value=mock_stats)

            response = await crm_client.get("/api/v1/crm/opportunities/pipeline/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_opportunities"] == 5
        assert data["open_opportunities"] == 3
        assert data["won_opportunities"] == 1
        assert data["total_value"] == 250000.0
        assert data["win_rate"] == 50.0
        assert "by_stage" in data
        assert "by_priority" in data

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_filtered_by_owner(self, crm_client):
        """Retorna estatisticas filtradas por owner_id — retorna 200."""
        owner_id = _uid()
        mock_stats = _make_pipeline_stats()

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_pipeline_stats = AsyncMock(return_value=mock_stats)

            response = await crm_client.get(
                "/api/v1/crm/opportunities/pipeline/stats",
                params={"owner_id": owner_id},
            )

        assert response.status_code == 200
        instance.get_pipeline_stats.assert_awaited_once_with(owner_id=owner_id)


class TestGetOpportunity:
    """GET /api/v1/crm/opportunities/{id}"""

    @pytest.mark.asyncio
    async def test_get_opportunity_found(self, crm_client):
        """Busca oportunidade existente pelo ID — retorna 200."""
        opp_id = _uid()
        mock_opp = _make_opportunity(id=opp_id)

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_opp)

            response = await crm_client.get(f"/api/v1/crm/opportunities/{opp_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == opp_id
        assert data["title"] == mock_opp.title

    @pytest.mark.asyncio
    async def test_get_opportunity_not_found(self, crm_client):
        """Busca oportunidade inexistente — retorna 404."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)

            response = await crm_client.get(f"/api/v1/crm/opportunities/{_uid()}")

        assert response.status_code == 404
        assert (
            "nao encontrada" in response.json()["detail"].lower()
            or "não encontrada" in response.json()["detail"].lower()
        )


class TestUpdateOpportunity:
    """PUT /api/v1/crm/opportunities/{id}"""

    @pytest.mark.asyncio
    async def test_update_opportunity_success(self, crm_client):
        """Atualiza oportunidade existente — retorna 200."""
        opp_id = _uid()
        mock_opp = _make_opportunity(id=opp_id, title="Titulo Atualizado", value=75000.0)

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=mock_opp)

            response = await crm_client.put(
                f"/api/v1/crm/opportunities/{opp_id}",
                json={"title": "Titulo Atualizado", "value": 75000.0},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == opp_id
        assert data["title"] == "Titulo Atualizado"

    @pytest.mark.asyncio
    async def test_update_opportunity_not_found(self, crm_client):
        """Tenta atualizar oportunidade inexistente — retorna 404."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=None)

            response = await crm_client.put(
                f"/api/v1/crm/opportunities/{_uid()}",
                json={"title": "Nao Existe"},
            )

        assert response.status_code == 404


class TestUpdateOpportunityStage:
    """PATCH /api/v1/crm/opportunities/{id}/stage"""

    @pytest.mark.asyncio
    async def test_update_stage_success(self, crm_client):
        """Avanca oportunidade no funil — retorna 200."""
        opp_id = _uid()
        mock_opp = _make_opportunity(id=opp_id, stage="needs_analysis")

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_stage = AsyncMock(return_value=mock_opp)

            response = await crm_client.patch(
                f"/api/v1/crm/opportunities/{opp_id}/stage",
                json={"stage": "needs_analysis"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "needs_analysis"

    @pytest.mark.asyncio
    async def test_update_stage_with_notes(self, crm_client):
        """Avanca estagio com nota — retorna 200."""
        opp_id = _uid()
        mock_opp = _make_opportunity(id=opp_id, stage="proposal")

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_stage = AsyncMock(return_value=mock_opp)

            response = await crm_client.patch(
                f"/api/v1/crm/opportunities/{opp_id}/stage",
                json={"stage": "proposal", "notes": "Proposta enviada por email"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_stage_not_found(self, crm_client):
        """Tenta atualizar estagio de oportunidade inexistente — retorna 404."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.update_stage = AsyncMock(return_value=None)

            response = await crm_client.patch(
                f"/api/v1/crm/opportunities/{_uid()}/stage",
                json={"stage": "needs_analysis"},
            )

        assert response.status_code == 404


class TestCloseOpportunity:
    """POST /api/v1/crm/opportunities/{id}/close"""

    @pytest.mark.asyncio
    async def test_close_opportunity_won(self, crm_client):
        """Fecha oportunidade como ganha — retorna 200."""
        opp_id = _uid()
        mock_opp = _make_opportunity(
            id=opp_id,
            stage="closed_won",
            is_open=False,
            is_won=True,
            is_lost=False,
        )

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.close = AsyncMock(return_value=mock_opp)

            response = await crm_client.post(
                f"/api/v1/crm/opportunities/{opp_id}/close",
                json={"won": True},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == opp_id
        assert data["is_won"] is True
        assert data["is_lost"] is False

    @pytest.mark.asyncio
    async def test_close_opportunity_lost(self, crm_client):
        """Fecha oportunidade como perdida com motivo — retorna 200."""
        opp_id = _uid()
        mock_opp = _make_opportunity(
            id=opp_id,
            stage="closed_lost",
            is_open=False,
            is_won=False,
            is_lost=True,
            loss_reason="price",
            competitor="Concorrente X",
        )

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.close = AsyncMock(return_value=mock_opp)

            response = await crm_client.post(
                f"/api/v1/crm/opportunities/{opp_id}/close",
                json={
                    "won": False,
                    "loss_reason": "price",
                    "competitor": "Concorrente X",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["is_lost"] is True
        assert data["is_won"] is False

    @pytest.mark.asyncio
    async def test_close_opportunity_not_found(self, crm_client):
        """Tenta fechar oportunidade inexistente — retorna 404."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.close = AsyncMock(return_value=None)

            response = await crm_client.post(
                f"/api/v1/crm/opportunities/{_uid()}/close",
                json={"won": True},
            )

        assert response.status_code == 404


class TestDeleteOpportunity:
    """DELETE /api/v1/crm/opportunities/{id}"""

    @pytest.mark.asyncio
    async def test_delete_opportunity_success(self, crm_client):
        """Remove oportunidade existente — retorna 204 sem corpo."""
        opp_id = _uid()

        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=True)

            response = await crm_client.delete(f"/api/v1/crm/opportunities/{opp_id}")

        assert response.status_code == 204
        assert response.content == b""

    @pytest.mark.asyncio
    async def test_delete_opportunity_not_found(self, crm_client):
        """Tenta remover oportunidade inexistente — retorna 404."""
        with patch(_OPP_PATCHER) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=False)

            response = await crm_client.delete(f"/api/v1/crm/opportunities/{_uid()}")

        assert response.status_code == 404

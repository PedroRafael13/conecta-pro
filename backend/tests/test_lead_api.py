"""Testes para endpoints de Lead."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from modules.crm.controllers.lead_controller import (
    create_lead,
    delete_lead,
    get_lead,
    get_lead_stats,
    get_recommended_action,
    list_leads,
    recalculate_lead_score,
    update_lead,
    update_lead_status,
)
from modules.crm.models.lead import LeadSource, LeadStatus
from modules.crm.schemas.lead import (
    LeadCreate,
    LeadFilter,
    LeadListResponse,
    LeadResponse,
    LeadStats,
    LeadStatusUpdate,
    LeadUpdate,
)
from tests.factories import TEST_LEAD_DATA, LeadFactory


class TestCreateLeadEndpoint:
    """Testes para endpoint de criação de lead."""

    @pytest.mark.asyncio
    async def test_create_lead_success(self):
        """Testa criação de lead com sucesso."""
        lead_data = LeadCreate(
            name="Novo Lead",
            email="novo@empresa.com",
            source=LeadSource.WEBSITE,
            expected_value=10000.0,
        )

        mock_lead = LeadFactory.build(
            name="Novo Lead",
            email="novo@empresa.com",
            source="website",
        )

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"

        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_by_email = AsyncMock(return_value=None)
            mock_repo.create = AsyncMock(return_value=mock_lead)

            result = await create_lead(lead_data, mock_user, mock_db)

            assert result.email == "novo@empresa.com"
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_lead_email_exists(self):
        """Testa criação com email já existente."""
        lead_data = LeadCreate(
            name="Lead Duplicado",
            email="existente@empresa.com",
            source=LeadSource.WEBSITE,
        )

        mock_existing = LeadFactory.build(email="existente@empresa.com")

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_by_email = AsyncMock(return_value=mock_existing)

            with pytest.raises(HTTPException) as exc_info:
                await create_lead(lead_data, mock_user, mock_db)

            assert exc_info.value.status_code == 400
            assert "email" in exc_info.value.detail.lower()


class TestListLeadsEndpoint:
    """Testes para endpoint de listagem de leads."""

    @pytest.mark.asyncio
    async def test_list_leads_success(self):
        """Testa listagem de leads."""
        mock_leads = LeadFactory.build_batch(3)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.list = AsyncMock(return_value=(mock_leads, 3))

            result = await list_leads(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                status_filter=None,
                source=None,
                assigned_to_id=None,
                min_score=None,
                max_score=None,
                is_hot=None,
                company=None,
                search=None,
            )

            assert result.total == 3
            assert len(result.items) == 3

    @pytest.mark.asyncio
    async def test_list_leads_with_filters(self):
        """Testa listagem com filtros."""
        mock_leads = [LeadFactory.build(status="qualified")]

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.list = AsyncMock(return_value=(mock_leads, 1))

            result = await list_leads(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                status_filter=LeadStatus.QUALIFIED,
                source=None,
                assigned_to_id=None,
                min_score=None,
                max_score=None,
                is_hot=None,
                company=None,
                search=None,
            )

            assert result.total == 1
            mock_repo.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_leads_pagination(self):
        """Testa paginação."""
        mock_leads = LeadFactory.build_batch(5)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.list = AsyncMock(return_value=(mock_leads, 25))

            result = await list_leads(
                current_user=mock_user,
                db=mock_db,
                page=2,
                page_size=5,
                status_filter=None,
                source=None,
                assigned_to_id=None,
                min_score=None,
                max_score=None,
                is_hot=None,
                company=None,
                search=None,
            )

            assert result.page == 2
            assert result.page_size == 5
            assert result.total_pages == 5


class TestGetLeadEndpoint:
    """Testes para endpoint de obter lead."""

    @pytest.mark.asyncio
    async def test_get_lead_success(self):
        """Testa obtenção de lead existente."""
        lead_id = str(uuid4())
        mock_lead = LeadFactory.build(id=lead_id)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_by_id = AsyncMock(return_value=mock_lead)

            result = await get_lead(lead_id, mock_user, mock_db)

            assert result.id == lead_id

    @pytest.mark.asyncio
    async def test_get_lead_not_found(self):
        """Testa obtenção de lead inexistente."""
        lead_id = str(uuid4())

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_lead(lead_id, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestUpdateLeadEndpoint:
    """Testes para endpoint de atualização de lead."""

    @pytest.mark.asyncio
    async def test_update_lead_success(self):
        """Testa atualização de lead."""
        lead_id = str(uuid4())
        update_data = LeadUpdate(name="Nome Atualizado")

        mock_lead = LeadFactory.build(id=lead_id, name="Nome Atualizado")

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.update = AsyncMock(return_value=mock_lead)

            result = await update_lead(lead_id, update_data, mock_user, mock_db)

            assert result.name == "Nome Atualizado"

    @pytest.mark.asyncio
    async def test_update_lead_not_found(self):
        """Testa atualização de lead inexistente."""
        lead_id = str(uuid4())
        update_data = LeadUpdate(name="Nome Novo")

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.update = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await update_lead(lead_id, update_data, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestUpdateLeadStatusEndpoint:
    """Testes para endpoint de atualização de status."""

    @pytest.mark.asyncio
    async def test_update_status_success(self):
        """Testa atualização de status."""
        lead_id = str(uuid4())
        status_data = LeadStatusUpdate(
            status=LeadStatus.QUALIFIED,
            notes="Lead qualificado após reunião",
        )

        mock_lead = LeadFactory.build(id=lead_id, status="qualified")

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.update_status = AsyncMock(return_value=mock_lead)

            result = await update_lead_status(lead_id, status_data, mock_user, mock_db)

            assert result.status == LeadStatus.QUALIFIED
            mock_repo.update_status.assert_called_once_with(
                lead_id,
                LeadStatus.QUALIFIED,
                "Lead qualificado após reunião",
            )

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        """Testa atualização de status para lead inexistente."""
        lead_id = str(uuid4())
        status_data = LeadStatusUpdate(status=LeadStatus.CONTACTED)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.update_status = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await update_lead_status(lead_id, status_data, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestRecalculateScoreEndpoint:
    """Testes para endpoint de recálculo de score."""

    @pytest.mark.asyncio
    async def test_recalculate_score_success(self):
        """Testa recálculo de score."""
        lead_id = str(uuid4())
        mock_lead = LeadFactory.build(id=lead_id, score=75)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.update_score = AsyncMock(return_value=mock_lead)

            result = await recalculate_lead_score(lead_id, mock_user, mock_db)

            assert result.score == 75

    @pytest.mark.asyncio
    async def test_recalculate_score_not_found(self):
        """Testa recálculo para lead inexistente."""
        lead_id = str(uuid4())

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.update_score = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await recalculate_lead_score(lead_id, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestGetRecommendedActionEndpoint:
    """Testes para endpoint de ação recomendada."""

    @pytest.mark.asyncio
    async def test_get_recommended_action_success(self):
        """Testa obtenção de ação recomendada."""
        lead_id = str(uuid4())
        mock_lead = LeadFactory.build(id=lead_id, score=85, status="new")

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_by_id = AsyncMock(return_value=mock_lead)

            result = await get_recommended_action(lead_id, mock_user, mock_db)

            assert "lead_id" in result
            assert "recommended_action" in result
            assert "score" in result

    @pytest.mark.asyncio
    async def test_get_recommended_action_not_found(self):
        """Testa ação recomendada para lead inexistente."""
        lead_id = str(uuid4())

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_recommended_action(lead_id, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestDeleteLeadEndpoint:
    """Testes para endpoint de exclusão de lead."""

    @pytest.mark.asyncio
    async def test_delete_lead_success(self):
        """Testa exclusão de lead."""
        lead_id = str(uuid4())

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.delete = AsyncMock(return_value=True)

            # Não deve lançar exceção
            await delete_lead(lead_id, mock_user, mock_db)

            mock_repo.delete.assert_called_once_with(lead_id)

    @pytest.mark.asyncio
    async def test_delete_lead_not_found(self):
        """Testa exclusão de lead inexistente."""
        lead_id = str(uuid4())

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.delete = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await delete_lead(lead_id, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestGetLeadStatsEndpoint:
    """Testes para endpoint de estatísticas."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self):
        """Testa obtenção de estatísticas."""
        mock_stats = LeadStats(
            total=10,
            by_status={"new": 5, "qualified": 3, "won": 2},
            by_source={"website": 6, "referral": 4},
            hot_leads=5,
            avg_score=65.5,
            total_expected_value=150000.0,
            total_weighted_value=97500.0,
        )

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_stats = AsyncMock(return_value=mock_stats)

            result = await get_lead_stats(mock_user, mock_db)

            assert result.total == 10
            assert result.hot_leads == 5

    @pytest.mark.asyncio
    async def test_get_stats_with_filter(self):
        """Testa estatísticas filtradas por responsável."""
        user_id = str(uuid4())
        mock_stats = LeadStats(
            total=3,
            by_status={"new": 2, "qualified": 1},
            by_source={"website": 3},
            hot_leads=1,
            avg_score=55.0,
            total_expected_value=45000.0,
            total_weighted_value=24750.0,
        )

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.lead_controller.LeadRepository") as mock_repo_cls:
            mock_repo = mock_repo_cls.return_value
            mock_repo.get_stats = AsyncMock(return_value=mock_stats)

            await get_lead_stats(mock_user, mock_db, assigned_to_id=user_id)

            mock_repo.get_stats.assert_called_once_with(assigned_to_id=user_id)


class TestLeadRouter:
    """Testes para configuração do router."""

    def test_router_prefix(self):
        """Testa prefixo do router."""
        from modules.crm.controllers.lead_controller import router

        assert router.prefix == "/leads"

    def test_router_tags(self):
        """Testa tags do router."""
        from modules.crm.controllers.lead_controller import router

        assert "CRM - Leads" in router.tags


class TestLeadSchemaValidation:
    """Testes para validação de schemas."""

    def test_lead_create_valid(self):
        """Testa criação de schema válido."""
        data = LeadCreate(
            name="Lead Teste",
            email="lead@test.com",
            source=LeadSource.WEBSITE,
        )

        assert data.name == "Lead Teste"
        assert data.email == "lead@test.com"

    def test_lead_create_with_all_fields(self):
        """Testa criação com todos os campos."""
        data = LeadCreate(**TEST_LEAD_DATA)

        assert data.name == "Lead Teste"
        assert data.company == "Empresa Teste"
        assert data.expected_value == 15000.0

    def test_lead_update_partial(self):
        """Testa atualização parcial."""
        data = LeadUpdate(name="Novo Nome")

        dump = data.model_dump(exclude_unset=True)
        assert "name" in dump
        assert len(dump) == 1

    def test_lead_status_update(self):
        """Testa atualização de status."""
        data = LeadStatusUpdate(
            status=LeadStatus.QUALIFIED,
            notes="Qualificado",
        )

        assert data.status == LeadStatus.QUALIFIED
        assert data.notes == "Qualificado"

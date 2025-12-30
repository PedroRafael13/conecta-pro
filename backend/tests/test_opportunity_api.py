"""Testes para endpoints de Opportunity."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from modules.crm.controllers.opportunity_controller import (
    close_opportunity,
    create_opportunity,
    create_opportunity_from_lead,
    delete_opportunity,
    get_opportunity,
    get_pipeline_stats,
    list_opportunities,
    update_opportunity,
    update_opportunity_stage,
)
from modules.crm.models.opportunity import OpportunityPriority, OpportunityStage
from modules.crm.schemas.opportunity import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityCreateFromLead,
    OpportunityFilter,
    OpportunityStageUpdate,
    OpportunityUpdate,
    PipelineStats,
)
from tests.factories import OpportunityFactory, TEST_OPPORTUNITY_DATA


class TestCreateOpportunityEndpoint:
    """Testes para endpoint de criacao de opportunity."""

    @pytest.mark.asyncio
    async def test_create_opportunity_success(self):
        """Testa criacao de opportunity com sucesso."""
        opp_data = OpportunityCreate(
            title="Nova Oportunidade",
            contact_name="Contato",
            contact_email="contato@empresa.com",
            value=10000.0,
        )

        mock_opp = OpportunityFactory.build(
            title="Nova Oportunidade",
            contact_email="contato@empresa.com",
        )

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create = AsyncMock(return_value=mock_opp)

            result = await create_opportunity(opp_data, mock_user, mock_db)

            assert result.contact_email == "contato@empresa.com"
            mock_repo.create.assert_called_once()


class TestCreateOpportunityFromLeadEndpoint:
    """Testes para endpoint de conversao lead -> opportunity."""

    @pytest.mark.asyncio
    async def test_create_from_lead_success(self):
        """Testa conversao de lead com sucesso."""
        lead_id = str(uuid4())
        opp_data = OpportunityCreateFromLead(
            lead_id=lead_id,
            title="Oportunidade do Lead",
            value=15000.0,
        )

        mock_opp = OpportunityFactory.build(
            title="Oportunidade do Lead",
            lead_id=lead_id,
        )

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create_from_lead = AsyncMock(return_value=mock_opp)

            result = await create_opportunity_from_lead(opp_data, mock_user, mock_db)

            assert result.lead_id == lead_id
            mock_repo.create_from_lead.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_from_lead_not_found(self):
        """Testa conversao quando lead nao existe."""
        opp_data = OpportunityCreateFromLead(
            lead_id=str(uuid4()),
            title="Oportunidade",
            value=10000.0,
        )

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.create_from_lead = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await create_opportunity_from_lead(opp_data, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestListOpportunitiesEndpoint:
    """Testes para endpoint de listagem de opportunities."""

    @pytest.mark.asyncio
    async def test_list_opportunities_success(self):
        """Testa listagem de opportunities."""
        mock_opps = OpportunityFactory.build_batch(3)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.list = AsyncMock(return_value=(mock_opps, 3))

            result = await list_opportunities(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                stage=None,
                priority=None,
                owner_id=None,
                is_open=None,
                min_value=None,
                max_value=None,
                company_name=None,
                search=None,
            )

            assert result.total == 3
            assert len(result.items) == 3

    @pytest.mark.asyncio
    async def test_list_opportunities_with_filters(self):
        """Testa listagem com filtros."""
        mock_opps = [OpportunityFactory.build(stage="proposal")]

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.list = AsyncMock(return_value=(mock_opps, 1))

            result = await list_opportunities(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                stage=OpportunityStage.PROPOSAL,
                priority=None,
                owner_id=None,
                is_open=None,
                min_value=None,
                max_value=None,
                company_name=None,
                search=None,
            )

            assert result.total == 1
            mock_repo.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_opportunities_pagination(self):
        """Testa paginacao."""
        mock_opps = OpportunityFactory.build_batch(5)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.list = AsyncMock(return_value=(mock_opps, 25))

            result = await list_opportunities(
                current_user=mock_user,
                db=mock_db,
                page=2,
                page_size=5,
                stage=None,
                priority=None,
                owner_id=None,
                is_open=None,
                min_value=None,
                max_value=None,
                company_name=None,
                search=None,
            )

            assert result.page == 2
            assert result.page_size == 5
            assert result.total_pages == 5


class TestGetOpportunityEndpoint:
    """Testes para endpoint de obter opportunity."""

    @pytest.mark.asyncio
    async def test_get_opportunity_success(self):
        """Testa obtencao de opportunity existente."""
        opp_id = str(uuid4())
        mock_opp = OpportunityFactory.build(id=opp_id)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=mock_opp)

            result = await get_opportunity(opp_id, mock_user, mock_db)

            assert result.id == opp_id

    @pytest.mark.asyncio
    async def test_get_opportunity_not_found(self):
        """Testa obtencao de opportunity inexistente."""
        opp_id = str(uuid4())

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_opportunity(opp_id, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestUpdateOpportunityEndpoint:
    """Testes para endpoint de atualizacao de opportunity."""

    @pytest.mark.asyncio
    async def test_update_opportunity_success(self):
        """Testa atualizacao de opportunity."""
        opp_id = str(uuid4())
        update_data = OpportunityUpdate(title="Titulo Atualizado")

        mock_opp = OpportunityFactory.build(id=opp_id, title="Titulo Atualizado")

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.update = AsyncMock(return_value=mock_opp)

            result = await update_opportunity(opp_id, update_data, mock_user, mock_db)

            assert result.title == "Titulo Atualizado"

    @pytest.mark.asyncio
    async def test_update_opportunity_not_found(self):
        """Testa atualizacao de opportunity inexistente."""
        opp_id = str(uuid4())
        update_data = OpportunityUpdate(title="Novo Titulo")

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.update = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await update_opportunity(opp_id, update_data, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestUpdateOpportunityStageEndpoint:
    """Testes para endpoint de atualizacao de estagio."""

    @pytest.mark.asyncio
    async def test_update_stage_success(self):
        """Testa atualizacao de estagio."""
        opp_id = str(uuid4())
        stage_data = OpportunityStageUpdate(
            stage=OpportunityStage.PROPOSAL,
            notes="Enviamos proposta",
        )

        mock_opp = OpportunityFactory.build(id=opp_id, stage="proposal")

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.update_stage = AsyncMock(return_value=mock_opp)

            result = await update_opportunity_stage(opp_id, stage_data, mock_user, mock_db)

            assert result.stage == OpportunityStage.PROPOSAL
            mock_repo.update_stage.assert_called_once_with(
                opp_id,
                OpportunityStage.PROPOSAL,
                "Enviamos proposta",
            )

    @pytest.mark.asyncio
    async def test_update_stage_not_found(self):
        """Testa atualizacao de estagio para opportunity inexistente."""
        opp_id = str(uuid4())
        stage_data = OpportunityStageUpdate(stage=OpportunityStage.NEGOTIATION)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.update_stage = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await update_opportunity_stage(opp_id, stage_data, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestCloseOpportunityEndpoint:
    """Testes para endpoint de fechamento de opportunity."""

    @pytest.mark.asyncio
    async def test_close_opportunity_won(self):
        """Testa fechamento como ganha."""
        opp_id = str(uuid4())
        close_data = OpportunityClose(
            won=True,
            notes="Fechamos o negocio!",
        )

        mock_opp = OpportunityFactory.build_won(id=opp_id)

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.close = AsyncMock(return_value=mock_opp)

            result = await close_opportunity(opp_id, close_data, mock_user, mock_db)

            assert result.is_won is True
            mock_repo.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_opportunity_lost(self):
        """Testa fechamento como perdida."""
        from modules.crm.models.opportunity import LossReason

        opp_id = str(uuid4())
        close_data = OpportunityClose(
            won=False,
            loss_reason=LossReason.PRICE,
            notes="Perdemos por preco",
        )

        mock_opp = OpportunityFactory.build_lost(id=opp_id)

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.close = AsyncMock(return_value=mock_opp)

            result = await close_opportunity(opp_id, close_data, mock_user, mock_db)

            assert result.is_lost is True

    @pytest.mark.asyncio
    async def test_close_opportunity_not_found(self):
        """Testa fechamento de opportunity inexistente."""
        opp_id = str(uuid4())
        close_data = OpportunityClose(won=True)

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.close = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await close_opportunity(opp_id, close_data, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestDeleteOpportunityEndpoint:
    """Testes para endpoint de exclusao de opportunity."""

    @pytest.mark.asyncio
    async def test_delete_opportunity_success(self):
        """Testa exclusao de opportunity."""
        opp_id = str(uuid4())

        mock_user = MagicMock()
        mock_user.email = "admin@test.com"
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.delete = AsyncMock(return_value=True)

            # Nao deve lancar excecao
            await delete_opportunity(opp_id, mock_user, mock_db)

            mock_repo.delete.assert_called_once_with(opp_id)

    @pytest.mark.asyncio
    async def test_delete_opportunity_not_found(self):
        """Testa exclusao de opportunity inexistente."""
        opp_id = str(uuid4())

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.delete = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await delete_opportunity(opp_id, mock_user, mock_db)

            assert exc_info.value.status_code == 404


class TestGetPipelineStatsEndpoint:
    """Testes para endpoint de estatisticas do pipeline."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self):
        """Testa obtencao de estatisticas."""
        mock_stats = PipelineStats(
            total_opportunities=10,
            open_opportunities=5,
            won_opportunities=3,
            lost_opportunities=2,
            total_value=150000.0,
            weighted_value=75000.0,
            won_value=100000.0,
            lost_value=50000.0,
            win_rate=60.0,
            avg_deal_size=15000.0,
            avg_days_to_close=45.0,
            by_stage={"qualification": 3, "proposal": 2},
            by_priority={"medium": 5, "high": 5},
            overdue_count=1,
        )

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_pipeline_stats = AsyncMock(return_value=mock_stats)

            result = await get_pipeline_stats(mock_user, mock_db)

            assert result.total_opportunities == 10
            assert result.win_rate == 60.0

    @pytest.mark.asyncio
    async def test_get_stats_with_filter(self):
        """Testa estatisticas filtradas por responsavel."""
        owner_id = str(uuid4())
        mock_stats = PipelineStats(
            total_opportunities=3,
            open_opportunities=2,
            won_opportunities=1,
            lost_opportunities=0,
            total_value=45000.0,
            weighted_value=22500.0,
            won_value=20000.0,
            lost_value=0.0,
            win_rate=100.0,
            avg_deal_size=15000.0,
            avg_days_to_close=30.0,
            by_stage={"qualification": 1, "proposal": 1},
            by_priority={"medium": 3},
            overdue_count=0,
        )

        mock_user = MagicMock()
        mock_db = AsyncMock()

        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_pipeline_stats = AsyncMock(return_value=mock_stats)

            result = await get_pipeline_stats(mock_user, mock_db, owner_id=owner_id)

            mock_repo.get_pipeline_stats.assert_called_once_with(owner_id=owner_id)


class TestOpportunityRouter:
    """Testes para configuracao do router."""

    def test_router_prefix(self):
        """Testa prefixo do router."""
        from modules.crm.controllers.opportunity_controller import router

        assert router.prefix == "/opportunities"

    def test_router_tags(self):
        """Testa tags do router."""
        from modules.crm.controllers.opportunity_controller import router

        assert "CRM - Opportunities" in router.tags


class TestOpportunitySchemaValidation:
    """Testes para validacao de schemas."""

    def test_opportunity_create_valid(self):
        """Testa criacao de schema valido."""
        data = OpportunityCreate(
            title="Oportunidade Teste",
            contact_name="Contato",
            contact_email="contato@test.com",
        )

        assert data.title == "Oportunidade Teste"
        assert data.contact_email == "contato@test.com"

    def test_opportunity_create_with_all_fields(self):
        """Testa criacao com todos os campos."""
        data = OpportunityCreate(**TEST_OPPORTUNITY_DATA)

        assert data.title == "Oportunidade Teste"
        assert data.company_name == "Empresa Teste"
        assert data.value == 25000.0

    def test_opportunity_update_partial(self):
        """Testa atualizacao parcial."""
        data = OpportunityUpdate(title="Novo Titulo")

        dump = data.model_dump(exclude_unset=True)
        assert "title" in dump
        assert len(dump) == 1

    def test_opportunity_close_won(self):
        """Testa schema de fechamento ganho."""
        data = OpportunityClose(
            won=True,
            notes="Fechou!",
        )

        assert data.won is True
        assert data.notes == "Fechou!"

    def test_opportunity_close_lost(self):
        """Testa schema de fechamento perdido."""
        from modules.crm.models.opportunity import LossReason

        data = OpportunityClose(
            won=False,
            loss_reason=LossReason.COMPETITOR,
            competitor="Concorrente X",
        )

        assert data.won is False
        assert data.loss_reason == LossReason.COMPETITOR
        assert data.competitor == "Concorrente X"

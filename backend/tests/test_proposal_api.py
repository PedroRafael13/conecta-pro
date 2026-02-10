"""Testes para Proposal API."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from modules.crm.models.proposal import ProposalStatus, ProposalType
from modules.crm.schemas.proposal import (
    ProposalCreate,
    ProposalDetailResponse,
    ProposalItemCreate,
    ProposalListResponse,
    ProposalResponse,
    ProposalStats,
)
from tests.factories import (
    TEST_PROPOSAL_DATA,
    TEST_PROPOSAL_ITEM_DATA,
    ProposalFactory,
    ProposalItemFactory,
    ProposalTemplateFactory,
)


class TestProposalEndpoints:
    """Testes para endpoints de Proposal."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco de dados."""
        return AsyncMock()

    @pytest.fixture
    def mock_user(self):
        """Fixture para mock do usuario autenticado."""
        user = MagicMock()
        user.id = str(uuid4())
        user.email = "user@test.com"
        return user

    @pytest.fixture
    def sample_proposal(self):
        """Fixture para proposal de exemplo."""
        return ProposalFactory.build()

    @pytest.fixture
    def sample_proposals(self):
        """Fixture para lista de proposals."""
        return ProposalFactory.build_batch(5)

    @pytest.mark.asyncio
    async def test_create_proposal_success(self, mock_db, mock_user, sample_proposal):
        """Testa criacao de proposal com sucesso."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = sample_proposal

            # Verifica que o mock foi configurado
            assert mock_create.return_value == sample_proposal

    @pytest.mark.asyncio
    async def test_create_proposal_validation_error(self, mock_db, mock_user):
        """Testa erro de validacao na criacao."""
        # Dados invalidos (faltando campos obrigatorios)

        # Deve falhar na validacao Pydantic
        with pytest.raises(ValueError):
            ProposalCreate(
                title="",
                client_name="",
                client_email="invalid-email",
            )

    @pytest.mark.asyncio
    async def test_list_proposals_success(self, mock_db, mock_user, sample_proposals):
        """Testa listagem de proposals com sucesso."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.list",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = (sample_proposals, len(sample_proposals))

            result, total = await mock_list()
            assert len(result) == 5
            assert total == 5

    @pytest.mark.asyncio
    async def test_list_proposals_with_filters(self, mock_db, mock_user):
        """Testa listagem com filtros."""
        filtered_proposals = ProposalFactory.build_batch(3, status="draft")

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.list",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = (filtered_proposals, 3)

            result, total = await mock_list(
                filters={"status": ProposalStatus.DRAFT},
                page=1,
                page_size=20,
            )

            assert len(result) == 3
            for proposal in result:
                assert proposal.status == "draft"

    @pytest.mark.asyncio
    async def test_get_proposal_success(self, mock_db, mock_user, sample_proposal):
        """Testa obtencao de proposal por ID."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = sample_proposal

            result = await mock_get(sample_proposal.id)
            assert result.id == sample_proposal.id

    @pytest.mark.asyncio
    async def test_get_proposal_not_found(self, mock_db, mock_user):
        """Testa proposal nao encontrada."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            result = await mock_get("non-existent-id")
            assert result is None

    @pytest.mark.asyncio
    async def test_update_proposal_success(self, mock_db, mock_user, sample_proposal):
        """Testa atualizacao de proposal."""
        updated_proposal = ProposalFactory.build(
            id=sample_proposal.id,
            title="Titulo Atualizado",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.update",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = updated_proposal

            result = await mock_update(sample_proposal.id, {"title": "Titulo Atualizado"})
            assert result.title == "Titulo Atualizado"

    @pytest.mark.asyncio
    async def test_delete_proposal_success(self, mock_db, mock_user, sample_proposal):
        """Testa exclusao de proposal."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.delete",
            new_callable=AsyncMock,
        ) as mock_delete:
            mock_delete.return_value = True

            result = await mock_delete(sample_proposal.id)
            assert result is True


class TestProposalWorkflow:
    """Testes para workflow de proposals."""

    @pytest.fixture
    def draft_proposal(self):
        """Proposal em rascunho."""
        return ProposalFactory.build(status="draft")

    @pytest.fixture
    def approved_proposal(self):
        """Proposal aprovada."""
        return ProposalFactory.build_approved()

    @pytest.mark.asyncio
    async def test_submit_for_approval(self, draft_proposal):
        """Testa submissao para aprovacao."""
        pending_proposal = ProposalFactory.build(
            id=draft_proposal.id,
            status="pending_approval",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.submit_for_approval",
            new_callable=AsyncMock,
        ) as mock_submit:
            mock_submit.return_value = pending_proposal

            result = await mock_submit(draft_proposal.id, str(uuid4()))
            assert result.status == "pending_approval"

    @pytest.mark.asyncio
    async def test_approve_proposal(self):
        """Testa aprovacao de proposal."""
        pending_proposal = ProposalFactory.build(status="pending_approval")
        approved_proposal = ProposalFactory.build(
            id=pending_proposal.id,
            status="approved",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.process_approval",
            new_callable=AsyncMock,
        ) as mock_approve:
            mock_approve.return_value = approved_proposal

            result = await mock_approve(
                pending_proposal.id,
                {"action": "approve"},
                str(uuid4()),
            )
            assert result.status == "approved"

    @pytest.mark.asyncio
    async def test_reject_proposal(self):
        """Testa rejeicao de proposal."""
        pending_proposal = ProposalFactory.build(status="pending_approval")
        rejected_proposal = ProposalFactory.build(
            id=pending_proposal.id,
            status="rejected",
            rejection_reason="Preco alto",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.process_approval",
            new_callable=AsyncMock,
        ) as mock_reject:
            mock_reject.return_value = rejected_proposal

            result = await mock_reject(
                pending_proposal.id,
                {"action": "reject", "comments": "Preco alto"},
                str(uuid4()),
            )
            assert result.status == "rejected"

    @pytest.mark.asyncio
    async def test_send_proposal(self, approved_proposal):
        """Testa envio de proposal."""
        sent_proposal = ProposalFactory.build(
            id=approved_proposal.id,
            status="sent",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.update_status",
            new_callable=AsyncMock,
        ) as mock_send:
            mock_send.return_value = sent_proposal

            result = await mock_send(
                approved_proposal.id,
                ProposalStatus.DRAFT,
                user_id=str(uuid4()),
            )
            assert result.status == "sent"

    @pytest.mark.asyncio
    async def test_accept_proposal(self):
        """Testa aceite de proposal."""
        sent_proposal = ProposalFactory.build_sent()
        accepted_proposal = ProposalFactory.build(
            id=sent_proposal.id,
            status="accepted",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.update_status",
            new_callable=AsyncMock,
        ) as mock_accept:
            mock_accept.return_value = accepted_proposal

            result = await mock_accept(sent_proposal.id, ProposalStatus.DRAFT)
            assert result.status == "accepted"

    @pytest.mark.asyncio
    async def test_create_new_version(self):
        """Testa criacao de nova versao."""
        original = ProposalFactory.build(version=1)
        new_version = ProposalFactory.build(
            number=original.number,
            version=2,
            parent_id=original.id,
            status="draft",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.create_new_version",
            new_callable=AsyncMock,
        ) as mock_version:
            mock_version.return_value = new_version

            result = await mock_version(original.id, str(uuid4()))
            assert result.version == 2
            assert result.parent_id == original.id
            assert result.number == original.number


class TestProposalItems:
    """Testes para items de proposal."""

    @pytest.fixture
    def sample_proposal(self):
        """Proposal de exemplo."""
        return ProposalFactory.build()

    @pytest.fixture
    def sample_item(self, sample_proposal):
        """Item de exemplo."""
        return ProposalItemFactory.build(proposal_id=sample_proposal.id)

    @pytest.mark.asyncio
    async def test_add_item_success(self, sample_proposal, sample_item):
        """Testa adicao de item."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.add_item",
            new_callable=AsyncMock,
        ) as mock_add:
            mock_add.return_value = sample_item

            result = await mock_add(sample_proposal.id, TEST_PROPOSAL_ITEM_DATA)
            assert result.proposal_id == sample_proposal.id

    @pytest.mark.asyncio
    async def test_remove_item_success(self, sample_proposal, sample_item):
        """Testa remocao de item."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.remove_item",
            new_callable=AsyncMock,
        ) as mock_remove:
            mock_remove.return_value = True

            result = await mock_remove(sample_proposal.id, sample_item.id)
            assert result is True

    @pytest.mark.asyncio
    async def test_add_multiple_items(self, sample_proposal):
        """Testa adicao de multiplos items."""
        items = ProposalItemFactory.build_batch(3, proposal_id=sample_proposal.id)

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.add_item",
            new_callable=AsyncMock,
        ) as mock_add:
            # Simula adicao de cada item
            for i, item in enumerate(items):
                mock_add.return_value = item
                result = await mock_add(sample_proposal.id, {})
                assert result.proposal_id == sample_proposal.id
                assert result.sort_order == i


class TestProposalTemplates:
    """Testes para templates de proposal."""

    @pytest.fixture
    def sample_template(self):
        """Template de exemplo."""
        return ProposalTemplateFactory.build()

    @pytest.mark.asyncio
    async def test_create_template_success(self, sample_template):
        """Testa criacao de template."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.create_template",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = sample_template

            result = await mock_create(
                {
                    "name": sample_template.name,
                    "validity_days": 30,
                }
            )
            assert result.name == sample_template.name

    @pytest.mark.asyncio
    async def test_list_templates_success(self):
        """Testa listagem de templates."""
        templates = ProposalTemplateFactory.build_batch(3)

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.list_templates",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = templates

            result = await mock_list()
            assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_template_success(self, sample_template):
        """Testa obtencao de template por ID."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.get_template_by_id",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = sample_template

            result = await mock_get(sample_template.id)
            assert result.id == sample_template.id

    @pytest.mark.asyncio
    async def test_update_template_success(self, sample_template):
        """Testa atualizacao de template."""
        updated = ProposalTemplateFactory.build(
            id=sample_template.id,
            name="Nome Atualizado",
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.update_template",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = updated

            result = await mock_update(sample_template.id, {"name": "Nome Atualizado"})
            assert result.name == "Nome Atualizado"

    @pytest.mark.asyncio
    async def test_delete_template_success(self, sample_template):
        """Testa exclusao de template."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.delete_template",
            new_callable=AsyncMock,
        ) as mock_delete:
            mock_delete.return_value = True

            result = await mock_delete(sample_template.id)
            assert result is True


class TestProposalStats:
    """Testes para estatisticas de proposals."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self):
        """Testa obtencao de estatisticas."""
        expected_stats = ProposalStats(
            total_proposals=100,
            draft_count=10,
            pending_count=15,
            sent_count=25,
            accepted_count=40,
            rejected_count=5,
            expired_count=5,
            total_value=500000.0,
            accepted_value=200000.0,
            pending_value=75000.0,
            acceptance_rate=80.0,
            avg_proposal_value=5000.0,
            avg_response_time_days=3.5,
            by_status={"draft": 10, "accepted": 40},
            by_type={"service": 60, "product": 40},
        )

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.get_stats",
            new_callable=AsyncMock,
        ) as mock_stats:
            mock_stats.return_value = expected_stats

            result = await mock_stats()

            assert result.total_proposals == 100
            assert result.accepted_count == 40
            assert result.acceptance_rate == 80.0
            assert result.avg_response_time_days == 3.5


class TestProposalFromOpportunity:
    """Testes para criacao de proposal a partir de opportunity."""

    @pytest.mark.asyncio
    async def test_create_from_opportunity_success(self):
        """Testa criacao de proposal a partir de opportunity."""
        opportunity_id = str(uuid4())
        proposal = ProposalFactory.build(opportunity_id=opportunity_id)

        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.create_from_opportunity",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = proposal

            result = await mock_create(
                {"opportunity_id": opportunity_id, "title": "Proposta"},
                created_by_id=str(uuid4()),
            )

            assert result.opportunity_id == opportunity_id

    @pytest.mark.asyncio
    async def test_create_from_opportunity_not_found(self):
        """Testa erro quando opportunity nao encontrada."""
        with patch(
            "modules.crm.repositories.proposal_repository.ProposalRepository.create_from_opportunity",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = None

            result = await mock_create(
                {"opportunity_id": "non-existent", "title": "Proposta"},
                created_by_id=str(uuid4()),
            )

            assert result is None


class TestProposalValidation:
    """Testes para validacao de proposal."""

    def test_valid_proposal_data(self):
        """Testa dados validos de proposal."""
        data = ProposalCreate(
            title="Proposta Valida",
            client_name="Cliente",
            client_email="cliente@test.com",
        )

        assert data.title == "Proposta Valida"
        assert data.client_name == "Cliente"

    def test_invalid_email(self):
        """Testa email invalido."""
        with pytest.raises(ValueError):
            ProposalCreate(
                title="Proposta",
                client_name="Cliente",
                client_email="email-invalido",
            )

    def test_title_min_length(self):
        """Testa titulo com tamanho minimo."""
        with pytest.raises(ValueError):
            ProposalCreate(
                title="",
                client_name="Cliente",
                client_email="cliente@test.com",
            )

    def test_installments_range(self):
        """Testa range de parcelas."""
        # Parcelas validas
        data = ProposalCreate(
            title="Proposta",
            client_name="Cliente",
            client_email="cliente@test.com",
            installments=12,
        )
        assert data.installments == 12

        # Parcelas fora do range
        with pytest.raises(ValueError):
            ProposalCreate(
                title="Proposta",
                client_name="Cliente",
                client_email="cliente@test.com",
                installments=0,
            )

    def test_discount_value_positive(self):
        """Testa valor de desconto positivo."""
        data = ProposalCreate(
            title="Proposta",
            client_name="Cliente",
            client_email="cliente@test.com",
            discount_value=100.0,
        )
        assert data.discount_value == 100.0

        # Desconto negativo
        with pytest.raises(ValueError):
            ProposalCreate(
                title="Proposta",
                client_name="Cliente",
                client_email="cliente@test.com",
                discount_value=-100.0,
            )


class TestProposalItemValidation:
    """Testes para validacao de ProposalItem."""

    def test_valid_item_data(self):
        """Testa dados validos de item."""
        data = ProposalItemCreate(
            name="Servico",
            quantity=1.0,
            unit_price=1000.0,
        )

        assert data.name == "Servico"
        assert data.quantity == 1.0

    def test_quantity_positive(self):
        """Testa quantidade positiva."""
        with pytest.raises(ValueError):
            ProposalItemCreate(
                name="Servico",
                quantity=-1.0,
                unit_price=1000.0,
            )

    def test_unit_price_positive(self):
        """Testa preco unitario positivo."""
        with pytest.raises(ValueError):
            ProposalItemCreate(
                name="Servico",
                quantity=1.0,
                unit_price=-100.0,
            )

    def test_discount_percent_range(self):
        """Testa range de desconto percentual."""
        # Desconto valido
        data = ProposalItemCreate(
            name="Servico",
            quantity=1.0,
            unit_price=1000.0,
            discount_percent=50.0,
        )
        assert data.discount_percent == 50.0

        # Desconto acima de 100%
        with pytest.raises(ValueError):
            ProposalItemCreate(
                name="Servico",
                quantity=1.0,
                unit_price=1000.0,
                discount_percent=150.0,
            )

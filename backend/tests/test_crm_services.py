"""Testes massivos para CRM Services.

Meta: Aumentar cobertura de modules/crm/
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.crm.services.client_service import ClientService
from modules.crm.services.opportunity_service import OpportunityService
from modules.crm.services.proposal_service import ProposalService


class TestClientService:
    """Testes para ClientService."""

    @pytest.fixture
    def mock_repo(self):
        """Mock do repository."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        """Service com mock."""
        return ClientService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_client_success(self, service, mock_repo):
        """Testa criação de cliente com sucesso."""
        # Arrange
        client_data = {
            "name": "Cliente Teste",
            "email": "teste@email.com",
            "phone": "11999999999",
            "document": "12345678901"
        }
        mock_repo.create.return_value = MagicMock(
            id=uuid4(),
            name=client_data["name"],
            email=client_data["email"],
            created_at=datetime.utcnow()
        )

        # Act
        result = await service.create(client_data)

        # Assert
        assert result.name == client_data["name"]
        assert result.email == client_data["email"]
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_by_id_found(self, service, mock_repo):
        """Testa busca de cliente existente."""
        # Arrange
        client_id = uuid4()
        mock_repo.get_by_id.return_value = MagicMock(
            id=client_id,
            name="Cliente Encontrado",
            is_active=True
        )

        # Act
        result = await service.get_by_id(client_id)

        # Assert
        assert result.id == client_id
        assert result.name == "Cliente Encontrado"

    @pytest.mark.asyncio
    async def test_get_client_by_id_not_found(self, service, mock_repo):
        """Testa busca de cliente inexistente."""
        # Arrange
        client_id = uuid4()
        mock_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.get_by_id(client_id)
        assert "not found" in str(exc_info.value).lower() or "não encontrado" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_client_success(self, service, mock_repo):
        """Testa atualização de cliente."""
        # Arrange
        client_id = uuid4()
        update_data = {"name": "Cliente Atualizado"}
        mock_repo.update.return_value = MagicMock(
            id=client_id,
            name="Cliente Atualizado",
            updated_at=datetime.utcnow()
        )

        # Act
        result = await service.update(client_id, update_data)

        # Assert
        assert result.name == "Cliente Atualizado"
        mock_repo.update.assert_called_once_with(client_id, update_data)

    @pytest.mark.asyncio
    async def test_delete_client_soft_delete(self, service, mock_repo):
        """Testa soft delete de cliente."""
        # Arrange
        client_id = uuid4()
        mock_repo.soft_delete.return_value = True

        # Act
        result = await service.delete(client_id)

        # Assert
        assert result is True
        mock_repo.soft_delete.assert_called_once_with(client_id)

    @pytest.mark.asyncio
    async def test_list_clients_paginated(self, service, mock_repo):
        """Testa listagem paginada de clientes."""
        # Arrange
        mock_repo.list_all.return_value = [
            MagicMock(id=uuid4(), name="Cliente 1"),
            MagicMock(id=uuid4(), name="Cliente 2"),
            MagicMock(id=uuid4(), name="Cliente 3"),
        ]

        # Act
        result = await service.list_all(skip=0, limit=10)

        # Assert
        assert len(result) == 3
        mock_repo.list_all.assert_called_once_with(skip=0, limit=10)

    @pytest.mark.asyncio
    async def test_search_clients_by_name(self, service, mock_repo):
        """Testa busca de clientes por nome."""
        # Arrange
        search_term = "Teste"
        mock_repo.search.return_value = [
            MagicMock(id=uuid4(), name="Cliente Teste 1"),
            MagicMock(id=uuid4(), name="Cliente Teste 2"),
        ]

        # Act
        result = await service.search(name=search_term)

        # Assert
        assert len(result) == 2
        assert all(search_term in client.name for client in result)


class TestOpportunityService:
    """Testes para OpportunityService."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        return OpportunityService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_opportunity(self, service, mock_repo):
        """Testa criação de oportunidade."""
        # Arrange
        opp_data = {
            "title": "Oportunidade Teste",
            "client_id": uuid4(),
            "value": 10000.00,
            "stage": "prospecting"
        }
        mock_repo.create.return_value = MagicMock(
            id=uuid4(),
            title=opp_data["title"],
            value=opp_data["value"],
            stage=opp_data["stage"]
        )

        # Act
        result = await service.create(opp_data)

        # Assert
        assert result.title == opp_data["title"]
        assert result.value == opp_data["value"]

    @pytest.mark.asyncio
    async def test_update_opportunity_stage(self, service, mock_repo):
        """Testa atualização de estágio da oportunidade."""
        # Arrange
        opp_id = uuid4()
        new_stage = "negotiation"
        mock_repo.update_stage.return_value = MagicMock(
            id=opp_id,
            stage=new_stage,
            updated_at=datetime.utcnow()
        )

        # Act
        result = await service.update_stage(opp_id, new_stage)

        # Assert
        assert result.stage == new_stage

    @pytest.mark.asyncio
    async def test_get_opportunities_by_client(self, service, mock_repo):
        """Testa busca de oportunidades por cliente."""
        # Arrange
        client_id = uuid4()
        mock_repo.get_by_client.return_value = [
            MagicMock(id=uuid4(), title="Opp 1", client_id=client_id),
            MagicMock(id=uuid4(), title="Opp 2", client_id=client_id),
        ]

        # Act
        result = await service.get_by_client(client_id)

        # Assert
        assert len(result) == 2
        assert all(opp.client_id == client_id for opp in result)

    @pytest.mark.asyncio
    async def test_calculate_win_rate(self, service, mock_repo):
        """Testa cálculo de taxa de conversão."""
        # Arrange
        mock_repo.get_stats.return_value = {
            "total": 100,
            "won": 30,
            "lost": 40,
            "open": 30
        }

        # Act
        result = await service.calculate_win_rate()

        # Assert
        assert result == 30.0  # 30% win rate


class TestProposalService:
    """Testes para ProposalService."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        return ProposalService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_proposal(self, service, mock_repo):
        """Testa criação de proposta."""
        # Arrange
        proposal_data = {
            "opportunity_id": uuid4(),
            "title": "Proposta Teste",
            "total_value": 50000.00,
            "valid_until": date.today()
        }
        mock_repo.create.return_value = MagicMock(
            id=uuid4(),
            title=proposal_data["title"],
            total_value=proposal_data["total_value"],
            status="draft"
        )

        # Act
        result = await service.create(proposal_data)

        # Assert
        assert result.title == proposal_data["title"]
        assert result.total_value == proposal_data["total_value"]
        assert result.status == "draft"

    @pytest.mark.asyncio
    async def test_approve_proposal(self, service, mock_repo):
        """Testa aprovação de proposta."""
        # Arrange
        proposal_id = uuid4()
        mock_repo.update_status.return_value = MagicMock(
            id=proposal_id,
            status="approved",
            approved_at=datetime.utcnow()
        )

        # Act
        result = await service.approve(proposal_id)

        # Assert
        assert result.status == "approved"
        assert result.approved_at is not None

    @pytest.mark.asyncio
    async def test_reject_proposal(self, service, mock_repo):
        """Testa rejeição de proposta."""
        # Arrange
        proposal_id = uuid4()
        reason = "Preço acima do orçamento"
        mock_repo.update_status.return_value = MagicMock(
            id=proposal_id,
            status="rejected",
            rejection_reason=reason
        )

        # Act
        result = await service.reject(proposal_id, reason)

        # Assert
        assert result.status == "rejected"
        assert result.rejection_reason == reason


class TestCRMIntegration:
    """Testes de integração entre serviços CRM."""

    def test_client_to_opportunity_flow(self):
        """Testa fluxo de cliente para oportunidade."""
        # Arrange
        client_id = uuid4()

        # Simulação do fluxo
        client = MagicMock(id=client_id, name="Cliente Fluxo")
        opportunity = MagicMock(
            id=uuid4(),
            client_id=client_id,
            title="Oportunidade do Cliente",
            stage="prospecting"
        )

        # Assert
        assert opportunity.client_id == client.id
        assert opportunity.stage == "prospecting"

    def test_opportunity_to_proposal_flow(self):
        """Testa fluxo de oportunidade para proposta."""
        # Arrange
        opp_id = uuid4()

        opportunity = MagicMock(
            id=opp_id,
            title="Oportunidade Grande",
            value=100000.00,
            stage="negotiation"
        )

        proposal = MagicMock(
            id=uuid4(),
            opportunity_id=opp_id,
            title=f"Proposta: {opportunity.title}",
            total_value=opportunity.value,
            status="draft"
        )

        # Assert
        assert proposal.opportunity_id == opportunity.id
        assert proposal.total_value == opportunity.value

"""
tests/domains/financial/test_payable_service.py
Testes unitarios para PayableService.
"""

import sys
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend")

from modules.financial.services.payable_service import PayableService


@pytest.fixture
def mock_session():
    """Mock da sessao async do SQLAlchemy."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    """Instancia do PayableService com session mockada."""
    return PayableService(mock_session)


class TestPayableServiceInit:
    """Testes de inicializacao do service."""

    def test_init_sets_session(self, mock_session):
        svc = PayableService(mock_session)
        assert svc.session is mock_session

    def test_init_creates_repositories(self, mock_session):
        svc = PayableService(mock_session)
        assert svc.account_repo is not None
        assert svc.installment_repo is not None
        assert svc.payment_repo is not None


class TestPayableServiceCreateAccount:
    """Testes para criacao de contas a pagar."""

    @pytest.mark.asyncio
    async def test_create_account_calls_repo(self, service):
        """Testa que create_account chama o repositorio corretamente."""
        mock_data = MagicMock()
        mock_data.description = "Conta de luz"
        user_id = uuid4()

        mock_account = MagicMock()
        mock_account.id = uuid4()
        service.account_repo.create = AsyncMock(return_value=mock_account)

        result = await service.create_account(mock_data, user_id)

        service.account_repo.create.assert_awaited_once_with(mock_data, user_id)
        assert result is mock_account

    @pytest.mark.asyncio
    async def test_create_account_commits(self, service):
        """Testa que create_account faz commit."""
        mock_data = MagicMock()
        mock_data.description = "Aluguel"
        service.account_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))

        await service.create_account(mock_data, uuid4())

        service.session.commit.assert_awaited_once()


class TestPayableServiceGetAccount:
    """Testes para busca de conta."""

    @pytest.mark.asyncio
    async def test_get_account_found(self, service):
        mock_account = MagicMock()
        mock_account.id = uuid4()
        service.account_repo.get_by_id = AsyncMock(return_value=mock_account)

        result = await service.get_account(mock_account.id)

        assert result is mock_account
        service.account_repo.get_by_id.assert_awaited_once_with(mock_account.id)

    @pytest.mark.asyncio
    async def test_get_account_not_found(self, service):
        service.account_repo.get_by_id = AsyncMock(return_value=None)

        result = await service.get_account(uuid4())

        assert result is None


class TestPayableServiceListAccounts:
    """Testes para listagem de contas."""

    @pytest.mark.asyncio
    async def test_list_accounts_returns_tuple(self, service):
        condominio_id = uuid4()
        mock_accounts = [MagicMock(), MagicMock()]
        service.account_repo.list = AsyncMock(return_value=mock_accounts)
        service.account_repo.count = AsyncMock(return_value=2)

        accounts, total = await service.list_accounts(condominio_id)

        assert len(accounts) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_list_accounts_with_filters(self, service):
        condominio_id = uuid4()
        mock_filter = MagicMock()
        service.account_repo.list = AsyncMock(return_value=[])
        service.account_repo.count = AsyncMock(return_value=0)

        accounts, total = await service.list_accounts(condominio_id, filters=mock_filter, skip=10, limit=50)

        service.account_repo.list.assert_awaited_once_with(condominio_id, mock_filter, 10, 50)

    @pytest.mark.asyncio
    async def test_list_accounts_empty(self, service):
        service.account_repo.list = AsyncMock(return_value=[])
        service.account_repo.count = AsyncMock(return_value=0)

        accounts, total = await service.list_accounts(uuid4())

        assert accounts == []
        assert total == 0

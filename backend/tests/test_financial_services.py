"""Testes massivos para Financial Services.

Meta: Aumentar cobertura de modules/financial/
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


class TestAccountService:
    """Testes para AccountService (Contas)."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        from modules.financial.services.account_service import AccountService
        return AccountService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_account_success(self, service, mock_repo):
        """Testa criação de conta com sucesso."""
        account_data = {
            "name": "Conta Corrente Principal",
            "bank_code": "001",
            "agency": "0001",
            "account_number": "12345-6",
            "balance": Decimal("10000.00")
        }
        mock_repo.create.return_value = MagicMock(
            id=uuid4(),
            name=account_data["name"],
            balance=account_data["balance"],
            is_active=True
        )

        result = await service.create(account_data)

        assert result.name == account_data["name"]
        assert result.balance == account_data["balance"]

    @pytest.mark.asyncio
    async def test_get_balance(self, service, mock_repo):
        """Testa consulta de saldo."""
        account_id = uuid4()
        mock_repo.get_balance.return_value = Decimal("5000.00")

        result = await service.get_balance(account_id)

        assert result == Decimal("5000.00")

    @pytest.mark.asyncio
    async def test_transfer_between_accounts(self, service, mock_repo):
        """Testa transferência entre contas."""
        from_account = uuid4()
        to_account = uuid4()
        amount = Decimal("1000.00")

        mock_repo.transfer.return_value = MagicMock(
            id=uuid4(),
            from_account_id=from_account,
            to_account_id=to_account,
            amount=amount,
            status="completed"
        )

        result = await service.transfer(from_account, to_account, amount)

        assert result.amount == amount
        assert result.status == "completed"


class TestPayableService:
    """Testes para PayableService (Contas a Pagar)."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        from modules.financial.services.payable_service import PayableService
        return PayableService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_payable(self, service, mock_repo):
        """Testa criação de conta a pagar."""
        payable_data = {
            "supplier_id": uuid4(),
            "description": "Pagamento Fornecedor",
            "amount": Decimal("5000.00"),
            "due_date": date.today(),
            "status": "pending"
        }
        mock_repo.create.return_value = MagicMock(
            id=uuid4(),
            description=payable_data["description"],
            amount=payable_data["amount"],
            status="pending"
        )

        result = await service.create(payable_data)

        assert result.amount == payable_data["amount"]
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_pay_payable(self, service, mock_repo):
        """Testa pagamento de conta."""
        payable_id = uuid4()
        payment_data = {
            "paid_amount": Decimal("5000.00"),
            "paid_date": date.today(),
            "payment_method": "bank_transfer"
        }
        mock_repo.pay.return_value = MagicMock(
            id=payable_id,
            status="paid",
            paid_amount=payment_data["paid_amount"],
            paid_date=payment_data["paid_date"]
        )

        result = await service.pay(payable_id, payment_data)

        assert result.status == "paid"
        assert result.paid_amount == payment_data["paid_amount"]

    @pytest.mark.asyncio
    async def test_get_overdue_payables(self, service, mock_repo):
        """Testa busca de contas vencidas."""
        mock_repo.get_overdue.return_value = [
            MagicMock(id=uuid4(), description="Conta 1", due_date=date(2024, 1, 1)),
            MagicMock(id=uuid4(), description="Conta 2", due_date=date(2024, 1, 5)),
        ]

        result = await service.get_overdue()

        assert len(result) == 2


class TestReceivableService:
    """Testes para ReceivableService (Contas a Receber)."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        from modules.financial.services.receivable_service import ReceivableService
        return ReceivableService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_receivable(self, service, mock_repo):
        """Testa criação de conta a receber."""
        receivable_data = {
            "client_id": uuid4(),
            "description": "Fatura Cliente",
            "amount": Decimal("8000.00"),
            "due_date": date.today(),
            "status": "pending"
        }
        mock_repo.create.return_value = MagicMock(
            id=uuid4(),
            amount=receivable_data["amount"],
            status="pending"
        )

        result = await service.create(receivable_data)

        assert result.amount == receivable_data["amount"]

    @pytest.mark.asyncio
    async def test_receive_payment(self, service, mock_repo):
        """Testa recebimento de pagamento."""
        receivable_id = uuid4()
        mock_repo.receive.return_value = MagicMock(
            id=receivable_id,
            status="received",
            received_amount=Decimal("8000.00"),
            received_date=date.today()
        )

        result = await service.receive(receivable_id, Decimal("8000.00"))

        assert result.status == "received"


class TestCashFlowService:
    """Testes para CashFlowService (Fluxo de Caixa)."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        from modules.financial.services.cashflow_service import CashFlowService
        return CashFlowService(mock_repo)

    @pytest.mark.asyncio
    async def test_get_daily_cash_flow(self, service, mock_repo):
        """Testa fluxo de caixa diário."""
        target_date = date.today()
        mock_repo.get_daily_flow.return_value = {
            "date": target_date,
            "opening_balance": Decimal("10000.00"),
            "inflows": Decimal("5000.00"),
            "outflows": Decimal("3000.00"),
            "closing_balance": Decimal("12000.00")
        }

        result = await service.get_daily_flow(target_date)

        assert result["closing_balance"] == Decimal("12000.00")

    @pytest.mark.asyncio
    async def test_get_monthly_projection(self, service, mock_repo):
        """Testa projeção mensal."""
        mock_repo.get_monthly_projection.return_value = {
            "month": "2024-02",
            "expected_inflows": Decimal("50000.00"),
            "expected_outflows": Decimal("40000.00"),
            "projected_balance": Decimal("10000.00")
        }

        result = await service.get_monthly_projection(2024, 2)

        assert result["projected_balance"] == Decimal("10000.00")


class TestDREService:
    """Testes para DREService (Demonstração do Resultado do Exercício)."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo):
        from modules.financial.services.dre_service import DREService
        return DREService(mock_repo)

    @pytest.mark.asyncio
    async def test_generate_dre(self, service, mock_repo):
        """Testa geração do DRE."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        mock_repo.generate.return_value = MagicMock(
            period_start=start_date,
            period_end=end_date,
            total_revenue=Decimal("100000.00"),
            total_expenses=Decimal("70000.00"),
            net_income=Decimal("30000.00"),
            net_margin=Decimal("30.0")
        )

        result = await service.generate(start_date, end_date)

        assert result.net_income == Decimal("30000.00")
        assert result.net_margin == Decimal("30.0")

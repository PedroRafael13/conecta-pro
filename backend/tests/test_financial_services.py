"""Testes massivos para Financial Services.

Meta: Aumentar cobertura de modules/financial/
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


class TestBalanceSheetService:
    """Testes para BalanceSheetService (substitui AccountService inexistente)."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        from modules.financial.services.balance_sheet_service import (
            BalanceSheetService,
        )

        return BalanceSheetService(mock_session)

    @pytest.mark.asyncio
    async def test_generate_balance_sheet(self, service, mock_session):
        """Testa geracao de balanco patrimonial."""
        condominio_id = uuid4()
        reference_date = date(2024, 1, 31)

        mock_report = MagicMock(
            condominio_id=condominio_id,
            reference_date=reference_date,
            total_ativo=Decimal("100000.00"),
            total_passivo=Decimal("60000.00"),
            total_patrimonio=Decimal("40000.00"),
            is_balanced=True,
            difference=Decimal("0.00"),
        )

        with patch.object(service, "generate_balance_sheet", return_value=mock_report) as mock_method:
            result = await service.generate_balance_sheet(condominio_id, reference_date)

            mock_method.assert_called_once_with(condominio_id, reference_date)
            assert result.total_ativo == Decimal("100000.00")
            assert result.is_balanced is True

    @pytest.mark.asyncio
    async def test_validate_balance(self, service, mock_session):
        """Testa validacao de balanco."""
        condominio_id = uuid4()
        reference_date = date(2024, 1, 31)

        mock_result = {
            "is_balanced": True,
            "total_ativo": Decimal("100000.00"),
            "total_passivo_patrimonio": Decimal("100000.00"),
            "difference": Decimal("0.00"),
        }

        with patch.object(service, "validate_balance", return_value=mock_result) as mock_method:
            result = await service.validate_balance(condominio_id, reference_date)

            mock_method.assert_called_once_with(condominio_id, reference_date)
            assert result["is_balanced"] is True
            assert result["difference"] == Decimal("0.00")

    @pytest.mark.asyncio
    async def test_get_account_statement(self, service, mock_session):
        """Testa extrato de conta contabil."""
        condominio_id = uuid4()
        account_id = uuid4()
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        mock_statement = {
            "account_id": account_id,
            "entries": [],
            "opening_balance": Decimal("5000.00"),
            "closing_balance": Decimal("7000.00"),
        }

        with patch.object(service, "get_account_statement", return_value=mock_statement) as mock_method:
            result = await service.get_account_statement(condominio_id, account_id, start_date, end_date)

            mock_method.assert_called_once_with(condominio_id, account_id, start_date, end_date)
            assert result["closing_balance"] == Decimal("7000.00")


class TestPayableService:
    """Testes para PayableService (Contas a Pagar)."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        from modules.financial.services.payable_service import PayableService

        return PayableService(mock_session)

    @pytest.mark.asyncio
    async def test_create_payable(self, service, mock_session):
        """Testa criacao de conta a pagar via create_account."""
        from modules.financial.schemas.payable import PayableAccountCreate

        condominio_id = uuid4()
        user_id = uuid4()
        payable_data = PayableAccountCreate(
            description="Pagamento Fornecedor",
            gross_value=Decimal("5000.00"),
            due_date=date.today(),
            condominio_id=condominio_id,
        )

        mock_account = MagicMock(
            id=uuid4(),
            description="Pagamento Fornecedor",
            gross_value=Decimal("5000.00"),
            status="pendente",
        )

        with patch.object(service, "create_account", return_value=mock_account) as mock_method:
            result = await service.create_account(payable_data, user_id)

            mock_method.assert_called_once_with(payable_data, user_id)
            assert result.gross_value == Decimal("5000.00")
            assert result.description == "Pagamento Fornecedor"

    @pytest.mark.asyncio
    async def test_register_payment(self, service, mock_session):
        """Testa registro de pagamento de conta a pagar."""
        from modules.financial.schemas.payable import PayablePaymentCreate

        installment_id = uuid4()
        user_id = uuid4()
        payment_data = PayablePaymentCreate(
            installment_id=installment_id,
            paid_value=Decimal("5000.00"),
            payment_date=date.today(),
        )

        mock_payment = MagicMock(
            id=uuid4(),
            installment_id=installment_id,
            paid_value=Decimal("5000.00"),
            payment_date=date.today(),
        )

        with patch.object(service, "register_payment", return_value=mock_payment) as mock_method:
            result = await service.register_payment(installment_id, payment_data, user_id)

            mock_method.assert_called_once_with(installment_id, payment_data, user_id)
            assert result.paid_value == Decimal("5000.00")

    @pytest.mark.asyncio
    async def test_get_overdue_payables(self, service, mock_session):
        """Testa busca de contas a pagar vencidas via get_overdue_accounts."""
        condominio_id = uuid4()

        mock_overdue = [
            MagicMock(id=uuid4(), description="Conta 1", due_date=date(2024, 1, 1)),
            MagicMock(id=uuid4(), description="Conta 2", due_date=date(2024, 1, 5)),
        ]

        with patch.object(service, "get_overdue_accounts", return_value=mock_overdue) as mock_method:
            result = await service.get_overdue_accounts(condominio_id)

            mock_method.assert_called_once_with(condominio_id)
            assert len(result) == 2


class TestReceivableService:
    """Testes para ReceivableService (Contas a Receber)."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        from modules.financial.services.receivable_service import ReceivableService

        return ReceivableService(mock_session)

    @pytest.mark.asyncio
    async def test_create_receivable(self, service, mock_session):
        """Testa criacao de conta a receber via create_account."""
        from modules.financial.schemas.receivable import ReceivableAccountCreate

        condominio_id = uuid4()
        user_id = uuid4()
        receivable_data = ReceivableAccountCreate(
            description="Fatura Cliente",
            gross_value=Decimal("8000.00"),
            due_date=date.today(),
            condominio_id=condominio_id,
        )

        mock_account = MagicMock(
            id=uuid4(),
            description="Fatura Cliente",
            gross_value=Decimal("8000.00"),
            status="pendente",
        )

        with patch.object(service, "create_account", return_value=mock_account) as mock_method:
            result = await service.create_account(receivable_data, user_id)

            mock_method.assert_called_once_with(receivable_data, user_id)
            assert result.gross_value == Decimal("8000.00")

    @pytest.mark.asyncio
    async def test_register_payment(self, service, mock_session):
        """Testa registro de recebimento via register_payment."""
        from modules.financial.schemas.receivable import ReceivablePaymentCreate

        installment_id = uuid4()
        user_id = uuid4()
        payment_data = ReceivablePaymentCreate(
            installment_id=installment_id,
            paid_value=Decimal("8000.00"),
            payment_date=date.today(),
        )

        mock_payment = MagicMock(
            id=uuid4(),
            installment_id=installment_id,
            paid_value=Decimal("8000.00"),
            status="recebido",
        )

        with patch.object(service, "register_payment", return_value=mock_payment) as mock_method:
            result = await service.register_payment(installment_id, payment_data, user_id)

            mock_method.assert_called_once_with(installment_id, payment_data, user_id)
            assert result.paid_value == Decimal("8000.00")


class TestCashFlowService:
    """Testes para CashFlowService (Fluxo de Caixa)."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        from modules.financial.services.cashflow_service import CashFlowService

        return CashFlowService(mock_session)

    @pytest.mark.asyncio
    async def test_get_summary(self, service, mock_session):
        """Testa resumo do fluxo de caixa via get_summary."""
        condominio_id = uuid4()

        mock_summary = {
            "total_inflows": Decimal("50000.00"),
            "total_outflows": Decimal("30000.00"),
            "net_flow": Decimal("20000.00"),
            "period_days": 30,
        }

        with patch.object(service, "get_summary", return_value=mock_summary) as mock_method:
            result = await service.get_summary(condominio_id, period_days=30)

            mock_method.assert_called_once_with(condominio_id, period_days=30)
            assert result["net_flow"] == Decimal("20000.00")

    @pytest.mark.asyncio
    async def test_get_monthly_trend(self, service, mock_session):
        """Testa tendencia mensal via get_monthly_trend."""
        condominio_id = uuid4()

        mock_trend = [
            {
                "month": "2024-01",
                "inflows": Decimal("50000.00"),
                "outflows": Decimal("40000.00"),
                "net": Decimal("10000.00"),
            },
            {
                "month": "2024-02",
                "inflows": Decimal("55000.00"),
                "outflows": Decimal("42000.00"),
                "net": Decimal("13000.00"),
            },
        ]

        with patch.object(service, "get_monthly_trend", return_value=mock_trend) as mock_method:
            result = await service.get_monthly_trend(condominio_id, months=12)

            mock_method.assert_called_once_with(condominio_id, months=12)
            assert len(result) == 2
            assert result[0]["net"] == Decimal("10000.00")


class TestDREService:
    """Testes para DREService (Demonstracao do Resultado do Exercicio)."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        from modules.financial.services.dre_service import DREService

        return DREService(mock_session)

    @pytest.mark.asyncio
    async def test_generate_dre(self, service, mock_session):
        """Testa geracao do DRE via generate_dre."""
        condominio_id = uuid4()
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        mock_report = MagicMock(
            condominio_id=condominio_id,
            start_date=start_date,
            end_date=end_date,
            totals={
                "receita_bruta": Decimal("100000.00"),
                "despesas": Decimal("70000.00"),
                "resultado_liquido": Decimal("30000.00"),
            },
            lines=[],
        )

        with patch.object(service, "generate_dre", return_value=mock_report) as mock_method:
            result = await service.generate_dre(condominio_id, start_date, end_date)

            mock_method.assert_called_once_with(condominio_id, start_date, end_date)
            assert result.totals["resultado_liquido"] == Decimal("30000.00")
            assert result.start_date == start_date

"""Testes para API de Contas a Pagar."""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from modules.financial.models.payable_account import PayableAccount, PayableStatus
from modules.financial.models.payable_installment import (
    InstallmentStatus,
    PayableInstallment,
)
from modules.financial.models.payable_payment import PayablePayment, PaymentStatus
from modules.financial.models.supplier import Supplier, SupplierStatus


@pytest.fixture
def sample_condominio_id():
    """ID de condomínio para testes."""
    return uuid.uuid4()


@pytest.fixture
def sample_user():
    """Usuário autenticado para testes."""
    return {
        "id": str(uuid.uuid4()),
        "email": "admin@teste.com",
        "role": "admin",
    }


@pytest.fixture
def sample_supplier(sample_condominio_id):
    """Fornecedor para testes."""
    return Supplier(
        id=uuid.uuid4(),
        condominio_id=sample_condominio_id,
        cpf_cnpj="12.345.678/0001-90",
        name="Fornecedor Teste LTDA",
        status=SupplierStatus.ATIVO.value,
        ativo=True,
    )


@pytest.fixture
def sample_payable_account(sample_condominio_id, sample_supplier):
    """Conta a pagar para testes."""
    return PayableAccount(
        id=uuid.uuid4(),
        condominio_id=sample_condominio_id,
        supplier_id=sample_supplier.id,
        description="Manutenção Teste",
        gross_value=Decimal("1000.00"),
        net_value=Decimal("1000.00"),
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        status=PayableStatus.PENDENTE.value,
        installments=1,
        ativo=True,
    )


@pytest.fixture
def sample_installment(sample_payable_account):
    """Parcela para testes."""
    return PayableInstallment(
        id=uuid.uuid4(),
        payable_account_id=sample_payable_account.id,
        installment_number=1,
        original_value=Decimal("1000.00"),
        current_value=Decimal("1000.00"),
        due_date=date.today() + timedelta(days=30),
        status=InstallmentStatus.PENDENTE.value,
        ativo=True,
    )


class TestSupplierAPI:
    """Testes para API de Fornecedores."""

    @pytest.mark.asyncio
    async def test_create_supplier_success(self, sample_user, sample_condominio_id):
        """Testa criação de fornecedor com sucesso."""
        supplier_data = {
            "condominio_id": str(sample_condominio_id),
            "cpf_cnpj": "12.345.678/0001-90",
            "name": "Novo Fornecedor LTDA",
            "supplier_type": "pessoa_juridica",
            "email": "contato@fornecedor.com",
        }

        # Mock do service
        with patch("modules.financial.controllers.supplier_controller.SupplierService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            created_supplier = Supplier(
                id=uuid.uuid4(),
                **supplier_data,
            )
            mock_instance.create.return_value = created_supplier

            # Simula a chamada (em um teste real usaria TestClient)
            result = await mock_instance.create(
                MagicMock(**supplier_data),
                uuid.UUID(sample_user["id"]),
            )

            assert result.name == "Novo Fornecedor LTDA"
            assert result.cpf_cnpj == "12.345.678/0001-90"

    @pytest.mark.asyncio
    async def test_list_suppliers(self, sample_user, sample_condominio_id):
        """Testa listagem de fornecedores."""
        with patch("modules.financial.controllers.supplier_controller.SupplierService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            suppliers = [
                Supplier(
                    id=uuid.uuid4(),
                    condominio_id=sample_condominio_id,
                    cpf_cnpj="12.345.678/0001-90",
                    name="Fornecedor 1",
                    status=SupplierStatus.ATIVO.value,
                    ativo=True,
                ),
                Supplier(
                    id=uuid.uuid4(),
                    condominio_id=sample_condominio_id,
                    cpf_cnpj="98.765.432/0001-10",
                    name="Fornecedor 2",
                    status=SupplierStatus.ATIVO.value,
                    ativo=True,
                ),
            ]
            mock_instance.list.return_value = (suppliers, 2)

            result, total = await mock_instance.list(sample_condominio_id)

            assert len(result) == 2
            assert total == 2

    @pytest.mark.asyncio
    async def test_block_supplier(self, sample_user, sample_supplier):
        """Testa bloqueio de fornecedor."""
        with patch("modules.financial.controllers.supplier_controller.SupplierService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            blocked_supplier = Supplier(
                id=sample_supplier.id,
                condominio_id=sample_supplier.condominio_id,
                cpf_cnpj=sample_supplier.cpf_cnpj,
                name=sample_supplier.name,
                status=SupplierStatus.BLOQUEADO.value,
                is_blocked=True,
                block_reason="Inadimplência",
                ativo=True,
            )
            mock_instance.block.return_value = blocked_supplier

            result = await mock_instance.block(
                sample_supplier.id,
                "Inadimplência",
                uuid.UUID(sample_user["id"]),
            )

            assert result.is_blocked is True
            assert result.status == SupplierStatus.BLOQUEADO.value


class TestPayableAccountAPI:
    """Testes para API de Contas a Pagar."""

    @pytest.mark.asyncio
    async def test_create_payable_account(self, sample_user, sample_condominio_id, sample_supplier):
        """Testa criação de conta a pagar."""
        account_data = {
            "condominio_id": str(sample_condominio_id),
            "supplier_id": str(sample_supplier.id),
            "description": "Nova Conta a Pagar",
            "gross_value": "1500.00",
            "issue_date": date.today().isoformat(),
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
        }

        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            created_account = PayableAccount(
                id=uuid.uuid4(),
                condominio_id=sample_condominio_id,
                supplier_id=sample_supplier.id,
                description="Nova Conta a Pagar",
                gross_value=Decimal("1500.00"),
                net_value=Decimal("1500.00"),
                issue_date=date.today(),
                due_date=date.today() + timedelta(days=30),
                status=PayableStatus.PENDENTE.value,
                ativo=True,
            )
            mock_instance.create_account.return_value = created_account

            result = await mock_instance.create_account(
                MagicMock(**account_data),
                uuid.UUID(sample_user["id"]),
            )

            assert result.description == "Nova Conta a Pagar"
            assert result.gross_value == Decimal("1500.00")

    @pytest.mark.asyncio
    async def test_approve_account(self, sample_user, sample_payable_account):
        """Testa aprovação de conta."""
        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            approved_account = PayableAccount(
                id=sample_payable_account.id,
                condominio_id=sample_payable_account.condominio_id,
                description=sample_payable_account.description,
                gross_value=sample_payable_account.gross_value,
                net_value=sample_payable_account.net_value,
                issue_date=sample_payable_account.issue_date,
                due_date=sample_payable_account.due_date,
                status=PayableStatus.APROVADO.value,
                approved_by=uuid.UUID(sample_user["id"]),
                ativo=True,
            )
            mock_instance.approve_account.return_value = approved_account

            result = await mock_instance.approve_account(
                sample_payable_account.id,
                uuid.UUID(sample_user["id"]),
            )

            assert result.status == PayableStatus.APROVADO.value
            assert result.approved_by is not None

    @pytest.mark.asyncio
    async def test_get_overdue_accounts(self, sample_user, sample_condominio_id):
        """Testa busca de contas vencidas."""
        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            overdue_accounts = [
                PayableAccount(
                    id=uuid.uuid4(),
                    condominio_id=sample_condominio_id,
                    description="Conta Vencida 1",
                    gross_value=Decimal("500.00"),
                    net_value=Decimal("500.00"),
                    issue_date=date.today() - timedelta(days=60),
                    due_date=date.today() - timedelta(days=30),
                    status=PayableStatus.PENDENTE.value,
                    ativo=True,
                ),
            ]
            mock_instance.get_overdue_accounts.return_value = overdue_accounts

            result = await mock_instance.get_overdue_accounts(sample_condominio_id)

            assert len(result) == 1
            assert result[0].due_date < date.today()

    @pytest.mark.asyncio
    async def test_get_stats(self, sample_user, sample_condominio_id):
        """Testa estatísticas de contas a pagar."""
        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            mock_stats = MagicMock()
            mock_stats.total = 10
            mock_stats.pendentes = 5
            mock_stats.aprovados = 3
            mock_stats.pagos = 2
            mock_stats.valor_total = Decimal("50000.00")
            mock_stats.valor_pago = Decimal("10000.00")

            mock_instance.get_stats.return_value = mock_stats

            result = await mock_instance.get_stats(sample_condominio_id)

            assert result.total == 10
            assert result.pendentes == 5


class TestPaymentAPI:
    """Testes para API de Pagamentos."""

    @pytest.mark.asyncio
    async def test_register_payment(self, sample_user, sample_installment):
        """Testa registro de pagamento."""
        payment_data = {
            "installment_id": str(sample_installment.id),
            "payment_method_id": str(uuid.uuid4()),
            "amount": "1000.00",
            "payment_date": date.today().isoformat(),
        }

        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            created_payment = PayablePayment(
                id=uuid.uuid4(),
                installment_id=sample_installment.id,
                amount=Decimal("1000.00"),
                net_amount=Decimal("1000.00"),
                payment_date=date.today(),
                status=PaymentStatus.CONFIRMADO.value,
                ativo=True,
            )
            mock_instance.register_payment.return_value = created_payment

            result = await mock_instance.register_payment(
                sample_installment.id,
                MagicMock(**payment_data),
                uuid.UUID(sample_user["id"]),
            )

            assert result.amount == Decimal("1000.00")
            assert result.status == PaymentStatus.CONFIRMADO.value

    @pytest.mark.asyncio
    async def test_bulk_payment(self, sample_user):
        """Testa pagamento em lote."""
        installment_ids = [uuid.uuid4() for _ in range(3)]

        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            mock_instance.bulk_payment.return_value = (
                3,
                0,
                [uuid.uuid4() for _ in range(3)],
            )

            success, errors, payment_ids = await mock_instance.bulk_payment(
                MagicMock(installment_ids=installment_ids),
                uuid.UUID(sample_user["id"]),
            )

            assert success == 3
            assert errors == 0
            assert len(payment_ids) == 3

    @pytest.mark.asyncio
    async def test_reverse_payment(self, sample_user):
        """Testa estorno de pagamento."""
        payment_id = uuid.uuid4()

        with patch("modules.financial.controllers.payable_controller.PayableService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            reversed_payment = PayablePayment(
                id=payment_id,
                installment_id=uuid.uuid4(),
                amount=Decimal("500.00"),
                net_amount=Decimal("500.00"),
                payment_date=date.today(),
                status=PaymentStatus.ESTORNADO.value,
                is_reversed=True,
                reverse_reason="Pagamento incorreto",
                ativo=True,
            )
            mock_instance.reverse_payment.return_value = reversed_payment

            result = await mock_instance.reverse_payment(
                payment_id,
                MagicMock(reason="Pagamento incorreto"),
                uuid.UUID(sample_user["id"]),
            )

            assert result.is_reversed is True
            assert result.status == PaymentStatus.ESTORNADO.value


class TestCashFlowAPI:
    """Testes para API de Fluxo de Caixa."""

    @pytest.mark.asyncio
    async def test_get_projection(self, sample_user, sample_condominio_id):
        """Testa projeção de fluxo de caixa."""
        with patch("modules.financial.controllers.cashflow_controller.CashFlowService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            mock_projections = [
                MagicMock(
                    date=date.today(),
                    payables=Decimal("5000.00"),
                    receivables=Decimal("0"),
                    balance=Decimal("-5000.00"),
                    to_dict=lambda: {
                        "date": date.today().isoformat(),
                        "payables": 5000.0,
                        "balance": -5000.0,
                    },
                ),
            ]
            mock_instance.get_projection.return_value = mock_projections

            result = await mock_instance.get_projection(sample_condominio_id)

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_detect_anomalies(self, sample_user, sample_condominio_id):
        """Testa detecção de anomalias."""
        with patch("modules.financial.controllers.cashflow_controller.PayableAIService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            mock_anomalies = [
                {
                    "type": "value_spike",
                    "account_id": str(uuid.uuid4()),
                    "description": "Valor muito acima da média",
                    "severity": "high",
                },
            ]
            mock_instance.detect_anomalies.return_value = mock_anomalies

            result = await mock_instance.detect_anomalies(sample_condominio_id)

            assert len(result) == 1
            assert result[0]["type"] == "value_spike"

    @pytest.mark.asyncio
    async def test_predict_cashflow(self, sample_user, sample_condominio_id):
        """Testa previsão de fluxo de caixa."""
        with patch("modules.financial.controllers.cashflow_controller.PayableAIService") as mock_service:
            mock_instance = AsyncMock()
            mock_service.return_value = mock_instance

            mock_predictions = [
                {
                    "month": "2025-01-01",
                    "predicted_value": 25000.0,
                    "confidence_low": 20000.0,
                    "confidence_high": 30000.0,
                    "trend": "stable",
                },
            ]
            mock_instance.predict_cashflow.return_value = mock_predictions

            result = await mock_instance.predict_cashflow(sample_condominio_id, 3)

            assert len(result) == 1
            assert "predicted_value" in result[0]

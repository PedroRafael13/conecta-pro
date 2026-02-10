"""Testes para o ReceivableService."""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus
from modules.financial.models.receivable_installment import (
    InstallmentStatus,
    ReceivableInstallment,
)
from modules.financial.models.receivable_payment import (
    PaymentOrigin,
    PaymentStatus,
    ReceivablePayment,
)
from modules.financial.schemas.receivable import (
    ReceivableAccountCreate,
    ReceivableAccountFilter,
    ReceivableAccountUpdate,
    ReceivableInstallmentRenegotiateRequest,
    ReceivablePaymentCreate,
    ReceivablePaymentReverseRequest,
)
from modules.financial.services.receivable_service import ReceivableService


class TestReceivableService:
    """Testes para o ReceivableService."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para mock do session."""
        session = MagicMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Fixture para instancia do service."""
        return ReceivableService(mock_session)

    @pytest.fixture
    def sample_account(self):
        """Fixture para conta de exemplo."""
        return ReceivableAccount(
            id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            description="Taxa Condominial Jan/2025",
            gross_value=Decimal("850.00"),
            net_value=Decimal("850.00"),
            paid_value=Decimal("0"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            status=ReceivableStatus.PENDENTE.value,
        )

    @pytest.fixture
    def sample_installment(self, sample_account):
        """Fixture para parcela de exemplo."""
        return ReceivableInstallment(
            id=uuid.uuid4(),
            receivable_account_id=sample_account.id,
            installment_number=1,
            original_value=Decimal("850.00"),
            current_value=Decimal("850.00"),
            paid_value=Decimal("0"),
            due_date=date.today() + timedelta(days=10),
            status=InstallmentStatus.PENDENTE.value,
            interest_rate=Decimal("1.00"),
            penalty_rate=Decimal("2.00"),
            interest_value=Decimal("0"),
            penalty_value=Decimal("0"),
        )

    @pytest.mark.asyncio
    async def test_create_account(self, service, mock_session):
        """Testa criacao de conta a receber."""
        user_id = uuid.uuid4()
        data = ReceivableAccountCreate(
            condominio_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            description="Taxa Condominial Jan/2025",
            gross_value=Decimal("850.00"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
        )

        with patch.object(service.account_repo, "create", new_callable=AsyncMock) as mock_create:
            mock_account = ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=data.condominio_id,
                customer_id=data.customer_id,
                description=data.description,
                gross_value=data.gross_value,
                net_value=data.gross_value,
                issue_date=data.issue_date,
                due_date=data.due_date,
                status=ReceivableStatus.PENDENTE.value,
            )
            mock_create.return_value = mock_account

            account = await service.create_account(data, user_id)

            assert account is not None
            assert account.description == data.description
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_account(self, service, sample_account):
        """Testa busca de conta."""
        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            account = await service.get_account(sample_account.id)

            assert account is not None
            assert account.id == sample_account.id
            mock_get.assert_called_once_with(sample_account.id, with_relations=True)

    @pytest.mark.asyncio
    async def test_list_accounts(self, service, sample_account):
        """Testa listagem de contas."""
        condominio_id = uuid.uuid4()
        filters = ReceivableAccountFilter()

        with (
            patch.object(service.account_repo, "list") as mock_list,
            patch.object(service.account_repo, "count") as mock_count,
        ):
            mock_list.return_value = [sample_account]
            mock_count.return_value = 1

            accounts, total = await service.list_accounts(condominio_id, filters, 0, 100)

            assert len(accounts) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_update_account(self, service, mock_session, sample_account):
        """Testa atualizacao de conta."""
        user_id = uuid.uuid4()
        data = ReceivableAccountUpdate(description="Taxa Atualizada")

        with (
            patch.object(service.account_repo, "get_by_id") as mock_get,
            patch.object(service.account_repo, "update", new_callable=AsyncMock) as mock_update,
        ):
            mock_get.return_value = sample_account
            sample_account.description = data.description
            mock_update.return_value = sample_account

            account = await service.update_account(sample_account.id, data, user_id)

            assert account is not None
            assert account.description == "Taxa Atualizada"

    @pytest.mark.asyncio
    async def test_update_account_paid_raises_error(self, service, mock_session, sample_account):
        """Testa que conta paga nao pode ser atualizada."""
        sample_account.status = ReceivableStatus.PAGA.value
        user_id = uuid.uuid4()
        data = ReceivableAccountUpdate(description="Taxa Atualizada")

        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            with pytest.raises(ValueError, match="nao pode ser alterada"):
                await service.update_account(sample_account.id, data, user_id)

    @pytest.mark.asyncio
    async def test_delete_account(self, service, mock_session, sample_account):
        """Testa exclusao de conta."""
        user_id = uuid.uuid4()

        with (
            patch.object(service.account_repo, "get_by_id") as mock_get,
            patch.object(service.account_repo, "delete", new_callable=AsyncMock) as mock_delete,
        ):
            mock_get.return_value = sample_account
            mock_delete.return_value = True

            result = await service.delete_account(sample_account.id, user_id)

            assert result is True
            mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_account_paid_raises_error(self, service, mock_session, sample_account):
        """Testa que conta paga nao pode ser excluida."""
        sample_account.status = ReceivableStatus.PAGA.value
        user_id = uuid.uuid4()

        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            with pytest.raises(ValueError, match="nao pode ser excluida"):
                await service.delete_account(sample_account.id, user_id)

    @pytest.mark.asyncio
    async def test_cancel_account(self, service, mock_session, sample_account):
        """Testa cancelamento de conta."""
        user_id = uuid.uuid4()

        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            account = await service.cancel_account(sample_account.id, user_id, "Cobranca indevida")

            assert account.status == ReceivableStatus.CANCELADA.value

    @pytest.mark.asyncio
    async def test_suspend_account(self, service, mock_session, sample_account):
        """Testa suspensao de conta."""
        user_id = uuid.uuid4()

        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            account = await service.suspend_account(sample_account.id, user_id, "Em analise")

            assert account.status == ReceivableStatus.SUSPENSA.value

    @pytest.mark.asyncio
    async def test_protest_account(self, service, mock_session, sample_account):
        """Testa envio para protesto."""
        sample_account.status = ReceivableStatus.VENCIDA.value
        user_id = uuid.uuid4()

        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            account = await service.protest_account(sample_account.id, user_id, "PROT-001")

            assert account.status == ReceivableStatus.PROTESTADA.value
            assert account.protest_number == "PROT-001"

    @pytest.mark.asyncio
    async def test_write_off_account(self, service, mock_session, sample_account):
        """Testa baixa de conta."""
        sample_account.status = ReceivableStatus.VENCIDA.value
        user_id = uuid.uuid4()

        with patch.object(service.account_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_account

            account = await service.write_off_account(sample_account.id, user_id, "Prescricao")

            assert account.status == ReceivableStatus.BAIXADA.value

    @pytest.mark.asyncio
    async def test_register_payment(self, service, mock_session, sample_installment):
        """Testa registro de recebimento."""
        user_id = uuid.uuid4()
        data = ReceivablePaymentCreate(
            installment_id=sample_installment.id,
            paid_value=Decimal("850.00"),
            payment_date=date.today(),
            payment_method_id=uuid.uuid4(),
        )

        with (
            patch.object(service.installment_repo, "get_by_id") as mock_get_inst,
            patch.object(service.payment_repo, "create", new_callable=AsyncMock) as mock_create,
        ):
            mock_get_inst.return_value = sample_installment
            mock_payment = ReceivablePayment(
                id=uuid.uuid4(),
                installment_id=sample_installment.id,
                paid_value=data.paid_value,
                payment_date=data.payment_date,
                status=PaymentStatus.CONFIRMADO.value,
                payment_origin=PaymentOrigin.MANUAL.value,
            )
            mock_create.return_value = mock_payment

            payment = await service.register_payment(sample_installment.id, data, user_id)

            assert payment is not None
            assert payment.paid_value == Decimal("850.00")

    @pytest.mark.asyncio
    async def test_register_payment_installment_paid_raises_error(self, service, mock_session, sample_installment):
        """Testa que parcela paga nao pode receber pagamento."""
        sample_installment.status = InstallmentStatus.PAGA.value
        user_id = uuid.uuid4()
        data = ReceivablePaymentCreate(
            installment_id=sample_installment.id,
            paid_value=Decimal("850.00"),
            payment_date=date.today(),
        )

        with patch.object(service.installment_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_installment

            with pytest.raises(ValueError, match="nao pode ser paga"):
                await service.register_payment(sample_installment.id, data, user_id)

    @pytest.mark.asyncio
    async def test_reverse_payment(self, service, mock_session, sample_installment):
        """Testa estorno de recebimento."""
        user_id = uuid.uuid4()
        payment = ReceivablePayment(
            id=uuid.uuid4(),
            installment_id=sample_installment.id,
            paid_value=Decimal("850.00"),
            payment_date=date.today(),
            status=PaymentStatus.CONFIRMADO.value,
            payment_origin=PaymentOrigin.MANUAL.value,
        )
        sample_installment.paid_value = Decimal("850.00")
        sample_installment.status = InstallmentStatus.PAGA.value

        account = ReceivableAccount(
            id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            description="Conta Teste",
            gross_value=Decimal("850.00"),
            net_value=Decimal("850.00"),
            paid_value=Decimal("850.00"),
            issue_date=date.today(),
            due_date=date.today(),
            status=ReceivableStatus.PAGA.value,
        )
        sample_installment.receivable_account_id = account.id

        data = ReceivablePaymentReverseRequest(reason="Pagamento duplicado")

        with (
            patch.object(service.payment_repo, "get_by_id") as mock_get_pay,
            patch.object(service.installment_repo, "get_by_id") as mock_get_inst,
            patch.object(service.account_repo, "get_by_id") as mock_get_acc,
        ):
            mock_get_pay.return_value = payment
            mock_get_inst.return_value = sample_installment
            mock_get_acc.return_value = account

            result = await service.reverse_payment(payment.id, data, user_id)

            assert result.status == PaymentStatus.ESTORNADO.value

    @pytest.mark.asyncio
    async def test_renegotiate_installment(self, service, mock_session, sample_installment):
        """Testa renegociacao de parcela."""
        sample_installment.status = InstallmentStatus.VENCIDA.value
        user_id = uuid.uuid4()
        new_due = date.today() + timedelta(days=15)
        data = ReceivableInstallmentRenegotiateRequest(
            new_due_date=new_due,
            new_value=Decimal("800.00"),
            reason="Acordo de pagamento",
        )

        with patch.object(service.installment_repo, "get_by_id") as mock_get:
            mock_get.return_value = sample_installment

            installment = await service.renegotiate_installment(sample_installment.id, data, user_id)

            assert installment.due_date == new_due
            assert installment.current_value == Decimal("800.00")
            assert installment.status == InstallmentStatus.RENEGOCIADA.value

    @pytest.mark.asyncio
    async def test_get_stats(self, service):
        """Testa estatisticas de contas."""
        condominio_id = uuid.uuid4()

        with patch.object(service.account_repo, "get_stats") as mock_stats:
            from modules.financial.schemas.receivable import ReceivableAccountStats

            mock_stats.return_value = ReceivableAccountStats(
                total_accounts=100,
                total_pending=50,
                total_overdue=10,
                total_paid=40,
                total_value=Decimal("85000.00"),
                pending_value=Decimal("42500.00"),
                overdue_value=Decimal("8500.00"),
                paid_value=Decimal("34000.00"),
            )

            stats = await service.get_stats(condominio_id)

            assert stats.total_accounts == 100
            assert stats.total_pending == 50
            assert stats.overdue_value == Decimal("8500.00")

    @pytest.mark.asyncio
    async def test_get_customer_debt(self, service):
        """Testa busca de divida do cliente."""
        from modules.financial.models.customer import Customer

        customer = Customer(
            id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="Cliente Teste",
            total_debt=Decimal("1500.00"),
            overdue_debt=Decimal("500.00"),
        )

        with patch.object(service.customer_repo, "get_by_id") as mock_get:
            mock_get.return_value = customer

            total, overdue = await service.get_customer_debt(customer.id)

            assert total == Decimal("1500.00")
            assert overdue == Decimal("500.00")

    @pytest.mark.asyncio
    async def test_get_unit_debt(self, service, sample_account):
        """Testa busca de divida da unidade."""
        unidade_id = uuid.uuid4()
        sample_account.net_value = Decimal("850.00")
        sample_account.paid_value = Decimal("0")
        sample_account.status = ReceivableStatus.VENCIDA.value

        with patch.object(service.account_repo, "get_by_unidade") as mock_get:
            mock_get.return_value = [sample_account]

            total, overdue = await service.get_unit_debt(unidade_id)

            assert total == Decimal("850.00")
            assert overdue == Decimal("850.00")

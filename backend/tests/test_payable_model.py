"""Testes para os modelos de Contas a Pagar."""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from modules.financial.models.payable_account import (
    PayableAccount,
    PayablePriority,
    PayableStatus,
    PayableType,
    RecurrenceType,
)
from modules.financial.models.payable_installment import InstallmentStatus, PayableInstallment
from modules.financial.models.payable_payment import PayablePayment, PaymentOrigin, PaymentStatus


class TestPayableAccountModel:
    """Testes para o modelo PayableAccount."""

    def test_create_payable_account(self):
        """Testa criação de conta a pagar."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            supplier_id=uuid.uuid4(),
            category_id=uuid.uuid4(),
            description="Manutenção do elevador",
            gross_value=Decimal("1000.00"),
            net_value=Decimal("1000.00"),
            due_date=date.today() + timedelta(days=30),
            status=PayableStatus.PENDENTE.value,
            total_installments=1,
            ativo=True,
        )

        assert account.description == "Manutenção do elevador"
        assert account.gross_value == Decimal("1000.00")
        assert account.status == PayableStatus.PENDENTE.value
        assert account.total_installments == 1
        assert account.ativo is True

    def test_payable_account_with_discount(self):
        """Testa conta a pagar com desconto."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Serviço com desconto",
            gross_value=Decimal("1000.00"),
            discount_value=Decimal("100.00"),
            net_value=Decimal("900.00"),
            due_date=date.today() + timedelta(days=30),
        )

        assert account.discount_value == Decimal("100.00")
        assert account.net_value == Decimal("900.00")

    def test_payable_account_with_withholdings(self):
        """Testa conta a pagar com retenções."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Serviço com retenções",
            gross_value=Decimal("1000.00"),
            withhold_iss=Decimal("50.00"),
            withhold_ir=Decimal("15.00"),
            total_withholdings=Decimal("65.00"),
            net_value=Decimal("935.00"),
            due_date=date.today() + timedelta(days=30),
        )

        assert account.withhold_iss == Decimal("50.00")
        assert account.withhold_ir == Decimal("15.00")
        assert account.total_withholdings == Decimal("65.00")

    def test_is_overdue_property(self):
        """Testa propriedade is_overdue."""
        # Conta vencida
        overdue_account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta vencida",
            gross_value=Decimal("100.00"),
            net_value=Decimal("100.00"),
            due_date=date.today() - timedelta(days=30),
            status=PayableStatus.PENDENTE.value,
            ativo=True,
        )
        assert overdue_account.is_overdue is True

        # Conta em dia
        current_account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta em dia",
            gross_value=Decimal("100.00"),
            net_value=Decimal("100.00"),
            due_date=date.today() + timedelta(days=30),
            status=PayableStatus.PENDENTE.value,
            ativo=True,
        )
        assert current_account.is_overdue is False

        # Conta paga (mesmo vencida não é overdue)
        paid_account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta paga",
            gross_value=Decimal("100.00"),
            net_value=Decimal("100.00"),
            due_date=date.today() - timedelta(days=30),
            status=PayableStatus.PAGA.value,
            ativo=True,
        )
        assert paid_account.is_overdue is False

    def test_balance_property(self):
        """Testa propriedade balance."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta parcialmente paga",
            gross_value=Decimal("1000.00"),
            net_value=Decimal("1000.00"),
            paid_value=Decimal("400.00"),
            due_date=date.today() + timedelta(days=30),
        )

        assert account.balance == Decimal("600.00")

    def test_payment_percentage_property(self):
        """Testa propriedade payment_percentage."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta parcialmente paga",
            gross_value=Decimal("1000.00"),
            net_value=Decimal("1000.00"),
            paid_value=Decimal("250.00"),
            due_date=date.today() + timedelta(days=30),
        )

        assert account.payment_percentage == 25.0

    def test_approve_account(self):
        """Testa aprovação de conta."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta para aprovação",
            gross_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
            status=PayableStatus.PENDENTE.value,
            ativo=True,
        )
        user_id = uuid.uuid4()

        account.approve(user_id)

        assert account.status == PayableStatus.APROVADA.value
        assert account.approved_by == user_id
        assert account.approved_at is not None

    def test_schedule_payment(self):
        """Testa agendamento de pagamento."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta para agendar",
            gross_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
            status=PayableStatus.APROVADA.value,
            ativo=True,
        )
        user_id = uuid.uuid4()
        scheduled_date = date.today() + timedelta(days=15)

        account.schedule_payment(scheduled_date, user_id)

        assert account.status == PayableStatus.AGENDADA.value
        assert account.scheduled_payment_date == scheduled_date
        assert account.scheduled_by == user_id

    def test_register_payment(self):
        """Testa registro de pagamento."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta para pagar",
            gross_value=Decimal("1000.00"),
            net_value=Decimal("1000.00"),
            paid_value=Decimal("0"),
            remaining_value=Decimal("1000.00"),
            due_date=date.today() + timedelta(days=30),
            status=PayableStatus.APROVADA.value,
            ativo=True,
        )

        # Pagamento parcial
        account.register_payment(Decimal("500.00"), date.today())
        assert account.paid_value == Decimal("500.00")
        assert account.status == PayableStatus.PARCIAL.value

        # Pagamento total
        account.register_payment(Decimal("500.00"), date.today())
        assert account.paid_value == Decimal("1000.00")
        assert account.status == PayableStatus.PAGA.value
        assert account.payment_date is not None

    def test_cancel_account(self):
        """Testa cancelamento de conta."""
        account = PayableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta para cancelar",
            gross_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
            status=PayableStatus.PENDENTE.value,
            internal_notes="",
            ativo=True,
        )

        account.cancel("Serviço não realizado")

        assert account.status == PayableStatus.CANCELADA.value
        assert "Cancelada: Serviço não realizado" in account.internal_notes

    def test_payable_priorities(self):
        """Testa todas as prioridades."""
        priorities = [
            PayablePriority.BAIXA,
            PayablePriority.MEDIA,
            PayablePriority.ALTA,
            PayablePriority.URGENTE,
            PayablePriority.CRITICA,
        ]

        for p in priorities:
            account = PayableAccount(
                condominio_id=uuid.uuid4(),
                description="Teste",
                gross_value=Decimal("100.00"),
                net_value=Decimal("100.00"),
                due_date=date.today() + timedelta(days=30),
                priority=p.value,
            )
            assert account.priority == p.value


class TestPayableInstallmentModel:
    """Testes para o modelo PayableInstallment."""

    def test_create_installment(self):
        """Testa criação de parcela."""
        installment = PayableInstallment(
            payable_account_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            installment_number=1,
            total_installments=1,
            original_value=Decimal("500.00"),
            current_value=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
            status=InstallmentStatus.PENDENTE.value,
            ativo=True,
        )

        assert installment.installment_number == 1
        assert installment.original_value == Decimal("500.00")
        assert installment.status == InstallmentStatus.PENDENTE.value

    def test_calculate_current_value_not_overdue(self):
        """Testa cálculo de valor sem atraso."""
        installment = PayableInstallment(
            payable_account_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            installment_number=1,
            total_installments=1,
            original_value=Decimal("1000.00"),
            current_value=Decimal("1000.00"),
            due_date=date.today() + timedelta(days=30),
            interest_rate=Decimal("0.1"),
            penalty_rate=Decimal("2.00"),
            status=InstallmentStatus.PENDENTE.value,
            discount_value=Decimal("0"),
            addition_value=Decimal("0"),
            penalty_value=Decimal("0"),
            interest_value=Decimal("0"),
            ativo=True,
        )

        value = installment.calculate_current_value()
        assert value == Decimal("1000.00")

    def test_calculate_current_value_overdue(self):
        """Testa cálculo de valor com atraso."""
        days_late = 10
        installment = PayableInstallment(
            payable_account_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            installment_number=1,
            total_installments=1,
            original_value=Decimal("1000.00"),
            current_value=Decimal("1000.00"),
            due_date=date.today() - timedelta(days=days_late),
            interest_rate=Decimal("3.0"),  # 3% ao mês = 0.1% ao dia
            penalty_rate=Decimal("2.00"),  # 2% de multa
            status=InstallmentStatus.PENDENTE.value,
            discount_value=Decimal("0"),
            addition_value=Decimal("0"),
            penalty_value=Decimal("0"),
            interest_value=Decimal("0"),
            paid_value=Decimal("0"),
            ativo=True,
        )

        value = installment.calculate_current_value()

        # Valor base = 1000
        # Multa = 1000 * 0.02 = 20
        # Juros = 1000 * (3.0/30/100) * 10 = 1000 * 0.001 * 10 = 10
        # Total = 1030
        expected = Decimal("1000.00") + Decimal("20.00") + Decimal("10.00")
        assert value == expected

    def test_renegotiate_installment(self):
        """Testa renegociação de parcela."""
        original_due = date.today() - timedelta(days=30)
        new_due = date.today() + timedelta(days=15)

        installment = PayableInstallment(
            payable_account_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            installment_number=1,
            total_installments=1,
            original_value=Decimal("1000.00"),
            current_value=Decimal("1000.00"),
            due_date=original_due,
            status=InstallmentStatus.PENDENTE.value,
            ativo=True,
        )

        installment.renegotiate(
            new_due_date=new_due,
            new_value=Decimal("1100.00"),
            reason="Acordo de parcelamento",
        )

        assert installment.is_renegotiated is True
        assert installment.original_due_date == original_due
        assert installment.due_date == new_due
        assert installment.current_value == Decimal("1100.00")
        assert installment.renegotiation_reason == "Acordo de parcelamento"
        assert installment.status == InstallmentStatus.RENEGOCIADA.value

    def test_installment_with_barcode(self):
        """Testa parcela com código de barras."""
        installment = PayableInstallment(
            payable_account_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            installment_number=1,
            total_installments=1,
            original_value=Decimal("500.00"),
            current_value=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
            barcode="12345678901234567890123456789012345678901234",
            digitable_line="12345.67890 12345.678901 12345.678901 1 12340000050000",
            status=InstallmentStatus.PENDENTE.value,
            ativo=True,
        )

        assert installment.barcode is not None
        assert installment.digitable_line is not None


class TestPayablePaymentModel:
    """Testes para o modelo PayablePayment."""

    def test_create_payment(self):
        """Testa criação de pagamento."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            payment_method_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDENTE.value,
            origin=PaymentOrigin.MANUAL.value,
            ativo=True,
        )

        assert payment.paid_value == Decimal("500.00")
        assert payment.status == PaymentStatus.PENDENTE.value
        assert payment.origin == PaymentOrigin.MANUAL.value

    def test_confirm_payment(self):
        """Testa confirmação de pagamento."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDENTE.value,
            ativo=True,
        )

        payment.confirm()

        assert payment.status == PaymentStatus.CONFIRMADO.value
        assert payment.confirmation_date == date.today()

    def test_reject_payment(self):
        """Testa rejeição de pagamento."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDENTE.value,
            ativo=True,
        )

        payment.reject("ERR001", "Saldo insuficiente")

        assert payment.status == PaymentStatus.REJEITADO.value
        assert payment.bank_return_code == "ERR001"

    def test_reverse_payment(self):
        """Testa estorno de pagamento."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.CONFIRMADO.value,
            is_reversed=False,
            ativo=True,
        )
        user_id = uuid.uuid4()

        payment.reverse(user_id, "Pagamento duplicado")

        assert payment.is_reversed is True
        assert payment.reversed_by == user_id
        assert payment.reversal_reason == "Pagamento duplicado"
        assert payment.status == PaymentStatus.ESTORNADO.value

    def test_reconcile_payment(self):
        """Testa reconciliação de pagamento."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.CONFIRMADO.value,
            is_reconciled=False,
            ativo=True,
        )
        user_id = uuid.uuid4()

        payment.reconcile(user_id, "Conferido com extrato")

        assert payment.is_reconciled is True
        assert payment.reconciled_by == user_id
        assert payment.reconciliation_notes == "Conferido com extrato"

    def test_payment_with_fees(self):
        """Testa pagamento com taxas."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            paid_value=Decimal("1000.00"),
            discount_value=Decimal("50.00"),
            interest_value=Decimal("10.00"),
            penalty_value=Decimal("20.00"),
            fee_value=Decimal("5.00"),
            net_value=Decimal("985.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDENTE.value,
            ativo=True,
        )

        assert payment.discount_value == Decimal("50.00")
        assert payment.interest_value == Decimal("10.00")
        assert payment.penalty_value == Decimal("20.00")
        assert payment.fee_value == Decimal("5.00")
        assert payment.net_value == Decimal("985.00")

    def test_cancel_payment(self):
        """Testa cancelamento de pagamento."""
        payment = PayablePayment(
            installment_id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDENTE.value,
            ativo=True,
        )

        payment.cancel()

        assert payment.status == PaymentStatus.CANCELADO.value
        assert payment.ativo is False

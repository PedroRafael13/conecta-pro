"""Testes para os modelos de Contas a Receber."""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from modules.financial.models.billing_rule import (
    BillingFrequency,
    BillingRule,
    BillingRuleStatus,
    BillingType,
    NotificationType,
)
from modules.financial.models.customer import (
    Customer,
    CustomerStatus,
    CustomerType,
)
from modules.financial.models.receivable_account import (
    ReceivableAccount,
    ReceivableStatus,
)
from modules.financial.models.receivable_category import (
    CategoryType,
    ReceivableCategory,
)
from modules.financial.models.receivable_installment import (
    InstallmentStatus,
    ReceivableInstallment,
)
from modules.financial.models.receivable_payment import (
    PaymentOrigin,
    PaymentStatus,
    ReceivablePayment,
)


class TestReceivableCategoryModel:
    """Testes para o modelo ReceivableCategory."""

    def test_create_category(self):
        """Testa criacao de categoria."""
        category = ReceivableCategory(
            condominio_id=uuid.uuid4(),
            code="TX001",
            name="Taxa Condominial",
            description="Taxa mensal de condominio",
            category_type=CategoryType.TAXA_CONDOMINIAL.value,
            default_interest_rate=Decimal("1.00"),
            default_penalty_rate=Decimal("2.00"),
            is_active=True,
        )

        assert category.name == "Taxa Condominial"
        assert category.category_type == CategoryType.TAXA_CONDOMINIAL.value
        assert category.default_interest_rate == Decimal("1.00")
        assert category.is_active is True

    def test_create_subcategory(self):
        """Testa criacao de subcategoria."""
        parent_id = uuid.uuid4()
        category = ReceivableCategory(
            condominio_id=uuid.uuid4(),
            parent_id=parent_id,
            code="TX001-01",
            name="Taxa Ordinaria",
            category_type=CategoryType.TAXA_CONDOMINIAL.value,
        )

        assert category.parent_id == parent_id

    def test_category_types(self):
        """Testa todos os tipos de categoria."""
        types = [
            CategoryType.TAXA_CONDOMINIAL,
            CategoryType.TAXA_EXTRA,
            CategoryType.RESERVA,
            CategoryType.MULTA,
            CategoryType.ALUGUEL,
            CategoryType.SERVICO,
            CategoryType.ACORDO,
            CategoryType.OUTROS,
        ]

        for t in types:
            category = ReceivableCategory(
                condominio_id=uuid.uuid4(),
                name=f"Categoria {t.value}",
                category_type=t.value,
            )
            assert category.category_type == t.value


class TestCustomerModel:
    """Testes para o modelo Customer."""

    def test_create_customer_morador(self):
        """Testa criacao de cliente morador."""
        customer = Customer(
            condominio_id=uuid.uuid4(),
            morador_id=uuid.uuid4(),
            unidade_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="Joao da Silva",
            customer_type=CustomerType.MORADOR.value,
            status=CustomerStatus.ATIVO.value,
            email="joao@email.com",
            phone="11999998888",
        )

        assert customer.name == "Joao da Silva"
        assert customer.customer_type == CustomerType.MORADOR.value
        assert customer.status == CustomerStatus.ATIVO.value

    def test_create_customer_empresa(self):
        """Testa criacao de cliente empresa."""
        customer = Customer(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="12.345.678/0001-90",
            name="Empresa XYZ LTDA",
            customer_type=CustomerType.EMPRESA.value,
            status=CustomerStatus.ATIVO.value,
        )

        assert customer.name == "Empresa XYZ LTDA"
        assert customer.customer_type == CustomerType.EMPRESA.value

    def test_block_customer(self):
        """Testa bloqueio de cliente."""
        customer = Customer(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="Cliente Teste",
            status=CustomerStatus.ATIVO.value,
            total_debt=Decimal("0"),
            overdue_debt=Decimal("0"),
        )

        customer.block("Inadimplencia recorrente")

        assert customer.status == CustomerStatus.BLOQUEADO.value
        assert "Inadimplencia" in customer.notes

    def test_unblock_customer(self):
        """Testa desbloqueio de cliente."""
        customer = Customer(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="Cliente Teste",
            status=CustomerStatus.BLOQUEADO.value,
            total_debt=Decimal("0"),
            overdue_debt=Decimal("0"),
        )

        customer.unblock()

        assert customer.status == CustomerStatus.ATIVO.value

    def test_update_debt(self):
        """Testa atualizacao de divida."""
        customer = Customer(
            condominio_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="Cliente Teste",
            status=CustomerStatus.ATIVO.value,
            total_debt=Decimal("0"),
            overdue_debt=Decimal("0"),
        )

        customer.update_debt(Decimal("1500.00"), Decimal("500.00"))

        assert customer.total_debt == Decimal("1500.00")
        assert customer.overdue_debt == Decimal("500.00")

    def test_customer_types(self):
        """Testa todos os tipos de cliente."""
        types = [
            CustomerType.MORADOR,
            CustomerType.PROPRIETARIO,
            CustomerType.INQUILINO,
            CustomerType.EXTERNO,
            CustomerType.EMPRESA,
        ]

        for t in types:
            customer = Customer(
                condominio_id=uuid.uuid4(),
                cpf_cnpj="123.456.789-00",
                name="Cliente Teste",
                customer_type=t.value,
            )
            assert customer.customer_type == t.value


class TestReceivableAccountModel:
    """Testes para o modelo ReceivableAccount."""

    def test_create_account(self):
        """Testa criacao de conta a receber."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            unidade_id=uuid.uuid4(),
            description="Taxa Condominial Jan/2025",
            reference_month="2025-01",
            gross_value=Decimal("850.00"),
            net_value=Decimal("850.00"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            status=ReceivableStatus.PENDENTE.value,
            interest_rate=Decimal("1.00"),
            penalty_rate=Decimal("2.00"),
        )

        assert account.description == "Taxa Condominial Jan/2025"
        assert account.gross_value == Decimal("850.00")
        assert account.status == ReceivableStatus.PENDENTE.value

    def test_account_is_overdue(self):
        """Testa verificacao de vencimento."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta Vencida",
            gross_value=Decimal("100.00"),
            net_value=Decimal("100.00"),
            issue_date=date.today() - timedelta(days=30),
            due_date=date.today() - timedelta(days=10),
            status=ReceivableStatus.VENCIDA.value,
        )

        assert account.is_overdue is True

    def test_register_payment(self):
        """Testa registro de pagamento."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Taxa Condominial",
            gross_value=Decimal("850.00"),
            net_value=Decimal("850.00"),
            paid_value=Decimal("0"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            status=ReceivableStatus.PENDENTE.value,
        )
        user_id = uuid.uuid4()

        account.register_payment(Decimal("850.00"), user_id)

        assert account.paid_value == Decimal("850.00")
        assert account.status == ReceivableStatus.PAGA.value
        assert account.payment_date is not None

    def test_partial_payment(self):
        """Testa pagamento parcial."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Taxa Condominial",
            gross_value=Decimal("850.00"),
            net_value=Decimal("850.00"),
            paid_value=Decimal("0"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            status=ReceivableStatus.PENDENTE.value,
        )
        user_id = uuid.uuid4()

        account.register_payment(Decimal("500.00"), user_id)

        assert account.paid_value == Decimal("500.00")
        assert account.status == ReceivableStatus.PARCIAL.value

    def test_cancel_account(self):
        """Testa cancelamento de conta."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta a Cancelar",
            gross_value=Decimal("100.00"),
            net_value=Decimal("100.00"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            status=ReceivableStatus.PENDENTE.value,
        )

        account.cancel("Cobranca indevida")

        assert account.status == ReceivableStatus.CANCELADA.value
        assert "Cobranca indevida" in account.notes

    def test_suspend_account(self):
        """Testa suspensao de conta."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta a Suspender",
            gross_value=Decimal("100.00"),
            net_value=Decimal("100.00"),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            status=ReceivableStatus.PENDENTE.value,
        )

        account.suspend("Em analise juridica")

        assert account.status == ReceivableStatus.SUSPENSA.value

    def test_protest_account(self):
        """Testa envio para protesto."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta para Protesto",
            gross_value=Decimal("1000.00"),
            net_value=Decimal("1000.00"),
            issue_date=date.today() - timedelta(days=60),
            due_date=date.today() - timedelta(days=30),
            status=ReceivableStatus.VENCIDA.value,
        )
        user_id = uuid.uuid4()

        account.protest(user_id, "PROT-2025-001")

        assert account.status == ReceivableStatus.PROTESTADA.value
        assert account.protest_number == "PROT-2025-001"
        assert account.protested_by == user_id

    def test_write_off_account(self):
        """Testa baixa de conta."""
        account = ReceivableAccount(
            condominio_id=uuid.uuid4(),
            description="Conta para Baixa",
            gross_value=Decimal("500.00"),
            net_value=Decimal("500.00"),
            issue_date=date.today() - timedelta(days=365),
            due_date=date.today() - timedelta(days=335),
            status=ReceivableStatus.VENCIDA.value,
        )
        user_id = uuid.uuid4()

        account.write_off(user_id, "Prescricao")

        assert account.status == ReceivableStatus.BAIXADA.value
        assert account.write_off_reason == "Prescricao"
        assert account.written_off_by == user_id

    def test_account_statuses(self):
        """Testa todos os status de conta."""
        statuses = [
            ReceivableStatus.PENDENTE,
            ReceivableStatus.VENCIDA,
            ReceivableStatus.PARCIAL,
            ReceivableStatus.PAGA,
            ReceivableStatus.CANCELADA,
            ReceivableStatus.SUSPENSA,
            ReceivableStatus.PROTESTADA,
            ReceivableStatus.ACORDO,
            ReceivableStatus.BAIXADA,
        ]

        for s in statuses:
            account = ReceivableAccount(
                condominio_id=uuid.uuid4(),
                description="Conta Teste",
                gross_value=Decimal("100.00"),
                net_value=Decimal("100.00"),
                issue_date=date.today(),
                due_date=date.today(),
                status=s.value,
            )
            assert account.status == s.value


class TestReceivableInstallmentModel:
    """Testes para o modelo ReceivableInstallment."""

    def test_create_installment(self):
        """Testa criacao de parcela."""
        installment = ReceivableInstallment(
            receivable_account_id=uuid.uuid4(),
            installment_number=1,
            original_value=Decimal("300.00"),
            current_value=Decimal("300.00"),
            due_date=date.today() + timedelta(days=30),
            status=InstallmentStatus.PENDENTE.value,
            interest_rate=Decimal("1.00"),
            penalty_rate=Decimal("2.00"),
        )

        assert installment.installment_number == 1
        assert installment.original_value == Decimal("300.00")
        assert installment.status == InstallmentStatus.PENDENTE.value

    def test_calculate_current_value_no_interest(self):
        """Testa calculo de valor sem juros."""
        installment = ReceivableInstallment(
            receivable_account_id=uuid.uuid4(),
            installment_number=1,
            original_value=Decimal("300.00"),
            current_value=Decimal("300.00"),
            due_date=date.today() + timedelta(days=10),
            status=InstallmentStatus.PENDENTE.value,
            interest_rate=Decimal("1.00"),
            penalty_rate=Decimal("2.00"),
            interest_value=Decimal("0"),
            penalty_value=Decimal("0"),
        )

        value = installment.calculate_current_value()

        assert value == Decimal("300.00")

    def test_calculate_current_value_with_interest(self):
        """Testa calculo de valor com juros e multa."""
        installment = ReceivableInstallment(
            receivable_account_id=uuid.uuid4(),
            installment_number=1,
            original_value=Decimal("300.00"),
            current_value=Decimal("300.00"),
            due_date=date.today() - timedelta(days=30),
            status=InstallmentStatus.VENCIDA.value,
            interest_rate=Decimal("1.00"),
            penalty_rate=Decimal("2.00"),
            interest_value=Decimal("3.00"),
            penalty_value=Decimal("6.00"),
        )

        value = installment.calculate_current_value()

        assert value == Decimal("309.00")

    def test_renegotiate_installment(self):
        """Testa renegociacao de parcela."""
        installment = ReceivableInstallment(
            receivable_account_id=uuid.uuid4(),
            installment_number=1,
            original_value=Decimal("500.00"),
            current_value=Decimal("500.00"),
            due_date=date.today() - timedelta(days=30),
            original_due_date=date.today() - timedelta(days=30),
            status=InstallmentStatus.VENCIDA.value,
        )

        new_due_date = date.today() + timedelta(days=15)
        installment.renegotiate(
            new_due_date=new_due_date,
            new_value=Decimal("450.00"),
            reason="Acordo de pagamento",
        )

        assert installment.due_date == new_due_date
        assert installment.current_value == Decimal("450.00")
        assert installment.status == InstallmentStatus.RENEGOCIADA.value
        assert installment.renegotiation_reason == "Acordo de pagamento"

    def test_installment_statuses(self):
        """Testa todos os status de parcela."""
        statuses = [
            InstallmentStatus.PENDENTE,
            InstallmentStatus.VENCIDA,
            InstallmentStatus.PARCIAL,
            InstallmentStatus.PAGA,
            InstallmentStatus.CANCELADA,
            InstallmentStatus.AGENDADA,
            InstallmentStatus.RENEGOCIADA,
        ]

        for s in statuses:
            installment = ReceivableInstallment(
                receivable_account_id=uuid.uuid4(),
                installment_number=1,
                original_value=Decimal("100.00"),
                current_value=Decimal("100.00"),
                due_date=date.today(),
                status=s.value,
            )
            assert installment.status == s.value


class TestReceivablePaymentModel:
    """Testes para o modelo ReceivablePayment."""

    def test_create_payment(self):
        """Testa criacao de recebimento."""
        payment = ReceivablePayment(
            installment_id=uuid.uuid4(),
            paid_value=Decimal("850.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDING.value,
            payment_origin=PaymentOrigin.MANUAL.value,
        )

        assert payment.paid_value == Decimal("850.00")
        assert payment.status == PaymentStatus.PENDING.value
        assert payment.payment_origin == PaymentOrigin.MANUAL.value

    def test_payment_boleto(self):
        """Testa recebimento por boleto."""
        payment = ReceivablePayment(
            installment_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDING.value,
            payment_origin=PaymentOrigin.BOLETO.value,
            transaction_id="BOL-123456789",
            authentication_code="AUTH-987654",
        )

        assert payment.payment_origin == PaymentOrigin.BOLETO.value
        assert payment.transaction_id == "BOL-123456789"

    def test_payment_pix(self):
        """Testa recebimento por PIX."""
        payment = ReceivablePayment(
            installment_id=uuid.uuid4(),
            paid_value=Decimal("750.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDING.value,
            payment_origin=PaymentOrigin.PIX.value,
            transaction_id="E12345678202501011234567890123456",
        )

        assert payment.payment_origin == PaymentOrigin.PIX.value

    def test_reconcile_payment(self):
        """Testa reconciliacao de recebimento."""
        payment = ReceivablePayment(
            installment_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDING.value,
            payment_origin=PaymentOrigin.BOLETO.value,
            is_reconciled=False,
        )
        user_id = uuid.uuid4()

        payment.reconcile(user_id, "Conferido com extrato")

        assert payment.is_reconciled is True
        assert payment.reconciled_by == user_id
        assert payment.reconciled_at is not None

    def test_reverse_payment(self):
        """Testa estorno de recebimento."""
        payment = ReceivablePayment(
            installment_id=uuid.uuid4(),
            paid_value=Decimal("500.00"),
            payment_date=date.today(),
            status=PaymentStatus.PENDING.value,
            payment_origin=PaymentOrigin.MANUAL.value,
        )
        user_id = uuid.uuid4()

        payment.reverse(user_id, "Pagamento duplicado")

        assert payment.status == PaymentStatus.PENDING.value
        assert payment.reversed_by == user_id
        assert payment.reversal_reason == "Pagamento duplicado"

    def test_payment_origins(self):
        """Testa todas as origens de pagamento."""
        origins = [
            PaymentOrigin.MANUAL,
            PaymentOrigin.BOLETO,
            PaymentOrigin.PIX,
            PaymentOrigin.CARTAO,
            PaymentOrigin.TRANSFERENCIA,
            PaymentOrigin.DINHEIRO,
            PaymentOrigin.CHEQUE,
            PaymentOrigin.DEBITO_AUTOMATICO,
            PaymentOrigin.MANUAL,
            PaymentOrigin.MANUAL,
        ]

        for o in origins:
            payment = ReceivablePayment(
                installment_id=uuid.uuid4(),
                paid_value=Decimal("100.00"),
                payment_date=date.today(),
                status=PaymentStatus.PENDING.value,
                payment_origin=o.value,
            )
            assert payment.payment_origin == o.value


class TestBillingRuleModel:
    """Testes para o modelo BillingRule."""

    def test_create_billing_rule(self):
        """Testa criacao de regra de cobranca."""
        rule = BillingRule(
            condominio_id=uuid.uuid4(),
            name="Taxa Condominial Mensal",
            description="Cobranca automatica da taxa condominial",
            billing_type=BillingType.TAXA_CONDOMINIAL.value,
            frequency=BillingFrequency.MENSAL.value,
            base_value=Decimal("850.00"),
            due_day=10,
            generation_day=1,
            interest_rate=Decimal("1.00"),
            penalty_rate=Decimal("2.00"),
            status=BillingRuleStatus.ATIVA.value,
            apply_to_all_units=True,
            auto_generate_boleto=True,
            auto_generate_pix=True,
        )

        assert rule.name == "Taxa Condominial Mensal"
        assert rule.billing_type == BillingType.TAXA_CONDOMINIAL.value
        assert rule.frequency == BillingFrequency.MENSAL.value
        assert rule.base_value == Decimal("850.00")

    def test_activate_rule(self):
        """Testa ativacao de regra."""
        rule = BillingRule(
            condominio_id=uuid.uuid4(),
            name="Regra Teste",
            billing_type=BillingType.TAXA_CONDOMINIAL.value,
            frequency=BillingFrequency.MENSAL.value,
            base_value=Decimal("100.00"),
            due_day=10,
            generation_day=1,
            status=BillingRuleStatus.PAUSADA.value,
        )

        rule.activate()

        assert rule.status == BillingRuleStatus.ATIVA.value

    def test_pause_rule(self):
        """Testa pausa de regra."""
        rule = BillingRule(
            condominio_id=uuid.uuid4(),
            name="Regra Teste",
            billing_type=BillingType.TAXA_CONDOMINIAL.value,
            frequency=BillingFrequency.MENSAL.value,
            base_value=Decimal("100.00"),
            due_day=10,
            generation_day=1,
            status=BillingRuleStatus.ATIVA.value,
        )

        rule.pause("Ferias coletivas")

        assert rule.status == BillingRuleStatus.PAUSADA.value

    def test_cancel_rule(self):
        """Testa cancelamento de regra."""
        rule = BillingRule(
            condominio_id=uuid.uuid4(),
            name="Regra Teste",
            billing_type=BillingType.TAXA_CONDOMINIAL.value,
            frequency=BillingFrequency.MENSAL.value,
            base_value=Decimal("100.00"),
            due_day=10,
            generation_day=1,
            status=BillingRuleStatus.ATIVA.value,
        )

        rule.cancel("Regra substituida")

        assert rule.status == BillingRuleStatus.CANCELADA.value
        assert "Regra substituida" in rule.notes

    def test_billing_frequencies(self):
        """Testa todas as frequencias de cobranca."""
        frequencies = [
            BillingFrequency.MENSAL,
            BillingFrequency.BIMESTRAL,
            BillingFrequency.TRIMESTRAL,
            BillingFrequency.SEMESTRAL,
            BillingFrequency.ANUAL,
            BillingFrequency.AVULSO,
        ]

        for f in frequencies:
            rule = BillingRule(
                condominio_id=uuid.uuid4(),
                name="Regra Teste",
                billing_type=BillingType.TAXA_CONDOMINIAL.value,
                frequency=f.value,
                base_value=Decimal("100.00"),
                due_day=10,
                generation_day=1,
            )
            assert rule.frequency == f.value

    def test_billing_types(self):
        """Testa todos os tipos de cobranca."""
        types = [
            BillingType.TAXA_CONDOMINIAL,
            BillingType.TAXA_EXTRA,
            BillingType.RESERVA,
            BillingType.MULTA,
            BillingType.AGUA,
            BillingType.GAS,
            BillingType.FUNDO_RESERVA,
            BillingType.RATEIO_EXTRA,
        ]

        for t in types:
            rule = BillingRule(
                condominio_id=uuid.uuid4(),
                name="Regra Teste",
                billing_type=t.value,
                frequency=BillingFrequency.MENSAL.value,
                base_value=Decimal("100.00"),
                due_day=10,
                generation_day=1,
            )
            assert rule.billing_type == t.value

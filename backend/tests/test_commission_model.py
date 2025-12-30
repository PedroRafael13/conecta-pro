"""
Testes para Commission Models.
"""

import json
import uuid
from datetime import date, datetime, timedelta

import pytest

from modules.crm.models.commission import (
    Commission,
    CommissionPayment,
    CommissionRule,
    CommissionStatus,
    CommissionSummary,
    CommissionTrigger,
    CommissionType,
    PaymentMethod,
    SellerCommissionRule,
)


class TestCommissionRule:
    """Testes para CommissionRule model."""

    def test_create_rule(self):
        """Testa criação de regra."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Regra Padrão",
            description="Regra padrão de comissão",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=30,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        assert rule.name == "Regra Padrão"
        assert rule.commission_type == "percentage"
        assert rule.base_value == 10.0

    def test_rule_is_valid(self):
        """Testa verificação de vigência."""
        # Regra válida
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Regra Válida",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today() - timedelta(days=10),
            valid_until=date.today() + timedelta(days=10),
            priority=0,
            is_active=True,
        )
        assert rule.is_valid is True

        # Regra expirada
        expired_rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Regra Expirada",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today() - timedelta(days=60),
            valid_until=date.today() - timedelta(days=30),
            priority=0,
            is_active=True,
        )
        assert expired_rule.is_valid is False

    def test_calculate_commission_fixed(self):
        """Testa cálculo de comissão fixa."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Comissão Fixa",
            commission_type=CommissionType.FIXED.value,
            base_value=500.0,
            trigger=CommissionTrigger.ON_SIGNATURE.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        # Independente do valor, comissão é fixa
        assert rule.calculate_commission(1000.0) == 500.0
        assert rule.calculate_commission(5000.0) == 500.0
        assert rule.calculate_commission(100000.0) == 500.0

    def test_calculate_commission_percentage(self):
        """Testa cálculo de comissão percentual."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Comissão 10%",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,  # 10%
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        assert rule.calculate_commission(1000.0) == 100.0
        assert rule.calculate_commission(5000.0) == 500.0
        assert rule.calculate_commission(10000.0) == 1000.0

    def test_calculate_commission_margin(self):
        """Testa cálculo de comissão sobre margem."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Comissão Margem",
            commission_type=CommissionType.MARGIN.value,
            base_value=20.0,  # 20% da margem
            trigger=CommissionTrigger.ON_FULL_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        # Venda de 10000 com margem de 3000
        assert rule.calculate_commission(10000.0, margin=3000.0) == 600.0

    def test_calculate_commission_progressive(self):
        """Testa cálculo de comissão progressiva."""
        scale = [
            {"min": 0, "max": 10000, "rate": 5},
            {"min": 10001, "max": 50000, "rate": 7},
            {"min": 50001, "max": float("inf"), "rate": 10},
        ]

        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Comissão Progressiva",
            commission_type=CommissionType.PROGRESSIVE.value,
            base_value=5.0,  # fallback
            progressive_scale=json.dumps(scale),
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        # Faixa 1: 5%
        assert rule.calculate_commission(5000.0) == 250.0

        # Faixa 2: 7%
        assert rule.calculate_commission(30000.0) == 2100.0

        # Faixa 3: 10%
        assert rule.calculate_commission(100000.0) == 10000.0

    def test_calculate_commission_with_limits(self):
        """Testa limites mínimo e máximo."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Comissão com Limites",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            min_value=100.0,  # Mínimo R$100
            max_value=5000.0,  # Máximo R$5000
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        # Abaixo do mínimo
        assert rule.calculate_commission(500.0) == 100.0  # 50 < 100, usa 100

        # Normal
        assert rule.calculate_commission(10000.0) == 1000.0

        # Acima do máximo
        assert rule.calculate_commission(100000.0) == 5000.0  # 10000 > 5000, usa 5000


class TestCommission:
    """Testes para Commission model."""

    def test_create_commission(self):
        """Testa criação de comissão."""
        commission = Commission(
            id=str(uuid.uuid4()),
            reference_number="COM-2024-00001",
            seller_id=str(uuid.uuid4()),
            sale_value=10000.0,
            sale_margin=3000.0,
            commission_type=CommissionType.PERCENTAGE.value,
            commission_rate=10.0,
            base_commission=1000.0,
            adjustments=0.0,
            final_commission=1000.0,
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            is_active=True,
        )

        assert commission.reference_number == "COM-2024-00001"
        assert commission.base_commission == 1000.0
        assert commission.final_commission == 1000.0
        assert commission.is_pending is True

    def test_commission_status_properties(self):
        """Testa propriedades de status."""
        commission = Commission(
            id=str(uuid.uuid4()),
            reference_number="COM-2024-00002",
            seller_id=str(uuid.uuid4()),
            sale_value=5000.0,
            sale_margin=0.0,
            commission_type="percentage",
            commission_rate=10.0,
            base_commission=500.0,
            adjustments=0.0,
            final_commission=500.0,
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_SIGNATURE.value,
            is_active=True,
        )

        assert commission.is_pending is True
        assert commission.is_approved is False
        assert commission.is_paid is False

        # Mudar para aprovada
        commission.status = CommissionStatus.APPROVED.value
        assert commission.is_pending is False
        assert commission.is_approved is True
        assert commission.is_paid is False

        # Mudar para paga
        commission.status = CommissionStatus.PAID.value
        assert commission.is_pending is False
        assert commission.is_approved is False
        assert commission.is_paid is True

    def test_commission_is_overdue(self):
        """Testa verificação de atraso."""
        # Não atrasada
        commission = Commission(
            id=str(uuid.uuid4()),
            reference_number="COM-2024-00003",
            seller_id=str(uuid.uuid4()),
            sale_value=5000.0,
            sale_margin=0.0,
            commission_type="percentage",
            commission_rate=10.0,
            base_commission=500.0,
            adjustments=0.0,
            final_commission=500.0,
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            due_date=date.today() + timedelta(days=30),
            is_active=True,
        )

        assert commission.is_overdue is False

        # Atrasada
        commission.due_date = date.today() - timedelta(days=5)
        assert commission.is_overdue is True

        # Paga não é atrasada
        commission.status = CommissionStatus.PAID.value
        assert commission.is_overdue is False

    def test_commission_days_until_due(self):
        """Testa cálculo de dias até vencimento."""
        commission = Commission(
            id=str(uuid.uuid4()),
            reference_number="COM-2024-00004",
            seller_id=str(uuid.uuid4()),
            sale_value=5000.0,
            sale_margin=0.0,
            commission_type="percentage",
            commission_rate=10.0,
            base_commission=500.0,
            adjustments=0.0,
            final_commission=500.0,
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            due_date=date.today() + timedelta(days=15),
            is_active=True,
        )

        assert commission.days_until_due == 15

        # Sem data de vencimento
        commission.due_date = None
        assert commission.days_until_due is None


class TestCommissionSummary:
    """Testes para CommissionSummary model."""

    def test_create_summary(self):
        """Testa criação de resumo mensal."""
        summary = CommissionSummary(
            id=str(uuid.uuid4()),
            seller_id=str(uuid.uuid4()),
            year=2024,
            month=12,
            total_sales=50000.0,
            total_sales_count=10,
            total_commissions=5000.0,
            total_paid=3000.0,
            total_pending=2000.0,
            sales_target=60000.0,
            target_percentage=83.33,
            bonus_earned=500.0,
            is_closed=False,
        )

        assert summary.year == 2024
        assert summary.month == 12
        assert summary.total_sales == 50000.0
        assert summary.is_target_achieved is False

    def test_summary_target_achieved(self):
        """Testa verificação de meta atingida."""
        summary = CommissionSummary(
            id=str(uuid.uuid4()),
            seller_id=str(uuid.uuid4()),
            year=2024,
            month=12,
            total_sales=65000.0,
            total_sales_count=12,
            total_commissions=6500.0,
            total_paid=6500.0,
            total_pending=0.0,
            sales_target=60000.0,
            target_percentage=108.33,
            bonus_earned=1000.0,
            is_closed=False,
        )

        assert summary.is_target_achieved is True
        assert summary.remaining_to_target == 0.0

    def test_summary_remaining_to_target(self):
        """Testa cálculo de valor restante para meta."""
        summary = CommissionSummary(
            id=str(uuid.uuid4()),
            seller_id=str(uuid.uuid4()),
            year=2024,
            month=12,
            total_sales=40000.0,
            total_sales_count=8,
            total_commissions=4000.0,
            total_paid=2000.0,
            total_pending=2000.0,
            sales_target=60000.0,
            bonus_earned=0.0,
            is_closed=False,
        )

        assert summary.remaining_to_target == 20000.0


class TestSellerCommissionRule:
    """Testes para SellerCommissionRule model."""

    def test_create_seller_rule(self):
        """Testa associação de regra a vendedor."""
        seller_rule = SellerCommissionRule(
            id=str(uuid.uuid4()),
            seller_id=str(uuid.uuid4()),
            rule_id=str(uuid.uuid4()),
            custom_base_value=12.0,  # Taxa customizada
            valid_from=date.today(),
            is_active=True,
        )

        assert seller_rule.custom_base_value == 12.0


class TestCommissionPayment:
    """Testes para CommissionPayment model."""

    def test_create_payment(self):
        """Testa criação de pagamento."""
        payment = CommissionPayment(
            id=str(uuid.uuid4()),
            commission_id=str(uuid.uuid4()),
            amount=1000.0,
            payment_method=PaymentMethod.PAYROLL.value,
            payment_date=date.today(),
            is_confirmed=False,
        )

        assert payment.amount == 1000.0
        assert payment.payment_method == "payroll"
        assert payment.is_confirmed is False


class TestCommissionTypeEnum:
    """Testes para enums."""

    def test_commission_types(self):
        """Testa tipos de comissão."""
        assert CommissionType.FIXED.value == "fixed"
        assert CommissionType.PERCENTAGE.value == "percentage"
        assert CommissionType.MARGIN.value == "margin"
        assert CommissionType.PROGRESSIVE.value == "progressive"
        assert CommissionType.BONUS.value == "bonus"

    def test_commission_triggers(self):
        """Testa gatilhos de comissão."""
        assert CommissionTrigger.ON_SIGNATURE.value == "on_signature"
        assert CommissionTrigger.ON_FIRST_PAYMENT.value == "on_first_payment"
        assert CommissionTrigger.ON_EACH_PAYMENT.value == "on_each_payment"
        assert CommissionTrigger.ON_FULL_PAYMENT.value == "on_full_payment"
        assert CommissionTrigger.MONTHLY.value == "monthly"

    def test_commission_status(self):
        """Testa status de comissão."""
        assert CommissionStatus.PENDING.value == "pending"
        assert CommissionStatus.APPROVED.value == "approved"
        assert CommissionStatus.PAID.value == "paid"
        assert CommissionStatus.CANCELLED.value == "cancelled"
        assert CommissionStatus.REVERSED.value == "reversed"

    def test_payment_methods(self):
        """Testa métodos de pagamento."""
        assert PaymentMethod.PAYROLL.value == "payroll"
        assert PaymentMethod.BANK_TRANSFER.value == "bank_transfer"
        assert PaymentMethod.PIX.value == "pix"
        assert PaymentMethod.CHECK.value == "check"

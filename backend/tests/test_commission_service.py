"""
Testes para Commission Service.
"""

import uuid
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from modules.crm.models.commission import (
    Commission,
    CommissionRule,
    CommissionStatus,
    CommissionSummary,
    CommissionTrigger,
    CommissionType,
)
from modules.crm.services.commission_service import CommissionService


class TestCommissionService:
    """Testes para CommissionService."""

    @pytest.fixture
    def service(self):
        """Fixture para o serviço."""
        return CommissionService()

    @pytest.fixture
    def sample_rule(self):
        """Fixture para regra de exemplo."""
        return CommissionRule(
            id=str(uuid.uuid4()),
            name="Regra Padrão 10%",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=30,
            applies_to_all=True,
            valid_from=date.today() - timedelta(days=30),
            priority=0,
            is_active=True,
        )

    @pytest.fixture
    def sample_commissions(self):
        """Fixture para comissões de exemplo."""
        seller_id = str(uuid.uuid4())
        now = datetime.utcnow()
        return [
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-2024-00001",
                seller_id=seller_id,
                sale_value=10000.0,
                sale_margin=3000.0,
                commission_type=CommissionType.PERCENTAGE.value,
                commission_rate=10.0,
                base_commission=1000.0,
                adjustments=0.0,
                final_commission=1000.0,
                status=CommissionStatus.PAID.value,
                trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
                is_active=True,
                created_at=now,
            ),
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-2024-00002",
                seller_id=seller_id,
                sale_value=5000.0,
                sale_margin=1500.0,
                commission_type=CommissionType.PERCENTAGE.value,
                commission_rate=10.0,
                base_commission=500.0,
                adjustments=0.0,
                final_commission=500.0,
                status=CommissionStatus.APPROVED.value,
                trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
                is_active=True,
                created_at=now,
            ),
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-2024-00003",
                seller_id=seller_id,
                sale_value=20000.0,
                sale_margin=6000.0,
                commission_type=CommissionType.PERCENTAGE.value,
                commission_rate=10.0,
                base_commission=2000.0,
                adjustments=0.0,
                final_commission=2000.0,
                status=CommissionStatus.PENDING.value,
                trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
                is_active=True,
                created_at=now,
            ),
        ]


class TestGenerateReferenceNumber:
    """Testes para geração de número de referência."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    def test_generate_reference_number(self, service):
        """Testa geração de número de referência."""
        ref = service.generate_reference_number(1)
        year = date.today().year
        assert ref == f"COM-{year}-00001"

    def test_generate_reference_sequential(self, service):
        """Testa sequência de referências."""
        ref1 = service.generate_reference_number(1)
        ref2 = service.generate_reference_number(100)
        ref3 = service.generate_reference_number(99999)

        year = date.today().year
        assert ref1 == f"COM-{year}-00001"
        assert ref2 == f"COM-{year}-00100"
        assert ref3 == f"COM-{year}-99999"


class TestFindApplicableRule:
    """Testes para encontrar regra aplicável."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    @pytest.fixture
    def sample_rules(self):
        """Fixture para regras de exemplo."""
        return [
            CommissionRule(
                id=str(uuid.uuid4()),
                name="Regra Padrão 10%",
                commission_type=CommissionType.PERCENTAGE.value,
                base_value=10.0,
                trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
                trigger_delay_days=0,
                applies_to_all=True,
                valid_from=date.today() - timedelta(days=30),
                priority=0,
                is_active=True,
            ),
            CommissionRule(
                id=str(uuid.uuid4()),
                name="Regra Premium 15%",
                commission_type=CommissionType.PERCENTAGE.value,
                base_value=15.0,
                trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
                trigger_delay_days=0,
                applies_to_all=False,
                min_sale_value=50000.0,
                valid_from=date.today() - timedelta(days=30),
                priority=10,  # Maior prioridade
                is_active=True,
            ),
        ]

    def test_find_applicable_rule_all(self, service, sample_rules):
        """Testa encontrar regra aplicável a todos."""
        rule = service.find_applicable_rule(
            rules=sample_rules,
            sale_value=10000.0,
        )

        assert rule is not None
        assert rule.name == "Regra Padrão 10%"

    def test_find_applicable_rule_by_value(self, service, sample_rules):
        """Testa encontrar regra por valor mínimo."""
        # Valor abaixo do mínimo da regra premium
        rule = service.find_applicable_rule(
            rules=sample_rules,
            sale_value=10000.0,
        )
        assert rule.name == "Regra Padrão 10%"

    def test_find_applicable_rule_expired_excluded(self, service):
        """Testa que regras expiradas são ignoradas."""
        expired_rules = [
            CommissionRule(
                id=str(uuid.uuid4()),
                name="Regra Expirada",
                commission_type=CommissionType.PERCENTAGE.value,
                base_value=20.0,
                trigger=CommissionTrigger.ON_SIGNATURE.value,
                trigger_delay_days=0,
                applies_to_all=True,
                valid_from=date.today() - timedelta(days=60),
                valid_until=date.today() - timedelta(days=30),
                priority=100,
                is_active=True,
            ),
        ]

        rule = service.find_applicable_rule(
            rules=expired_rules,
            sale_value=10000.0,
        )

        assert rule is None

    def test_find_applicable_rule_no_rules(self, service):
        """Testa com lista vazia."""
        rule = service.find_applicable_rule(
            rules=[],
            sale_value=10000.0,
        )
        assert rule is None


class TestCalculateCommission:
    """Testes para cálculo de comissão."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    def test_calculate_commission_percentage(self, service):
        """Testa cálculo de comissão percentual."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="10%",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        result = service.calculate_commission(
            rule=rule,
            sale_value=10000.0,
        )

        assert isinstance(result, dict)
        assert result["base_commission"] == 1000.0
        assert result["commission_rate"] == 10.0
        assert result["commission_type"] == "percentage"

    def test_calculate_commission_fixed(self, service):
        """Testa cálculo de comissão fixa."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Fixa R$500",
            commission_type=CommissionType.FIXED.value,
            base_value=500.0,
            trigger=CommissionTrigger.ON_SIGNATURE.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        result = service.calculate_commission(
            rule=rule,
            sale_value=10000.0,
        )

        assert result["base_commission"] == 500.0
        assert result["commission_type"] == "fixed"

    def test_calculate_commission_margin(self, service):
        """Testa cálculo sobre margem."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="Margem 20%",
            commission_type=CommissionType.MARGIN.value,
            base_value=20.0,
            trigger=CommissionTrigger.ON_FULL_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        result = service.calculate_commission(
            rule=rule,
            sale_value=10000.0,
            sale_margin=3000.0,
        )

        assert result["base_commission"] == 600.0  # 20% de 3000

    def test_calculate_commission_with_limits(self, service):
        """Testa cálculo com limites."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="10% com limites",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            min_value=100.0,
            max_value=5000.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        # Abaixo do mínimo
        result = service.calculate_commission(rule=rule, sale_value=500.0)
        assert result["base_commission"] == 100.0  # Mínimo

        # Normal
        result = service.calculate_commission(rule=rule, sale_value=10000.0)
        assert result["base_commission"] == 1000.0

        # Acima do máximo
        result = service.calculate_commission(rule=rule, sale_value=100000.0)
        assert result["base_commission"] == 5000.0  # Máximo

    def test_calculate_commission_custom_rate(self, service):
        """Testa cálculo com taxa customizada."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="10%",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            trigger_delay_days=0,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        result = service.calculate_commission(
            rule=rule,
            sale_value=10000.0,
            custom_rate=15.0,  # Override para 15%
        )

        assert result["base_commission"] == 1500.0
        assert result["commission_rate"] == 15.0

    def test_calculate_commission_has_due_date(self, service):
        """Testa que resultado inclui data de vencimento."""
        rule = CommissionRule(
            id=str(uuid.uuid4()),
            name="10%",
            commission_type=CommissionType.PERCENTAGE.value,
            base_value=10.0,
            trigger=CommissionTrigger.ON_SIGNATURE.value,
            trigger_delay_days=30,
            applies_to_all=True,
            valid_from=date.today(),
            priority=0,
            is_active=True,
        )

        result = service.calculate_commission(rule=rule, sale_value=10000.0)

        assert "due_date" in result
        assert result["due_date"] == date.today() + timedelta(days=30)


class TestCalculateStats:
    """Testes para cálculo de estatísticas."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    @pytest.fixture
    def sample_commissions(self):
        seller_id = str(uuid.uuid4())
        now = datetime.utcnow()
        return [
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-001",
                seller_id=seller_id,
                sale_value=10000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=1000.0,
                adjustments=0.0,
                final_commission=1000.0,
                status=CommissionStatus.PAID.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-002",
                seller_id=seller_id,
                sale_value=5000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=500.0,
                adjustments=0.0,
                final_commission=500.0,
                status=CommissionStatus.PENDING.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
        ]

    def test_calculate_stats(self, service, sample_commissions):
        """Testa cálculo de estatísticas."""
        stats = service.calculate_stats(sample_commissions)

        assert stats.total_commissions == 2
        assert stats.total_value == 1500.0
        assert stats.paid_value == 1000.0
        assert stats.pending_value == 500.0
        assert stats.paid_count == 1
        assert stats.pending_count == 1

    def test_calculate_stats_empty(self, service):
        """Testa estatísticas com lista vazia."""
        stats = service.calculate_stats([])

        assert stats.total_commissions == 0
        assert stats.total_value == 0.0
        assert stats.avg_commission_value == 0.0


class TestCalculateSellerStats:
    """Testes para estatísticas por vendedor."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    def test_calculate_seller_stats(self, service):
        """Testa estatísticas por vendedor."""
        seller_id = str(uuid.uuid4())
        now = datetime.utcnow()

        commissions = [
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-001",
                seller_id=seller_id,
                sale_value=10000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=1000.0,
                adjustments=0.0,
                final_commission=1000.0,
                status=CommissionStatus.PAID.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-002",
                seller_id=seller_id,
                sale_value=5000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=500.0,
                adjustments=0.0,
                final_commission=500.0,
                status=CommissionStatus.PENDING.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
        ]

        stats = service.calculate_seller_stats(
            commissions=commissions,
            seller_id=seller_id,
            seller_name="Vendedor Teste",
        )

        assert stats.seller_id == seller_id
        assert stats.seller_name == "Vendedor Teste"
        assert stats.total_sales == 15000.0
        assert stats.total_commissions == 1500.0
        assert stats.paid_commissions == 1000.0
        assert stats.pending_commissions == 500.0
        assert stats.sales_count == 2

    def test_calculate_seller_stats_with_target(self, service):
        """Testa estatísticas com meta."""
        seller_id = str(uuid.uuid4())
        now = datetime.utcnow()

        commissions = [
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-001",
                seller_id=seller_id,
                sale_value=50000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=5000.0,
                adjustments=0.0,
                final_commission=5000.0,
                status=CommissionStatus.PAID.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
        ]

        stats = service.calculate_seller_stats(
            commissions=commissions,
            seller_id=seller_id,
            target=100000.0,
        )

        assert stats.target == 100000.0
        # target_percentage é calculado sobre current_month_sales
        assert stats.current_month_sales == 50000.0

    def test_calculate_seller_stats_no_commissions(self, service):
        """Testa estatísticas de vendedor sem comissões."""
        seller_id = str(uuid.uuid4())

        stats = service.calculate_seller_stats(
            commissions=[],
            seller_id=seller_id,
        )

        assert stats.seller_id == seller_id
        assert stats.total_sales == 0.0
        assert stats.sales_count == 0


class TestGenerateRanking:
    """Testes para ranking de vendedores."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    def test_generate_ranking(self, service):
        """Testa geração de ranking."""
        seller1 = str(uuid.uuid4())
        seller2 = str(uuid.uuid4())
        now = datetime.utcnow()

        commissions = [
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-001",
                seller_id=seller1,
                sale_value=10000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=1000.0,
                adjustments=0.0,
                final_commission=1000.0,
                status=CommissionStatus.PAID.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
            Commission(
                id=str(uuid.uuid4()),
                reference_number="COM-002",
                seller_id=seller2,
                sale_value=50000.0,
                sale_margin=0.0,
                commission_type="percentage",
                commission_rate=10.0,
                base_commission=5000.0,
                adjustments=0.0,
                final_commission=5000.0,
                status=CommissionStatus.PAID.value,
                trigger="on_first_payment",
                is_active=True,
                created_at=now,
            ),
        ]

        sellers = {
            seller1: "Vendedor 1",
            seller2: "Vendedor 2",
        }

        ranking = service.generate_ranking(
            commissions=commissions,
            sellers=sellers,
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
        )

        assert ranking.total_commissions == 6000.0
        assert ranking.total_sales == 60000.0
        assert len(ranking.sellers) == 2

        # Seller2 deve estar em primeiro (maior valor)
        assert ranking.sellers[0].seller_id == seller2
        assert ranking.sellers[0].total_commissions == 5000.0


class TestApplyAdjustment:
    """Testes para aplicação de ajustes."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    @pytest.fixture
    def sample_commission(self):
        return Commission(
            id=str(uuid.uuid4()),
            reference_number="COM-001",
            seller_id=str(uuid.uuid4()),
            sale_value=10000.0,
            sale_margin=0.0,
            commission_type="percentage",
            commission_rate=10.0,
            base_commission=1000.0,
            adjustments=0.0,
            final_commission=1000.0,
            status=CommissionStatus.PENDING.value,
            trigger="on_first_payment",
            is_active=True,
        )

    def test_apply_positive_adjustment(self, service, sample_commission):
        """Testa ajuste positivo."""
        new_final = service.apply_adjustment(
            commission=sample_commission,
            adjustment=200.0,
            reason="Bônus de performance",
        )

        assert new_final == 1200.0

    def test_apply_negative_adjustment(self, service, sample_commission):
        """Testa ajuste negativo."""
        new_final = service.apply_adjustment(
            commission=sample_commission,
            adjustment=-300.0,
            reason="Desconto por devolução",
        )

        assert new_final == 700.0

    def test_apply_adjustment_no_negative_result(self, service, sample_commission):
        """Testa que não permite resultado negativo."""
        new_final = service.apply_adjustment(
            commission=sample_commission,
            adjustment=-2000.0,  # Maior que a comissão base
            reason="Grande estorno",
        )

        assert new_final == 0.0  # Mínimo é 0


class TestProcessTrigger:
    """Testes para processamento de gatilhos."""

    @pytest.fixture
    def service(self):
        return CommissionService()

    @pytest.fixture
    def sample_commission(self):
        return Commission(
            id=str(uuid.uuid4()),
            reference_number="COM-001",
            seller_id=str(uuid.uuid4()),
            sale_value=10000.0,
            sale_margin=0.0,
            commission_type="percentage",
            commission_rate=10.0,
            base_commission=1000.0,
            adjustments=0.0,
            final_commission=1000.0,
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
            is_active=True,
        )

    def test_should_process_trigger_match(self, service, sample_commission):
        """Testa gatilho correspondente."""
        should = service.should_process_trigger(
            commission=sample_commission,
            event="first_payment",
        )

        assert should is True

    def test_should_process_trigger_no_match(self, service, sample_commission):
        """Testa gatilho não correspondente."""
        should = service.should_process_trigger(
            commission=sample_commission,
            event="signature",  # Não é o gatilho correto
        )

        assert should is False

    def test_should_process_trigger_already_approved(self, service, sample_commission):
        """Testa que comissão já aprovada não é processada."""
        sample_commission.status = CommissionStatus.APPROVED.value

        should = service.should_process_trigger(
            commission=sample_commission,
            event="first_payment",
        )

        assert should is False

    def test_process_trigger(self, service, sample_commission):
        """Testa processamento de gatilho."""
        updated = service.process_trigger(sample_commission)

        assert updated.status == CommissionStatus.APPROVED.value
        assert updated.trigger_date == date.today()

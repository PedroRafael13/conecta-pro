"""
Comprehensive tests for CRM services:
- CommissionService (commission_service.py)
- ContractService (contract_service.py)
- ProposalService (proposal_service.py)
- PDFGenerator (pdf_generator.py)
- ProposalSignatureService (signature_integration.py)
"""

import json
import os
import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.crm.models.commission import (
    Commission,
    CommissionRule,
    CommissionStatus,
    CommissionSummary,
    CommissionTrigger,
    CommissionType,
)
from modules.crm.models.contract import AdjustmentIndex, Contract, ContractStatus, ContractType
from modules.crm.models.proposal import ApprovalAction, ProposalStatus, ProposalType
from modules.crm.services.commission_service import CommissionService
from modules.crm.services.contract_service import ContractService
from modules.crm.services.pdf_generator import (
    ClientInfo,
    CompanyInfo,
    PDFGenerator,
    ProposalData,
    ProposalItem,
)
from modules.crm.services.proposal_service import ProposalService
from modules.crm.services.signature_integration import (
    ProposalSignatureService,
    SignatureProvider,
    SignatureRequest,
    SignatureResult,
    SignatureStatus,
    SignerInfo,
)

# ===========================
# Helper factories
# ===========================


def _uid():
    return "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _make_rule(**overrides):
    rule = MagicMock(spec=CommissionRule)
    rule.is_valid = True
    rule.min_sale_value = None
    rule.max_sale_value = None
    rule.applies_to_all = True
    rule.product_categories = None
    rule.service_types = None
    rule.commission_type = CommissionType.PERCENTAGE.value
    rule.base_value = 10.0
    rule.min_value = None
    rule.max_value = None
    rule.progressive_scale = None
    rule.trigger = CommissionTrigger.ON_FIRST_PAYMENT.value
    rule.trigger_delay_days = 30
    rule.priority = 1
    rule.id = _uid()
    for k, v in overrides.items():
        setattr(rule, k, v)
    return rule


def _make_commission(**overrides):
    c = MagicMock(spec=Commission)
    c.seller_id = _uid()
    c.sale_value = 10000.0
    c.sale_margin = 3000.0
    c.base_commission = 1000.0
    c.adjustments = 0.0
    c.final_commission = 1000.0
    c.status = CommissionStatus.PENDING.value
    c.trigger = CommissionTrigger.ON_FIRST_PAYMENT.value
    c.trigger_date = date.today()
    c.due_date = date.today() + timedelta(days=30)
    c.paid_date = None
    c.is_pending = True
    c.is_approved = False
    c.is_paid = False
    c.is_overdue = False
    c.pending_amount = 1000.0
    c.reference_number = "COM-2026-00001"
    c.created_at = datetime(2026, 3, 15, 10, 0, 0)
    c.payments = []
    c.rule = None
    c.updated_at = datetime.utcnow()
    for k, v in overrides.items():
        setattr(c, k, v)
    return c


def _make_contract(**overrides):
    c = MagicMock(spec=Contract)
    c.id = _uid()
    c.contract_number = "CT-001"
    c.status = ContractStatus.ACTIVE
    c.contract_type = ContractType.RECURRING
    c.monthly_value = Decimal("10000.00")
    c.is_renewable = True
    c.end_date = date.today() + timedelta(days=365)
    c.renewal_period_months = 12
    c.adjustment_enabled = True
    c.adjustment_index = AdjustmentIndex.IPCA
    c.adjustment_fixed_percent = None
    c.needs_adjustment = False
    c.next_adjustment_date = None
    c.days_until_adjustment = None
    c.has_sla = False
    c.sla_config = None
    c.is_expiring_soon = False
    for k, v in overrides.items():
        setattr(c, k, v)
    return c


def _make_proposal_data(**overrides):
    company = CompanyInfo(
        name="Test Co",
        cnpj="00.000.000/0001-00",
        address="Rua Test 123",
        city="Manaus",
        state="AM",
        zip_code="69000-000",
        phone="(92) 9999-9999",
        email="test@test.com",
        website="https://test.com",
    )
    client = ClientInfo(
        name="Client Co",
        document="11.111.111/0001-11",
        contact_name="John",
        email="john@client.com",
    )
    items = [
        ProposalItem(
            description="Vigilancia 24h",
            quantity=2,
            unit="mês",
            unit_price=Decimal("5000.00"),
            discount_percent=Decimal("0"),
            total=Decimal("10000.00"),
        )
    ]
    defaults = {
        "number": "PRO-2026-00001",
        "version": 1,
        "issue_date": date(2026, 3, 1),
        "valid_until": date(2026, 4, 1),
        "company": company,
        "client": client,
        "items": items,
        "subtotal": Decimal("10000.00"),
        "discount_value": Decimal("0.00"),
        "taxes": Decimal("0.00"),
        "total": Decimal("10000.00"),
    }
    defaults.update(overrides)
    return ProposalData(**defaults)


# ===========================
# CommissionService Tests
# ===========================


class TestCommissionService:
    def setup_method(self):
        self.svc = CommissionService()

    # -- generate_reference_number --
    def test_generate_reference_number(self):
        ref = self.svc.generate_reference_number(42)
        assert ref == f"COM-{date.today().year}-00042"

    def test_generate_reference_number_large_sequence(self):
        ref = self.svc.generate_reference_number(99999)
        assert "99999" in ref

    # -- find_applicable_rule --
    def test_find_applicable_rule_returns_highest_priority(self):
        r1 = _make_rule(priority=1)
        r2 = _make_rule(priority=5)
        result = self.svc.find_applicable_rule([r1, r2], 5000.0)
        assert result is r2

    def test_find_applicable_rule_none_when_empty(self):
        assert self.svc.find_applicable_rule([], 5000.0) is None

    def test_find_applicable_rule_skips_invalid(self):
        r = _make_rule(is_valid=False)
        assert self.svc.find_applicable_rule([r], 5000.0) is None

    def test_find_applicable_rule_filters_by_min_sale_value(self):
        r = _make_rule(min_sale_value=10000.0)
        assert self.svc.find_applicable_rule([r], 5000.0) is None
        assert self.svc.find_applicable_rule([r], 15000.0) is r

    def test_find_applicable_rule_filters_by_max_sale_value(self):
        r = _make_rule(max_sale_value=8000.0)
        assert self.svc.find_applicable_rule([r], 10000.0) is None
        assert self.svc.find_applicable_rule([r], 7000.0) is r

    def test_find_applicable_rule_applies_to_all_false_category_match(self):
        r = _make_rule(
            applies_to_all=False,
            product_categories=json.dumps(["security"]),
            service_types=None,
        )
        assert self.svc.find_applicable_rule([r], 5000.0, product_category="security") is r

    def test_find_applicable_rule_applies_to_all_false_no_match(self):
        r = _make_rule(
            applies_to_all=False,
            product_categories=json.dumps(["cleaning"]),
            service_types=None,
        )
        assert self.svc.find_applicable_rule([r], 5000.0, product_category="security") is None

    def test_find_applicable_rule_service_type_match(self):
        r = _make_rule(
            applies_to_all=False,
            product_categories=None,
            service_types=json.dumps(["monitoring"]),
        )
        result = self.svc.find_applicable_rule([r], 5000.0, service_type="monitoring")
        assert result is r

    def test_find_applicable_rule_bad_json_categories(self):
        r = _make_rule(
            applies_to_all=False,
            product_categories="not-json",
            service_types=None,
        )
        assert self.svc.find_applicable_rule([r], 5000.0, product_category="x") is None

    def test_find_applicable_rule_bad_json_service_types(self):
        r = _make_rule(
            applies_to_all=False,
            product_categories=None,
            service_types="not-json",
        )
        assert self.svc.find_applicable_rule([r], 5000.0, service_type="x") is None

    # -- calculate_commission --
    def test_calculate_commission_percentage(self):
        rule = _make_rule(commission_type=CommissionType.PERCENTAGE.value, base_value=10.0)
        result = self.svc.calculate_commission(rule, 50000.0)
        assert result["base_commission"] == 5000.0
        assert result["commission_type"] == CommissionType.PERCENTAGE.value

    def test_calculate_commission_fixed(self):
        rule = _make_rule(commission_type=CommissionType.FIXED.value, base_value=500.0)
        result = self.svc.calculate_commission(rule, 50000.0)
        assert result["base_commission"] == 500.0

    def test_calculate_commission_margin(self):
        rule = _make_rule(commission_type=CommissionType.MARGIN.value, base_value=20.0)
        result = self.svc.calculate_commission(rule, 50000.0, sale_margin=15000.0)
        assert result["base_commission"] == 3000.0

    def test_calculate_commission_bonus(self):
        rule = _make_rule(commission_type=CommissionType.BONUS.value, base_value=1000.0)
        result = self.svc.calculate_commission(rule, 50000.0)
        assert result["base_commission"] == 1000.0

    def test_calculate_commission_progressive(self):
        scale = json.dumps(
            [
                {"min": 0, "max": 10000, "rate": 5},
                {"min": 10001, "max": 50000, "rate": 8},
            ]
        )
        rule = _make_rule(
            commission_type=CommissionType.PROGRESSIVE.value,
            base_value=3.0,
            progressive_scale=scale,
        )
        result = self.svc.calculate_commission(rule, 20000.0)
        assert result["base_commission"] == 1600.0  # 20000 * 8%

    def test_calculate_commission_custom_rate_overrides(self):
        rule = _make_rule(base_value=10.0)
        result = self.svc.calculate_commission(rule, 10000.0, custom_rate=5.0)
        assert result["base_commission"] == 500.0
        assert result["commission_rate"] == 5.0

    def test_calculate_commission_min_value_applied(self):
        rule = _make_rule(base_value=1.0, min_value=500.0)
        result = self.svc.calculate_commission(rule, 1000.0)
        # 1% of 1000 = 10, but min is 500
        assert result["base_commission"] == 500.0

    def test_calculate_commission_max_value_applied(self):
        rule = _make_rule(base_value=50.0, max_value=100.0)
        result = self.svc.calculate_commission(rule, 10000.0)
        # 50% of 10000 = 5000, but max is 100
        assert result["base_commission"] == 100.0

    def test_calculate_commission_due_date(self):
        rule = _make_rule(trigger_delay_days=15)
        result = self.svc.calculate_commission(rule, 10000.0)
        assert result["due_date"] == result["trigger_date"] + timedelta(days=15)

    # -- _calculate_progressive --
    def test_progressive_no_scale(self):
        result = self.svc._calculate_progressive(None, 10000.0, 5.0)
        assert result == 500.0

    def test_progressive_bad_json(self):
        result = self.svc._calculate_progressive("bad-json", 10000.0, 5.0)
        assert result == 500.0

    def test_progressive_no_matching_tier(self):
        scale = json.dumps([{"min": 0, "max": 100, "rate": 2}])
        result = self.svc._calculate_progressive(scale, 10000.0, 5.0)
        assert result == 500.0  # falls back to default_rate

    # -- _calculate_trigger_date --
    def test_trigger_date_on_signature(self):
        result = self.svc._calculate_trigger_date(CommissionTrigger.ON_SIGNATURE.value)
        assert result == date.today()

    def test_trigger_date_monthly(self):
        result = self.svc._calculate_trigger_date(CommissionTrigger.MONTHLY.value)
        today = date.today()
        if today.month == 12:
            assert result == date(today.year + 1, 1, 1)
        else:
            assert result == date(today.year, today.month + 1, 1)

    def test_trigger_date_other(self):
        result = self.svc._calculate_trigger_date(CommissionTrigger.ON_FIRST_PAYMENT.value)
        assert result == date.today()

    # -- create_commission_from_proposal --
    def test_create_commission_from_proposal(self):
        proposal = MagicMock()
        proposal.total = 20000.0
        proposal.id = _uid()
        proposal.number = "PRO-2026-00001"
        rule = _make_rule(base_value=10.0)
        seller_id = "seller-123"

        result = self.svc.create_commission_from_proposal(proposal, rule, seller_id)
        assert result["seller_id"] == seller_id
        assert result["proposal_id"] == str(proposal.id)
        assert result["sale_value"] == 20000.0
        assert result["status"] == CommissionStatus.PENDING.value
        assert result["base_commission"] == 2000.0
        assert result["final_commission"] == 2000.0
        assert "Proposta PRO-2026-00001" in result["description"]

    def test_create_commission_from_proposal_with_custom_rate(self):
        proposal = MagicMock()
        proposal.total = 10000.0
        proposal.id = _uid()
        proposal.number = "PRO-2026-00002"
        rule = _make_rule(base_value=10.0)

        result = self.svc.create_commission_from_proposal(proposal, rule, "seller-1", custom_rate=5.0)
        assert result["commission_rate"] == 5.0
        assert result["base_commission"] == 500.0

    # -- apply_adjustment --
    def test_apply_adjustment_positive(self):
        c = _make_commission(base_commission=1000.0, adjustments=0.0)
        result = self.svc.apply_adjustment(c, 200.0, "bonus")
        assert result == 1200.0

    def test_apply_adjustment_negative_no_below_zero(self):
        c = _make_commission(base_commission=100.0, adjustments=0.0)
        result = self.svc.apply_adjustment(c, -500.0, "penalidade")
        assert result == 0.0

    def test_apply_adjustment_accumulates(self):
        c = _make_commission(base_commission=1000.0, adjustments=100.0)
        result = self.svc.apply_adjustment(c, 50.0, "extra")
        assert result == 1150.0  # 1000 + (100 + 50)

    # -- calculate_stats --
    def test_calculate_stats_empty(self):
        stats = self.svc.calculate_stats([])
        assert stats.total_commissions == 0
        assert stats.avg_commission_value == 0.0

    def test_calculate_stats_with_commissions(self):
        c1 = _make_commission(
            status=CommissionStatus.PENDING.value,
            final_commission=1000.0,
            is_overdue=False,
        )
        c2 = _make_commission(
            status=CommissionStatus.PAID.value,
            final_commission=2000.0,
            is_paid=True,
            is_overdue=False,
            paid_date=date(2026, 3, 20),
            trigger_date=date(2026, 3, 10),
        )
        stats = self.svc.calculate_stats([c1, c2])
        assert stats.total_commissions == 2
        assert stats.pending_count == 1
        assert stats.paid_count == 1
        assert stats.total_value == 3000.0
        assert stats.paid_value == 2000.0
        assert stats.avg_commission_value == 1500.0

    def test_calculate_stats_date_filtering(self):
        c1 = _make_commission(created_at=datetime(2026, 1, 15))
        c2 = _make_commission(created_at=datetime(2026, 3, 15))
        stats = self.svc.calculate_stats([c1, c2], date_from=date(2026, 3, 1))
        assert stats.total_commissions == 1

    def test_calculate_stats_date_to_filtering(self):
        c1 = _make_commission(created_at=datetime(2026, 1, 15))
        c2 = _make_commission(created_at=datetime(2026, 3, 15))
        stats = self.svc.calculate_stats([c1, c2], date_to=date(2026, 2, 1))
        assert stats.total_commissions == 1

    def test_calculate_stats_overdue(self):
        c = _make_commission(is_overdue=True, pending_amount=500.0)
        stats = self.svc.calculate_stats([c])
        assert stats.overdue_count == 1
        assert stats.overdue_value == 500.0

    def test_calculate_stats_avg_days_to_payment(self):
        c = _make_commission(
            status=CommissionStatus.PAID.value,
            is_paid=True,
            paid_date=date(2026, 3, 20),
            trigger_date=date(2026, 3, 10),
            is_overdue=False,
        )
        stats = self.svc.calculate_stats([c])
        assert stats.avg_days_to_payment == 10.0

    def test_calculate_stats_by_status_and_trigger(self):
        c = _make_commission(
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_SIGNATURE.value,
            is_overdue=False,
        )
        stats = self.svc.calculate_stats([c])
        assert CommissionStatus.PENDING.value in stats.by_status
        assert CommissionTrigger.ON_SIGNATURE.value in stats.by_trigger

    # -- calculate_seller_stats --
    def test_calculate_seller_stats(self):
        sid = "seller-1"
        c = _make_commission(
            seller_id=sid,
            sale_value=50000.0,
            final_commission=5000.0,
            is_pending=True,
            is_paid=False,
            created_at=datetime(date.today().year, date.today().month, 15),
        )
        stats = self.svc.calculate_seller_stats([c], sid, "Ana", target=100000.0)
        assert stats.seller_id == sid
        assert stats.seller_name == "Ana"
        assert stats.total_sales == 50000.0
        assert stats.total_commissions == 5000.0
        assert stats.sales_count == 1
        assert stats.commission_rate_avg == 10.0
        assert stats.target_percentage is not None

    def test_calculate_seller_stats_no_sales(self):
        stats = self.svc.calculate_seller_stats([], "seller-1")
        assert stats.total_sales == 0.0
        assert stats.commission_rate_avg == 0.0

    def test_calculate_seller_stats_no_target(self):
        stats = self.svc.calculate_seller_stats([], "seller-1", target=None)
        assert stats.target_percentage is None

    # -- generate_ranking --
    def test_generate_ranking(self):
        s1 = "seller-1"
        s2 = "seller-2"
        c1 = _make_commission(
            seller_id=s1,
            final_commission=5000.0,
            sale_value=50000.0,
            created_at=datetime(2026, 3, 10),
            is_pending=True,
            is_paid=False,
        )
        c2 = _make_commission(
            seller_id=s2,
            final_commission=3000.0,
            sale_value=30000.0,
            created_at=datetime(2026, 3, 10),
            is_pending=True,
            is_paid=False,
        )
        sellers = {s1: "Ana", s2: "Bob"}
        ranking = self.svc.generate_ranking([c1, c2], sellers, date(2026, 3, 1), date(2026, 3, 31))
        assert ranking.sellers[0].seller_name == "Ana"
        assert ranking.total_commissions == 8000.0
        assert ranking.total_sales == 80000.0

    # -- update_summary --
    def test_update_summary_with_target(self):
        summary = MagicMock(spec=CommissionSummary)
        summary.seller_id = "seller-1"
        summary.year = 2026
        summary.month = 3
        summary.sales_target = 100000.0
        c = _make_commission(
            seller_id="seller-1",
            sale_value=50000.0,
            final_commission=5000.0,
            is_paid=True,
            created_at=datetime(2026, 3, 15),
        )
        result = self.svc.update_summary(summary, [c])
        assert result.total_sales == 50000.0
        assert result.total_sales_count == 1
        assert result.total_commissions == 5000.0
        assert result.total_paid == 5000.0
        assert result.total_pending == 0.0
        assert result.target_percentage == 50.0

    def test_update_summary_no_target(self):
        summary = MagicMock(spec=CommissionSummary)
        summary.seller_id = "seller-1"
        summary.year = 2026
        summary.month = 3
        summary.sales_target = None
        result = self.svc.update_summary(summary, [])
        assert result.target_percentage is None

    # -- should_process_trigger --
    def test_should_process_trigger_signature(self):
        c = _make_commission(
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_SIGNATURE.value,
        )
        assert self.svc.should_process_trigger(c, "signature") is True

    def test_should_process_trigger_not_pending(self):
        c = _make_commission(status=CommissionStatus.APPROVED.value)
        assert self.svc.should_process_trigger(c, "signature") is False

    def test_should_process_trigger_wrong_event(self):
        c = _make_commission(
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT.value,
        )
        assert self.svc.should_process_trigger(c, "signature") is False

    def test_should_process_trigger_unknown_event(self):
        c = _make_commission(status=CommissionStatus.PENDING.value)
        assert self.svc.should_process_trigger(c, "unknown_event") is False

    def test_should_process_trigger_each_payment(self):
        c = _make_commission(
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_EACH_PAYMENT.value,
        )
        assert self.svc.should_process_trigger(c, "payment") is True

    def test_should_process_trigger_full_payment(self):
        c = _make_commission(
            status=CommissionStatus.PENDING.value,
            trigger=CommissionTrigger.ON_FULL_PAYMENT.value,
        )
        assert self.svc.should_process_trigger(c, "full_payment") is True

    # -- process_trigger --
    def test_process_trigger_default_date(self):
        c = _make_commission()
        c.rule = None
        result = self.svc.process_trigger(c)
        assert result.status == CommissionStatus.APPROVED.value
        assert result.trigger_date == date.today()

    def test_process_trigger_with_event_date(self):
        c = _make_commission()
        c.rule = None
        event_date = date(2026, 4, 1)
        result = self.svc.process_trigger(c, event_date)
        assert result.trigger_date == event_date

    def test_process_trigger_with_rule_delay(self):
        c = _make_commission()
        rule = MagicMock()
        rule.trigger_delay_days = 10
        c.rule = rule
        event_date = date(2026, 4, 1)
        result = self.svc.process_trigger(c, event_date)
        assert result.due_date == date(2026, 4, 11)


# ===========================
# ContractService Tests
# ===========================


class TestContractService:
    def setup_method(self):
        self.svc = ContractService()

    # -- calculate_renewal --
    def test_renewal_not_renewable(self):
        c = _make_contract(is_renewable=False)
        result = self.svc.calculate_renewal(c)
        assert result.success is False
        assert "não é elegível" in result.message

    def test_renewal_not_active(self):
        c = _make_contract(status=ContractStatus.DRAFT)
        result = self.svc.calculate_renewal(c)
        assert result.success is False
        assert "ativos" in result.message

    def test_renewal_success_no_adjustment(self):
        c = _make_contract(
            adjustment_enabled=False,
            needs_adjustment=False,
            end_date=date(2026, 12, 31),
            renewal_period_months=12,
        )
        result = self.svc.calculate_renewal(c)
        assert result.success is True
        assert result.adjustment_applied is False
        assert result.new_end_date == date(2027, 12, 31)

    def test_renewal_with_custom_end_date(self):
        c = _make_contract()
        custom = date(2028, 6, 30)
        result = self.svc.calculate_renewal(c, new_end_date=custom)
        assert result.new_end_date == custom

    def test_renewal_with_custom_adjustment(self):
        c = _make_contract(needs_adjustment=True)
        result = self.svc.calculate_renewal(c, custom_adjustment_percent=Decimal("10.0"))
        assert result.success is True
        assert result.adjustment_applied is True
        assert result.new_value == Decimal("11000.00")

    def test_renewal_with_fixed_index(self):
        c = _make_contract(
            needs_adjustment=True,
            adjustment_index=AdjustmentIndex.FIXED,
            adjustment_fixed_percent=Decimal("5.00"),
        )
        result = self.svc.calculate_renewal(c)
        assert result.adjustment_applied is True
        assert result.new_value == Decimal("10500.00")

    def test_renewal_with_economic_index_ipca(self):
        c = _make_contract(needs_adjustment=True, adjustment_index=AdjustmentIndex.IPCA)
        result = self.svc.calculate_renewal(c)
        assert result.adjustment_applied is True
        # IPCA = 4.23%
        expected = (Decimal("10000.00") * Decimal("1.0423")).quantize(Decimal("0.01"))
        assert result.new_value == expected

    def test_renewal_no_end_date_uses_today(self):
        c = _make_contract(end_date=None, needs_adjustment=False, adjustment_enabled=False)
        result = self.svc.calculate_renewal(c)
        assert result.success is True

    # -- calculate_adjustment --
    def test_adjustment_disabled(self):
        c = _make_contract(adjustment_enabled=False)
        result = self.svc.calculate_adjustment(c)
        assert result.success is False

    def test_adjustment_custom_percent(self):
        c = _make_contract()
        result = self.svc.calculate_adjustment(c, custom_percent=Decimal("8.00"))
        assert result.success is True
        assert result.index_used == AdjustmentIndex.CUSTOM
        expected = Decimal("10800.00")
        assert result.new_value == expected

    def test_adjustment_fixed_index(self):
        c = _make_contract(
            adjustment_index=AdjustmentIndex.FIXED,
            adjustment_fixed_percent=Decimal("3.00"),
        )
        result = self.svc.calculate_adjustment(c)
        assert result.index_used == AdjustmentIndex.FIXED
        assert result.new_value == Decimal("10300.00")

    def test_adjustment_igpm(self):
        c = _make_contract(adjustment_index=AdjustmentIndex.IGPM)
        result = self.svc.calculate_adjustment(c)
        assert result.index_used == AdjustmentIndex.IGPM
        expected = (Decimal("10000.00") * Decimal("1.045")).quantize(Decimal("0.01"))
        assert result.new_value == expected

    def test_adjustment_unknown_index(self):
        c = _make_contract(adjustment_index="unknown_index")
        result = self.svc.calculate_adjustment(c)
        assert result.adjustment_percent == Decimal("0")

    def test_adjustment_effective_date_custom(self):
        c = _make_contract()
        eff = date(2026, 7, 1)
        result = self.svc.calculate_adjustment(c, effective_date=eff)
        assert result.effective_date == eff

    def test_adjustment_effective_date_from_contract(self):
        c = _make_contract(next_adjustment_date=date(2026, 9, 1))
        result = self.svc.calculate_adjustment(c)
        assert result.effective_date == date(2026, 9, 1)

    # -- calculate_sla --
    def test_sla_no_sla(self):
        c = _make_contract(has_sla=False, sla_config=None)
        result = self.svc.calculate_sla(c, [])
        assert result.target_met is True
        assert result.penalty_amount == Decimal("0")

    def test_sla_all_targets_met(self):
        c = _make_contract(
            has_sla=True,
            sla_config={"penalty": {"min_score": 80, "max_penalty_percent": 10}},
        )
        indicators = [
            {"name": "uptime", "target": 95, "actual": 98, "weight": 1},
        ]
        result = self.svc.calculate_sla(c, indicators)
        assert result.overall_score > Decimal("100")
        assert result.target_met is True
        assert result.penalty_applicable is False

    def test_sla_below_min_score_penalty(self):
        c = _make_contract(
            has_sla=True,
            sla_config={"penalty": {"min_score": 80, "max_penalty_percent": 10}},
        )
        indicators = [
            {"name": "uptime", "target": 100, "actual": 70, "weight": 1},
        ]
        result = self.svc.calculate_sla(c, indicators)
        assert result.target_met is False
        assert result.penalty_applicable is True
        assert result.penalty_amount > Decimal("0")

    def test_sla_above_min_but_below_100(self):
        c = _make_contract(
            has_sla=True,
            sla_config={"penalty": {"min_score": 80, "max_penalty_percent": 10}},
        )
        indicators = [
            {"name": "uptime", "target": 100, "actual": 90, "weight": 1},
        ]
        result = self.svc.calculate_sla(c, indicators)
        assert result.target_met is False
        assert result.penalty_applicable is True
        # above min_score=80, so penalty_percent stays 0
        assert result.penalty_percent == Decimal("0")

    def test_sla_zero_target(self):
        c = _make_contract(
            has_sla=True,
            sla_config={"penalty": {}},
        )
        indicators = [
            {"name": "uptime", "target": 0, "actual": 50, "weight": 1},
        ]
        result = self.svc.calculate_sla(c, indicators)
        assert result.overall_score == Decimal("100")

    def test_sla_weighted_score(self):
        c = _make_contract(
            has_sla=True,
            sla_config={"penalty": {"min_score": 50, "max_penalty_percent": 20}},
        )
        indicators = [
            {"name": "a", "target": 100, "actual": 100, "weight": 3},
            {"name": "b", "target": 100, "actual": 50, "weight": 1},
        ]
        result = self.svc.calculate_sla(c, indicators)
        # weighted: (100*3 + 50*1) / 4 = 87.5
        assert result.overall_score == Decimal("87.50")

    # -- get_contract_alerts --
    def test_alerts_inactive_skipped(self):
        c = _make_contract(status=ContractStatus.DRAFT)
        alerts = self.svc.get_contract_alerts([c])
        assert len(alerts) == 0

    def test_alerts_expiring_soon(self):
        c = _make_contract(end_date=date.today() + timedelta(days=10))
        alerts = self.svc.get_contract_alerts([c])
        assert any(a.alert_type == "expiring" for a in alerts)
        exp_alert = [a for a in alerts if a.alert_type == "expiring"][0]
        assert exp_alert.severity == "high"

    def test_alerts_expired(self):
        c = _make_contract(end_date=date.today() - timedelta(days=1))
        alerts = self.svc.get_contract_alerts([c])
        assert any(a.message == "Contrato vencido" for a in alerts)

    def test_alerts_critical_severity(self):
        c = _make_contract(end_date=date.today() + timedelta(days=3))
        alerts = self.svc.get_contract_alerts([c])
        assert alerts[0].severity == "critical"

    def test_alerts_medium_severity(self):
        c = _make_contract(end_date=date.today() + timedelta(days=25))
        alerts = self.svc.get_contract_alerts([c])
        exp = [a for a in alerts if a.alert_type == "expiring"]
        assert len(exp) == 1
        assert exp[0].severity == "medium"

    def test_alerts_needs_adjustment(self):
        c = _make_contract(needs_adjustment=True, days_until_adjustment=5, end_date=None)
        alerts = self.svc.get_contract_alerts([c])
        assert any(a.alert_type == "needs_adjustment" for a in alerts)

    def test_alerts_adjustment_upcoming(self):
        c = _make_contract(
            needs_adjustment=False,
            days_until_adjustment=15,
            end_date=None,
        )
        alerts = self.svc.get_contract_alerts([c])
        assert any(a.alert_type == "needs_adjustment" for a in alerts)

    def test_alerts_sorted_by_severity(self):
        c1 = _make_contract(
            id="1",
            contract_number="CT-1",
            end_date=date.today() + timedelta(days=3),
        )
        c2 = _make_contract(
            id="2",
            contract_number="CT-2",
            end_date=date.today() + timedelta(days=20),
        )
        alerts = self.svc.get_contract_alerts([c1, c2])
        severities = [a.severity for a in alerts]
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for i in range(len(severities) - 1):
            assert severity_order[severities[i]] <= severity_order[severities[i + 1]]

    # -- generate_contract_summary --
    def test_contract_summary(self):
        active = _make_contract()
        draft = _make_contract(status=ContractStatus.DRAFT, contract_type=ContractType.ONE_TIME)
        summary = self.svc.generate_contract_summary([active, draft])
        assert summary["total_contracts"] == 2
        assert summary["active_contracts"] == 1
        assert summary["recurring_contracts"] == 1
        assert summary["total_monthly_revenue"] == 10000.0

    def test_contract_summary_no_recurring(self):
        c = _make_contract(contract_type=ContractType.ONE_TIME)
        summary = self.svc.generate_contract_summary([c])
        assert summary["average_contract_value"] == 0.0

    # -- get_current_economic_index --
    def test_get_current_economic_index_ipca(self):
        assert self.svc.get_current_economic_index(AdjustmentIndex.IPCA) == Decimal("4.23")

    def test_get_current_economic_index_unknown(self):
        assert self.svc.get_current_economic_index("nonexistent") == Decimal("0")

    # -- _add_months --
    def test_add_months_simple(self):
        result = self.svc._add_months(date(2026, 1, 15), 6)
        assert result == date(2026, 7, 15)

    def test_add_months_year_wrap(self):
        result = self.svc._add_months(date(2026, 11, 15), 3)
        assert result == date(2027, 2, 15)

    def test_add_months_day_overflow(self):
        # Jan 31 + 1 month => Feb 28 (non-leap 2027)
        result = self.svc._add_months(date(2027, 1, 31), 1)
        assert result == date(2027, 2, 28)

    def test_add_months_leap_year(self):
        result = self.svc._add_months(date(2028, 1, 31), 1)
        assert result == date(2028, 2, 29)

    # -- _days_in_month --
    def test_days_in_month_31(self):
        assert self.svc._days_in_month(2026, 1) == 31

    def test_days_in_month_30(self):
        assert self.svc._days_in_month(2026, 4) == 30

    def test_days_in_month_feb_non_leap(self):
        assert self.svc._days_in_month(2025, 2) == 28

    def test_days_in_month_feb_leap(self):
        assert self.svc._days_in_month(2028, 2) == 29

    def test_days_in_month_feb_century_non_leap(self):
        assert self.svc._days_in_month(1900, 2) == 28

    def test_days_in_month_feb_400_leap(self):
        assert self.svc._days_in_month(2000, 2) == 29


# ===========================
# ProposalService Tests
# ===========================


class TestProposalService:
    def setup_method(self):
        self.svc = ProposalService(pricing_engine=MagicMock())

    # -- generate_proposal_number --
    def test_generate_proposal_number_service(self):
        result = self.svc.generate_proposal_number(ProposalType.SERVICE, 1)
        assert result == f"PRO-{datetime.now().year}-00001"

    def test_generate_proposal_number_product(self):
        result = self.svc.generate_proposal_number(ProposalType.PRODUCT, 99)
        assert result.startswith("PRP-")
        assert result.endswith("00099")

    def test_generate_proposal_number_mixed(self):
        result = self.svc.generate_proposal_number(ProposalType.MIXED, 5)
        assert result.startswith("PRM-")

    def test_generate_proposal_number_unknown_type(self):
        # Falls back to "PRO" for unknown types
        result = self.svc.generate_proposal_number("nonexistent", 1)
        assert result.startswith("PRO-")

    # -- calculate_validity_date --
    def test_calculate_validity_date_default(self):
        result = self.svc.calculate_validity_date()
        assert result == date.today() + timedelta(days=30)

    def test_calculate_validity_date_custom(self):
        result = self.svc.calculate_validity_date(days=60)
        assert result == date.today() + timedelta(days=60)

    # -- calculate_proposal_pricing --
    def test_calculate_proposal_pricing(self):
        mock_result = MagicMock()
        mock_result.total_contract = Decimal("120000")
        mock_result.margin_percent = Decimal("15")
        self.svc.pricing_engine.calculate.return_value = mock_result

        result = self.svc.calculate_proposal_pricing(
            base_salary=Decimal("2000"),
            headcount=5,
            contract_months=12,
        )
        assert result is mock_result
        self.svc.pricing_engine.calculate.assert_called_once()

    # -- can_apply_discount --
    def test_can_apply_discount_vendedor_within_limit(self):
        ok, msg = self.svc.can_apply_discount(Decimal("3.00"), "vendedor")
        assert ok is True

    def test_can_apply_discount_vendedor_over_limit(self):
        ok, msg = self.svc.can_apply_discount(Decimal("10.00"), "vendedor")
        assert ok is False
        assert "gerente" in msg

    def test_can_apply_discount_gerente(self):
        ok, _ = self.svc.can_apply_discount(Decimal("12.00"), "gerente")
        assert ok is True

    def test_can_apply_discount_exceeds_max(self):
        ok, msg = self.svc.can_apply_discount(Decimal("200.00"), "vendedor")
        assert ok is False
        assert "excede" in msg.lower() or "aprovacao" in msg.lower()

    def test_can_apply_discount_admin_any(self):
        ok, _ = self.svc.can_apply_discount(Decimal("99.00"), "admin")
        assert ok is True

    def test_can_apply_discount_unknown_role(self):
        ok, _ = self.svc.can_apply_discount(Decimal("1.00"), "unknown_role")
        assert ok is False

    # -- can_transition_status --
    def test_transition_draft_to_pending(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.DRAFT, ProposalStatus.PENDING_APPROVAL)
        assert ok is True

    def test_transition_draft_to_accepted_invalid(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.DRAFT, ProposalStatus.ACCEPTED)
        assert ok is False

    def test_transition_accepted_terminal(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.ACCEPTED, ProposalStatus.DRAFT)
        assert ok is False

    def test_transition_cancelled_terminal(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.CANCELLED, ProposalStatus.DRAFT)
        assert ok is False

    def test_transition_rejected_to_draft(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.REJECTED, ProposalStatus.DRAFT)
        assert ok is True

    def test_transition_expired_to_draft(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.EXPIRED, ProposalStatus.DRAFT)
        assert ok is True

    def test_transition_sent_to_accepted(self):
        ok, _ = self.svc.can_transition_status(ProposalStatus.SENT, ProposalStatus.ACCEPTED)
        assert ok is True

    # -- process_approval --
    def test_process_approval_not_pending(self):
        status, msg = self.svc.process_approval(ProposalStatus.DRAFT, ApprovalAction.APPROVE, "gerente")
        assert status == ProposalStatus.DRAFT
        assert "nao esta pendente" in msg

    def test_process_approval_no_permission(self):
        status, msg = self.svc.process_approval(ProposalStatus.PENDING_APPROVAL, ApprovalAction.APPROVE, "vendedor")
        assert status == ProposalStatus.PENDING_APPROVAL
        assert "nao tem permissao" in msg

    def test_process_approval_approve(self):
        status, _ = self.svc.process_approval(ProposalStatus.PENDING_APPROVAL, ApprovalAction.APPROVE, "gerente")
        assert status == ProposalStatus.APPROVED

    def test_process_approval_reject(self):
        status, _ = self.svc.process_approval(ProposalStatus.PENDING_APPROVAL, ApprovalAction.REJECT, "diretor")
        assert status == ProposalStatus.REJECTED

    def test_process_approval_request_changes(self):
        status, _ = self.svc.process_approval(ProposalStatus.PENDING_APPROVAL, ApprovalAction.REQUEST_CHANGES, "admin")
        assert status == ProposalStatus.DRAFT

    def test_process_approval_unknown_action(self):
        status, msg = self.svc.process_approval(ProposalStatus.PENDING_APPROVAL, "bogus_action", "admin")
        assert status == ProposalStatus.PENDING_APPROVAL
        assert "nao reconhecida" in msg

    # -- calculate_items_totals --
    def test_calculate_items_totals(self):
        items = [
            {"quantity": 2, "unit_price": 100, "discount_percent": 10},
            {"quantity": 1, "unit_price": 500, "discount_percent": 0},
        ]
        subtotal, discount, total = self.svc.calculate_items_totals(items)
        assert subtotal == Decimal("700.00")
        assert discount == Decimal("20.00")
        assert total == Decimal("680.00")

    def test_calculate_items_totals_empty(self):
        sub, disc, tot = self.svc.calculate_items_totals([])
        assert sub == Decimal("0.00")
        assert tot == Decimal("0.00")

    def test_calculate_items_totals_defaults(self):
        items = [{}]  # missing keys use defaults
        sub, disc, tot = self.svc.calculate_items_totals(items)
        assert sub == Decimal("0")

    # -- check_expiration --
    def test_check_expiration_not_expired(self):
        expired, days = self.svc.check_expiration(date.today() + timedelta(days=10))
        assert expired is False
        assert days == 10

    def test_check_expiration_expired(self):
        expired, days = self.svc.check_expiration(date.today() - timedelta(days=5))
        assert expired is True
        assert days == -5

    def test_check_expiration_today(self):
        expired, days = self.svc.check_expiration(date.today())
        assert expired is False
        assert days == 0

    # -- generate_version --
    def test_generate_version(self):
        assert self.svc.generate_version(1) == 2
        assert self.svc.generate_version(5) == 6

    # -- format_currency --
    def test_format_currency(self):
        assert self.svc.format_currency(Decimal("1234.56")) == "R$ 1.234,56"
        assert self.svc.format_currency(Decimal("0.00")) == "R$ 0,00"

    def test_format_currency_large(self):
        result = self.svc.format_currency(Decimal("1234567.89"))
        assert result == "R$ 1.234.567,89"

    # -- calculate_commission --
    def test_calculate_commission(self):
        result = self.svc.calculate_commission(Decimal("10000"), Decimal("5"))
        assert result == Decimal("500.00")


# ===========================
# PDFGenerator Tests
# ===========================


class TestPDFGenerator:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.gen = PDFGenerator(template_dir=self.tmpdir, output_dir=self.tmpdir)

    # -- generate_preview --
    def test_generate_preview_returns_html(self):
        data = _make_proposal_data()
        html = self.gen.generate_preview(data)
        assert "<!DOCTYPE html>" in html
        assert data.number in html
        assert data.company.name in html
        assert data.client.name in html

    def test_preview_contains_items(self):
        data = _make_proposal_data()
        html = self.gen.generate_preview(data)
        assert "Vigilancia 24h" in html

    def test_preview_with_introduction(self):
        data = _make_proposal_data(introduction="Welcome to our proposal")
        html = self.gen.generate_preview(data)
        assert "Welcome to our proposal" in html

    def test_preview_with_terms(self):
        data = _make_proposal_data(terms="Payment due in 30 days")
        html = self.gen.generate_preview(data)
        assert "Payment due in 30 days" in html

    def test_preview_with_payment_terms(self):
        data = _make_proposal_data(payment_terms="Net 30")
        html = self.gen.generate_preview(data)
        assert "Net 30" in html

    def test_preview_with_notes(self):
        data = _make_proposal_data(notes="Please review carefully")
        html = self.gen.generate_preview(data)
        assert "Please review carefully" in html

    def test_preview_with_discount(self):
        data = _make_proposal_data(discount_value=Decimal("500.00"))
        html = self.gen.generate_preview(data)
        assert "Desconto" in html

    def test_preview_no_discount(self):
        data = _make_proposal_data(discount_value=Decimal("0.00"))
        html = self.gen.generate_preview(data)
        # discount row should be empty string
        assert "Desconto:" not in html

    def test_preview_with_taxes(self):
        data = _make_proposal_data(taxes=Decimal("1000.00"))
        html = self.gen.generate_preview(data)
        assert "Impostos" in html

    def test_preview_no_taxes(self):
        data = _make_proposal_data(taxes=Decimal("0.00"))
        html = self.gen.generate_preview(data)
        assert "Impostos:" not in html

    def test_preview_with_cct(self):
        data = _make_proposal_data(cct_value=Decimal("2000.00"))
        html = self.gen.generate_preview(data)
        assert "Encargos (CCT)" in html

    def test_preview_no_cct(self):
        data = _make_proposal_data(cct_value=None)
        html = self.gen.generate_preview(data)
        assert "Encargos (CCT)" not in html

    def test_preview_salesperson(self):
        data = _make_proposal_data(salesperson_name="Maria")
        html = self.gen.generate_preview(data)
        assert "Maria" in html

    def test_preview_no_salesperson_fallback(self):
        data = _make_proposal_data(salesperson_name=None)
        html = self.gen.generate_preview(data)
        assert "Responsável" in html

    # -- _render_items --
    def test_render_items_with_discount(self):
        item = ProposalItem(
            description="Item A",
            quantity=3,
            unit="un",
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("10"),
            total=Decimal("270.00"),
            details="Extra info",
        )
        html = self.gen._render_items([item])
        assert "Item A" in html
        assert "Extra info" in html
        assert "10%" in html

    def test_render_items_no_discount(self):
        item = ProposalItem(
            description="Item B",
            quantity=1,
            unit="un",
            unit_price=Decimal("500.00"),
            discount_percent=Decimal("0"),
            total=Decimal("500.00"),
        )
        html = self.gen._render_items([item])
        assert "-" in html  # shows dash for 0 discount

    # -- _render_logo --
    def test_render_logo_no_path(self):
        result = self.gen._render_logo(None)
        assert "LOGO" in result

    def test_render_logo_missing_file(self):
        result = self.gen._render_logo("/nonexistent/logo.png")
        assert "LOGO" in result

    def test_render_logo_existing_file(self):
        logo_path = self.tmpdir / "logo.png"
        logo_path.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header
        result = self.gen._render_logo(str(logo_path))
        assert "base64" in result
        assert "image/png" in result

    def test_render_logo_jpg(self):
        logo_path = self.tmpdir / "logo.jpg"
        logo_path.write_bytes(b"\xff\xd8\xff")  # minimal JPEG header
        result = self.gen._render_logo(str(logo_path))
        assert "image/jpeg" in result

    # -- _render_optional_row --
    def test_render_optional_row_with_value(self):
        result = self.gen._render_optional_row("Label:", "Value")
        assert "Label:" in result
        assert "Value" in result

    def test_render_optional_row_none(self):
        assert self.gen._render_optional_row("Label:", None) == ""

    # -- _render_introduction, _render_terms, etc --
    def test_render_introduction_none(self):
        assert self.gen._render_introduction(None) == ""

    def test_render_introduction_with_text(self):
        result = self.gen._render_introduction("Hello")
        assert "Hello" in result

    def test_render_terms_none(self):
        assert self.gen._render_terms(None) == ""

    def test_render_payment_terms_none(self):
        assert self.gen._render_payment_terms(None) == ""

    def test_render_notes_none(self):
        assert self.gen._render_notes(None) == ""

    # -- _format_currency --
    def test_format_currency(self):
        assert self.gen._format_currency(Decimal("1234.56")) == "R$ 1.234,56"

    # -- _days_until --
    def test_days_until_future(self):
        future = date.today() + timedelta(days=15)
        assert self.gen._days_until(future) == 15

    def test_days_until_past(self):
        past = date.today() - timedelta(days=5)
        assert self.gen._days_until(past) == 0

    # -- generate (PDF generation with fallback) --
    def test_generate_fallback_no_weasyprint_no_reportlab(self):
        data = _make_proposal_data()
        with patch.dict(
            "sys.modules",
            {
                "weasyprint": None,
                "reportlab": None,
                "reportlab.lib.pagesizes": None,
                "reportlab.pdfgen": None,
                "reportlab.pdfgen.canvas": None,
            },
        ):
            # _html_to_pdf will hit ImportError for weasyprint, then ImportError for reportlab
            output_path = self.gen.generate(data)
            assert output_path.endswith(".pdf")

    def test_generate_creates_file(self):
        data = _make_proposal_data()
        output_path = self.gen.generate(data)
        assert os.path.exists(output_path) or os.path.exists(output_path.replace(".pdf", ".html"))

    # -- _html_to_pdf --
    def test_html_to_pdf_weasyprint_importerror(self):
        """Test fallback path when weasyprint is not available."""
        output_path = self.tmpdir / "test.pdf"
        html = "<html><body>Test</body></html>"
        # The actual environment likely doesn't have weasyprint
        self.gen._html_to_pdf(html, output_path)
        # Should have created either a PDF or HTML fallback
        assert output_path.exists() or output_path.with_suffix(".html").exists()

    # -- _render_cct_row --
    def test_render_cct_row_zero(self):
        assert self.gen._render_cct_row(Decimal("0")) == ""

    def test_render_cct_row_none(self):
        assert self.gen._render_cct_row(None) == ""

    # -- _render_discount_row --
    def test_render_discount_row_zero(self):
        assert self.gen._render_discount_row(Decimal("0"), "R$ 0,00") == ""

    # -- _render_taxes_row --
    def test_render_taxes_row_zero(self):
        assert self.gen._render_taxes_row(Decimal("0"), "R$ 0,00") == ""

    # -- client optional fields --
    def test_preview_client_phone_address(self):
        data = _make_proposal_data()
        data.client.phone = "(92) 8888-8888"
        data.client.address = "Rua X, 100"
        html = self.gen.generate_preview(data)
        assert "(92) 8888-8888" in html
        assert "Rua X, 100" in html


# ===========================
# ProposalSignatureService Tests
# ===========================


class TestProposalSignatureService:
    def setup_method(self):
        self.svc = ProposalSignatureService(
            provider=SignatureProvider.INTERNAL,
            api_key="test-key",  # pragma: allowlist secret
            api_secret="test-secret",  # pragma: allowlist secret
        )

    def _make_request(self, **overrides):
        defaults = {
            "proposal_id": "prop-123",
            "proposal_number": "PRO-2026-00001",
            "document_url": "https://example.com/doc.pdf",
            "signers": [SignerInfo(name="John", email="john@test.com")],
            "provider": SignatureProvider.INTERNAL,
        }
        defaults.update(overrides)
        return SignatureRequest(**defaults)

    # -- create_signature_request --
    @pytest.mark.asyncio
    async def test_create_internal_signature(self):
        req = self._make_request()
        result = await self.svc.create_signature_request(req)
        assert result.success is True
        assert result.external_id is not None
        assert "/sign?" in result.signing_url

    @pytest.mark.asyncio
    async def test_create_docusign_signature(self):
        svc = ProposalSignatureService(provider=SignatureProvider.DOCUSIGN, api_key="key123")
        req = self._make_request(provider=SignatureProvider.DOCUSIGN)
        result = await svc.create_signature_request(req)
        assert result.success is True
        assert "docusign" in result.external_id
        assert result.status == SignatureStatus.SENT

    @pytest.mark.asyncio
    async def test_create_docusign_no_api_key(self):
        svc = ProposalSignatureService(provider=SignatureProvider.DOCUSIGN, api_key=None)
        req = self._make_request(provider=SignatureProvider.DOCUSIGN)
        result = await svc.create_signature_request(req)
        assert result.success is False
        assert "API key" in result.error

    @pytest.mark.asyncio
    async def test_create_clicksign_signature(self):
        svc = ProposalSignatureService(provider=SignatureProvider.CLICKSIGN, api_key="key123")
        req = self._make_request(provider=SignatureProvider.CLICKSIGN)
        result = await svc.create_signature_request(req)
        assert result.success is True
        assert "clicksign" in result.external_id

    @pytest.mark.asyncio
    async def test_create_clicksign_no_api_key(self):
        svc = ProposalSignatureService(provider=SignatureProvider.CLICKSIGN, api_key=None)
        req = self._make_request(provider=SignatureProvider.CLICKSIGN)
        result = await svc.create_signature_request(req)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_create_generic_signature(self):
        svc = ProposalSignatureService(provider=SignatureProvider.D4SIGN)
        req = self._make_request(provider=SignatureProvider.D4SIGN)
        result = await svc.create_signature_request(req)
        assert result.success is True
        assert "d4sign" in result.external_id

    @pytest.mark.asyncio
    async def test_create_signature_validation_no_proposal_id(self):
        req = self._make_request(proposal_id="")
        result = await self.svc.create_signature_request(req)
        assert result.success is False
        assert "obrigatorio" in result.error.lower()

    @pytest.mark.asyncio
    async def test_create_signature_validation_no_signers(self):
        req = self._make_request(signers=[])
        result = await self.svc.create_signature_request(req)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_create_signature_validation_signer_no_email(self):
        req = self._make_request(signers=[SignerInfo(name="John", email="")])
        result = await self.svc.create_signature_request(req)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_create_signature_validation_signer_no_name(self):
        req = self._make_request(signers=[SignerInfo(name="", email="john@test.com")])
        result = await self.svc.create_signature_request(req)
        assert result.success is False

    # -- check_signature_status --
    @pytest.mark.asyncio
    async def test_check_status_internal(self):
        status = await self.svc.check_signature_status("ext-123")
        assert status == SignatureStatus.PENDING

    @pytest.mark.asyncio
    async def test_check_status_external(self):
        svc = ProposalSignatureService(provider=SignatureProvider.DOCUSIGN)
        status = await svc.check_signature_status("ext-123")
        assert status == SignatureStatus.PENDING

    # -- cancel_signature_request --
    @pytest.mark.asyncio
    async def test_cancel_request(self):
        result = await self.svc.cancel_signature_request("ext-123", "No longer needed")
        assert result is True

    @pytest.mark.asyncio
    async def test_cancel_request_no_reason(self):
        result = await self.svc.cancel_signature_request("ext-123")
        assert result is True

    # -- process_webhook --
    @pytest.mark.asyncio
    async def test_process_docusign_webhook_completed(self):
        payload = {"envelopeId": "env-123", "status": "completed"}
        ext_id, status = await self.svc.process_webhook(SignatureProvider.DOCUSIGN, payload)
        assert ext_id == "env-123"
        assert status == SignatureStatus.SIGNED

    @pytest.mark.asyncio
    async def test_process_docusign_webhook_declined(self):
        payload = {"envelopeId": "env-123", "status": "declined"}
        ext_id, status = await self.svc.process_webhook(SignatureProvider.DOCUSIGN, payload)
        assert status == SignatureStatus.REFUSED

    @pytest.mark.asyncio
    async def test_process_docusign_webhook_sent(self):
        payload = {"envelopeId": "env-123", "status": "sent"}
        _, status = await self.svc.process_webhook(SignatureProvider.DOCUSIGN, payload)
        assert status == SignatureStatus.SENT

    @pytest.mark.asyncio
    async def test_process_docusign_webhook_delivered(self):
        payload = {"envelopeId": "env-123", "status": "delivered"}
        _, status = await self.svc.process_webhook(SignatureProvider.DOCUSIGN, payload)
        assert status == SignatureStatus.VIEWED

    @pytest.mark.asyncio
    async def test_process_docusign_webhook_voided(self):
        payload = {"envelopeId": "env-123", "status": "voided"}
        _, status = await self.svc.process_webhook(SignatureProvider.DOCUSIGN, payload)
        assert status == SignatureStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_process_docusign_webhook_unknown_status(self):
        payload = {"envelopeId": "env-123", "status": "something_else"}
        _, status = await self.svc.process_webhook(SignatureProvider.DOCUSIGN, payload)
        assert status == SignatureStatus.PENDING

    @pytest.mark.asyncio
    async def test_process_clicksign_webhook_sign(self):
        payload = {
            "document": {"key": "doc-key-1"},
            "event": {"name": "sign"},
        }
        ext_id, status = await self.svc.process_webhook(SignatureProvider.CLICKSIGN, payload)
        assert ext_id == "doc-key-1"
        assert status == SignatureStatus.SIGNED

    @pytest.mark.asyncio
    async def test_process_clicksign_webhook_refuse(self):
        payload = {
            "document": {"key": "doc-key-2"},
            "event": {"name": "refuse"},
        }
        _, status = await self.svc.process_webhook(SignatureProvider.CLICKSIGN, payload)
        assert status == SignatureStatus.REFUSED

    @pytest.mark.asyncio
    async def test_process_clicksign_webhook_cancel(self):
        payload = {
            "document": {"key": "doc-key-3"},
            "event": {"name": "cancel"},
        }
        _, status = await self.svc.process_webhook(SignatureProvider.CLICKSIGN, payload)
        assert status == SignatureStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_process_clicksign_webhook_auto_close(self):
        payload = {
            "document": {"key": "doc-key-4"},
            "event": {"name": "auto_close"},
        }
        _, status = await self.svc.process_webhook(SignatureProvider.CLICKSIGN, payload)
        assert status == SignatureStatus.SIGNED

    @pytest.mark.asyncio
    async def test_process_webhook_fallback_provider(self):
        payload = {"external_id": "ext-999"}
        ext_id, status = await self.svc.process_webhook(SignatureProvider.AUTENTIQUE, payload)
        assert ext_id == "ext-999"
        assert status == SignatureStatus.PENDING

    @pytest.mark.asyncio
    async def test_process_webhook_fallback_empty_payload(self):
        ext_id, status = await self.svc.process_webhook(SignatureProvider.AUTENTIQUE, {})
        assert ext_id == ""
        assert status == SignatureStatus.PENDING

    # -- resend_signature_request --
    @pytest.mark.asyncio
    async def test_resend_request(self):
        result = await self.svc.resend_signature_request("ext-123", "john@test.com")
        assert result is True

    # -- _validate_request --
    def test_validate_request_ok(self):
        req = self._make_request()
        # Should not raise
        self.svc._validate_request(req)

    def test_validate_request_no_proposal_id(self):
        req = self._make_request(proposal_id="")
        with pytest.raises(ValueError, match="ID da proposta"):
            self.svc._validate_request(req)

    def test_validate_request_no_signers(self):
        req = self._make_request(signers=[])
        with pytest.raises(ValueError, match="signatario"):
            self.svc._validate_request(req)

    def test_validate_request_signer_missing_email(self):
        req = self._make_request(signers=[SignerInfo(name="John", email="")])
        with pytest.raises(ValueError, match="Email"):
            self.svc._validate_request(req)

    def test_validate_request_signer_missing_name(self):
        req = self._make_request(signers=[SignerInfo(name="", email="j@test.com")])
        with pytest.raises(ValueError, match="Nome"):
            self.svc._validate_request(req)

    # -- constructor defaults --
    def test_default_constructor(self):
        svc = ProposalSignatureService()
        assert svc.provider == SignatureProvider.INTERNAL
        assert svc.api_key is None

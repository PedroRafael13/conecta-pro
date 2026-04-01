"""
Tests for commission_controller.py and contract_controller.py.

Covers all endpoints with mocked DB, repositories, and services.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.crm.models.commission import CommissionStatus, CommissionTrigger
from modules.crm.models.contract import (
    AddendumType,
    AdjustmentIndex,
    ContractStatus,
    ContractType,
    ServiceType,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_user():
    u = MagicMock()
    u.id = str(uuid4())
    u.email = "test@conectapro.com.br"
    return u


def _mock_db():
    return AsyncMock()


def _uid():
    return str(uuid4())


# ---------------------------------------------------------------------------
# Commission Rule mock object builder
# ---------------------------------------------------------------------------


def _make_rule(**overrides):
    uid = overrides.pop("id", _uid())
    rule = MagicMock()
    defaults = {
        "id": uid,
        "name": "Rule A",
        "description": "desc",
        "commission_type": "percentage",
        "base_value": 10.0,
        "min_value": 0.0,
        "max_value": 1000.0,
        "trigger": "on_first_payment",
        "trigger_delay_days": 0,
        "progressive_scale": None,
        "applies_to_all": True,
        "product_categories": None,
        "service_types": None,
        "min_sale_value": None,
        "max_sale_value": None,
        "valid_from": date.today(),
        "valid_until": None,
        "priority": 0,
        "is_valid": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by_id": None,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(rule, k, v)
    return rule


def _make_commission(**overrides):
    uid = overrides.pop("id", _uid())
    c = MagicMock()
    defaults = {
        "id": uid,
        "reference_number": "COM-001",
        "seller_id": _uid(),
        "proposal_id": None,
        "rule_id": None,
        "sale_value": 10000.0,
        "sale_margin": 0.0,
        "commission_type": "percentage",
        "commission_rate": 10.0,
        "base_commission": 1000.0,
        "adjustments": 0.0,
        "final_commission": 1000.0,
        "status": CommissionStatus.PENDING,
        "trigger": "on_first_payment",
        "trigger_date": None,
        "due_date": None,
        "paid_date": None,
        "period_start": None,
        "period_end": None,
        "description": None,
        "notes": None,
        "is_pending": True,
        "is_approved": False,
        "is_paid": False,
        "paid_amount": 0.0,
        "pending_amount": 1000.0,
        "is_overdue": False,
        "days_until_due": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by_id": None,
        "approved_by_id": None,
        "approved_at": None,
        "payments": [],
        "rule": None,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


def _make_payment(**overrides):
    p = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "commission_id": _uid(),
        "amount": 500.0,
        "payment_method": "payroll",
        "payment_date": date.today(),
        "payment_reference": None,
        "bank_account": None,
        "transaction_id": None,
        "is_confirmed": False,
        "confirmed_at": None,
        "confirmed_by_id": None,
        "notes": None,
        "created_at": datetime.utcnow(),
        "created_by_id": None,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(p, k, v)
    return p


def _make_summary(**overrides):
    s = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "seller_id": _uid(),
        "year": 2026,
        "month": 3,
        "total_sales": 50000.0,
        "total_sales_count": 5,
        "total_commissions": 5000.0,
        "total_paid": 3000.0,
        "total_pending": 2000.0,
        "sales_target": None,
        "target_percentage": None,
        "bonus_earned": 0.0,
        "is_target_achieved": False,
        "remaining_to_target": 0.0,
        "is_closed": False,
        "closed_at": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


def _make_seller_rule(**overrides):
    sr = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "seller_id": _uid(),
        "rule_id": _uid(),
        "custom_base_value": None,
        "valid_from": date.today(),
        "valid_until": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(sr, k, v)
    return sr


# ---------------------------------------------------------------------------
# Contract mock object builders
# ---------------------------------------------------------------------------


def _make_contract(**overrides):
    uid = overrides.pop("id", _uid())
    c = MagicMock()
    defaults = {
        "id": uid,
        "contract_number": "CTR-001",
        "name": "Contrato Test",
        "contract_type": ContractType.RECURRING,
        "status": ContractStatus.DRAFT,
        "client_id": _uid(),
        "monthly_value": Decimal("10000"),
        "total_value": Decimal("120000"),
        "start_date": date(2026, 1, 1),
        "end_date": date(2027, 1, 1),
        "auto_renewal": True,
        "adjustment_enabled": True,
        "has_sla": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active_contract": False,
        "is_expiring_soon": False,
        "days_until_end": None,
        "needs_adjustment": False,
        "description": None,
        "opportunity_id": None,
        "proposal_id": None,
        "template_id": None,
        "setup_fee": Decimal("0"),
        "grace_period_days": 0,
        "notice_period_days": 30,
        "renewal_period_months": 12,
        "renewal_notification_days": 30,
        "adjustment_index": None,
        "adjustment_fixed_percent": None,
        "adjustment_base_date": None,
        "last_adjustment_date": None,
        "next_adjustment_date": None,
        "sla_config": None,
        "content": None,
        "clauses": None,
        "signature_required": True,
        "signature_provider": None,
        "signed_at": None,
        "signed_by_client": None,
        "signed_by_company": None,
        "pdf_file_path": None,
        "commercial_manager_id": None,
        "account_manager_id": None,
        "created_by": None,
        "items": [],
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


def _make_contract_item(**overrides):
    it = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "service_type": ServiceType.SECURITY,
        "service_name": "Vigilancia",
        "description": None,
        "quantity": 1,
        "unit_price": Decimal("5000"),
        "total_price": Decimal("5000"),
        "notes": None,
        "created_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(it, k, v)
    return it


def _make_addendum(**overrides):
    a = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "contract_id": _uid(),
        "addendum_number": "ADD-001",
        "addendum_type": AddendumType.ADJUSTMENT,
        "previous_value": Decimal("10000"),
        "new_value": Decimal("11000"),
        "adjustment_percent": Decimal("10"),
        "adjustment_index": None,
        "effective_date": date.today(),
        "description": "Reajuste anual",
        "reason": None,
        "signed": False,
        "signed_at": None,
        "pdf_file_path": None,
        "created_at": datetime.utcnow(),
        "created_by": None,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(a, k, v)
    return a


def _make_template(**overrides):
    t = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "name": "Template A",
        "description": None,
        "service_type": None,
        "content_template": "x" * 101,
        "clauses": None,
        "variables": None,
        "version": 1,
        "approved_by_legal": False,
        "approved_at": None,
        "created_at": datetime.utcnow(),
        "updated_at": None,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(t, k, v)
    return t


def _make_sla_report(**overrides):
    r = MagicMock()
    defaults = {
        "id": overrides.pop("id", _uid()),
        "contract_id": _uid(),
        "year": 2026,
        "month": 3,
        "indicators": [],
        "overall_score": Decimal("95"),
        "penalty_applied": False,
        "penalty_percent": Decimal("0"),
        "penalty_amount": Decimal("0"),
        "status": "draft",
        "period_label": "2026-03",
        "is_target_met": True,
        "generated_at": datetime.utcnow(),
        "generated_by": None,
        "approved_at": None,
        "approved_by": None,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(r, k, v)
    return r


# ====================================================================
# COMMISSION CONTROLLER TESTS
# ====================================================================

COMM_CTRL = "modules.crm.controllers.commission_controller"


# ---------- Commission Rules ----------


@pytest.mark.asyncio
async def test_create_commission_rule():
    from modules.crm.controllers.commission_controller import create_commission_rule
    from modules.crm.schemas.commission import CommissionRuleCreate

    data = CommissionRuleCreate(name="Rule A", base_value=10.0)
    user = _mock_user()
    db = _mock_db()
    rule = _make_rule()

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.create_rule = AsyncMock(return_value=rule)
        result = await create_commission_rule(data=data, current_user=user, db=db)

    assert result.id == rule.id
    assert result.name == "Rule A"


@pytest.mark.asyncio
async def test_list_commission_rules():
    from modules.crm.controllers.commission_controller import list_commission_rules

    user = _mock_user()
    db = _mock_db()
    rules = [_make_rule(), _make_rule()]

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.list_rules = AsyncMock(return_value=(rules, 2))
        result = await list_commission_rules(current_user=user, db=db, page=1, page_size=20, active_only=True)

    assert result.total == 2
    assert len(result.items) == 2
    assert result.total_pages == 1


@pytest.mark.asyncio
async def test_get_commission_rule_found():
    from modules.crm.controllers.commission_controller import get_commission_rule

    rule = _make_rule()
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.get_rule_by_id = AsyncMock(return_value=rule)
        result = await get_commission_rule(rule_id=rule.id, current_user=_mock_user(), db=_mock_db())

    assert result.id == rule.id


@pytest.mark.asyncio
async def test_get_commission_rule_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import get_commission_rule

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.get_rule_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_commission_rule(rule_id="bad-id", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_commission_rule():
    from modules.crm.controllers.commission_controller import update_commission_rule
    from modules.crm.schemas.commission import CommissionRuleUpdate

    rule = _make_rule(name="Updated")
    data = CommissionRuleUpdate(name="Updated")

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update_rule = AsyncMock(return_value=rule)
        result = await update_commission_rule(rule_id=rule.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.name == "Updated"


@pytest.mark.asyncio
async def test_update_commission_rule_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import update_commission_rule
    from modules.crm.schemas.commission import CommissionRuleUpdate

    data = CommissionRuleUpdate(name="X")
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update_rule = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_commission_rule(rule_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_commission_rule():
    from modules.crm.controllers.commission_controller import delete_commission_rule

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.delete_rule = AsyncMock(return_value=True)
        result = await delete_commission_rule(rule_id="x", current_user=_mock_user(), db=_mock_db())

    assert result is None


@pytest.mark.asyncio
async def test_delete_commission_rule_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import delete_commission_rule

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.delete_rule = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await delete_commission_rule(rule_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_assign_rule_to_seller():
    from modules.crm.controllers.commission_controller import assign_rule_to_seller
    from modules.crm.schemas.commission import SellerCommissionRuleCreate

    sr = _make_seller_rule()
    data = SellerCommissionRuleCreate(seller_id=sr.seller_id, rule_id=sr.rule_id)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.assign_rule_to_seller = AsyncMock(return_value=sr)
        result = await assign_rule_to_seller(data=data, current_user=_mock_user(), db=_mock_db())

    assert result.seller_id == sr.seller_id


# ---------- Commission CRUD ----------


@pytest.mark.asyncio
async def test_create_commission():
    from modules.crm.controllers.commission_controller import create_commission
    from modules.crm.schemas.commission import CommissionCreate

    comm = _make_commission()
    data = CommissionCreate(seller_id=comm.seller_id, sale_value=10000.0)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.create = AsyncMock(return_value=comm)
        result = await create_commission(data=data, current_user=_mock_user(), db=_mock_db())

    assert result.reference_number == "COM-001"


@pytest.mark.asyncio
async def test_calculate_commission_success_with_rule_id():
    from modules.crm.controllers.commission_controller import calculate_commission
    from modules.crm.schemas.commission import CommissionCalculateRequest

    rule = _make_rule()
    comm = _make_commission()
    data = CommissionCalculateRequest(seller_id=_uid(), proposal_id=_uid(), sale_value=10000.0, rule_id=rule.id)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService") as MockSvc:
        repo = MockRepo.return_value
        repo.get_valid_rules = AsyncMock(return_value=[rule])
        repo.get_rule_by_id = AsyncMock(return_value=rule)
        repo.create = AsyncMock(return_value=comm)
        result = await calculate_commission(data=data, current_user=_mock_user(), db=_mock_db())

    assert result.reference_number == "COM-001"


@pytest.mark.asyncio
async def test_calculate_commission_auto_rule():
    from modules.crm.controllers.commission_controller import calculate_commission
    from modules.crm.schemas.commission import CommissionCalculateRequest

    rule = _make_rule()
    comm = _make_commission()
    data = CommissionCalculateRequest(seller_id=_uid(), proposal_id=_uid(), sale_value=10000.0)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService") as MockSvc:
        repo = MockRepo.return_value
        repo.get_valid_rules = AsyncMock(return_value=[rule])
        MockSvc.return_value.find_applicable_rule = MagicMock(return_value=rule)
        repo.create = AsyncMock(return_value=comm)
        result = await calculate_commission(data=data, current_user=_mock_user(), db=_mock_db())

    assert result.reference_number == "COM-001"


@pytest.mark.asyncio
async def test_calculate_commission_no_valid_rules():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import calculate_commission
    from modules.crm.schemas.commission import CommissionCalculateRequest

    data = CommissionCalculateRequest(seller_id=_uid(), proposal_id=_uid(), sale_value=10000.0)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService"):
        MockRepo.return_value.get_valid_rules = AsyncMock(return_value=[])
        with pytest.raises(HTTPException) as exc:
            await calculate_commission(data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_calculate_commission_rule_id_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import calculate_commission
    from modules.crm.schemas.commission import CommissionCalculateRequest

    data = CommissionCalculateRequest(seller_id=_uid(), proposal_id=_uid(), sale_value=10000.0, rule_id="bad")

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService"):
        MockRepo.return_value.get_valid_rules = AsyncMock(return_value=[_make_rule()])
        MockRepo.return_value.get_rule_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await calculate_commission(data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_calculate_commission_no_applicable_rule():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import calculate_commission
    from modules.crm.schemas.commission import CommissionCalculateRequest

    data = CommissionCalculateRequest(seller_id=_uid(), proposal_id=_uid(), sale_value=10000.0)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService") as MockSvc:
        MockRepo.return_value.get_valid_rules = AsyncMock(return_value=[_make_rule()])
        MockSvc.return_value.find_applicable_rule = MagicMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await calculate_commission(data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_list_commissions():
    from modules.crm.controllers.commission_controller import list_commissions

    comms = [_make_commission(), _make_commission()]
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.list = AsyncMock(return_value=(comms, 2))
        result = await list_commissions(
            current_user=_mock_user(),
            db=_mock_db(),
            page=1,
            page_size=20,
            seller_id=None,
            proposal_id=None,
            status_filter=None,
            trigger=None,
            is_overdue=None,
            min_value=None,
            max_value=None,
            date_from=None,
            date_to=None,
            due_date_from=None,
            due_date_to=None,
        )

    assert result.total == 2
    assert len(result.items) == 2


@pytest.mark.asyncio
async def test_get_commission_stats():
    from modules.crm.controllers.commission_controller import get_commission_stats
    from modules.crm.schemas.commission import CommissionStats

    stats = CommissionStats(
        total_commissions=10,
        pending_count=2,
        approved_count=3,
        paid_count=4,
        cancelled_count=1,
        total_value=100000,
        pending_value=20000,
        approved_value=30000,
        paid_value=40000,
        overdue_count=0,
        overdue_value=0,
        avg_commission_value=10000,
        avg_days_to_payment=5,
        by_status={},
        by_trigger={},
        by_month={},
    )

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService") as MockSvc:
        MockRepo.return_value.get_all_for_stats = AsyncMock(return_value=[])
        MockSvc.return_value.calculate_stats = MagicMock(return_value=stats)
        result = await get_commission_stats(current_user=_mock_user(), db=_mock_db())

    assert result.total_commissions == 10


@pytest.mark.asyncio
async def test_get_seller_commission_stats():
    from modules.crm.controllers.commission_controller import get_seller_commission_stats
    from modules.crm.schemas.commission import SellerCommissionStats

    sid = _uid()
    stats = SellerCommissionStats(
        seller_id=sid,
        total_sales=50000,
        total_commissions=5000,
        pending_commissions=2000,
        paid_commissions=3000,
        commission_rate_avg=10,
        sales_count=5,
        current_month_sales=10000,
        current_month_commissions=1000,
    )

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo, patch(f"{COMM_CTRL}.CommissionService") as MockSvc:
        MockRepo.return_value.list = AsyncMock(return_value=([], 0))
        MockSvc.return_value.calculate_seller_stats = MagicMock(return_value=stats)
        result = await get_seller_commission_stats(seller_id=sid, current_user=_mock_user(), db=_mock_db())

    assert result.seller_id == sid


@pytest.mark.asyncio
async def test_get_commission_found():
    from modules.crm.controllers.commission_controller import get_commission

    comm = _make_commission()
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=comm)
        result = await get_commission(commission_id=comm.id, current_user=_mock_user(), db=_mock_db())

    assert result.id == comm.id


@pytest.mark.asyncio
async def test_get_commission_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import get_commission

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_commission(commission_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_commission():
    from modules.crm.controllers.commission_controller import update_commission
    from modules.crm.schemas.commission import CommissionUpdate

    comm = _make_commission()
    data = CommissionUpdate(notes="updated")

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update = AsyncMock(return_value=comm)
        result = await update_commission(commission_id=comm.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.id == comm.id


@pytest.mark.asyncio
async def test_update_commission_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import update_commission
    from modules.crm.schemas.commission import CommissionUpdate

    data = CommissionUpdate(notes="x")
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_commission(commission_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_commission_status():
    from modules.crm.controllers.commission_controller import update_commission_status
    from modules.crm.schemas.commission import CommissionStatusUpdate

    comm = _make_commission(status=CommissionStatus.APPROVED)
    data = CommissionStatusUpdate(status=CommissionStatus.APPROVED)

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=comm)
        result = await update_commission_status(
            commission_id=comm.id, data=data, current_user=_mock_user(), db=_mock_db()
        )

    assert result.id == comm.id


@pytest.mark.asyncio
async def test_update_commission_status_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import update_commission_status
    from modules.crm.schemas.commission import CommissionStatusUpdate

    data = CommissionStatusUpdate(status=CommissionStatus.CANCELLED)
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_commission_status(commission_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_commission_status_approved_sets_approved_by():
    from modules.crm.controllers.commission_controller import update_commission_status
    from modules.crm.schemas.commission import CommissionStatusUpdate

    comm = _make_commission()
    data = CommissionStatusUpdate(status=CommissionStatus.APPROVED)
    user = _mock_user()

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=comm)
        await update_commission_status(commission_id=comm.id, data=data, current_user=user, db=_mock_db())
        repo.update_status.assert_called_once_with(
            commission_id=comm.id,
            status=CommissionStatus.APPROVED,
            approved_by_id=str(user.id),
            notes=None,
        )


@pytest.mark.asyncio
async def test_update_commission_status_non_approved_no_approved_by():
    from modules.crm.controllers.commission_controller import update_commission_status
    from modules.crm.schemas.commission import CommissionStatusUpdate

    comm = _make_commission()
    data = CommissionStatusUpdate(status=CommissionStatus.CANCELLED)
    user = _mock_user()

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=comm)
        await update_commission_status(commission_id=comm.id, data=data, current_user=user, db=_mock_db())
        repo.update_status.assert_called_once_with(
            commission_id=comm.id,
            status=CommissionStatus.CANCELLED,
            approved_by_id=None,
            notes=None,
        )


@pytest.mark.asyncio
async def test_approve_commission():
    from modules.crm.controllers.commission_controller import approve_commission
    from modules.crm.schemas.commission import CommissionApprove

    comm = _make_commission(status=CommissionStatus.APPROVED)
    data = CommissionApprove(notes="ok")
    user = _mock_user()

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=comm)
        result = await approve_commission(commission_id=comm.id, data=data, current_user=user, db=_mock_db())

    assert result.id == comm.id
    repo.update_status.assert_called_once_with(
        commission_id=comm.id,
        status=CommissionStatus.APPROVED,
        approved_by_id=str(user.id),
        notes="ok",
    )


@pytest.mark.asyncio
async def test_approve_commission_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import approve_commission
    from modules.crm.schemas.commission import CommissionApprove

    data = CommissionApprove()
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await approve_commission(commission_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_commission():
    from modules.crm.controllers.commission_controller import delete_commission

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.delete = AsyncMock(return_value=True)
        result = await delete_commission(commission_id="x", current_user=_mock_user(), db=_mock_db())
    assert result is None


@pytest.mark.asyncio
async def test_delete_commission_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import delete_commission

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.delete = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await delete_commission(commission_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


# ---------- Commission Payments ----------


@pytest.mark.asyncio
async def test_create_commission_payment():
    from modules.crm.controllers.commission_controller import create_commission_payment
    from modules.crm.schemas.commission import CommissionPaymentCreate

    cid = _uid()
    payment = _make_payment(commission_id=cid)
    data = CommissionPaymentCreate(commission_id=cid, amount=500.0, payment_date=date.today())

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.create_payment = AsyncMock(return_value=payment)
        result = await create_commission_payment(commission_id=cid, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.amount == 500.0


@pytest.mark.asyncio
async def test_create_commission_payment_id_mismatch():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import create_commission_payment
    from modules.crm.schemas.commission import CommissionPaymentCreate

    data = CommissionPaymentCreate(commission_id="id-a", amount=500.0, payment_date=date.today())
    with pytest.raises(HTTPException) as exc:
        await create_commission_payment(commission_id="id-b", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_commission_payment_repo_returns_none():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import create_commission_payment
    from modules.crm.schemas.commission import CommissionPaymentCreate

    cid = _uid()
    data = CommissionPaymentCreate(commission_id=cid, amount=500.0, payment_date=date.today())

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.create_payment = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await create_commission_payment(commission_id=cid, data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_confirm_commission_payment():
    from modules.crm.controllers.commission_controller import confirm_commission_payment
    from modules.crm.schemas.commission import CommissionPaymentConfirm

    payment = _make_payment(is_confirmed=True)
    data = CommissionPaymentConfirm(notes="confirmed")

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.confirm_payment = AsyncMock(return_value=payment)
        result = await confirm_commission_payment(
            payment_id=payment.id, data=data, current_user=_mock_user(), db=_mock_db()
        )

    assert result.is_confirmed is True


@pytest.mark.asyncio
async def test_confirm_commission_payment_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import confirm_commission_payment
    from modules.crm.schemas.commission import CommissionPaymentConfirm

    data = CommissionPaymentConfirm()
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.confirm_payment = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await confirm_commission_payment(payment_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


# ---------- Commission Summaries ----------


@pytest.mark.asyncio
async def test_list_commission_summaries():
    from modules.crm.controllers.commission_controller import list_commission_summaries

    summaries = [_make_summary(), _make_summary()]
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.list_summaries = AsyncMock(return_value=summaries)
        result = await list_commission_summaries(current_user=_mock_user(), db=_mock_db())

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_commission_summary():
    from modules.crm.controllers.commission_controller import get_commission_summary

    summary = _make_summary()
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.update_summary = AsyncMock(return_value=summary)
        result = await get_commission_summary(
            seller_id=summary.seller_id, year=2026, month=3, current_user=_mock_user(), db=_mock_db()
        )

    assert result.year == 2026


@pytest.mark.asyncio
async def test_close_commission_summary():
    from modules.crm.controllers.commission_controller import close_commission_summary

    summary = _make_summary(is_closed=True)
    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.close_summary = AsyncMock(return_value=summary)
        result = await close_commission_summary(
            seller_id=summary.seller_id, year=2026, month=3, current_user=_mock_user(), db=_mock_db()
        )

    assert result.is_closed is True


@pytest.mark.asyncio
async def test_close_commission_summary_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.commission_controller import close_commission_summary

    with patch(f"{COMM_CTRL}.CommissionRepository") as MockRepo:
        MockRepo.return_value.close_summary = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await close_commission_summary(seller_id="x", year=2026, month=3, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


# ====================================================================
# CONTRACT CONTROLLER TESTS
# ====================================================================

CONTR_CTRL = "modules.crm.controllers.contract_controller"


# ---------- Contracts CRUD ----------


@pytest.mark.asyncio
async def test_create_contract():
    from modules.crm.controllers.contract_controller import create_contract
    from modules.crm.schemas.contract import ContractCreate

    contract = _make_contract()
    cid = _uid()
    data = ContractCreate(
        name="Test Contract",
        monthly_value=Decimal("10000"),
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
        client_id=cid,
    )

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.create = AsyncMock(return_value=contract)
        result = await create_contract(data=data, current_user=_mock_user(), db=_mock_db())

    assert result.contract_number == "CTR-001"


@pytest.mark.asyncio
async def test_list_contracts():
    from modules.crm.controllers.contract_controller import list_contracts

    contracts = [_make_contract(), _make_contract()]
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.list = AsyncMock(return_value=(contracts, 2))
        result = await list_contracts(
            current_user=_mock_user(),
            db=_mock_db(),
            page=1,
            page_size=20,
            status_filter=None,
            contract_type=None,
            client_id=None,
            commercial_manager_id=None,
            account_manager_id=None,
            has_sla=None,
            min_value=None,
            max_value=None,
            search=None,
        )

    assert result.total == 2
    assert len(result.items) == 2


@pytest.mark.asyncio
async def test_get_contract_stats():
    from modules.crm.controllers.contract_controller import get_contract_stats
    from modules.crm.schemas.contract import ContractStats

    stats = ContractStats(
        total_contracts=10,
        active_contracts=5,
        total_monthly_revenue=Decimal("50000"),
        average_contract_value=Decimal("10000"),
        expiring_soon=1,
        needs_adjustment=2,
        by_status={"active": 5},
        by_type={"recurring": 8},
    )

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.get_stats = AsyncMock(return_value=stats)
        result = await get_contract_stats(current_user=_mock_user(), db=_mock_db())

    assert result.total_contracts == 10


@pytest.mark.asyncio
async def test_get_contract_alerts():
    from modules.crm.controllers.contract_controller import get_contract_alerts
    from modules.crm.services.contract_service import ContractAlert

    alerts = [
        ContractAlert(
            contract_id=_uid(),
            contract_number="CTR-001",
            alert_type="expiring",
            severity="high",
            message="Expiring soon",
        )
    ]

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService") as MockSvc:
        MockRepo.return_value.list = AsyncMock(return_value=([], 0))
        MockSvc.return_value.get_contract_alerts = MagicMock(return_value=alerts)
        result = await get_contract_alerts(current_user=_mock_user(), db=_mock_db())

    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_contract_found():
    from modules.crm.controllers.contract_controller import get_contract

    contract = _make_contract()
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=contract)
        result = await get_contract(contract_id=contract.id, current_user=_mock_user(), db=_mock_db())

    assert result.id == contract.id


@pytest.mark.asyncio
async def test_get_contract_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import get_contract

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_contract(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_contract():
    from modules.crm.controllers.contract_controller import update_contract
    from modules.crm.schemas.contract import ContractUpdate

    contract = _make_contract()
    data = ContractUpdate(name="Updated")

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update = AsyncMock(return_value=contract)
        result = await update_contract(contract_id=contract.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.contract_number == "CTR-001"


@pytest.mark.asyncio
async def test_update_contract_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import update_contract
    from modules.crm.schemas.contract import ContractUpdate

    data = ContractUpdate(name="XYZ")
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_contract(contract_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_submit_contract_for_signature():
    from modules.crm.controllers.contract_controller import submit_contract_for_signature

    contract = _make_contract(status=ContractStatus.PENDING_SIGNATURE)
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=contract)
        result = await submit_contract_for_signature(contract_id=contract.id, current_user=_mock_user(), db=_mock_db())

    assert result.status == ContractStatus.PENDING_SIGNATURE


@pytest.mark.asyncio
async def test_submit_contract_for_signature_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import submit_contract_for_signature

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await submit_contract_for_signature(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_activate_contract():
    from modules.crm.controllers.contract_controller import activate_contract

    contract = _make_contract(status=ContractStatus.ACTIVE)
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=contract)
        result = await activate_contract(contract_id=contract.id, current_user=_mock_user(), db=_mock_db())

    assert result.status == ContractStatus.ACTIVE


@pytest.mark.asyncio
async def test_activate_contract_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import activate_contract

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await activate_contract(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_suspend_contract():
    from modules.crm.controllers.contract_controller import suspend_contract

    contract = _make_contract(status=ContractStatus.SUSPENDED)
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=contract)
        result = await suspend_contract(contract_id=contract.id, current_user=_mock_user(), db=_mock_db())

    assert result.status == ContractStatus.SUSPENDED


@pytest.mark.asyncio
async def test_suspend_contract_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import suspend_contract

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await suspend_contract(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_terminate_contract():
    from modules.crm.controllers.contract_controller import terminate_contract

    contract = _make_contract(status=ContractStatus.TERMINATED)
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=contract)
        result = await terminate_contract(contract_id=contract.id, current_user=_mock_user(), db=_mock_db())

    assert result.status == ContractStatus.TERMINATED


@pytest.mark.asyncio
async def test_terminate_contract_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import terminate_contract

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await terminate_contract(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_calculate_renewal():
    from modules.crm.controllers.contract_controller import calculate_renewal
    from modules.crm.schemas.contract import ContractRenewal
    from modules.crm.services.contract_service import RenewalResult

    contract = _make_contract()
    data = ContractRenewal(new_end_date=date(2028, 1, 1), adjustment_percent=Decimal("5"))
    renewal = RenewalResult(success=True, new_end_date=date(2028, 1, 1), message="OK")

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService") as MockSvc:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=contract)
        MockSvc.return_value.calculate_renewal = MagicMock(return_value=renewal)
        result = await calculate_renewal(contract_id=contract.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.success is True


@pytest.mark.asyncio
async def test_calculate_renewal_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import calculate_renewal
    from modules.crm.schemas.contract import ContractRenewal

    data = ContractRenewal(new_end_date=date(2028, 1, 1))
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService"):
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await calculate_renewal(contract_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_calculate_adjustment():
    from modules.crm.controllers.contract_controller import calculate_adjustment
    from modules.crm.services.contract_service import AdjustmentResult

    contract = _make_contract()
    adj = AdjustmentResult(
        success=True,
        previous_value=Decimal("10000"),
        new_value=Decimal("10500"),
        adjustment_percent=Decimal("5"),
        effective_date=date.today(),
    )

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService") as MockSvc:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=contract)
        MockSvc.return_value.calculate_adjustment = MagicMock(return_value=adj)
        result = await calculate_adjustment(contract_id=contract.id, current_user=_mock_user(), db=_mock_db())

    assert result.success is True


@pytest.mark.asyncio
async def test_calculate_adjustment_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import calculate_adjustment

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService"):
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await calculate_adjustment(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_contract():
    from modules.crm.controllers.contract_controller import delete_contract

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.delete = AsyncMock(return_value=True)
        result = await delete_contract(contract_id="x", current_user=_mock_user(), db=_mock_db())
    assert result is None


@pytest.mark.asyncio
async def test_delete_contract_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import delete_contract

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.delete = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await delete_contract(contract_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


# ---------- Contract Items ----------


@pytest.mark.asyncio
async def test_add_contract_item():
    from modules.crm.controllers.contract_controller import add_contract_item
    from modules.crm.schemas.contract import ContractItemCreate

    item = _make_contract_item()
    data = ContractItemCreate(service_type=ServiceType.SECURITY, service_name="Vigilancia", unit_price=Decimal("5000"))

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.add_item = AsyncMock(return_value=item)
        result = await add_contract_item(contract_id=_uid(), data=data, current_user=_mock_user(), db=_mock_db())

    assert result.service_name == "Vigilancia"


@pytest.mark.asyncio
async def test_add_contract_item_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import add_contract_item
    from modules.crm.schemas.contract import ContractItemCreate

    data = ContractItemCreate(service_type=ServiceType.SECURITY, service_name="Vig", unit_price=Decimal("5000"))
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.add_item = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await add_contract_item(contract_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_update_contract_item():
    from modules.crm.controllers.contract_controller import update_contract_item
    from modules.crm.schemas.contract import ContractItemUpdate

    item = _make_contract_item()
    data = ContractItemUpdate(quantity=2)

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_item = AsyncMock(return_value=item)
        result = await update_contract_item(
            contract_id=_uid(), item_id=item.id, data=data, current_user=_mock_user(), db=_mock_db()
        )

    assert result.id == item.id


@pytest.mark.asyncio
async def test_update_contract_item_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import update_contract_item
    from modules.crm.schemas.contract import ContractItemUpdate

    data = ContractItemUpdate(quantity=2)
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_item = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_contract_item(
                contract_id="x", item_id="y", data=data, current_user=_mock_user(), db=_mock_db()
            )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_remove_contract_item():
    from modules.crm.controllers.contract_controller import remove_contract_item

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.remove_item = AsyncMock(return_value=True)
        result = await remove_contract_item(
            contract_id=_uid(), item_id=_uid(), current_user=_mock_user(), db=_mock_db()
        )
    assert result is None


@pytest.mark.asyncio
async def test_remove_contract_item_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import remove_contract_item

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.remove_item = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await remove_contract_item(contract_id="x", item_id="y", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


# ---------- Contract Addendums ----------


@pytest.mark.asyncio
async def test_create_addendum():
    from modules.crm.controllers.contract_controller import create_addendum
    from modules.crm.schemas.contract import ContractAddendumCreate

    addendum = _make_addendum()
    data = ContractAddendumCreate(
        addendum_type=AddendumType.ADJUSTMENT,
        effective_date=date.today(),
        description="Reajuste anual do contrato conforme clausula",
        new_value=Decimal("11000"),
    )

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.create_addendum = AsyncMock(return_value=addendum)
        result = await create_addendum(contract_id=_uid(), data=data, current_user=_mock_user(), db=_mock_db())

    assert result.addendum_number == "ADD-001"


@pytest.mark.asyncio
async def test_create_addendum_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import create_addendum
    from modules.crm.schemas.contract import ContractAddendumCreate

    data = ContractAddendumCreate(
        addendum_type=AddendumType.SCOPE_CHANGE,
        effective_date=date.today(),
        description="Mudanca de escopo do contrato conforme solicitacao",
    )
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.create_addendum = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await create_addendum(contract_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_list_addendums():
    from modules.crm.controllers.contract_controller import list_addendums

    addendums = [_make_addendum(), _make_addendum()]
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.list_addendums = AsyncMock(return_value=addendums)
        result = await list_addendums(contract_id=_uid(), current_user=_mock_user(), db=_mock_db())

    assert len(result) == 2


@pytest.mark.asyncio
async def test_sign_addendum():
    from modules.crm.controllers.contract_controller import sign_addendum
    from modules.crm.schemas.contract import ContractAddendumSign

    addendum = _make_addendum(signed=True)
    data = ContractAddendumSign(signature_document_id="doc-123")

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.sign_addendum = AsyncMock(return_value=addendum)
        result = await sign_addendum(addendum_id=addendum.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.signed is True


@pytest.mark.asyncio
async def test_sign_addendum_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import sign_addendum
    from modules.crm.schemas.contract import ContractAddendumSign

    data = ContractAddendumSign(signature_document_id="x")
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.sign_addendum = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await sign_addendum(addendum_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


# ---------- Contract Templates ----------


@pytest.mark.asyncio
async def test_create_template():
    from modules.crm.controllers.contract_controller import create_template
    from modules.crm.schemas.contract import ContractTemplateCreate

    template = _make_template()
    data = ContractTemplateCreate(name="Template A", content_template="x" * 101)

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.create_template = AsyncMock(return_value=template)
        result = await create_template(data=data, current_user=_mock_user(), db=_mock_db())

    assert result.name == "Template A"


@pytest.mark.asyncio
async def test_list_templates():
    from modules.crm.controllers.contract_controller import list_templates

    templates = [_make_template(), _make_template()]
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.list_templates = AsyncMock(return_value=templates)
        result = await list_templates(current_user=_mock_user(), db=_mock_db())

    assert result.total == 2


@pytest.mark.asyncio
async def test_list_templates_with_service_type():
    from modules.crm.controllers.contract_controller import list_templates

    templates = [_make_template()]
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.list_templates = AsyncMock(return_value=templates)
        result = await list_templates(current_user=_mock_user(), db=_mock_db(), service_type=ServiceType.SECURITY)

    assert result.total == 1
    MockRepo.return_value.list_templates.assert_called_once_with(
        service_type="security",
        approved_only=False,
    )


@pytest.mark.asyncio
async def test_get_template_found():
    from modules.crm.controllers.contract_controller import get_template

    template = _make_template()
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.get_template_by_id = AsyncMock(return_value=template)
        result = await get_template(template_id=template.id, current_user=_mock_user(), db=_mock_db())

    assert result.id == template.id


@pytest.mark.asyncio
async def test_get_template_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import get_template

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.get_template_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_template(template_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_template():
    from modules.crm.controllers.contract_controller import update_template
    from modules.crm.schemas.contract import ContractTemplateUpdate

    template = _make_template(name="Updated")
    data = ContractTemplateUpdate(name="Updated")

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_template = AsyncMock(return_value=template)
        result = await update_template(template_id=template.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.name == "Updated"


@pytest.mark.asyncio
async def test_update_template_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import update_template
    from modules.crm.schemas.contract import ContractTemplateUpdate

    data = ContractTemplateUpdate(name="XYZ")
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.update_template = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_template(template_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_approve_template():
    from modules.crm.controllers.contract_controller import approve_template

    template = _make_template(approved_by_legal=True)
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.approve_template = AsyncMock(return_value=template)
        result = await approve_template(template_id=template.id, current_user=_mock_user(), db=_mock_db())

    assert result.approved_by_legal is True


@pytest.mark.asyncio
async def test_approve_template_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import approve_template

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.approve_template = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await approve_template(template_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_template():
    from modules.crm.controllers.contract_controller import delete_template

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.delete_template = AsyncMock(return_value=True)
        result = await delete_template(template_id="x", current_user=_mock_user(), db=_mock_db())
    assert result is None


@pytest.mark.asyncio
async def test_delete_template_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import delete_template

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.delete_template = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await delete_template(template_id="bad", current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404


# ---------- SLA Reports ----------


@pytest.mark.asyncio
async def test_create_sla_report():
    from modules.crm.controllers.contract_controller import create_sla_report
    from modules.crm.schemas.contract import ContractSLAReportCreate, SLAIndicatorResult

    report = _make_sla_report()
    data = ContractSLAReportCreate(
        year=2026,
        month=3,
        indicators=[SLAIndicatorResult(name="uptime", target=Decimal("99"), actual=Decimal("99.5"), achieved=True)],
        overall_score=Decimal("99"),
    )

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.create_sla_report = AsyncMock(return_value=report)
        result = await create_sla_report(contract_id=_uid(), data=data, current_user=_mock_user(), db=_mock_db())

    assert result.year == 2026


@pytest.mark.asyncio
async def test_create_sla_report_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import create_sla_report
    from modules.crm.schemas.contract import ContractSLAReportCreate, SLAIndicatorResult

    data = ContractSLAReportCreate(
        year=2026,
        month=3,
        indicators=[SLAIndicatorResult(name="uptime", target=Decimal("99"), actual=Decimal("99.5"), achieved=True)],
        overall_score=Decimal("99"),
    )
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.create_sla_report = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await create_sla_report(contract_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_list_sla_reports():
    from modules.crm.controllers.contract_controller import list_sla_reports

    reports = [_make_sla_report(), _make_sla_report()]
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.list_sla_reports = AsyncMock(return_value=reports)
        result = await list_sla_reports(contract_id=_uid(), current_user=_mock_user(), db=_mock_db())

    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_sla_reports_with_year():
    from modules.crm.controllers.contract_controller import list_sla_reports

    reports = [_make_sla_report()]
    cid = _uid()
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.list_sla_reports = AsyncMock(return_value=reports)
        result = await list_sla_reports(contract_id=cid, current_user=_mock_user(), db=_mock_db(), year=2026)

    assert len(result) == 1
    MockRepo.return_value.list_sla_reports.assert_called_once_with(cid, year=2026)


@pytest.mark.asyncio
async def test_approve_sla_report():
    from modules.crm.controllers.contract_controller import approve_sla_report
    from modules.crm.schemas.contract import ContractSLAReportApprove

    report = _make_sla_report(status="approved")
    data = ContractSLAReportApprove(disputed=False)

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.approve_sla_report = AsyncMock(return_value=report)
        result = await approve_sla_report(report_id=report.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.status == "approved"


@pytest.mark.asyncio
async def test_approve_sla_report_disputed():
    from modules.crm.controllers.contract_controller import approve_sla_report
    from modules.crm.schemas.contract import ContractSLAReportApprove

    report = _make_sla_report(status="disputed")
    data = ContractSLAReportApprove(disputed=True)

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.approve_sla_report = AsyncMock(return_value=report)
        result = await approve_sla_report(report_id=report.id, data=data, current_user=_mock_user(), db=_mock_db())

    assert result.status == "disputed"


@pytest.mark.asyncio
async def test_approve_sla_report_fail():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import approve_sla_report
    from modules.crm.schemas.contract import ContractSLAReportApprove

    data = ContractSLAReportApprove()
    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo:
        MockRepo.return_value.approve_sla_report = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await approve_sla_report(report_id="bad", data=data, current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_calculate_sla():
    from modules.crm.controllers.contract_controller import calculate_sla
    from modules.crm.services.contract_service import SLACalculation

    contract = _make_contract(has_sla=True)
    calc = SLACalculation(
        overall_score=Decimal("95"),
        indicators=[],
        penalty_applicable=False,
        penalty_percent=Decimal("0"),
        penalty_amount=Decimal("0"),
        target_met=True,
    )

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService") as MockSvc:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=contract)
        MockSvc.return_value.calculate_sla = MagicMock(return_value=calc)
        result = await calculate_sla(
            contract_id=contract.id,
            indicator_results=[{"name": "uptime", "value": 99.5}],
            current_user=_mock_user(),
            db=_mock_db(),
        )

    assert result.target_met is True


@pytest.mark.asyncio
async def test_calculate_sla_not_found():
    from fastapi import HTTPException

    from modules.crm.controllers.contract_controller import calculate_sla

    with patch(f"{CONTR_CTRL}.ContractRepository") as MockRepo, patch(f"{CONTR_CTRL}.ContractService"):
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await calculate_sla(contract_id="bad", indicator_results=[], current_user=_mock_user(), db=_mock_db())
    assert exc.value.status_code == 404

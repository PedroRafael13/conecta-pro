"""
Comprehensive tests for CRM repositories:
- LeadRepository
- OpportunityRepository
- CommissionRepository

All tests use mocked AsyncSession (no real DB).
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

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
from modules.crm.models.lead import Lead, LeadSource, LeadStatus
from modules.crm.models.opportunity import (
    LossReason,
    Opportunity,
    OpportunityPriority,
    OpportunityStage,
)
from modules.crm.repositories.commission_repository import CommissionRepository
from modules.crm.repositories.lead_repository import LeadRepository
from modules.crm.repositories.opportunity_repository import OpportunityRepository
from modules.crm.schemas.commission import (
    CommissionCreate,
    CommissionFilter,
    CommissionPaymentCreate,
    CommissionRuleCreate,
    CommissionRuleUpdate,
    CommissionSummaryFilter,
    CommissionUpdate,
    SellerCommissionRuleCreate,
)
from modules.crm.schemas.lead import LeadCreate, LeadFilter, LeadUpdate
from modules.crm.schemas.opportunity import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityCreateFromLead,
    OpportunityFilter,
    OpportunityUpdate,
)

# ===================== HELPERS =====================


def _mock_db():
    """Create a mocked AsyncSession."""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


def _scalar_result(value):
    """Mock for db.execute() that returns scalar_one_or_none()."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    result.scalar.return_value = value
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [value] if value else []
    result.scalars.return_value = scalars_mock
    return result


def _scalars_result(values):
    """Mock for db.execute() that returns scalars().all()."""
    result = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = values
    result.scalars.return_value = scalars_mock
    result.scalar.return_value = len(values)
    result.scalar_one_or_none.return_value = values[0] if values else None
    return result


def _make_lead(**overrides):
    """Create a fake Lead object."""
    defaults = {
        "id": str(uuid4()),
        "name": "Test Lead",
        "email": "test@example.com",
        "phone": "11999999999",
        "company": "ACME",
        "position": "Manager",
        "company_size": "medium",
        "industry": "seguranca",
        "source": LeadSource.WEBSITE.value,
        "status": LeadStatus.NEW.value,
        "score": 50,
        "probability": 30.0,
        "expected_value": 10000.0,
        "notes": None,
        "assigned_to_id": None,
        "last_contact_at": None,
        "next_contact_at": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    lead = MagicMock(spec=Lead)
    for k, v in defaults.items():
        setattr(lead, k, v)
    # Properties
    lead.is_hot = defaults.get("score", 50) >= 70
    lead.weighted_value = defaults.get("expected_value", 0) * (defaults.get("probability", 0) / 100)
    return lead


def _make_opportunity(**overrides):
    """Create a fake Opportunity object."""
    defaults = {
        "id": str(uuid4()),
        "title": "Test Opp",
        "description": None,
        "lead_id": None,
        "contact_name": "John",
        "contact_email": "john@example.com",
        "contact_phone": None,
        "company_name": "ACME",
        "stage": OpportunityStage.QUALIFICATION.value,
        "priority": OpportunityPriority.MEDIUM.value,
        "value": 50000.0,
        "probability": 10,
        "expected_close_date": None,
        "actual_close_date": None,
        "owner_id": None,
        "loss_reason": None,
        "competitor": None,
        "win_notes": None,
        "loss_notes": None,
        "notes": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    opp = MagicMock(spec=Opportunity)
    for k, v in defaults.items():
        setattr(opp, k, v)
    opp.weighted_value = defaults["value"] * (defaults["probability"] / 100)
    opp.is_open = defaults["stage"] not in (
        OpportunityStage.CLOSED_WON.value,
        OpportunityStage.CLOSED_LOST.value,
    )
    opp.is_won = defaults["stage"] == OpportunityStage.CLOSED_WON.value
    opp.is_lost = defaults["stage"] == OpportunityStage.CLOSED_LOST.value
    opp.is_overdue = False
    opp.days_in_pipeline = 5
    return opp


def _make_commission(**overrides):
    """Create a fake Commission object."""
    defaults = {
        "id": str(uuid4()),
        "reference_number": "COM-2026-00001",
        "seller_id": str(uuid4()),
        "proposal_id": None,
        "rule_id": None,
        "sale_value": 100000.0,
        "sale_margin": 20000.0,
        "commission_type": CommissionType.PERCENTAGE.value,
        "commission_rate": 5.0,
        "base_commission": 5000.0,
        "adjustments": 0.0,
        "final_commission": 5000.0,
        "status": CommissionStatus.PENDING.value,
        "trigger": CommissionTrigger.ON_FIRST_PAYMENT.value,
        "trigger_date": date.today(),
        "due_date": date.today() + timedelta(days=30),
        "paid_date": None,
        "period_start": None,
        "period_end": None,
        "description": None,
        "notes": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by_id": None,
        "approved_by_id": None,
        "approved_at": None,
        "payments": [],
    }
    defaults.update(overrides)
    comm = MagicMock(spec=Commission)
    for k, v in defaults.items():
        setattr(comm, k, v)
    comm.is_pending = defaults["status"] == CommissionStatus.PENDING.value
    comm.is_approved = defaults["status"] == CommissionStatus.APPROVED.value
    comm.is_paid = defaults["status"] == CommissionStatus.PAID.value
    paid_amount = sum(p.amount for p in defaults.get("payments", []) if getattr(p, "is_confirmed", False))
    comm.paid_amount = paid_amount
    comm.pending_amount = defaults["final_commission"] - paid_amount
    comm.is_overdue = False
    return comm


def _make_commission_rule(**overrides):
    """Create a fake CommissionRule object."""
    defaults = {
        "id": str(uuid4()),
        "name": "Standard Rule",
        "description": None,
        "commission_type": CommissionType.PERCENTAGE.value,
        "base_value": 5.0,
        "min_value": None,
        "max_value": None,
        "progressive_scale": None,
        "trigger": CommissionTrigger.ON_FIRST_PAYMENT.value,
        "trigger_delay_days": 0,
        "applies_to_all": True,
        "product_categories": None,
        "service_types": None,
        "min_sale_value": None,
        "max_sale_value": None,
        "valid_from": date.today() - timedelta(days=30),
        "valid_until": None,
        "priority": 0,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by_id": None,
    }
    defaults.update(overrides)
    rule = MagicMock(spec=CommissionRule)
    for k, v in defaults.items():
        setattr(rule, k, v)
    rule.is_valid = True
    return rule


def _make_summary(**overrides):
    """Create a fake CommissionSummary object."""
    defaults = {
        "id": str(uuid4()),
        "seller_id": str(uuid4()),
        "year": 2026,
        "month": 3,
        "total_sales": 0.0,
        "total_sales_count": 0,
        "total_commissions": 0.0,
        "total_paid": 0.0,
        "total_pending": 0.0,
        "bonus_earned": 0.0,
        "is_closed": False,
        "closed_at": None,
        "sales_target": None,
        "target_percentage": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    s = MagicMock(spec=CommissionSummary)
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


# ============================================================
#                    LEAD REPOSITORY TESTS
# ============================================================


class TestLeadRepository:
    """Tests for LeadRepository."""

    # --- get_by_id ---

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        result = await repo.get_by_id(lead.id)
        assert result is lead
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = LeadRepository(db)
        result = await repo.get_by_id("nonexistent")
        assert result is None

    # --- get_by_email ---

    @pytest.mark.asyncio
    async def test_get_by_email_found(self):
        db = _mock_db()
        lead = _make_lead(email="found@test.com")
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        result = await repo.get_by_email("found@test.com")
        assert result is lead

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = LeadRepository(db)
        result = await repo.get_by_email("nope@test.com")
        assert result is None

    # --- create ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    @patch("modules.crm.repositories.lead_repository.uuid4")
    async def test_create(self, mock_uuid, mock_lead_svc):
        mock_uuid.return_value = "test-uuid-123"
        mock_lead_svc.calculate_score.return_value = (75, 45.0)
        db = _mock_db()
        repo = LeadRepository(db)
        data = LeadCreate(
            name="New Lead",
            email="new@example.com",
            phone="11999887766",
            company="Test Corp",
            source=LeadSource.WEBSITE,
            expected_value=5000.0,
        )
        result = await repo.create(data)
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()
        # The Lead object was passed to db.add
        added_lead = db.add.call_args[0][0]
        assert added_lead.name == "New Lead"
        assert added_lead.email == "new@example.com"
        assert added_lead.score == 75
        assert added_lead.probability == 45.0

    # --- update ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_found(self, mock_lead_svc):
        mock_lead_svc.calculate_score.return_value = (80, 50.0)
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        data = LeadUpdate(company="Updated Corp")
        result = await repo.update(lead.id, data)
        assert result is lead
        assert lead.company == "Updated Corp"
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = LeadRepository(db)
        data = LeadUpdate(name="XX")
        result = await repo.update("nonexistent", data)
        assert result is None

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_with_status_enum(self, mock_lead_svc):
        """When updating status field with enum, .value should be used."""
        mock_lead_svc.calculate_score.return_value = (60, 40.0)
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        data = LeadUpdate(status=LeadStatus.QUALIFIED)
        result = await repo.update(lead.id, data)
        assert result is lead
        db.commit.assert_awaited()

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_with_source_enum(self, mock_lead_svc):
        """When updating source field with enum, .value should be used."""
        mock_lead_svc.calculate_score.return_value = (60, 40.0)
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        data = LeadUpdate(source=LeadSource.REFERRAL)
        result = await repo.update(lead.id, data)
        assert result is lead

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_recalculates_score_on_relevant_fields(self, mock_lead_svc):
        mock_lead_svc.calculate_score.return_value = (90, 60.0)
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        data = LeadUpdate(industry="seguranca")
        await repo.update(lead.id, data)
        mock_lead_svc.calculate_score.assert_called_once()

    # --- update_score ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_score_found(self, mock_lead_svc):
        mock_lead_svc.calculate_score.return_value = (85, 55.0)
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        result = await repo.update_score(lead.id)
        assert result is lead
        assert lead.score == 85
        assert lead.probability == 55.0

    @pytest.mark.asyncio
    async def test_update_score_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = LeadRepository(db)
        result = await repo.update_score("nonexistent")
        assert result is None

    # --- update_status ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_status_found(self, mock_lead_svc):
        mock_lead_svc.calculate_score.return_value = (70, 45.0)
        mock_lead_svc.get_next_contact_date.return_value = datetime.utcnow() + timedelta(days=3)
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        result = await repo.update_status(lead.id, LeadStatus.CONTACTED)
        assert result is lead
        assert lead.status == LeadStatus.CONTACTED.value

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_status_with_notes(self, mock_lead_svc):
        mock_lead_svc.calculate_score.return_value = (70, 45.0)
        mock_lead_svc.get_next_contact_date.return_value = None
        db = _mock_db()
        lead = _make_lead(notes="Existing")
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        result = await repo.update_status(lead.id, LeadStatus.QUALIFIED, notes="Qualified now")
        assert result is lead
        assert "Qualified now" in lead.notes

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.lead_repository.lead_service")
    async def test_update_status_with_notes_no_existing(self, mock_lead_svc):
        mock_lead_svc.calculate_score.return_value = (70, 45.0)
        mock_lead_svc.get_next_contact_date.return_value = None
        db = _mock_db()
        lead = _make_lead(notes=None)
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        await repo.update_status(lead.id, LeadStatus.CONTACTED, notes="First note")
        assert "First note" in lead.notes

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = LeadRepository(db)
        result = await repo.update_status("nonexistent", LeadStatus.CONTACTED)
        assert result is None

    # --- delete ---

    @pytest.mark.asyncio
    async def test_delete_found(self):
        db = _mock_db()
        lead = _make_lead()
        db.execute.return_value = _scalar_result(lead)
        repo = LeadRepository(db)
        result = await repo.delete(lead.id)
        assert result is True
        assert lead.is_active is False
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = LeadRepository(db)
        result = await repo.delete("nonexistent")
        assert result is False

    # --- list ---

    @pytest.mark.asyncio
    async def test_list_no_filters(self):
        db = _mock_db()
        leads = [_make_lead(), _make_lead()]
        # First call: count query, second call: data query
        count_result = MagicMock()
        count_result.scalar.return_value = 2
        data_result = _scalars_result(leads)
        db.execute.side_effect = [count_result, data_result]
        repo = LeadRepository(db)
        items, total = await repo.list()
        assert total == 2
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_list_with_filters(self):
        db = _mock_db()
        lead = _make_lead(status=LeadStatus.QUALIFIED.value)
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        data_result = _scalars_result([lead])
        db.execute.side_effect = [count_result, data_result]
        repo = LeadRepository(db)
        filters = LeadFilter(
            status=LeadStatus.QUALIFIED,
            source=LeadSource.WEBSITE,
            assigned_to_id="user-1",
            min_score=30,
            max_score=90,
            is_hot=False,
            company="ACME",
            search="test",
        )
        items, total = await repo.list(filters=filters, page=1, page_size=10)
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_with_is_hot_true(self):
        db = _mock_db()
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = _scalars_result([])
        db.execute.side_effect = [count_result, data_result]
        repo = LeadRepository(db)
        filters = LeadFilter(is_hot=True)
        items, total = await repo.list(filters=filters)
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_pagination(self):
        db = _mock_db()
        count_result = MagicMock()
        count_result.scalar.return_value = 50
        data_result = _scalars_result([_make_lead() for _ in range(10)])
        db.execute.side_effect = [count_result, data_result]
        repo = LeadRepository(db)
        items, total = await repo.list(page=3, page_size=10)
        assert total == 50
        assert len(items) == 10

    @pytest.mark.asyncio
    async def test_list_count_returns_none(self):
        """When scalar() returns None, total should be 0."""
        db = _mock_db()
        count_result = MagicMock()
        count_result.scalar.return_value = None
        data_result = _scalars_result([])
        db.execute.side_effect = [count_result, data_result]
        repo = LeadRepository(db)
        items, total = await repo.list()
        assert total == 0

    # --- get_stats ---

    @pytest.mark.asyncio
    async def test_get_stats_empty(self):
        db = _mock_db()
        db.execute.return_value = _scalars_result([])
        repo = LeadRepository(db)
        stats = await repo.get_stats()
        assert stats.total == 0
        assert stats.avg_score == 0.0

    @pytest.mark.asyncio
    async def test_get_stats_with_leads(self):
        db = _mock_db()
        lead1 = _make_lead(
            score=80,
            expected_value=10000.0,
            probability=50.0,
            status=LeadStatus.NEW.value,
            source=LeadSource.WEBSITE.value,
        )
        lead2 = _make_lead(
            score=40,
            expected_value=5000.0,
            probability=20.0,
            status=LeadStatus.CONTACTED.value,
            source=LeadSource.REFERRAL.value,
        )
        db.execute.return_value = _scalars_result([lead1, lead2])
        repo = LeadRepository(db)
        stats = await repo.get_stats()
        assert stats.total == 2
        assert stats.avg_score == 60.0
        assert stats.hot_leads == 1  # lead1 score>=70

    @pytest.mark.asyncio
    async def test_get_stats_with_assigned_to_id(self):
        db = _mock_db()
        db.execute.return_value = _scalars_result([])
        repo = LeadRepository(db)
        stats = await repo.get_stats(assigned_to_id="user-123")
        assert stats.total == 0


# ============================================================
#                 OPPORTUNITY REPOSITORY TESTS
# ============================================================


class TestOpportunityRepository:
    """Tests for OpportunityRepository."""

    # --- create ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.opportunity_repository.uuid4")
    async def test_create(self, mock_uuid):
        mock_uuid.return_value = "opp-uuid-123"
        db = _mock_db()
        repo = OpportunityRepository(db)
        data = OpportunityCreate(
            title="New Opp",
            contact_name="John",
            contact_email="john@test.com",
            company_name="ACME",
            value=50000.0,
            stage=OpportunityStage.QUALIFICATION,
            priority=OpportunityPriority.HIGH,
        )
        result = await repo.create(data)
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()
        added = db.add.call_args[0][0]
        assert added.title == "New Opp"
        assert added.stage == OpportunityStage.QUALIFICATION.value

    # --- create_from_lead ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.opportunity_repository.uuid4")
    async def test_create_from_lead_found(self, mock_uuid):
        mock_uuid.return_value = "opp-from-lead-uuid"
        db = _mock_db()
        lead = _make_lead(
            id="lead-1",
            name="Lead Name",
            email="lead@test.com",
            phone="11999",
            company="LeadCorp",
            assigned_to_id="owner-1",
        )
        db.execute.return_value = _scalar_result(lead)
        repo = OpportunityRepository(db)
        data = OpportunityCreateFromLead(
            lead_id="lead-1",
            title="From Lead",
            value=30000.0,
            priority=OpportunityPriority.MEDIUM,
        )
        result = await repo.create_from_lead(data)
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        added = db.add.call_args[0][0]
        assert added.lead_id == "lead-1"
        assert added.contact_name == "Lead Name"
        assert lead.status == LeadStatus.WON.value

    @pytest.mark.asyncio
    async def test_create_from_lead_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = OpportunityRepository(db)
        data = OpportunityCreateFromLead(
            lead_id="missing",
            title="From Lead",
            value=10000.0,
        )
        result = await repo.create_from_lead(data)
        assert result is None

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.opportunity_repository.uuid4")
    async def test_create_from_lead_with_owner_id(self, mock_uuid):
        mock_uuid.return_value = "opp-uuid"
        db = _mock_db()
        lead = _make_lead(assigned_to_id="fallback-owner")
        db.execute.return_value = _scalar_result(lead)
        repo = OpportunityRepository(db)
        data = OpportunityCreateFromLead(
            lead_id=lead.id,
            title="Opp",
            value=1000.0,
            owner_id="explicit-owner",
        )
        result = await repo.create_from_lead(data)
        added = db.add.call_args[0][0]
        assert added.owner_id == "explicit-owner"

    # --- get_by_id ---

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.get_by_id(opp.id)
        assert result is opp

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = OpportunityRepository(db)
        result = await repo.get_by_id("nonexistent")
        assert result is None

    # --- list ---

    @pytest.mark.asyncio
    async def test_list_no_filters(self):
        db = _mock_db()
        opps = [_make_opportunity(), _make_opportunity()]
        count_result = MagicMock()
        count_result.scalar.return_value = 2
        data_result = _scalars_result(opps)
        db.execute.side_effect = [count_result, data_result]
        repo = OpportunityRepository(db)
        items, total = await repo.list()
        assert total == 2
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_list_with_all_filters(self):
        db = _mock_db()
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        data_result = _scalars_result([_make_opportunity()])
        db.execute.side_effect = [count_result, data_result]
        repo = OpportunityRepository(db)
        filters = OpportunityFilter(
            stage=OpportunityStage.PROPOSAL,
            priority=OpportunityPriority.HIGH,
            owner_id="user-1",
            is_open=True,
            min_value=1000.0,
            max_value=100000.0,
            company_name="ACME",
            search="test",
        )
        items, total = await repo.list(filters=filters)
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_with_is_open_false(self):
        db = _mock_db()
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = _scalars_result([])
        db.execute.side_effect = [count_result, data_result]
        repo = OpportunityRepository(db)
        filters = OpportunityFilter(is_open=False)
        items, total = await repo.list(filters=filters)
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_count_returns_none(self):
        db = _mock_db()
        count_result = MagicMock()
        count_result.scalar.return_value = None
        data_result = _scalars_result([])
        db.execute.side_effect = [count_result, data_result]
        repo = OpportunityRepository(db)
        items, total = await repo.list()
        assert total == 0

    # --- update ---

    @pytest.mark.asyncio
    async def test_update_found(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        data = OpportunityUpdate(title="Updated Title")
        result = await repo.update(opp.id, data)
        assert result is opp
        assert opp.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = OpportunityRepository(db)
        data = OpportunityUpdate(title="X")
        result = await repo.update("nonexistent", data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_stage_enum(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        data = OpportunityUpdate(stage=OpportunityStage.PROPOSAL)
        result = await repo.update(opp.id, data)
        assert result is opp

    @pytest.mark.asyncio
    async def test_update_with_priority_enum(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        data = OpportunityUpdate(priority=OpportunityPriority.CRITICAL)
        result = await repo.update(opp.id, data)
        assert result is opp

    # --- update_stage ---

    @pytest.mark.asyncio
    async def test_update_stage_found(self):
        db = _mock_db()
        opp = _make_opportunity(stage=OpportunityStage.QUALIFICATION.value)
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.update_stage(opp.id, OpportunityStage.PROPOSAL)
        assert result is opp
        assert opp.stage == OpportunityStage.PROPOSAL.value
        assert opp.probability == 50  # from stage_probabilities map

    @pytest.mark.asyncio
    async def test_update_stage_with_notes(self):
        db = _mock_db()
        opp = _make_opportunity(notes="Old notes", stage=OpportunityStage.QUALIFICATION.value)
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.update_stage(opp.id, OpportunityStage.NEGOTIATION, notes="Good progress")
        assert "Good progress" in opp.notes

    @pytest.mark.asyncio
    async def test_update_stage_with_notes_no_existing(self):
        db = _mock_db()
        opp = _make_opportunity(notes=None, stage=OpportunityStage.QUALIFICATION.value)
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.update_stage(opp.id, OpportunityStage.PROPOSAL, notes="Sent proposal")
        assert "Sent proposal" in opp.notes

    @pytest.mark.asyncio
    async def test_update_stage_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = OpportunityRepository(db)
        result = await repo.update_stage("nonexistent", OpportunityStage.PROPOSAL)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_stage_closed_won(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.update_stage(opp.id, OpportunityStage.CLOSED_WON)
        assert opp.probability == 100

    @pytest.mark.asyncio
    async def test_update_stage_closed_lost(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.update_stage(opp.id, OpportunityStage.CLOSED_LOST)
        assert opp.probability == 0

    # --- close ---

    @pytest.mark.asyncio
    async def test_close_won(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        data = OpportunityClose(won=True, notes="Great deal!")
        result = await repo.close(opp.id, data)
        assert result is opp
        assert opp.stage == OpportunityStage.CLOSED_WON.value
        assert opp.probability == 100
        assert opp.win_notes == "Great deal!"

    @pytest.mark.asyncio
    async def test_close_lost(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        data = OpportunityClose(
            won=False,
            notes="Lost to competitor",
            loss_reason=LossReason.COMPETITOR,
            competitor="OtherCo",
        )
        result = await repo.close(opp.id, data)
        assert result is opp
        assert opp.stage == OpportunityStage.CLOSED_LOST.value
        assert opp.probability == 0
        assert opp.loss_reason == LossReason.COMPETITOR.value
        assert opp.competitor == "OtherCo"

    @pytest.mark.asyncio
    async def test_close_lost_no_loss_reason(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        data = OpportunityClose(won=False, notes="Just lost")
        result = await repo.close(opp.id, data)
        assert opp.loss_reason is None

    @pytest.mark.asyncio
    async def test_close_with_actual_close_date(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        close_date = date(2026, 3, 15)
        data = OpportunityClose(won=True, actual_close_date=close_date)
        result = await repo.close(opp.id, data)
        assert opp.actual_close_date == close_date

    @pytest.mark.asyncio
    async def test_close_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = OpportunityRepository(db)
        data = OpportunityClose(won=True)
        result = await repo.close("nonexistent", data)
        assert result is None

    # --- delete ---

    @pytest.mark.asyncio
    async def test_delete_found(self):
        db = _mock_db()
        opp = _make_opportunity()
        db.execute.return_value = _scalar_result(opp)
        repo = OpportunityRepository(db)
        result = await repo.delete(opp.id)
        assert result is True
        assert opp.is_active is False

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = OpportunityRepository(db)
        result = await repo.delete("nonexistent")
        assert result is False

    # --- get_pipeline_stats ---

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_empty(self):
        db = _mock_db()
        db.execute.return_value = _scalars_result([])
        repo = OpportunityRepository(db)
        stats = await repo.get_pipeline_stats()
        assert stats.total_opportunities == 0
        assert stats.win_rate == 0.0

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_with_data(self):
        db = _mock_db()
        opp_open = _make_opportunity(
            stage=OpportunityStage.PROPOSAL.value,
            value=50000.0,
            probability=50,
            priority=OpportunityPriority.HIGH.value,
        )
        opp_open.is_open = True
        opp_open.is_won = False
        opp_open.is_lost = False
        opp_open.is_overdue = True
        opp_open.weighted_value = 25000.0

        opp_won = _make_opportunity(
            stage=OpportunityStage.CLOSED_WON.value,
            value=100000.0,
            probability=100,
            priority=OpportunityPriority.MEDIUM.value,
            actual_close_date=date(2026, 3, 10),
        )
        opp_won.is_open = False
        opp_won.is_won = True
        opp_won.is_lost = False
        opp_won.is_overdue = False
        opp_won.weighted_value = 100000.0
        opp_won.days_in_pipeline = 30

        opp_lost = _make_opportunity(
            stage=OpportunityStage.CLOSED_LOST.value,
            value=20000.0,
            probability=0,
            priority=OpportunityPriority.LOW.value,
            actual_close_date=date(2026, 3, 5),
        )
        opp_lost.is_open = False
        opp_lost.is_won = False
        opp_lost.is_lost = True
        opp_lost.is_overdue = False
        opp_lost.weighted_value = 0.0
        opp_lost.days_in_pipeline = 15

        db.execute.return_value = _scalars_result([opp_open, opp_won, opp_lost])
        repo = OpportunityRepository(db)
        stats = await repo.get_pipeline_stats()

        assert stats.total_opportunities == 3
        assert stats.open_opportunities == 1
        assert stats.won_opportunities == 1
        assert stats.lost_opportunities == 1
        assert stats.won_value == 100000.0
        assert stats.lost_value == 20000.0
        assert stats.overdue_count == 1
        assert stats.win_rate == 50.0
        assert stats.avg_days_to_close == (30 + 15) / 2

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_with_owner_id(self):
        db = _mock_db()
        db.execute.return_value = _scalars_result([])
        repo = OpportunityRepository(db)
        stats = await repo.get_pipeline_stats(owner_id="user-123")
        assert stats.total_opportunities == 0

    @pytest.mark.asyncio
    async def test_get_pipeline_stats_no_closed(self):
        """All open opportunities => win_rate=0, avg_days_to_close=0."""
        db = _mock_db()
        opp = _make_opportunity(
            stage=OpportunityStage.NEGOTIATION.value,
            value=10000.0,
            probability=75,
            priority=OpportunityPriority.MEDIUM.value,
        )
        opp.is_open = True
        opp.is_won = False
        opp.is_lost = False
        opp.is_overdue = False
        opp.weighted_value = 7500.0
        db.execute.return_value = _scalars_result([opp])
        repo = OpportunityRepository(db)
        stats = await repo.get_pipeline_stats()
        assert stats.win_rate == 0.0
        assert stats.avg_days_to_close == 0.0


# ============================================================
#                 COMMISSION REPOSITORY TESTS
# ============================================================


class TestCommissionRepository:
    """Tests for CommissionRepository."""

    # --- create_rule ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_create_rule(self, mock_uuid):
        mock_uuid.return_value = "rule-uuid-1"
        db = _mock_db()
        repo = CommissionRepository(db)
        data = CommissionRuleCreate(
            name="Test Rule",
            commission_type=CommissionType.PERCENTAGE,
            base_value=5.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT,
        )
        result = await repo.create_rule(data, created_by_id="admin-1")
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        added = db.add.call_args[0][0]
        assert added.name == "Test Rule"

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_create_rule_with_progressive_scale(self, mock_uuid):
        mock_uuid.return_value = "rule-uuid-2"
        db = _mock_db()
        repo = CommissionRepository(db)
        from modules.crm.schemas.commission import ProgressiveTier

        data = CommissionRuleCreate(
            name="Progressive Rule",
            commission_type=CommissionType.PROGRESSIVE,
            base_value=5.0,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT,
            progressive_scale=[ProgressiveTier(min=0, max=10000, rate=5)],
            product_categories=["cat1"],
            service_types=["type1"],
        )
        result = await repo.create_rule(data)
        added = db.add.call_args[0][0]
        assert added.progressive_scale is not None
        assert added.product_categories is not None
        assert added.service_types is not None

    # --- get_rule_by_id ---

    @pytest.mark.asyncio
    async def test_get_rule_by_id_found(self):
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        result = await repo.get_rule_by_id(rule.id)
        assert result is rule

    @pytest.mark.asyncio
    async def test_get_rule_by_id_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.get_rule_by_id("nonexistent")
        assert result is None

    # --- list_rules ---

    @pytest.mark.asyncio
    async def test_list_rules_active_only(self):
        db = _mock_db()
        rules = [_make_commission_rule(), _make_commission_rule()]
        data_result = _scalars_result(rules)
        count_result = MagicMock()
        count_result.scalar.return_value = 2
        db.execute.side_effect = [data_result, count_result]
        repo = CommissionRepository(db)
        items, total = await repo.list_rules(active_only=True)
        assert len(items) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_list_rules_all(self):
        db = _mock_db()
        rules = [_make_commission_rule()]
        data_result = _scalars_result(rules)
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        db.execute.side_effect = [data_result, count_result]
        repo = CommissionRepository(db)
        items, total = await repo.list_rules(active_only=False)
        assert len(items) == 1

    # --- update_rule ---

    @pytest.mark.asyncio
    async def test_update_rule_found(self):
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        data = CommissionRuleUpdate(name="Updated Rule")
        result = await repo.update_rule(rule.id, data)
        assert result is rule
        db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_rule_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        data = CommissionRuleUpdate(name="X")
        result = await repo.update_rule("nonexistent", data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_rule_with_progressive_scale(self):
        """progressive_scale after model_dump becomes list of dicts; patch model_dump."""
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        from modules.crm.schemas.commission import ProgressiveTier

        data = CommissionRuleUpdate(
            progressive_scale=[ProgressiveTier(min=0, max=50000, rate=7)],
        )
        # The production code calls t.model_dump() on results of data.model_dump().
        # Patch model_dump to return ProgressiveTier objects (which have model_dump).
        tiers = data.progressive_scale  # These are real ProgressiveTier objects
        with patch.object(
            type(data),
            "model_dump",
            return_value={"progressive_scale": tiers},
        ):
            result = await repo.update_rule(rule.id, data)
        assert result is rule

    @pytest.mark.asyncio
    async def test_update_rule_with_categories_and_types(self):
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        data = CommissionRuleUpdate(
            product_categories=["security"],
            service_types=["monitoring"],
        )
        result = await repo.update_rule(rule.id, data)
        assert result is rule

    @pytest.mark.asyncio
    async def test_update_rule_with_commission_type_enum(self):
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        data = CommissionRuleUpdate(commission_type=CommissionType.FIXED)
        result = await repo.update_rule(rule.id, data)
        assert result is rule

    @pytest.mark.asyncio
    async def test_update_rule_with_trigger_enum(self):
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        data = CommissionRuleUpdate(trigger=CommissionTrigger.MONTHLY)
        result = await repo.update_rule(rule.id, data)
        assert result is rule

    # --- delete_rule ---

    @pytest.mark.asyncio
    async def test_delete_rule_found(self):
        db = _mock_db()
        rule = _make_commission_rule()
        db.execute.return_value = _scalar_result(rule)
        repo = CommissionRepository(db)
        result = await repo.delete_rule(rule.id)
        assert result is True
        assert rule.is_active is False

    @pytest.mark.asyncio
    async def test_delete_rule_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.delete_rule("nonexistent")
        assert result is False

    # --- get_valid_rules ---

    @pytest.mark.asyncio
    async def test_get_valid_rules_no_seller(self):
        db = _mock_db()
        rules = [_make_commission_rule()]
        db.execute.return_value = _scalars_result(rules)
        repo = CommissionRepository(db)
        result = await repo.get_valid_rules()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_valid_rules_with_seller_specific_rules(self):
        db = _mock_db()
        rules = [_make_commission_rule()]
        # First call: seller_rules_query, returns specific rule IDs
        seller_result = MagicMock()
        seller_result.all.return_value = [("rule-id-1",)]
        # Second call: main rules query
        rules_result = _scalars_result(rules)
        db.execute.side_effect = [seller_result, rules_result]
        repo = CommissionRepository(db)
        result = await repo.get_valid_rules(seller_id="seller-1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_valid_rules_with_seller_no_specific_rules(self):
        db = _mock_db()
        rules = [_make_commission_rule()]
        seller_result = MagicMock()
        seller_result.all.return_value = []
        rules_result = _scalars_result(rules)
        db.execute.side_effect = [seller_result, rules_result]
        repo = CommissionRepository(db)
        result = await repo.get_valid_rules(seller_id="seller-2")
        assert len(result) == 1

    # --- assign_rule_to_seller ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_assign_rule_to_seller(self, mock_uuid):
        mock_uuid.return_value = "seller-rule-uuid"
        db = _mock_db()
        repo = CommissionRepository(db)
        data = SellerCommissionRuleCreate(
            seller_id="seller-1",
            rule_id="rule-1",
            custom_base_value=7.5,
        )
        result = await repo.assign_rule_to_seller(data)
        db.add.assert_called_once()
        db.commit.assert_awaited_once()

    # --- get_seller_custom_rate ---

    @pytest.mark.asyncio
    async def test_get_seller_custom_rate_found(self):
        db = _mock_db()
        seller_rule = MagicMock(spec=SellerCommissionRule)
        seller_rule.custom_base_value = 7.5
        db.execute.return_value = _scalar_result(seller_rule)
        repo = CommissionRepository(db)
        result = await repo.get_seller_custom_rate("seller-1", "rule-1")
        assert result == 7.5

    @pytest.mark.asyncio
    async def test_get_seller_custom_rate_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.get_seller_custom_rate("seller-1", "rule-1")
        assert result is None

    # --- create commission ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_create_commission_with_rule(self, mock_uuid):
        mock_uuid.return_value = "comm-uuid-1"
        db = _mock_db()
        rule = _make_commission_rule()
        # _get_next_reference_number: first execute
        ref_result = MagicMock()
        ref_result.scalar.return_value = 0
        # get_rule_by_id: second execute
        rule_result = _scalar_result(rule)
        # get_seller_custom_rate: third execute
        rate_result = _scalar_result(None)
        db.execute.side_effect = [rule_result, rate_result, ref_result]
        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.calculate_commission.return_value = {
            "commission_type": "percentage",
            "commission_rate": 5.0,
            "base_commission": 5000.0,
            "trigger": CommissionTrigger.ON_FIRST_PAYMENT.value,
            "trigger_date": date.today(),
            "due_date": date.today() + timedelta(days=30),
        }
        repo.service.generate_reference_number.return_value = "COM-2026-00001"

        data = CommissionCreate(
            seller_id="seller-1",
            sale_value=100000.0,
            rule_id="rule-1",
        )
        result = await repo.create(data, created_by_id="admin-1")
        db.add.assert_called_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_create_commission_without_rule(self, mock_uuid):
        mock_uuid.return_value = "comm-uuid-2"
        db = _mock_db()
        # _get_next_reference_number
        ref_result = MagicMock()
        ref_result.scalar.return_value = 5
        db.execute.return_value = ref_result
        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.generate_reference_number.return_value = "COM-2026-00006"

        data = CommissionCreate(
            seller_id="seller-1",
            sale_value=50000.0,
            commission_type=CommissionType.PERCENTAGE,
            commission_rate=3.0,
            trigger=CommissionTrigger.ON_SIGNATURE,
        )
        result = await repo.create(data)
        db.add.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.commission_rate == 3.0
        assert added.base_commission == 50000.0 * (3.0 / 100)

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_create_commission_no_type_no_rule(self, mock_uuid):
        mock_uuid.return_value = "comm-uuid-3"
        db = _mock_db()
        ref_result = MagicMock()
        ref_result.scalar.return_value = 0
        db.execute.return_value = ref_result
        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.generate_reference_number.return_value = "COM-2026-00001"

        data = CommissionCreate(
            seller_id="seller-1",
            sale_value=10000.0,
        )
        result = await repo.create(data)
        added = db.add.call_args[0][0]
        assert added.commission_type == "percentage"
        assert added.commission_rate == 0.0

    # --- get_by_id ---

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        db = _mock_db()
        comm = _make_commission()
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        result = await repo.get_by_id(comm.id)
        assert result is comm

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.get_by_id("nonexistent")
        assert result is None

    # --- get_by_reference ---

    @pytest.mark.asyncio
    async def test_get_by_reference_found(self):
        db = _mock_db()
        comm = _make_commission(reference_number="COM-2026-00001")
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        result = await repo.get_by_reference("COM-2026-00001")
        assert result is comm

    @pytest.mark.asyncio
    async def test_get_by_reference_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.get_by_reference("COM-2026-99999")
        assert result is None

    # --- list commissions ---

    @pytest.mark.asyncio
    async def test_list_no_filters(self):
        db = _mock_db()
        comms = [_make_commission()]
        data_result = _scalars_result(comms)
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        db.execute.side_effect = [data_result, count_result]
        repo = CommissionRepository(db)
        items, total = await repo.list()
        assert len(items) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_with_all_filters(self):
        db = _mock_db()
        data_result = _scalars_result([_make_commission()])
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        db.execute.side_effect = [data_result, count_result]
        repo = CommissionRepository(db)
        filters = CommissionFilter(
            seller_id="seller-1",
            proposal_id="prop-1",
            status=CommissionStatus.PENDING,
            trigger=CommissionTrigger.ON_FIRST_PAYMENT,
            is_overdue=True,
            min_value=100.0,
            max_value=10000.0,
            date_from=date(2026, 1, 1),
            date_to=date(2026, 12, 31),
            due_date_from=date(2026, 1, 1),
            due_date_to=date(2026, 12, 31),
        )
        items, total = await repo.list(filters=filters)
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_count_none(self):
        db = _mock_db()
        data_result = _scalars_result([])
        count_result = MagicMock()
        count_result.scalar.return_value = None
        db.execute.side_effect = [data_result, count_result]
        repo = CommissionRepository(db)
        items, total = await repo.list()
        assert total == 0

    # --- update commission ---

    @pytest.mark.asyncio
    async def test_update_found(self):
        db = _mock_db()
        comm = _make_commission(base_commission=5000.0, adjustments=0.0, final_commission=5000.0)
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        data = CommissionUpdate(description="Updated desc")
        result = await repo.update(comm.id, data)
        assert result is comm
        assert comm.description == "Updated desc"

    @pytest.mark.asyncio
    async def test_update_with_adjustments(self):
        db = _mock_db()
        comm = _make_commission(base_commission=5000.0, adjustments=0.0, final_commission=5000.0)
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        data = CommissionUpdate(adjustments=500.0)
        result = await repo.update(comm.id, data)
        assert comm.adjustments == 500.0
        assert comm.final_commission == 5500.0

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        data = CommissionUpdate(notes="X")
        result = await repo.update("nonexistent", data)
        assert result is None

    # --- update_status ---

    @pytest.mark.asyncio
    async def test_update_status_approved(self):
        db = _mock_db()
        comm = _make_commission()
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        result = await repo.update_status(comm.id, CommissionStatus.APPROVED, approved_by_id="admin-1")
        assert comm.status == CommissionStatus.APPROVED.value
        assert comm.approved_by_id == "admin-1"
        assert comm.approved_at is not None

    @pytest.mark.asyncio
    async def test_update_status_paid(self):
        db = _mock_db()
        comm = _make_commission()
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        result = await repo.update_status(comm.id, CommissionStatus.PAID)
        assert comm.status == CommissionStatus.PAID.value
        assert comm.paid_date == date.today()

    @pytest.mark.asyncio
    async def test_update_status_with_notes(self):
        db = _mock_db()
        comm = _make_commission()
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        result = await repo.update_status(comm.id, CommissionStatus.CANCELLED, notes="Cancelled reason")
        assert comm.notes == "Cancelled reason"

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.update_status("nonexistent", CommissionStatus.APPROVED)
        assert result is None

    # --- delete commission ---

    @pytest.mark.asyncio
    async def test_delete_found(self):
        db = _mock_db()
        comm = _make_commission()
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        result = await repo.delete(comm.id)
        assert result is True
        assert comm.is_active is False

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.delete("nonexistent")
        assert result is False

    # --- create_payment ---

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_create_payment_success(self, mock_uuid):
        mock_uuid.return_value = "pay-uuid-1"
        db = _mock_db()
        comm = _make_commission(final_commission=5000.0)
        comm.pending_amount = 5000.0
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        data = CommissionPaymentCreate(
            commission_id=comm.id,
            amount=2000.0,
            payment_method=PaymentMethod.PIX,
            payment_date=date.today(),
        )
        result = await repo.create_payment(data, created_by_id="admin-1")
        db.add.assert_called_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_payment_exceeds_pending(self):
        db = _mock_db()
        comm = _make_commission(final_commission=5000.0)
        comm.pending_amount = 1000.0
        db.execute.return_value = _scalar_result(comm)
        repo = CommissionRepository(db)
        data = CommissionPaymentCreate(
            commission_id=comm.id,
            amount=2000.0,
            payment_method=PaymentMethod.PAYROLL,
            payment_date=date.today(),
        )
        result = await repo.create_payment(data)
        assert result is None

    @pytest.mark.asyncio
    async def test_create_payment_commission_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        data = CommissionPaymentCreate(
            commission_id="nonexistent",
            amount=100.0,
            payment_method=PaymentMethod.PAYROLL,
            payment_date=date.today(),
        )
        result = await repo.create_payment(data)
        assert result is None

    # --- confirm_payment ---

    @pytest.mark.asyncio
    async def test_confirm_payment_success(self):
        db = _mock_db()
        payment = MagicMock(spec=CommissionPayment)
        payment.id = "pay-1"
        payment.commission_id = "comm-1"
        payment.is_confirmed = False
        payment.confirmed_at = None
        payment.confirmed_by_id = None
        payment.notes = None

        comm = _make_commission(id="comm-1", final_commission=5000.0)
        comm.pending_amount = 0  # Fully paid after confirmation

        # First execute: find payment
        pay_result = _scalar_result(payment)
        # Second execute: find commission (get_by_id)
        comm_result = _scalar_result(comm)
        db.execute.side_effect = [pay_result, comm_result]

        repo = CommissionRepository(db)
        result = await repo.confirm_payment("pay-1", "admin-1", notes="Confirmed")
        assert payment.is_confirmed is True
        assert payment.confirmed_by_id == "admin-1"
        assert payment.notes == "Confirmed"
        # Commission should be marked paid since pending_amount <= 0
        assert comm.status == CommissionStatus.PAID.value

    @pytest.mark.asyncio
    async def test_confirm_payment_not_found(self):
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.confirm_payment("nonexistent", "admin-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_confirm_payment_partial(self):
        """When pending_amount > 0 after confirmation, commission stays same status."""
        db = _mock_db()
        payment = MagicMock(spec=CommissionPayment)
        payment.id = "pay-1"
        payment.commission_id = "comm-1"
        payment.is_confirmed = False

        comm = _make_commission(id="comm-1", final_commission=5000.0, status=CommissionStatus.APPROVED.value)
        comm.pending_amount = 3000.0  # Still has pending amount

        pay_result = _scalar_result(payment)
        comm_result = _scalar_result(comm)
        db.execute.side_effect = [pay_result, comm_result]

        repo = CommissionRepository(db)
        result = await repo.confirm_payment("pay-1", "admin-1")
        # pending_amount > 0, so status should NOT change to PAID
        assert comm.status == CommissionStatus.APPROVED.value

    # --- get_or_create_summary ---

    @pytest.mark.asyncio
    async def test_get_or_create_summary_existing(self):
        db = _mock_db()
        summary = _make_summary()
        db.execute.return_value = _scalar_result(summary)
        repo = CommissionRepository(db)
        result = await repo.get_or_create_summary("seller-1", 2026, 3)
        assert result is summary
        db.add.assert_not_called()

    @pytest.mark.asyncio
    @patch("modules.crm.repositories.commission_repository.uuid4")
    async def test_get_or_create_summary_new(self, mock_uuid):
        mock_uuid.return_value = "summary-uuid"
        db = _mock_db()
        db.execute.return_value = _scalar_result(None)
        repo = CommissionRepository(db)
        result = await repo.get_or_create_summary("seller-1", 2026, 3)
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        added = db.add.call_args[0][0]
        assert added.seller_id == "seller-1"
        assert added.year == 2026
        assert added.month == 3

    # --- update_summary ---

    @pytest.mark.asyncio
    async def test_update_summary(self):
        db = _mock_db()
        summary = _make_summary(seller_id="seller-1")
        # First call: get_or_create_summary -> find existing
        summary_result = _scalar_result(summary)
        # Second call: fetch commissions for period
        comms = [_make_commission(seller_id="seller-1")]
        comms_result = _scalars_result(comms)
        db.execute.side_effect = [summary_result, comms_result]

        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.update_summary.return_value = summary

        result = await repo.update_summary("seller-1", 2026, 3)
        repo.service.update_summary.assert_called_once()
        db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_summary_december(self):
        """Test month=12 edge case for end_date calculation."""
        db = _mock_db()
        summary = _make_summary(seller_id="seller-1", year=2026, month=12)
        summary_result = _scalar_result(summary)
        comms_result = _scalars_result([])
        db.execute.side_effect = [summary_result, comms_result]

        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.update_summary.return_value = summary

        result = await repo.update_summary("seller-1", 2026, 12)
        repo.service.update_summary.assert_called_once()

    # --- list_summaries ---

    @pytest.mark.asyncio
    async def test_list_summaries_no_filters(self):
        db = _mock_db()
        summaries = [_make_summary()]
        db.execute.return_value = _scalars_result(summaries)
        repo = CommissionRepository(db)
        result = await repo.list_summaries()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_summaries_with_filters(self):
        db = _mock_db()
        summaries = [_make_summary()]
        db.execute.return_value = _scalars_result(summaries)
        repo = CommissionRepository(db)
        filters = CommissionSummaryFilter(
            seller_id="seller-1",
            year=2026,
            month=3,
            is_closed=False,
        )
        result = await repo.list_summaries(filters=filters)
        assert len(result) == 1

    # --- close_summary ---

    @pytest.mark.asyncio
    async def test_close_summary(self):
        db = _mock_db()
        summary = _make_summary()
        db.execute.return_value = _scalar_result(summary)
        repo = CommissionRepository(db)
        result = await repo.close_summary("seller-1", 2026, 3)
        assert summary.is_closed is True
        assert summary.closed_at is not None

    # --- get_all_for_stats ---

    @pytest.mark.asyncio
    async def test_get_all_for_stats_no_dates(self):
        db = _mock_db()
        comms = [_make_commission()]
        db.execute.return_value = _scalars_result(comms)
        repo = CommissionRepository(db)
        result = await repo.get_all_for_stats()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_for_stats_with_dates(self):
        db = _mock_db()
        comms = [_make_commission()]
        db.execute.return_value = _scalars_result(comms)
        repo = CommissionRepository(db)
        result = await repo.get_all_for_stats(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 12, 31),
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_for_stats_only_date_from(self):
        db = _mock_db()
        db.execute.return_value = _scalars_result([])
        repo = CommissionRepository(db)
        result = await repo.get_all_for_stats(date_from=date(2026, 6, 1))
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_all_for_stats_only_date_to(self):
        db = _mock_db()
        db.execute.return_value = _scalars_result([])
        repo = CommissionRepository(db)
        result = await repo.get_all_for_stats(date_to=date(2026, 6, 30))
        assert len(result) == 0

    # --- _get_next_reference_number ---

    @pytest.mark.asyncio
    async def test_get_next_reference_number(self):
        db = _mock_db()
        ref_result = MagicMock()
        ref_result.scalar.return_value = 10
        db.execute.return_value = ref_result
        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.generate_reference_number.return_value = "COM-2026-00011"
        result = await repo._get_next_reference_number()
        assert result == "COM-2026-00011"
        repo.service.generate_reference_number.assert_called_once_with(11)

    @pytest.mark.asyncio
    async def test_get_next_reference_number_none_count(self):
        db = _mock_db()
        ref_result = MagicMock()
        ref_result.scalar.return_value = None
        db.execute.return_value = ref_result
        repo = CommissionRepository(db)
        repo.service = MagicMock()
        repo.service.generate_reference_number.return_value = "COM-2026-00001"
        result = await repo._get_next_reference_number()
        repo.service.generate_reference_number.assert_called_once_with(1)

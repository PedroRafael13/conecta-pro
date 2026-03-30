"""
Tests for CRM controllers: lead, opportunity, proposal, dashboard.
Covers all endpoints with mocked repositories, services, and DB.
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

# Dashboard controller + deps
from modules.crm.controllers.dashboard_controller import (
    get_commissions_by_status_chart,
    get_commissions_trends,
    get_conversion_rates,
    get_dashboard_kpis,
    get_leads_by_status_chart,
    get_leads_trends,
    get_opportunities_by_stage_chart,
    get_proposals_by_status_chart,
    get_sales_funnel,
    get_sales_trends,
    get_seller_performance,
    get_top_performers,
)

# Lead controller + deps
from modules.crm.controllers.lead_controller import (
    create_lead,
    delete_lead,
    get_lead,
    get_lead_stats,
    get_recommended_action,
    list_leads,
    recalculate_lead_score,
    update_lead,
    update_lead_status,
)

# Opportunity controller + deps
from modules.crm.controllers.opportunity_controller import (
    close_opportunity,
    create_opportunity,
    create_opportunity_from_lead,
    delete_opportunity,
    get_opportunity,
    get_pipeline_stats,
    list_opportunities,
    update_opportunity,
    update_opportunity_stage,
)

# Proposal controller + deps
from modules.crm.controllers.proposal_controller import (
    accept_proposal,
    add_proposal_item,
    create_new_version,
    create_proposal,
    create_proposal_from_opportunity,
    create_template,
    delete_proposal,
    delete_template,
    get_proposal,
    get_proposal_stats,
    get_template,
    list_proposals,
    list_templates,
    process_proposal_approval,
    reject_proposal,
    remove_proposal_item,
    send_proposal,
    submit_proposal_for_approval,
    update_proposal,
    update_template,
)
from modules.crm.models.lead import LeadSource, LeadStatus
from modules.crm.models.opportunity import OpportunityPriority, OpportunityStage
from modules.crm.models.proposal import ApprovalAction, ProposalStatus, ProposalType
from modules.crm.schemas.lead import (
    LeadCreate,
    LeadStatusUpdate,
    LeadUpdate,
)
from modules.crm.schemas.opportunity import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityCreateFromLead,
    OpportunityStageUpdate,
    OpportunityUpdate,
)
from modules.crm.schemas.proposal import (
    ProposalApprovalRequest,
    ProposalCreate,
    ProposalCreateFromOpportunity,
    ProposalItemCreate,
    ProposalTemplateCreate,
    ProposalTemplateUpdate,
    ProposalUpdate,
)

# ============== Fixtures ==============


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = str(uuid4())
    user.email = "test@conectapro.com.br"
    return user


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    return db


def _make_mock_lead(**overrides):
    """Create a mock lead with all required attributes."""
    now = datetime.now()
    lead = MagicMock()
    defaults = {
        "id": str(uuid4()),
        "name": "Test Lead",
        "email": "lead@test.com",
        "phone": "11999999999",
        "company": "Test Corp",
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
        "created_at": now,
        "updated_at": now,
        "is_hot": False,
        "is_qualified": False,
        "weighted_value": 3000.0,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(lead, k, v)
    return lead


def _make_mock_opportunity(**overrides):
    now = datetime.now()
    opp = MagicMock()
    defaults = {
        "id": str(uuid4()),
        "title": "Opp Test",
        "description": None,
        "lead_id": None,
        "contact_name": "Contact",
        "contact_email": "c@test.com",
        "contact_phone": None,
        "company_name": "Corp",
        "stage": OpportunityStage.QUALIFICATION,
        "priority": OpportunityPriority.MEDIUM,
        "value": 50000.0,
        "probability": 20,
        "weighted_value": 10000.0,
        "expected_close_date": None,
        "actual_close_date": None,
        "owner_id": None,
        "loss_reason": None,
        "competitor": None,
        "win_notes": None,
        "loss_notes": None,
        "notes": None,
        "is_open": True,
        "is_won": False,
        "is_lost": False,
        "is_overdue": False,
        "days_in_pipeline": 5,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(opp, k, v)
    return opp


def _make_mock_proposal(**overrides):
    now = datetime.now()
    prop = MagicMock()
    defaults = {
        "id": str(uuid4()),
        "number": "PROP-001",
        "version": 1,
        "parent_id": None,
        "opportunity_id": None,
        "template_id": None,
        "client_name": "Client",
        "client_email": "client@test.com",
        "client_phone": None,
        "client_company": None,
        "client_document": None,
        "client_address": None,
        "title": "Proposta Test",
        "description": None,
        "proposal_type": ProposalType.SERVICE,
        "terms_conditions": None,
        "notes": None,
        "subtotal": 10000.0,
        "discount_type": None,
        "discount_value": 0.0,
        "discount_reason": None,
        "discount_amount": 0.0,
        "taxes": 0.0,
        "total": 10000.0,
        "payment_terms": None,
        "payment_conditions": None,
        "installments": 1,
        "issue_date": date.today(),
        "valid_until": None,
        "sent_at": None,
        "viewed_at": None,
        "responded_at": None,
        "status": ProposalStatus.DRAFT,
        "rejection_reason": None,
        "created_by_id": None,
        "approved_by_id": None,
        "approved_at": None,
        "is_draft": True,
        "is_pending": False,
        "is_approved": False,
        "is_sent": False,
        "is_closed": False,
        "is_accepted": False,
        "is_expired": False,
        "days_until_expiry": None,
        "item_count": 0,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "items": [],
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(prop, k, v)
    return prop


def _make_mock_template(**overrides):
    now = datetime.now()
    t = MagicMock()
    defaults = {
        "id": str(uuid4()),
        "name": "Template Test",
        "description": None,
        "default_title": None,
        "default_description": None,
        "terms_conditions": None,
        "payment_terms": None,
        "validity_days": 30,
        "proposal_type": ProposalType.SERVICE,
        "header_html": None,
        "footer_html": None,
        "css_styles": None,
        "is_default": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(t, k, v)
    return t


def _make_mock_item(**overrides):
    now = datetime.now()
    item = MagicMock()
    defaults = {
        "id": str(uuid4()),
        "proposal_id": str(uuid4()),
        "code": None,
        "name": "Item Test",
        "description": None,
        "unit": "un",
        "quantity": 1.0,
        "unit_price": 100.0,
        "discount_percent": 0.0,
        "is_optional": False,
        "total": 100.0,
        "subtotal": 100.0,
        "discount_amount": 0.0,
        "sort_order": 0,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        setattr(item, k, v)
    return item


# ============== Lead Controller Tests ==============


class TestLeadController:
    @pytest.mark.asyncio
    async def test_create_lead_success(self, mock_user, mock_db):
        mock_lead = _make_mock_lead()
        data = LeadCreate(
            name="Test Lead",
            email="lead@test.com",
            source=LeadSource.WEBSITE,
        )
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_email = AsyncMock(return_value=None)
            repo.create = AsyncMock(return_value=mock_lead)
            result = await create_lead(data=data, current_user=mock_user, db=mock_db)
        assert result.id == mock_lead.id
        repo.create.assert_awaited_once_with(data)

    @pytest.mark.asyncio
    async def test_create_lead_duplicate_email(self, mock_user, mock_db):
        existing = _make_mock_lead()
        data = LeadCreate(name="Dup", email="lead@test.com")
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_email = AsyncMock(return_value=existing)
            with pytest.raises(HTTPException) as exc:
                await create_lead(data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_list_leads(self, mock_user, mock_db):
        leads = [_make_mock_lead(), _make_mock_lead()]
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list = AsyncMock(return_value=(leads, 2))
            result = await list_leads(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                status_filter=None,
                source=None,
                assigned_to_id=None,
                min_score=None,
                max_score=None,
                is_hot=None,
                company=None,
                search=None,
            )
        assert result.total == 2
        assert len(result.items) == 2
        assert result.total_pages == 1

    @pytest.mark.asyncio
    async def test_list_leads_empty(self, mock_user, mock_db):
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list = AsyncMock(return_value=([], 0))
            result = await list_leads(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                status_filter=None,
                source=None,
                assigned_to_id=None,
                min_score=None,
                max_score=None,
                is_hot=None,
                company=None,
                search=None,
            )
        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_get_lead_stats(self, mock_user, mock_db):
        mock_stats = MagicMock()
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_stats = AsyncMock(return_value=mock_stats)
            result = await get_lead_stats(current_user=mock_user, db=mock_db)
        assert result == mock_stats

    @pytest.mark.asyncio
    async def test_get_lead_found(self, mock_user, mock_db):
        lead = _make_mock_lead()
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=lead)
            result = await get_lead(lead_id=lead.id, current_user=mock_user, db=mock_db)
        assert result.id == lead.id

    @pytest.mark.asyncio
    async def test_get_lead_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await get_lead(lead_id="nope", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_lead_success(self, mock_user, mock_db):
        lead = _make_mock_lead(name="Updated")
        data = LeadUpdate(name="Updated")
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update = AsyncMock(return_value=lead)
            result = await update_lead(lead_id=lead.id, data=data, current_user=mock_user, db=mock_db)
        assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_update_lead_not_found(self, mock_user, mock_db):
        data = LeadUpdate(name="XX")
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await update_lead(lead_id="nope", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_lead_status_success(self, mock_user, mock_db):
        lead = _make_mock_lead(status=LeadStatus.CONTACTED.value)
        data = LeadStatusUpdate(status=LeadStatus.CONTACTED)
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=lead)
            result = await update_lead_status(lead_id=lead.id, data=data, current_user=mock_user, db=mock_db)
        assert result.status == LeadStatus.CONTACTED.value

    @pytest.mark.asyncio
    async def test_update_lead_status_not_found(self, mock_user, mock_db):
        data = LeadStatusUpdate(status=LeadStatus.QUALIFIED)
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await update_lead_status(lead_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_recalculate_lead_score_success(self, mock_user, mock_db):
        lead = _make_mock_lead(score=75)
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_score = AsyncMock(return_value=lead)
            result = await recalculate_lead_score(lead_id=lead.id, current_user=mock_user, db=mock_db)
        assert result.score == 75

    @pytest.mark.asyncio
    async def test_recalculate_lead_score_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_score = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await recalculate_lead_score(lead_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_recommended_action_success(self, mock_user, mock_db):
        lead = _make_mock_lead(score=85, status=LeadStatus.NEW.value)
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=lead)
            result = await get_recommended_action(lead_id=lead.id, current_user=mock_user, db=mock_db)
        assert "lead_id" in result
        assert "recommended_action" in result
        assert result["score"] == 85

    @pytest.mark.asyncio
    async def test_get_recommended_action_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await get_recommended_action(lead_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_lead_success(self, mock_user, mock_db):
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete = AsyncMock(return_value=True)
            result = await delete_lead(lead_id="abc", current_user=mock_user, db=mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_lead_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.lead_controller.LeadRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc:
                await delete_lead(lead_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404


# ============== Opportunity Controller Tests ==============


class TestOpportunityController:
    @pytest.mark.asyncio
    async def test_create_opportunity_success(self, mock_user, mock_db):
        opp = _make_mock_opportunity()
        data = OpportunityCreate(
            title="New Opp",
            contact_name="Contact",
            contact_email="c@test.com",
        )
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create = AsyncMock(return_value=opp)
            result = await create_opportunity(data=data, current_user=mock_user, db=mock_db)
        assert result.id == opp.id

    @pytest.mark.asyncio
    async def test_create_opportunity_from_lead_success(self, mock_user, mock_db):
        opp = _make_mock_opportunity()
        data = OpportunityCreateFromLead(
            lead_id=str(uuid4()),
            title="From Lead",
        )
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_from_lead = AsyncMock(return_value=opp)
            result = await create_opportunity_from_lead(data=data, current_user=mock_user, db=mock_db)
        assert result.id == opp.id

    @pytest.mark.asyncio
    async def test_create_opportunity_from_lead_not_found(self, mock_user, mock_db):
        data = OpportunityCreateFromLead(lead_id=str(uuid4()), title="X")
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_from_lead = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await create_opportunity_from_lead(data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_opportunities(self, mock_user, mock_db):
        opps = [_make_mock_opportunity(), _make_mock_opportunity()]
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list = AsyncMock(return_value=(opps, 2))
            result = await list_opportunities(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                stage=None,
                priority=None,
                owner_id=None,
                is_open=None,
                min_value=None,
                max_value=None,
                company_name=None,
                search=None,
            )
        assert result.total == 2
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_list_opportunities_empty(self, mock_user, mock_db):
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list = AsyncMock(return_value=([], 0))
            result = await list_opportunities(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                stage=None,
                priority=None,
                owner_id=None,
                is_open=None,
                min_value=None,
                max_value=None,
                company_name=None,
                search=None,
            )
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_pipeline_stats(self, mock_user, mock_db):
        stats = MagicMock()
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_pipeline_stats = AsyncMock(return_value=stats)
            result = await get_pipeline_stats(current_user=mock_user, db=mock_db)
        assert result == stats

    @pytest.mark.asyncio
    async def test_get_opportunity_found(self, mock_user, mock_db):
        opp = _make_mock_opportunity()
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=opp)
            result = await get_opportunity(opportunity_id=opp.id, current_user=mock_user, db=mock_db)
        assert result.id == opp.id

    @pytest.mark.asyncio
    async def test_get_opportunity_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await get_opportunity(opportunity_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_opportunity_success(self, mock_user, mock_db):
        opp = _make_mock_opportunity(title="Updated")
        data = OpportunityUpdate(title="Updated")
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update = AsyncMock(return_value=opp)
            result = await update_opportunity(opportunity_id=opp.id, data=data, current_user=mock_user, db=mock_db)
        assert result.title == "Updated"

    @pytest.mark.asyncio
    async def test_update_opportunity_not_found(self, mock_user, mock_db):
        data = OpportunityUpdate(title="X")
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await update_opportunity(opportunity_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_opportunity_stage_success(self, mock_user, mock_db):
        opp = _make_mock_opportunity(stage=OpportunityStage.PROPOSAL)
        data = OpportunityStageUpdate(stage=OpportunityStage.PROPOSAL)
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_stage = AsyncMock(return_value=opp)
            result = await update_opportunity_stage(
                opportunity_id=opp.id, data=data, current_user=mock_user, db=mock_db
            )
        assert result.stage == OpportunityStage.PROPOSAL

    @pytest.mark.asyncio
    async def test_update_opportunity_stage_not_found(self, mock_user, mock_db):
        data = OpportunityStageUpdate(stage=OpportunityStage.NEGOTIATION)
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_stage = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await update_opportunity_stage(opportunity_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_close_opportunity_won(self, mock_user, mock_db):
        opp = _make_mock_opportunity(is_won=True, is_open=False)
        data = OpportunityClose(won=True)
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.close = AsyncMock(return_value=opp)
            result = await close_opportunity(opportunity_id=opp.id, data=data, current_user=mock_user, db=mock_db)
        assert result.is_won is True

    @pytest.mark.asyncio
    async def test_close_opportunity_lost(self, mock_user, mock_db):
        opp = _make_mock_opportunity(is_lost=True, is_open=False)
        data = OpportunityClose(won=False)
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.close = AsyncMock(return_value=opp)
            result = await close_opportunity(opportunity_id=opp.id, data=data, current_user=mock_user, db=mock_db)
        assert result.is_lost is True

    @pytest.mark.asyncio
    async def test_close_opportunity_not_found(self, mock_user, mock_db):
        data = OpportunityClose(won=True)
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.close = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await close_opportunity(opportunity_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_opportunity_success(self, mock_user, mock_db):
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete = AsyncMock(return_value=True)
            result = await delete_opportunity(opportunity_id="abc", current_user=mock_user, db=mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_opportunity_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.opportunity_controller.OpportunityRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc:
                await delete_opportunity(opportunity_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404


# ============== Proposal Controller Tests ==============


class TestProposalController:
    @pytest.mark.asyncio
    async def test_create_proposal_success(self, mock_user, mock_db):
        prop = _make_mock_proposal()
        data = ProposalCreate(
            title="Test",
            client_name="Client",
            client_email="c@test.com",
        )
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create = AsyncMock(return_value=prop)
            result = await create_proposal(data=data, current_user=mock_user, db=mock_db)
        assert result.number == prop.number
        repo.create.assert_awaited_once_with(data, created_by_id=str(mock_user.id))

    @pytest.mark.asyncio
    async def test_create_proposal_from_opportunity_success(self, mock_user, mock_db):
        prop = _make_mock_proposal()
        data = ProposalCreateFromOpportunity(
            opportunity_id=str(uuid4()),
            title="From Opp",
        )
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_from_opportunity = AsyncMock(return_value=prop)
            result = await create_proposal_from_opportunity(data=data, current_user=mock_user, db=mock_db)
        assert result.number == prop.number

    @pytest.mark.asyncio
    async def test_create_proposal_from_opportunity_not_found(self, mock_user, mock_db):
        data = ProposalCreateFromOpportunity(opportunity_id=str(uuid4()), title="X")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_from_opportunity = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await create_proposal_from_opportunity(data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_proposals(self, mock_user, mock_db):
        props = [_make_mock_proposal(), _make_mock_proposal()]
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list = AsyncMock(return_value=(props, 2))
            result = await list_proposals(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                status_filter=None,
                proposal_type=None,
                opportunity_id=None,
                is_expired=None,
                min_value=None,
                max_value=None,
                client_name=None,
                search=None,
            )
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_list_proposals_empty(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list = AsyncMock(return_value=([], 0))
            result = await list_proposals(
                current_user=mock_user,
                db=mock_db,
                page=1,
                page_size=20,
                status_filter=None,
                proposal_type=None,
                opportunity_id=None,
                is_expired=None,
                min_value=None,
                max_value=None,
                client_name=None,
                search=None,
            )
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_proposal_stats(self, mock_user, mock_db):
        stats = MagicMock()
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_stats = AsyncMock(return_value=stats)
            result = await get_proposal_stats(current_user=mock_user, db=mock_db)
        assert result == stats

    @pytest.mark.asyncio
    async def test_get_proposal_found(self, mock_user, mock_db):
        prop = _make_mock_proposal()
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=prop)
            result = await get_proposal(proposal_id=prop.id, current_user=mock_user, db=mock_db)
        assert result.id == prop.id

    @pytest.mark.asyncio
    async def test_get_proposal_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await get_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_proposal_success(self, mock_user, mock_db):
        prop = _make_mock_proposal(title="Updated")
        data = ProposalUpdate(title="Updated")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update = AsyncMock(return_value=prop)
            result = await update_proposal(proposal_id=prop.id, data=data, current_user=mock_user, db=mock_db)
        assert result.title == "Updated"

    @pytest.mark.asyncio
    async def test_update_proposal_not_found(self, mock_user, mock_db):
        data = ProposalUpdate(title="X")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await update_proposal(proposal_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_submit_for_approval_success(self, mock_user, mock_db):
        prop = _make_mock_proposal(status=ProposalStatus.PENDING_APPROVAL)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.submit_for_approval = AsyncMock(return_value=prop)
            result = await submit_proposal_for_approval(proposal_id=prop.id, current_user=mock_user, db=mock_db)
        assert result.status == ProposalStatus.PENDING_APPROVAL

    @pytest.mark.asyncio
    async def test_submit_for_approval_fail(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.submit_for_approval = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await submit_proposal_for_approval(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_process_approval_approve(self, mock_user, mock_db):
        prop = _make_mock_proposal(status=ProposalStatus.APPROVED)
        data = ProposalApprovalRequest(action=ApprovalAction.APPROVE)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.process_approval = AsyncMock(return_value=prop)
            result = await process_proposal_approval(proposal_id=prop.id, data=data, current_user=mock_user, db=mock_db)
        assert result.status == ProposalStatus.APPROVED

    @pytest.mark.asyncio
    async def test_process_approval_reject(self, mock_user, mock_db):
        prop = _make_mock_proposal(status=ProposalStatus.REJECTED)
        data = ProposalApprovalRequest(action=ApprovalAction.REJECT, comments="No good")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.process_approval = AsyncMock(return_value=prop)
            result = await process_proposal_approval(proposal_id=prop.id, data=data, current_user=mock_user, db=mock_db)
        assert result.status == ProposalStatus.REJECTED

    @pytest.mark.asyncio
    async def test_process_approval_not_found(self, mock_user, mock_db):
        data = ProposalApprovalRequest(action=ApprovalAction.APPROVE)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.process_approval = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await process_proposal_approval(proposal_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_send_proposal_success(self, mock_user, mock_db):
        prop = _make_mock_proposal(status=ProposalStatus.SENT)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=prop)
            result = await send_proposal(proposal_id=prop.id, current_user=mock_user, db=mock_db)
        assert result.status == ProposalStatus.SENT

    @pytest.mark.asyncio
    async def test_send_proposal_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await send_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_accept_proposal_success(self, mock_user, mock_db):
        prop = _make_mock_proposal(status=ProposalStatus.ACCEPTED)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=prop)
            result = await accept_proposal(proposal_id=prop.id, current_user=mock_user, db=mock_db)
        assert result.status == ProposalStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_accept_proposal_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await accept_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_reject_proposal_success(self, mock_user, mock_db):
        prop = _make_mock_proposal(status=ProposalStatus.REJECTED)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=prop)
            result = await reject_proposal(
                proposal_id=prop.id, current_user=mock_user, db=mock_db, reason="Too expensive"
            )
        assert result.status == ProposalStatus.REJECTED

    @pytest.mark.asyncio
    async def test_reject_proposal_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_status = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await reject_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_new_version_success(self, mock_user, mock_db):
        prop = _make_mock_proposal(version=2)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_new_version = AsyncMock(return_value=prop)
            result = await create_new_version(proposal_id=prop.id, current_user=mock_user, db=mock_db)
        assert result.version == 2

    @pytest.mark.asyncio
    async def test_create_new_version_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_new_version = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await create_new_version(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_proposal_success(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete = AsyncMock(return_value=True)
            result = await delete_proposal(proposal_id="abc", current_user=mock_user, db=mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_proposal_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc:
                await delete_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    # --- Item endpoints ---

    @pytest.mark.asyncio
    async def test_add_proposal_item_success(self, mock_user, mock_db):
        item = _make_mock_item()
        data = ProposalItemCreate(name="Camera IP", unit_price=500.0, quantity=10)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.add_item = AsyncMock(return_value=item)
            result = await add_proposal_item(proposal_id="pid", data=data, current_user=mock_user, db=mock_db)
        assert result.name == item.name

    @pytest.mark.asyncio
    async def test_add_proposal_item_fail(self, mock_user, mock_db):
        data = ProposalItemCreate(name="X", unit_price=10.0)
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.add_item = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await add_proposal_item(proposal_id="pid", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_remove_proposal_item_success(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.remove_item = AsyncMock(return_value=True)
            result = await remove_proposal_item(proposal_id="pid", item_id="iid", current_user=mock_user, db=mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_proposal_item_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.remove_item = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc:
                await remove_proposal_item(proposal_id="pid", item_id="iid", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    # --- Template endpoints ---

    @pytest.mark.asyncio
    async def test_create_template_success(self, mock_user, mock_db):
        tmpl = _make_mock_template()
        data = ProposalTemplateCreate(name="My Template")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create_template = AsyncMock(return_value=tmpl)
            result = await create_template(data=data, current_user=mock_user, db=mock_db)
        assert result.name == tmpl.name

    @pytest.mark.asyncio
    async def test_list_templates(self, mock_user, mock_db):
        templates = [_make_mock_template(), _make_mock_template()]
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.list_templates = AsyncMock(return_value=templates)
            result = await list_templates(current_user=mock_user, db=mock_db)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_template_found(self, mock_user, mock_db):
        tmpl = _make_mock_template()
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_template_by_id = AsyncMock(return_value=tmpl)
            result = await get_template(template_id=tmpl.id, current_user=mock_user, db=mock_db)
        assert result.id == tmpl.id

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_template_by_id = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await get_template(template_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_template_success(self, mock_user, mock_db):
        tmpl = _make_mock_template(name="Updated Template")
        data = ProposalTemplateUpdate(name="Updated Template")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_template = AsyncMock(return_value=tmpl)
            result = await update_template(template_id=tmpl.id, data=data, current_user=mock_user, db=mock_db)
        assert result.name == "Updated Template"

    @pytest.mark.asyncio
    async def test_update_template_not_found(self, mock_user, mock_db):
        data = ProposalTemplateUpdate(name="X")
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_template = AsyncMock(return_value=None)
            with pytest.raises(HTTPException) as exc:
                await update_template(template_id="x", data=data, current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_template_success(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete_template = AsyncMock(return_value=True)
            result = await delete_template(template_id="abc", current_user=mock_user, db=mock_db)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self, mock_user, mock_db):
        with patch("modules.crm.controllers.proposal_controller.ProposalRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.delete_template = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc:
                await delete_template(template_id="x", current_user=mock_user, db=mock_db)
            assert exc.value.status_code == 404


# ============== Dashboard Controller Tests ==============


# Helper to mock db.execute for _get_all_* functions
def _mock_db_returning_empty():
    """Create a mock db whose execute returns empty scalars."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    db.execute = AsyncMock(return_value=mock_result)
    return db


def _mock_db_returning(*items_lists):
    """
    Create a mock db whose successive execute calls return different item lists.
    items_lists: each element is a list of items for one call.
    """
    db = AsyncMock()
    results = []
    for items in items_lists:
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = items
        mock_result.scalars.return_value = mock_scalars
        results.append(mock_result)
    db.execute = AsyncMock(side_effect=results)
    return db


class TestDashboardController:
    @pytest.mark.asyncio
    async def test_get_dashboard_kpis(self, mock_user):
        db = _mock_db_returning([], [], [], [])  # leads, opps, proposals, commissions
        mock_kpis = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.calculate_kpis = MagicMock(return_value=mock_kpis)
            result = await get_dashboard_kpis(current_user=mock_user, db=db)
        assert result == mock_kpis
        svc.calculate_kpis.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_dashboard_kpis_with_dates(self, mock_user):
        db = _mock_db_returning([], [], [], [])
        mock_kpis = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.calculate_kpis = MagicMock(return_value=mock_kpis)
            result = await get_dashboard_kpis(
                current_user=mock_user,
                db=db,
                date_from=date(2026, 1, 1),
                date_to=date(2026, 3, 31),
            )
        assert result == mock_kpis

    @pytest.mark.asyncio
    async def test_get_sales_funnel(self, mock_user):
        db = _mock_db_returning([])  # opportunities
        mock_chart = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_funnel_chart = MagicMock(return_value=mock_chart)
            result = await get_sales_funnel(current_user=mock_user, db=db)
        assert result == mock_chart

    @pytest.mark.asyncio
    async def test_get_leads_trends(self, mock_user):
        db = _mock_db_returning([])  # leads
        mock_trends = [MagicMock()]
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_trends = MagicMock(return_value=mock_trends)
            result = await get_leads_trends(current_user=mock_user, db=db)
        assert result == mock_trends
        svc.generate_trends.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_leads_trends_custom_params(self, mock_user):
        db = _mock_db_returning([])
        mock_trends = []
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_trends = MagicMock(return_value=mock_trends)
            result = await get_leads_trends(current_user=mock_user, db=db, period="week", periods_count=4)
        assert result == mock_trends

    @pytest.mark.asyncio
    async def test_get_sales_trends_empty(self, mock_user):
        db = _mock_db_returning([])  # opportunities (none won)
        mock_trends = []
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_trends = MagicMock(return_value=mock_trends)
            result = await get_sales_trends(current_user=mock_user, db=db)
        assert result == mock_trends

    @pytest.mark.asyncio
    async def test_get_sales_trends_with_won(self, mock_user):
        won_opp = MagicMock()
        won_opp.is_won = True
        won_opp.actual_close_date = date(2026, 3, 1)
        won_opp.is_active = True
        db = _mock_db_returning([won_opp])
        mock_trends = [MagicMock()]
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_trends = MagicMock(return_value=mock_trends)
            result = await get_sales_trends(current_user=mock_user, db=db)
        assert result == mock_trends
        call_kwargs = svc.generate_trends.call_args
        assert (
            call_kwargs[1]["date_field"] == "actual_close_date"
            or call_kwargs.kwargs.get("date_field") == "actual_close_date"
        )

    @pytest.mark.asyncio
    async def test_get_commissions_trends(self, mock_user):
        db = _mock_db_returning([])  # commissions
        mock_trends = []
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_trends = MagicMock(return_value=mock_trends)
            result = await get_commissions_trends(current_user=mock_user, db=db)
        assert result == mock_trends

    @pytest.mark.asyncio
    async def test_get_conversion_rates(self, mock_user):
        db = _mock_db_returning([])  # opportunities
        mock_rates = {"lead_to_opp": 0.5}
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.calculate_conversion_rates = MagicMock(return_value=mock_rates)
            result = await get_conversion_rates(current_user=mock_user, db=db)
        assert result == mock_rates

    @pytest.mark.asyncio
    async def test_get_seller_performance(self, mock_user):
        seller_id = str(uuid4())
        db = _mock_db_returning([], [], [])  # leads, opps, commissions
        mock_metrics = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.calculate_seller_performance = MagicMock(return_value=mock_metrics)
            result = await get_seller_performance(seller_id=seller_id, current_user=mock_user, db=db)
        assert result == mock_metrics

    @pytest.mark.asyncio
    async def test_get_seller_performance_with_target(self, mock_user):
        seller_id = str(uuid4())
        db = _mock_db_returning([], [], [])
        mock_metrics = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.calculate_seller_performance = MagicMock(return_value=mock_metrics)
            result = await get_seller_performance(seller_id=seller_id, current_user=mock_user, db=db, target=100000.0)
        assert result == mock_metrics

    @pytest.mark.asyncio
    async def test_get_top_performers_empty(self, mock_user):
        db = _mock_db_returning([], [], [])  # leads, opps, commissions
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.get_top_performers = MagicMock(return_value=[])
            result = await get_top_performers(current_user=mock_user, db=db)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_top_performers_with_sellers(self, mock_user):
        lead = MagicMock()
        lead.assigned_to_id = str(uuid4())
        opp = MagicMock()
        opp.owner_id = str(uuid4())
        db = _mock_db_returning([lead], [opp], [])
        mock_top = [MagicMock(), MagicMock()]
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.get_top_performers = MagicMock(return_value=mock_top)
            result = await get_top_performers(current_user=mock_user, db=db)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_leads_by_status_chart(self, mock_user):
        db = _mock_db_returning([])
        mock_chart = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_pie_chart_by_status = MagicMock(return_value=mock_chart)
            result = await get_leads_by_status_chart(current_user=mock_user, db=db)
        assert result == mock_chart

    @pytest.mark.asyncio
    async def test_get_opportunities_by_stage_chart(self, mock_user):
        db = _mock_db_returning([])
        mock_chart = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_pie_chart_by_status = MagicMock(return_value=mock_chart)
            result = await get_opportunities_by_stage_chart(current_user=mock_user, db=db)
        assert result == mock_chart

    @pytest.mark.asyncio
    async def test_get_proposals_by_status_chart(self, mock_user):
        db = _mock_db_returning([])
        mock_chart = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_pie_chart_by_status = MagicMock(return_value=mock_chart)
            result = await get_proposals_by_status_chart(current_user=mock_user, db=db)
        assert result == mock_chart

    @pytest.mark.asyncio
    async def test_get_commissions_by_status_chart(self, mock_user):
        db = _mock_db_returning([])
        mock_chart = MagicMock()
        with patch("modules.crm.controllers.dashboard_controller.DashboardService") as MockSvc:
            svc = MockSvc.return_value
            svc.generate_pie_chart_by_status = MagicMock(return_value=mock_chart)
            result = await get_commissions_by_status_chart(current_user=mock_user, db=db)
        assert result == mock_chart

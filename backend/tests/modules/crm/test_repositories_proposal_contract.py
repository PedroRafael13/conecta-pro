"""
Tests for ProposalRepository and ContractRepository.
Covers all public methods with mocked DB sessions.
"""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid():
    return str(uuid.uuid4())


def _mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    return db


def _scalars_all(items):
    """Return a result whose .scalars().all() yields *items*."""
    scalars = MagicMock()
    scalars.all.return_value = items
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


def _scalar_one(item):
    """Return a result whose .scalar_one_or_none() yields *item*."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = item
    return result


def _scalar(value):
    """Return a result whose .scalar() yields *value*."""
    result = MagicMock()
    result.scalar.return_value = value
    return result


# ===================================================================
# ProposalRepository tests
# ===================================================================


class TestProposalRepository:
    """Tests for ProposalRepository."""

    # Lazy import inside each helper so the module‑level deprecation
    # warning does not break collection when the import itself is slow.

    def _repo(self, db=None):
        from modules.crm.repositories.proposal_repository import ProposalRepository

        return ProposalRepository(db or _mock_db())

    # ------ _generate_proposal_number ------

    def test_generate_proposal_number_format(self):
        repo = self._repo()
        num = repo._generate_proposal_number()
        assert num.startswith("PROP-")
        parts = num.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 6  # hex chunk

    # ------ create ------

    @pytest.mark.asyncio
    async def test_create_proposal_no_template(self):
        from modules.crm.models.proposal import ProposalStatus
        from modules.crm.schemas.proposal import ProposalCreate, ProposalItemCreate

        db = _mock_db()
        repo = self._repo(db)

        item = ProposalItemCreate(name="Serv A", quantity=2, unit_price=100.0)
        data = ProposalCreate(
            title="Proposta 1",
            client_name="Acme",
            client_email="a@b.com",
            proposal_type="service",
            items=[item],
        )

        # After flush & refresh, simulate the proposal returned
        proposal_mock = MagicMock()
        proposal_mock.id = _uid()
        proposal_mock.number = "PROP-20260101-AABBCC"
        proposal_mock.calculate_totals = MagicMock()

        # get_by_id won't be called; we patch refresh to set proposal attrs
        db.refresh = AsyncMock()

        result = await repo.create(data, created_by_id=_uid())
        # We verify that db.add was called (proposal + item)
        assert db.add.call_count >= 2  # proposal + 1 item
        assert db.commit.await_count >= 1
        assert db.flush.await_count >= 1

    @pytest.mark.asyncio
    async def test_create_proposal_with_template(self):
        from modules.crm.schemas.proposal import ProposalCreate

        db = _mock_db()
        repo = self._repo(db)

        template_mock = MagicMock()
        template_mock.validity_days = 45

        # Patch get_template_by_id
        repo.get_template_by_id = AsyncMock(return_value=template_mock)

        tid = _uid()
        data = ProposalCreate(
            title="P2",
            client_name="Corp",
            client_email="c@d.com",
            proposal_type="product",
            template_id=tid,
            items=[],
        )

        await repo.create(data)
        repo.get_template_by_id.assert_awaited_once_with(tid)

    # ------ create_from_opportunity ------

    @pytest.mark.asyncio
    async def test_create_from_opportunity_found(self):
        from modules.crm.models.proposal import Proposal
        from modules.crm.schemas.proposal import ProposalCreateFromOpportunity

        db = _mock_db()
        repo = self._repo(db)

        opp = MagicMock()
        opp.id = _uid()
        opp.contact_name = "John"
        opp.contact_email = "j@e.com"
        opp.contact_phone = "123"
        opp.company_name = "JCorp"

        db.execute = AsyncMock(return_value=_scalar_one(opp))

        data = ProposalCreateFromOpportunity(
            opportunity_id=opp.id,
            title="From Opp",
            items=[],
        )

        with patch.object(Proposal, "calculate_totals", return_value=None):
            result = await repo.create_from_opportunity(data, created_by_id=_uid())
        # Should not be None since opp was found
        assert db.add.called

    @pytest.mark.asyncio
    async def test_create_from_opportunity_not_found(self):
        from modules.crm.schemas.proposal import ProposalCreateFromOpportunity

        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))

        data = ProposalCreateFromOpportunity(
            opportunity_id=_uid(),
            title="X",
            items=[],
        )
        result = await repo.create_from_opportunity(data)
        assert result is None

    # ------ get_by_id ------

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(proposal))
        result = await repo.get_by_id(_uid())
        assert result is proposal

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.get_by_id(_uid()) is None

    # ------ get_by_number ------

    @pytest.mark.asyncio
    async def test_get_by_number(self):
        db = _mock_db()
        repo = self._repo(db)
        p = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(p))
        assert await repo.get_by_number("PROP-123") is p

    @pytest.mark.asyncio
    async def test_get_by_number_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.get_by_number("NOPE") is None

    # ------ list ------

    @pytest.mark.asyncio
    async def test_list_no_filters(self):
        db = _mock_db()
        repo = self._repo(db)

        p1, p2 = MagicMock(), MagicMock()
        # First call: count, second call: list
        db.execute = AsyncMock(side_effect=[_scalar(2), _scalars_all([p1, p2])])

        proposals, total = await repo.list()
        assert total == 2
        assert len(proposals) == 2

    @pytest.mark.asyncio
    async def test_list_with_filters(self):
        from modules.crm.schemas.proposal import ProposalFilter

        db = _mock_db()
        repo = self._repo(db)

        db.execute = AsyncMock(side_effect=[_scalar(0), _scalars_all([])])

        filters = ProposalFilter(
            status="draft",
            proposal_type="service",
            opportunity_id=_uid(),
            created_by_id=_uid(),
            is_expired=False,
            min_value=100.0,
            max_value=5000.0,
            client_name="Acme",
            search="test",
            date_from=date.today() - timedelta(days=30),
            date_to=date.today(),
        )

        proposals, total = await repo.list(filters=filters, page=1, page_size=10)
        assert total == 0

    # ------ update ------

    @pytest.mark.asyncio
    async def test_update_success(self):
        from modules.crm.schemas.proposal import ProposalUpdate

        db = _mock_db()
        repo = self._repo(db)

        proposal = MagicMock()
        proposal.is_closed = False
        proposal.calculate_totals = MagicMock()
        repo.get_by_id = AsyncMock(return_value=proposal)

        data = ProposalUpdate(title="Updated Title")
        result = await repo.update(_uid(), data)
        assert result is proposal
        assert db.commit.await_count >= 1

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        from modules.crm.schemas.proposal import ProposalUpdate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        result = await repo.update(_uid(), ProposalUpdate(title="X"))
        assert result is None

    @pytest.mark.asyncio
    async def test_update_closed_proposal(self):
        from modules.crm.schemas.proposal import ProposalUpdate

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_closed = True
        repo.get_by_id = AsyncMock(return_value=proposal)
        result = await repo.update(_uid(), ProposalUpdate(title="X"))
        assert result is None

    # ------ add_item ------

    @pytest.mark.asyncio
    async def test_add_item_success(self):
        from modules.crm.schemas.proposal import ProposalItemCreate

        db = _mock_db()
        repo = self._repo(db)

        proposal = MagicMock()
        proposal.is_closed = False
        proposal.items = [MagicMock(), MagicMock()]
        proposal.calculate_totals = MagicMock()
        repo.get_by_id = AsyncMock(return_value=proposal)

        item_data = ProposalItemCreate(name="Item X", quantity=3, unit_price=50.0)
        result = await repo.add_item(_uid(), item_data)
        assert result is not None
        assert db.add.called

    @pytest.mark.asyncio
    async def test_add_item_proposal_not_found(self):
        from modules.crm.schemas.proposal import ProposalItemCreate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        result = await repo.add_item(_uid(), ProposalItemCreate(name="X", quantity=1, unit_price=1.0))
        assert result is None

    @pytest.mark.asyncio
    async def test_add_item_closed_proposal(self):
        from modules.crm.schemas.proposal import ProposalItemCreate

        db = _mock_db()
        repo = self._repo(db)
        p = MagicMock()
        p.is_closed = True
        repo.get_by_id = AsyncMock(return_value=p)
        result = await repo.add_item(_uid(), ProposalItemCreate(name="X", quantity=1, unit_price=1.0))
        assert result is None

    # ------ remove_item ------

    @pytest.mark.asyncio
    async def test_remove_item_success(self):
        db = _mock_db()
        repo = self._repo(db)

        proposal = MagicMock()
        proposal.is_closed = False
        proposal.calculate_totals = MagicMock()
        repo.get_by_id = AsyncMock(return_value=proposal)

        item_mock = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(item_mock))

        result = await repo.remove_item(_uid(), _uid())
        assert result is True
        db.delete.assert_awaited()

    @pytest.mark.asyncio
    async def test_remove_item_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_closed = False
        repo.get_by_id = AsyncMock(return_value=proposal)
        db.execute = AsyncMock(return_value=_scalar_one(None))

        assert await repo.remove_item(_uid(), _uid()) is False

    @pytest.mark.asyncio
    async def test_remove_item_proposal_closed(self):
        db = _mock_db()
        repo = self._repo(db)
        p = MagicMock()
        p.is_closed = True
        repo.get_by_id = AsyncMock(return_value=p)
        assert await repo.remove_item(_uid(), _uid()) is False

    @pytest.mark.asyncio
    async def test_remove_item_proposal_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.remove_item(_uid(), _uid()) is False

    # ------ update_status ------

    @pytest.mark.asyncio
    async def test_update_status_sent(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.status = ProposalStatus.APPROVED.value
        repo.get_by_id = AsyncMock(return_value=proposal)

        result = await repo.update_status(_uid(), ProposalStatus.SENT)
        assert result is proposal
        assert proposal.status == ProposalStatus.SENT.value
        assert proposal.sent_at is not None

    @pytest.mark.asyncio
    async def test_update_status_viewed(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.status = ProposalStatus.SENT.value
        repo.get_by_id = AsyncMock(return_value=proposal)

        result = await repo.update_status(_uid(), ProposalStatus.VIEWED)
        assert proposal.viewed_at is not None

    @pytest.mark.asyncio
    async def test_update_status_accepted(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.status = ProposalStatus.SENT.value
        repo.get_by_id = AsyncMock(return_value=proposal)

        result = await repo.update_status(_uid(), ProposalStatus.ACCEPTED)
        assert proposal.responded_at is not None

    @pytest.mark.asyncio
    async def test_update_status_rejected_with_notes(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.status = ProposalStatus.SENT.value
        repo.get_by_id = AsyncMock(return_value=proposal)

        result = await repo.update_status(_uid(), ProposalStatus.REJECTED, notes="Too expensive")
        assert proposal.rejection_reason == "Too expensive"

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.update_status(_uid(), ProposalStatus.SENT) is None

    # ------ submit_for_approval ------

    @pytest.mark.asyncio
    async def test_submit_for_approval_success(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_draft = True
        repo.get_by_id = AsyncMock(return_value=proposal)

        result = await repo.submit_for_approval(_uid())
        assert proposal.status == ProposalStatus.PENDING_APPROVAL.value

    @pytest.mark.asyncio
    async def test_submit_for_approval_not_draft(self):
        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_draft = False
        repo.get_by_id = AsyncMock(return_value=proposal)
        assert await repo.submit_for_approval(_uid()) is None

    @pytest.mark.asyncio
    async def test_submit_for_approval_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.submit_for_approval(_uid()) is None

    # ------ process_approval ------

    @pytest.mark.asyncio
    async def test_process_approval_approve(self):
        from modules.crm.models.proposal import ApprovalAction, ProposalStatus
        from modules.crm.schemas.proposal import ProposalApprovalRequest

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_pending = True
        repo.get_by_id = AsyncMock(return_value=proposal)

        uid = _uid()
        data = ProposalApprovalRequest(action=ApprovalAction.APPROVE)
        result = await repo.process_approval(_uid(), data, uid)
        assert proposal.status == ProposalStatus.APPROVED.value
        assert proposal.approved_by_id == uid

    @pytest.mark.asyncio
    async def test_process_approval_reject(self):
        from modules.crm.models.proposal import ApprovalAction, ProposalStatus
        from modules.crm.schemas.proposal import ProposalApprovalRequest

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_pending = True
        proposal.notes = "existing"
        repo.get_by_id = AsyncMock(return_value=proposal)

        data = ProposalApprovalRequest(action=ApprovalAction.REJECT, comments="Needs work")
        result = await repo.process_approval(_uid(), data, _uid())
        assert proposal.status == ProposalStatus.DRAFT.value
        assert "[REVISAO]" in proposal.notes

    @pytest.mark.asyncio
    async def test_process_approval_reject_no_comments(self):
        from modules.crm.models.proposal import ApprovalAction, ProposalStatus
        from modules.crm.schemas.proposal import ProposalApprovalRequest

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_pending = True
        proposal.notes = None
        repo.get_by_id = AsyncMock(return_value=proposal)

        data = ProposalApprovalRequest(action=ApprovalAction.REJECT, comments=None)
        result = await repo.process_approval(_uid(), data, _uid())
        assert proposal.status == ProposalStatus.DRAFT.value

    @pytest.mark.asyncio
    async def test_process_approval_request_changes(self):
        from modules.crm.models.proposal import ApprovalAction, ProposalStatus
        from modules.crm.schemas.proposal import ProposalApprovalRequest

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_pending = True
        repo.get_by_id = AsyncMock(return_value=proposal)

        data = ProposalApprovalRequest(action=ApprovalAction.REQUEST_CHANGES, comments="Fix price")
        result = await repo.process_approval(_uid(), data, _uid())
        assert proposal.status == ProposalStatus.PENDING_REVIEW.value

    @pytest.mark.asyncio
    async def test_process_approval_not_pending(self):
        from modules.crm.models.proposal import ApprovalAction
        from modules.crm.schemas.proposal import ProposalApprovalRequest

        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        proposal.is_pending = False
        repo.get_by_id = AsyncMock(return_value=proposal)

        data = ProposalApprovalRequest(action=ApprovalAction.APPROVE)
        assert await repo.process_approval(_uid(), data, _uid()) is None

    # ------ create_new_version ------

    @pytest.mark.asyncio
    async def test_create_new_version_success(self):
        db = _mock_db()
        repo = self._repo(db)

        original = MagicMock()
        original.id = _uid()
        original.number = "PROP-20260101-AAA"
        original.version = 2
        original.items = [MagicMock(), MagicMock()]
        # Give items proper attrs
        for it in original.items:
            it.code = "C"
            it.name = "N"
            it.description = "D"
            it.unit = "un"
            it.quantity = 1
            it.unit_price = 100
            it.discount_percent = 0
            it.total = 100
            it.sort_order = 0
            it.is_optional = False

        repo.get_by_id = AsyncMock(return_value=original)

        result = await repo.create_new_version(original.id, _uid())
        # proposal + 2 items = 3 adds
        assert db.add.call_count >= 3

    @pytest.mark.asyncio
    async def test_create_new_version_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.create_new_version(_uid()) is None

    # ------ delete ------

    @pytest.mark.asyncio
    async def test_delete_success(self):
        db = _mock_db()
        repo = self._repo(db)
        proposal = MagicMock()
        repo.get_by_id = AsyncMock(return_value=proposal)
        assert await repo.delete(_uid()) is True
        assert proposal.is_active is False

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.delete(_uid()) is False

    # ------ get_stats ------

    @pytest.mark.asyncio
    async def test_get_stats_empty(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([]))
        stats = await repo.get_stats()
        assert stats.total_proposals == 0
        assert stats.acceptance_rate == 0.0

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self):
        from modules.crm.models.proposal import ProposalStatus

        db = _mock_db()
        repo = self._repo(db)

        def _make_proposal(status, total, ptype="service", sent_at=None, responded_at=None):
            p = MagicMock()
            p.status = status
            p.total = total
            p.proposal_type = ptype
            p.sent_at = sent_at
            p.responded_at = responded_at
            return p

        now = datetime.utcnow()
        proposals = [
            _make_proposal(ProposalStatus.DRAFT.value, 100.0),
            _make_proposal(ProposalStatus.PENDING_APPROVAL.value, 200.0),
            _make_proposal(ProposalStatus.SENT.value, 300.0),
            _make_proposal(
                ProposalStatus.ACCEPTED.value,
                400.0,
                sent_at=now - timedelta(days=5),
                responded_at=now,
            ),
            _make_proposal(
                ProposalStatus.REJECTED.value,
                150.0,
                sent_at=now - timedelta(days=3),
                responded_at=now,
            ),
            _make_proposal(ProposalStatus.EXPIRED.value, 50.0),
            _make_proposal(ProposalStatus.VIEWED.value, 250.0),
        ]

        db.execute = AsyncMock(return_value=_scalars_all(proposals))
        stats = await repo.get_stats(created_by_id=_uid())
        assert stats.total_proposals == 7
        assert stats.draft_count == 1
        assert stats.pending_count == 1
        assert stats.sent_count == 2  # SENT + VIEWED
        assert stats.accepted_count == 1
        assert stats.rejected_count == 1
        assert stats.expired_count == 1
        assert stats.acceptance_rate == 50.0  # 1 accepted / 2 responded
        assert stats.avg_response_time_days == 4.0  # (5+3)/2

    # ------ Template methods ------

    @pytest.mark.asyncio
    async def test_create_template(self):
        from modules.crm.schemas.proposal import ProposalTemplateCreate

        db = _mock_db()
        repo = self._repo(db)

        # No existing defaults
        db.execute = AsyncMock(
            side_effect=[
                _scalars_all([]),  # first execute (unused select)
                _scalars_all([]),  # reset defaults
            ]
        )

        data = ProposalTemplateCreate(
            name="Tmpl 1",
            proposal_type="service",
            is_default=True,
        )
        result = await repo.create_template(data)
        assert db.add.called

    @pytest.mark.asyncio
    async def test_create_template_not_default(self):
        from modules.crm.schemas.proposal import ProposalTemplateCreate

        db = _mock_db()
        repo = self._repo(db)

        data = ProposalTemplateCreate(name="Tmpl 2", proposal_type="product", is_default=False)
        result = await repo.create_template(data)
        assert db.add.called

    @pytest.mark.asyncio
    async def test_get_template_by_id(self):
        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(tmpl))
        assert await repo.get_template_by_id(_uid()) is tmpl

    @pytest.mark.asyncio
    async def test_get_template_by_id_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.get_template_by_id(_uid()) is None

    @pytest.mark.asyncio
    async def test_list_templates(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([MagicMock(), MagicMock()]))
        result = await repo.list_templates()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_update_template_success(self):
        from modules.crm.schemas.proposal import ProposalTemplateUpdate

        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        repo.get_template_by_id = AsyncMock(return_value=tmpl)
        data = ProposalTemplateUpdate(name="New Name")
        result = await repo.update_template(_uid(), data)
        assert result is tmpl

    @pytest.mark.asyncio
    async def test_update_template_not_found(self):
        from modules.crm.schemas.proposal import ProposalTemplateUpdate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_template_by_id = AsyncMock(return_value=None)
        assert await repo.update_template(_uid(), ProposalTemplateUpdate(name="X")) is None

    @pytest.mark.asyncio
    async def test_update_template_with_proposal_type(self):
        from modules.crm.models.proposal import ProposalType
        from modules.crm.schemas.proposal import ProposalTemplateUpdate

        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        repo.get_template_by_id = AsyncMock(return_value=tmpl)
        data = ProposalTemplateUpdate(proposal_type=ProposalType.PROJECT)
        result = await repo.update_template(_uid(), data)
        assert result is tmpl

    @pytest.mark.asyncio
    async def test_delete_template_success(self):
        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        repo.get_template_by_id = AsyncMock(return_value=tmpl)
        assert await repo.delete_template(_uid()) is True
        assert tmpl.is_active is False

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_template_by_id = AsyncMock(return_value=None)
        assert await repo.delete_template(_uid()) is False

    # ------ _create_item helper ------

    def test_create_item_helper(self):
        from modules.crm.schemas.proposal import ProposalItemCreate

        repo = self._repo()
        data = ProposalItemCreate(name="Svc", quantity=2, unit_price=50.0, sort_order=5)
        item = repo._create_item("pid", data, 0)
        assert item.name == "Svc"
        assert item.sort_order == 5  # data.sort_order used
        assert item.total == 100.0

    def test_create_item_helper_no_sort_order(self):
        from modules.crm.schemas.proposal import ProposalItemCreate

        repo = self._repo()
        data = ProposalItemCreate(name="Svc", quantity=1, unit_price=10.0, sort_order=0)
        item = repo._create_item("pid", data, 7)
        # sort_order=0 is falsy, so should use the passed sort_order
        assert item.sort_order == 7

    # ------ _apply_filters (is_expired=True) ------

    @pytest.mark.asyncio
    async def test_list_with_expired_filter_true(self):
        from modules.crm.schemas.proposal import ProposalFilter

        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(side_effect=[_scalar(0), _scalars_all([])])
        filters = ProposalFilter(is_expired=True)
        proposals, total = await repo.list(filters=filters)
        assert total == 0


# ===================================================================
# ContractRepository tests
# ===================================================================


class TestContractRepository:
    """Tests for ContractRepository."""

    def _repo(self, db=None):
        from modules.crm.repositories.contract_repository import ContractRepository

        return ContractRepository(db or _mock_db())

    # ------ create ------

    @pytest.mark.asyncio
    async def test_create_contract(self):
        from modules.crm.models.contract import ContractStatus, ContractType
        from modules.crm.schemas.contract import ContractCreate

        db = _mock_db()
        repo = self._repo(db)

        # _get_next_contract_sequence
        repo._get_next_contract_sequence = AsyncMock(return_value=1)

        cid = _uid()
        data = ContractCreate(
            name="Contrato Vigilancia",
            client_id=cid,
            monthly_value=Decimal("10000"),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            contract_type=ContractType.RECURRING,
            adjustment_enabled=False,
        )

        result = await repo.create(data, created_by_id=_uid())
        assert db.add.called
        assert db.commit.await_count >= 1

    @pytest.mark.asyncio
    async def test_create_contract_with_adjustment(self):
        from modules.crm.models.contract import AdjustmentIndex, ContractType
        from modules.crm.schemas.contract import ContractCreate

        db = _mock_db()
        repo = self._repo(db)
        repo._get_next_contract_sequence = AsyncMock(return_value=2)

        data = ContractCreate(
            name="Contrato Reajuste",
            client_id=_uid(),
            monthly_value=Decimal("5000"),
            start_date=date(2026, 1, 1),
            adjustment_enabled=True,
            adjustment_index=AdjustmentIndex.IGPM,
        )
        result = await repo.create(data, created_by_id=_uid())
        assert db.add.called

    @pytest.mark.asyncio
    async def test_create_contract_total_calculated(self):
        from modules.crm.schemas.contract import ContractCreate

        db = _mock_db()
        repo = self._repo(db)
        repo._get_next_contract_sequence = AsyncMock(return_value=3)

        data = ContractCreate(
            name="Contrato Total Calc",
            client_id=_uid(),
            monthly_value=Decimal("1000"),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            total_value=None,
        )
        result = await repo.create(data, created_by_id=_uid())
        assert db.add.called

    # ------ get_by_id ------

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(contract))
        assert await repo.get_by_id(_uid()) is contract

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.get_by_id(_uid()) is None

    # ------ get_by_number ------

    @pytest.mark.asyncio
    async def test_get_by_number_found(self):
        db = _mock_db()
        repo = self._repo(db)
        c = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(c))
        assert await repo.get_by_number("CONT-2026-00001") is c

    @pytest.mark.asyncio
    async def test_get_by_number_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.get_by_number("NOPE") is None

    # ------ list ------

    @pytest.mark.asyncio
    async def test_list_no_filters(self):
        db = _mock_db()
        repo = self._repo(db)
        c1 = MagicMock()
        db.execute = AsyncMock(side_effect=[_scalar(1), _scalars_all([c1])])
        contracts, total = await repo.list()
        assert total == 1
        assert len(contracts) == 1

    @pytest.mark.asyncio
    async def test_list_with_all_filters(self):
        from modules.crm.models.contract import ContractStatus, ContractType
        from modules.crm.schemas.contract import ContractFilter

        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(side_effect=[_scalar(0), _scalars_all([])])

        filters = ContractFilter(
            status=ContractStatus.ACTIVE,
            contract_type=ContractType.RECURRING,
            client_id=_uid(),
            commercial_manager_id=_uid(),
            account_manager_id=_uid(),
            has_sla=True,
            min_value=Decimal("100"),
            max_value=Decimal("50000"),
            start_date_from=date(2026, 1, 1),
            start_date_to=date(2026, 12, 31),
            end_date_from=date(2026, 6, 1),
            end_date_to=date(2026, 12, 31),
            search="vigilancia",
        )
        contracts, total = await repo.list(filters=filters)
        assert total == 0

    # ------ update ------

    @pytest.mark.asyncio
    async def test_update_draft_contract(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        contract.calculate_next_adjustment_date = MagicMock(return_value=None)
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractUpdate(name="Updated", adjustment_enabled=True)
        result = await repo.update(_uid(), data)
        assert result is contract

    @pytest.mark.asyncio
    async def test_update_suspended_contract(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.SUSPENDED
        contract.calculate_next_adjustment_date = MagicMock(return_value=None)
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractUpdate(description="suspended update")
        result = await repo.update(_uid(), data)
        assert result is contract

    @pytest.mark.asyncio
    async def test_update_active_contract_limited_fields(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        contract.calculate_next_adjustment_date = MagicMock(return_value=None)
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractUpdate(description="new desc", name="should be ignored for active")
        result = await repo.update(_uid(), data)
        assert result is contract

    @pytest.mark.asyncio
    async def test_update_terminated_contract_returns_none(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.TERMINATED
        repo.get_by_id = AsyncMock(return_value=contract)

        result = await repo.update(_uid(), ContractUpdate(name="Updated Name"))
        assert result is None

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        from modules.crm.schemas.contract import ContractUpdate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.update(_uid(), ContractUpdate(name="Updated Name")) is None

    @pytest.mark.asyncio
    async def test_update_with_id_field(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        contract.calculate_next_adjustment_date = MagicMock(return_value=None)
        repo.get_by_id = AsyncMock(return_value=contract)

        uid = _uid()
        data = ContractUpdate(account_manager_id=uid)
        result = await repo.update(_uid(), data)
        assert result is contract

    # ------ update_status ------

    @pytest.mark.asyncio
    async def test_update_status_draft_to_pending(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        contract.signature_required = False
        repo.get_by_id = AsyncMock(return_value=contract)

        result = await repo.update_status(_uid(), ContractStatus.PENDING_SIGNATURE)
        assert result is contract
        assert contract.status == ContractStatus.PENDING_SIGNATURE

    @pytest.mark.asyncio
    async def test_update_status_pending_to_active_with_signature(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.PENDING_SIGNATURE
        contract.signature_required = True
        repo.get_by_id = AsyncMock(return_value=contract)

        result = await repo.update_status(_uid(), ContractStatus.ACTIVE)
        assert contract.signed_at is not None

    @pytest.mark.asyncio
    async def test_update_status_invalid_transition(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        repo.get_by_id = AsyncMock(return_value=contract)

        # DRAFT -> ACTIVE not valid (must go through PENDING_SIGNATURE)
        result = await repo.update_status(_uid(), ContractStatus.ACTIVE)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.update_status(_uid(), ContractStatus.ACTIVE) is None

    @pytest.mark.asyncio
    async def test_update_status_active_to_suspended(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        contract.signature_required = False
        repo.get_by_id = AsyncMock(return_value=contract)

        result = await repo.update_status(_uid(), ContractStatus.SUSPENDED)
        assert contract.status == ContractStatus.SUSPENDED

    @pytest.mark.asyncio
    async def test_update_status_suspended_to_active(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.SUSPENDED
        contract.signature_required = False
        repo.get_by_id = AsyncMock(return_value=contract)

        result = await repo.update_status(_uid(), ContractStatus.ACTIVE)
        assert contract.status == ContractStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_update_status_terminated_no_transitions(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.TERMINATED
        repo.get_by_id = AsyncMock(return_value=contract)

        result = await repo.update_status(_uid(), ContractStatus.ACTIVE)
        assert result is None

    # ------ delete ------

    @pytest.mark.asyncio
    async def test_delete_draft_success(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        repo.get_by_id = AsyncMock(return_value=contract)

        assert await repo.delete(_uid()) is True
        assert contract.is_active is False

    @pytest.mark.asyncio
    async def test_delete_active_fails(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        repo.get_by_id = AsyncMock(return_value=contract)

        assert await repo.delete(_uid()) is False

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.delete(_uid()) is False

    # ------ get_stats ------

    @pytest.mark.asyncio
    async def test_get_stats_empty(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([]))
        stats = await repo.get_stats()
        assert stats.total_contracts == 0
        assert stats.active_contracts == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self):
        from modules.crm.models.contract import ContractStatus, ContractType

        db = _mock_db()
        repo = self._repo(db)

        c1 = MagicMock()
        c1.status = ContractStatus.ACTIVE
        c1.contract_type = ContractType.RECURRING
        c1.monthly_value = Decimal("5000")
        c1.is_expiring_soon = True
        c1.needs_adjustment = False

        c2 = MagicMock()
        c2.status = ContractStatus.DRAFT
        c2.contract_type = ContractType.ONE_TIME
        c2.monthly_value = Decimal("3000")
        c2.is_expiring_soon = False
        c2.needs_adjustment = True

        db.execute = AsyncMock(return_value=_scalars_all([c1, c2]))
        stats = await repo.get_stats(client_id=_uid(), commercial_manager_id=_uid())
        assert stats.total_contracts == 2
        assert stats.active_contracts == 1
        assert stats.total_monthly_revenue == Decimal("5000")
        assert stats.expiring_soon == 1
        assert stats.needs_adjustment == 1

    # ------ add_item ------

    @pytest.mark.asyncio
    async def test_add_item_success(self):
        from modules.crm.models.contract import ContractStatus, ServiceType
        from modules.crm.schemas.contract import ContractItemCreate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        contract.id = uuid.uuid4()
        contract.monthly_value = Decimal("1000")
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractItemCreate(
            service_type=ServiceType.SECURITY,
            service_name="Vigilancia 24h",
            quantity=2,
            unit_price=Decimal("500"),
        )
        result = await repo.add_item(_uid(), data)
        assert result is not None
        assert db.add.called

    @pytest.mark.asyncio
    async def test_add_item_not_draft(self):
        from modules.crm.models.contract import ContractStatus, ServiceType
        from modules.crm.schemas.contract import ContractItemCreate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractItemCreate(
            service_type=ServiceType.SECURITY,
            service_name="Servico Teste",
            quantity=1,
            unit_price=Decimal("100"),
        )
        assert await repo.add_item(_uid(), data) is None

    @pytest.mark.asyncio
    async def test_add_item_contract_not_found(self):
        from modules.crm.models.contract import ServiceType
        from modules.crm.schemas.contract import ContractItemCreate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        data = ContractItemCreate(
            service_type=ServiceType.SECURITY,
            service_name="Servico Teste",
            quantity=1,
            unit_price=Decimal("100"),
        )
        assert await repo.add_item(_uid(), data) is None

    # ------ update_item ------

    @pytest.mark.asyncio
    async def test_update_item_success(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractItemUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        contract.monthly_value = Decimal("2000")
        repo.get_by_id = AsyncMock(return_value=contract)

        item = MagicMock()
        item.total_price = Decimal("500")
        item.quantity = 2
        item.unit_price = Decimal("250")
        db.execute = AsyncMock(return_value=_scalar_one(item))

        data = ContractItemUpdate(quantity=3)
        result = await repo.update_item(_uid(), _uid(), data)
        assert result is item

    @pytest.mark.asyncio
    async def test_update_item_not_found(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractItemUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        repo.get_by_id = AsyncMock(return_value=contract)
        db.execute = AsyncMock(return_value=_scalar_one(None))

        assert await repo.update_item(_uid(), _uid(), ContractItemUpdate(quantity=1)) is None

    @pytest.mark.asyncio
    async def test_update_item_not_draft(self):
        from modules.crm.models.contract import ContractStatus
        from modules.crm.schemas.contract import ContractItemUpdate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        repo.get_by_id = AsyncMock(return_value=contract)

        assert await repo.update_item(_uid(), _uid(), ContractItemUpdate(quantity=1)) is None

    # ------ remove_item ------

    @pytest.mark.asyncio
    async def test_remove_item_success(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        contract.monthly_value = Decimal("1000")
        repo.get_by_id = AsyncMock(return_value=contract)

        item = MagicMock()
        item.total_price = Decimal("500")
        db.execute = AsyncMock(return_value=_scalar_one(item))

        assert await repo.remove_item(_uid(), _uid()) is True
        assert item.is_active is False

    @pytest.mark.asyncio
    async def test_remove_item_not_found(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        repo.get_by_id = AsyncMock(return_value=contract)
        db.execute = AsyncMock(return_value=_scalar_one(None))

        assert await repo.remove_item(_uid(), _uid()) is False

    @pytest.mark.asyncio
    async def test_remove_item_not_draft(self):
        from modules.crm.models.contract import ContractStatus

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        repo.get_by_id = AsyncMock(return_value=contract)

        assert await repo.remove_item(_uid(), _uid()) is False

    @pytest.mark.asyncio
    async def test_remove_item_contract_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        assert await repo.remove_item(_uid(), _uid()) is False

    # ------ create_addendum ------

    @pytest.mark.asyncio
    async def test_create_addendum_success(self):
        from modules.crm.models.contract import AddendumType, ContractStatus
        from modules.crm.schemas.contract import ContractAddendumCreate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.ACTIVE
        contract.id = uuid.uuid4()
        contract.monthly_value = Decimal("5000")
        repo.get_by_id = AsyncMock(return_value=contract)
        repo._get_next_addendum_sequence = AsyncMock(return_value=1)

        data = ContractAddendumCreate(
            addendum_type=AddendumType.ADJUSTMENT,
            effective_date=date(2026, 7, 1),
            description="Reajuste anual do contrato de vigilancia",
            new_value=Decimal("5500"),
            adjustment_percent=Decimal("10"),
        )
        result = await repo.create_addendum(_uid(), data, _uid())
        assert result is not None
        assert db.add.called

    @pytest.mark.asyncio
    async def test_create_addendum_not_active(self):
        from modules.crm.models.contract import AddendumType, ContractStatus
        from modules.crm.schemas.contract import ContractAddendumCreate

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.status = ContractStatus.DRAFT
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractAddendumCreate(
            addendum_type=AddendumType.SCOPE_CHANGE,
            effective_date=date(2026, 7, 1),
            description="Alteracao de escopo do contrato de seguranca",
        )
        assert await repo.create_addendum(_uid(), data, _uid()) is None

    @pytest.mark.asyncio
    async def test_create_addendum_contract_not_found(self):
        from modules.crm.models.contract import AddendumType
        from modules.crm.schemas.contract import ContractAddendumCreate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)

        data = ContractAddendumCreate(
            addendum_type=AddendumType.OTHER,
            effective_date=date(2026, 7, 1),
            description="Aditivo generico para ajustes contratuais",
        )
        assert await repo.create_addendum(_uid(), data, _uid()) is None

    # ------ sign_addendum ------

    @pytest.mark.asyncio
    async def test_sign_addendum_adjustment(self):
        from modules.crm.models.contract import AddendumType

        db = _mock_db()
        repo = self._repo(db)

        contract = MagicMock()
        contract.calculate_next_adjustment_date = MagicMock(return_value=date(2027, 7, 1))

        addendum = MagicMock()
        addendum.signed = False
        addendum.addendum_type = AddendumType.ADJUSTMENT
        addendum.new_value = Decimal("6000")
        addendum.effective_date = date(2026, 7, 1)
        addendum.contract = contract

        db.execute = AsyncMock(return_value=_scalar_one(addendum))

        result = await repo.sign_addendum(_uid(), "sig-doc-123")
        assert addendum.signed is True
        assert contract.monthly_value == Decimal("6000")

    @pytest.mark.asyncio
    async def test_sign_addendum_already_signed(self):
        db = _mock_db()
        repo = self._repo(db)
        addendum = MagicMock()
        addendum.signed = True
        db.execute = AsyncMock(return_value=_scalar_one(addendum))
        assert await repo.sign_addendum(_uid(), "sig") is None

    @pytest.mark.asyncio
    async def test_sign_addendum_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.sign_addendum(_uid(), "sig") is None

    @pytest.mark.asyncio
    async def test_sign_addendum_non_adjustment(self):
        from modules.crm.models.contract import AddendumType

        db = _mock_db()
        repo = self._repo(db)

        contract = MagicMock()
        addendum = MagicMock()
        addendum.signed = False
        addendum.addendum_type = AddendumType.SCOPE_CHANGE
        addendum.new_value = None
        addendum.contract = contract

        db.execute = AsyncMock(return_value=_scalar_one(addendum))
        result = await repo.sign_addendum(_uid(), "sig-456")
        assert addendum.signed is True
        # contract.monthly_value should not have been touched
        # (no assertion needed, just verifying no error)

    # ------ list_addendums ------

    @pytest.mark.asyncio
    async def test_list_addendums(self):
        db = _mock_db()
        repo = self._repo(db)
        a1, a2 = MagicMock(), MagicMock()
        db.execute = AsyncMock(return_value=_scalars_all([a1, a2]))
        result = await repo.list_addendums(_uid())
        assert len(result) == 2

    # ------ create_template ------

    @pytest.mark.asyncio
    async def test_create_template(self):
        from modules.crm.models.contract import ServiceType
        from modules.crm.schemas.contract import ContractTemplateCreate

        db = _mock_db()
        repo = self._repo(db)

        data = ContractTemplateCreate(
            name="Template Seg",
            service_type=ServiceType.SECURITY,
            content_template="x" * 100,
        )
        result = await repo.create_template(data)
        assert db.add.called

    # ------ get_template_by_id ------

    @pytest.mark.asyncio
    async def test_get_template_by_id_found(self):
        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        db.execute = AsyncMock(return_value=_scalar_one(tmpl))
        assert await repo.get_template_by_id(_uid()) is tmpl

    @pytest.mark.asyncio
    async def test_get_template_by_id_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.get_template_by_id(_uid()) is None

    # ------ list_templates ------

    @pytest.mark.asyncio
    async def test_list_templates_no_filter(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([MagicMock()]))
        result = await repo.list_templates()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_templates_with_service_type(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([]))
        result = await repo.list_templates(service_type="security")
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_templates_approved_only(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([]))
        result = await repo.list_templates(approved_only=True)
        assert len(result) == 0

    # ------ update_template ------

    @pytest.mark.asyncio
    async def test_update_template_success(self):
        from modules.crm.schemas.contract import ContractTemplateUpdate

        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        tmpl.version = 1
        repo.get_template_by_id = AsyncMock(return_value=tmpl)

        data = ContractTemplateUpdate(name="New Name")
        result = await repo.update_template(_uid(), data)
        assert result is tmpl

    @pytest.mark.asyncio
    async def test_update_template_content_bumps_version(self):
        from modules.crm.schemas.contract import ContractTemplateUpdate

        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        tmpl.version = 1
        tmpl.approved_by_legal = True
        repo.get_template_by_id = AsyncMock(return_value=tmpl)

        data = ContractTemplateUpdate(content_template="y" * 100)
        result = await repo.update_template(_uid(), data)
        assert tmpl.version == 2
        assert tmpl.approved_by_legal is False

    @pytest.mark.asyncio
    async def test_update_template_not_found(self):
        from modules.crm.schemas.contract import ContractTemplateUpdate

        db = _mock_db()
        repo = self._repo(db)
        repo.get_template_by_id = AsyncMock(return_value=None)
        assert await repo.update_template(_uid(), ContractTemplateUpdate(name="Template Atualizado")) is None

    # ------ approve_template ------

    @pytest.mark.asyncio
    async def test_approve_template_success(self):
        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        repo.get_template_by_id = AsyncMock(return_value=tmpl)

        result = await repo.approve_template(_uid(), _uid())
        assert tmpl.approved_by_legal is True

    @pytest.mark.asyncio
    async def test_approve_template_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_template_by_id = AsyncMock(return_value=None)
        assert await repo.approve_template(_uid(), _uid()) is None

    # ------ delete_template ------

    @pytest.mark.asyncio
    async def test_delete_template_success(self):
        db = _mock_db()
        repo = self._repo(db)
        tmpl = MagicMock()
        repo.get_template_by_id = AsyncMock(return_value=tmpl)
        assert await repo.delete_template(_uid()) is True
        assert tmpl.is_active is False

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        repo.get_template_by_id = AsyncMock(return_value=None)
        assert await repo.delete_template(_uid()) is False

    # ------ create_sla_report ------

    @pytest.mark.asyncio
    async def test_create_sla_report_success(self):
        from modules.crm.schemas.contract import ContractSLAReportCreate, SLAIndicatorResult

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.has_sla = True
        contract.id = uuid.uuid4()
        repo.get_by_id = AsyncMock(return_value=contract)

        # No existing report
        db.execute = AsyncMock(return_value=_scalar_one(None))

        data = ContractSLAReportCreate(
            year=2026,
            month=3,
            indicators=[
                SLAIndicatorResult(name="Uptime", target=Decimal("99.5"), actual=Decimal("99.8"), achieved=True),
            ],
            overall_score=Decimal("100"),
            penalty_applied=False,
        )
        result = await repo.create_sla_report(_uid(), data, _uid())
        assert db.add.called

    @pytest.mark.asyncio
    async def test_create_sla_report_no_sla(self):
        from modules.crm.schemas.contract import ContractSLAReportCreate, SLAIndicatorResult

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.has_sla = False
        repo.get_by_id = AsyncMock(return_value=contract)

        data = ContractSLAReportCreate(
            year=2026,
            month=3,
            indicators=[SLAIndicatorResult(name="X", target=Decimal("99"), actual=Decimal("98"), achieved=False)],
            overall_score=Decimal("98"),
        )
        assert await repo.create_sla_report(_uid(), data, _uid()) is None

    @pytest.mark.asyncio
    async def test_create_sla_report_already_exists(self):
        from modules.crm.schemas.contract import ContractSLAReportCreate, SLAIndicatorResult

        db = _mock_db()
        repo = self._repo(db)
        contract = MagicMock()
        contract.has_sla = True
        repo.get_by_id = AsyncMock(return_value=contract)

        # Existing report found
        db.execute = AsyncMock(return_value=_scalar_one(MagicMock()))

        data = ContractSLAReportCreate(
            year=2026,
            month=3,
            indicators=[SLAIndicatorResult(name="X", target=Decimal("99"), actual=Decimal("99"), achieved=True)],
            overall_score=Decimal("100"),
        )
        assert await repo.create_sla_report(_uid(), data, _uid()) is None

    @pytest.mark.asyncio
    async def test_create_sla_report_contract_not_found(self):
        from modules.crm.schemas.contract import ContractSLAReportCreate, SLAIndicatorResult

        db = _mock_db()
        repo = self._repo(db)
        repo.get_by_id = AsyncMock(return_value=None)
        data = ContractSLAReportCreate(
            year=2026,
            month=3,
            indicators=[SLAIndicatorResult(name="X", target=Decimal("99"), actual=Decimal("99"), achieved=True)],
            overall_score=Decimal("100"),
        )
        assert await repo.create_sla_report(_uid(), data, _uid()) is None

    # ------ approve_sla_report ------

    @pytest.mark.asyncio
    async def test_approve_sla_report_approved(self):
        db = _mock_db()
        repo = self._repo(db)
        report = MagicMock()
        report.status = "draft"
        db.execute = AsyncMock(return_value=_scalar_one(report))

        result = await repo.approve_sla_report(_uid(), _uid(), disputed=False)
        assert report.status == "approved"

    @pytest.mark.asyncio
    async def test_approve_sla_report_disputed(self):
        db = _mock_db()
        repo = self._repo(db)
        report = MagicMock()
        report.status = "draft"
        db.execute = AsyncMock(return_value=_scalar_one(report))

        result = await repo.approve_sla_report(_uid(), _uid(), disputed=True)
        assert report.status == "disputed"

    @pytest.mark.asyncio
    async def test_approve_sla_report_not_draft(self):
        db = _mock_db()
        repo = self._repo(db)
        report = MagicMock()
        report.status = "approved"
        db.execute = AsyncMock(return_value=_scalar_one(report))
        assert await repo.approve_sla_report(_uid(), _uid()) is None

    @pytest.mark.asyncio
    async def test_approve_sla_report_not_found(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar_one(None))
        assert await repo.approve_sla_report(_uid(), _uid()) is None

    # ------ list_sla_reports ------

    @pytest.mark.asyncio
    async def test_list_sla_reports(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([MagicMock()]))
        result = await repo.list_sla_reports(_uid())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_sla_reports_with_year(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalars_all([]))
        result = await repo.list_sla_reports(_uid(), year=2026)
        assert len(result) == 0

    # ------ helpers ------

    @pytest.mark.asyncio
    async def test_get_next_contract_sequence(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar(5))
        seq = await repo._get_next_contract_sequence()
        assert seq == 6

    @pytest.mark.asyncio
    async def test_get_next_addendum_sequence(self):
        db = _mock_db()
        repo = self._repo(db)
        db.execute = AsyncMock(return_value=_scalar(3))
        seq = await repo._get_next_addendum_sequence(_uid())
        assert seq == 4

    def test_calculate_months(self):
        repo = self._repo()
        assert repo._calculate_months(date(2026, 1, 1), date(2026, 6, 30)) == 6
        assert repo._calculate_months(date(2026, 1, 1), date(2026, 1, 31)) == 1
        assert repo._calculate_months(date(2025, 12, 1), date(2026, 2, 28)) == 3

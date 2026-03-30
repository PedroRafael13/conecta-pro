"""
Testes E2E para o submodulo Proposals do CRM.

Padrao: chamada direta das funcoes de controller com mocks de db e user.
Este padrao e consistente com test_controllers_lead_opp_proposal_dashboard.py,
test_proposal_api.py e test_lead_api.py — todos os testes E2E funcionais do projeto.

Endpoints cobertos (happy path + erro para cada um que pode retornar erro):
    create_proposal               → sucesso / erro de validacao Pydantic
    create_proposal_from_opportunity → sucesso / 404 opportunity nao encontrada
    list_proposals                → sucesso com resultados / lista vazia / com filtros
    get_proposal_stats            → sucesso / com filtro por usuario
    get_proposal                  → sucesso / 404
    update_proposal               → sucesso / 404
    submit_proposal_for_approval  → sucesso / 400 nao em rascunho
    process_proposal_approval     → approve / reject / 400 nao encontrada
    send_proposal                 → sucesso / 404
    accept_proposal               → sucesso / 404
    reject_proposal               → sucesso com reason / sem reason / 404
    create_new_version            → sucesso / 404
    delete_proposal               → sucesso / 404
    add_proposal_item             → sucesso / 400 proposta nao editavel
    remove_proposal_item          → sucesso / 404
    create_template               → sucesso
    list_templates                → sucesso com resultados / lista vazia
    get_template                  → sucesso / 404
    update_template               → sucesso / 404
    delete_template               → sucesso / 404
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

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
from modules.crm.models.proposal import ApprovalAction, ProposalStatus, ProposalType
from modules.crm.schemas.proposal import (
    ProposalApprovalRequest,
    ProposalCreate,
    ProposalCreateFromOpportunity,
    ProposalItemCreate,
    ProposalStats,
    ProposalTemplateCreate,
    ProposalTemplateUpdate,
    ProposalUpdate,
)

# ---------------------------------------------------------------------------
# Constante de patcher
# ---------------------------------------------------------------------------

PATCHER = "modules.crm.controllers.proposal_controller.ProposalRepository"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime(2026, 3, 30, 12, 0, 0)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_user():
    """Mock do usuario autenticado."""
    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@erp.com.br"
    user.role = "admin"
    user.is_active = True
    return user


@pytest.fixture
def mock_db():
    """Mock da sessao de banco de dados."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


# ---------------------------------------------------------------------------
# Mock builders
# ---------------------------------------------------------------------------


def _make_proposal(**kwargs) -> MagicMock:
    """Retorna mock de Proposal com todos os atributos necessarios para model_validate."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.number = kwargs.get("number", "PRO-001")
    m.version = kwargs.get("version", 1)
    m.parent_id = kwargs.get("parent_id")
    m.opportunity_id = kwargs.get("opportunity_id", _uid())
    m.template_id = kwargs.get("template_id")
    m.client_name = kwargs.get("client_name", "Cliente Teste")
    m.client_email = kwargs.get("client_email", "cliente@teste.com.br")
    m.client_phone = kwargs.get("client_phone")
    m.client_company = kwargs.get("client_company", "Empresa Seguranca Ltda")
    m.client_document = kwargs.get("client_document")
    m.client_address = kwargs.get("client_address")
    m.title = kwargs.get("title", "Proposta de Seguranca Patrimonial")
    m.description = kwargs.get("description")
    m.proposal_type = kwargs.get("proposal_type", "service")
    m.terms_conditions = kwargs.get("terms_conditions")
    m.notes = kwargs.get("notes")
    m.subtotal = kwargs.get("subtotal", 10000.0)
    m.discount_type = kwargs.get("discount_type", "percentage")
    m.discount_value = kwargs.get("discount_value", 0.0)
    m.discount_reason = kwargs.get("discount_reason")
    m.discount_amount = kwargs.get("discount_amount", 0.0)
    m.taxes = kwargs.get("taxes", 0.0)
    m.total = kwargs.get("total", 10000.0)
    m.payment_terms = kwargs.get("payment_terms")
    m.payment_conditions = kwargs.get("payment_conditions")
    m.installments = kwargs.get("installments", 1)
    m.issue_date = kwargs.get("issue_date", date(2026, 3, 30))
    m.valid_until = kwargs.get("valid_until", date(2026, 6, 30))
    m.sent_at = kwargs.get("sent_at")
    m.viewed_at = kwargs.get("viewed_at")
    m.responded_at = kwargs.get("responded_at")
    m.status = kwargs.get("status", "draft")
    m.rejection_reason = kwargs.get("rejection_reason")
    m.created_by_id = kwargs.get("created_by_id", "test-user-id")
    m.approved_by_id = kwargs.get("approved_by_id")
    m.approved_at = kwargs.get("approved_at")
    m.is_draft = kwargs.get("is_draft", True)
    m.is_pending = kwargs.get("is_pending", False)
    m.is_approved = kwargs.get("is_approved", False)
    m.is_sent = kwargs.get("is_sent", False)
    m.is_closed = kwargs.get("is_closed", False)
    m.is_accepted = kwargs.get("is_accepted", False)
    m.is_rejected = kwargs.get("is_rejected", False)
    m.is_expired = kwargs.get("is_expired", False)
    m.days_until_expiry = kwargs.get("days_until_expiry", 92)
    m.item_count = kwargs.get("item_count", 0)
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    m.items = kwargs.get("items", [])
    return m


def _make_proposal_item(**kwargs) -> MagicMock:
    """Retorna mock de ProposalItem com todos os atributos necessarios para model_validate."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.proposal_id = kwargs.get("proposal_id", _uid())
    m.code = kwargs.get("code")
    m.name = kwargs.get("name", "Vigilancia 24h")
    m.description = kwargs.get("description")
    m.unit = kwargs.get("unit", "mes")
    m.quantity = kwargs.get("quantity", 1.0)
    m.unit_price = kwargs.get("unit_price", 5000.0)
    m.discount_percent = kwargs.get("discount_percent", 0.0)
    m.is_optional = kwargs.get("is_optional", False)
    m.total = kwargs.get("total", 5000.0)
    m.subtotal = kwargs.get("subtotal", 5000.0)
    m.discount_amount = kwargs.get("discount_amount", 0.0)
    m.sort_order = kwargs.get("sort_order", 0)
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    return m


def _make_template(**kwargs) -> MagicMock:
    """Retorna mock de ProposalTemplate com todos os atributos necessarios para model_validate."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.name = kwargs.get("name", "Template Padrao")
    m.description = kwargs.get("description")
    m.default_title = kwargs.get("default_title")
    m.default_description = kwargs.get("default_description")
    m.terms_conditions = kwargs.get("terms_conditions")
    m.payment_terms = kwargs.get("payment_terms")
    m.validity_days = kwargs.get("validity_days", 30)
    m.proposal_type = kwargs.get("proposal_type", "service")
    m.header_html = kwargs.get("header_html")
    m.footer_html = kwargs.get("footer_html")
    m.css_styles = kwargs.get("css_styles")
    m.is_default = kwargs.get("is_default", False)
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    return m


def _make_stats() -> ProposalStats:
    """Retorna instancia real de ProposalStats para testes de stats."""
    return ProposalStats(
        total_proposals=10,
        draft_count=3,
        pending_count=1,
        sent_count=2,
        accepted_count=2,
        rejected_count=1,
        expired_count=1,
        total_value=100000.0,
        accepted_value=20000.0,
        pending_value=15000.0,
        acceptance_rate=50.0,
        avg_proposal_value=10000.0,
        avg_response_time_days=15.0,
        by_status={"draft": 3, "sent": 2, "accepted": 2},
        by_type={"service": 8, "product": 2},
    )


# ===========================================================================
# 1. create_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_create_proposal_sucesso(mock_user, mock_db):
    """create_proposal → retorna ProposalDetailResponse com dados da proposta."""
    prop = _make_proposal()
    data = ProposalCreate(
        title="Proposta de Seguranca Patrimonial",
        client_name="Condominio Central",
        client_email="contato@condominio.com.br",
    )
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create = AsyncMock(return_value=prop)
        result = await create_proposal(data=data, current_user=mock_user, db=mock_db)
    assert result.number == "PRO-001"
    assert result.status == "draft"
    repo.create.assert_awaited_once_with(data, created_by_id=str(mock_user.id))


@pytest.mark.asyncio
async def test_create_proposal_com_opportunity_id(mock_user, mock_db):
    """create_proposal com opportunity_id → repassa corretamente ao repositorio."""
    opp_id = _uid()
    prop = _make_proposal(opportunity_id=opp_id)
    data = ProposalCreate(
        title="Proposta via Opportunity",
        client_name="Cliente",
        client_email="c@c.com.br",
        opportunity_id=opp_id,
    )
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create = AsyncMock(return_value=prop)
        result = await create_proposal(data=data, current_user=mock_user, db=mock_db)
    assert result.opportunity_id == opp_id


@pytest.mark.asyncio
async def test_create_proposal_email_invalido_levanta_validation_error():
    """ProposalCreate com email invalido levanta ValidationError do Pydantic."""
    import pydantic

    with pytest.raises((pydantic.ValidationError, ValueError)):
        ProposalCreate(
            title="T",
            client_name="C",
            client_email="email-invalido",
        )


# ===========================================================================
# 2. create_proposal_from_opportunity
# ===========================================================================


@pytest.mark.asyncio
async def test_create_from_opportunity_sucesso(mock_user, mock_db):
    """create_proposal_from_opportunity → 201 quando opportunity encontrada."""
    prop = _make_proposal(title="Proposta via Opportunity")
    data = ProposalCreateFromOpportunity(
        opportunity_id=_uid(),
        title="Proposta via Opportunity",
    )
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_from_opportunity = AsyncMock(return_value=prop)
        result = await create_proposal_from_opportunity(data=data, current_user=mock_user, db=mock_db)
    assert result.title == "Proposta via Opportunity"
    repo.create_from_opportunity.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_from_opportunity_404(mock_user, mock_db):
    """create_proposal_from_opportunity → HTTPException 404 quando opportunity nao encontrada."""
    data = ProposalCreateFromOpportunity(opportunity_id=_uid(), title="X")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_from_opportunity = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await create_proposal_from_opportunity(data=data, current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404
    assert "opportunity" in exc.value.detail.lower()


# ===========================================================================
# 3. list_proposals
# ===========================================================================


@pytest.mark.asyncio
async def test_list_proposals_com_resultados(mock_user, mock_db):
    """list_proposals → retorna lista paginada com total correto."""
    props = [_make_proposal(), _make_proposal(number="PRO-002")]
    with patch(PATCHER) as MockRepo:
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
    assert len(result.items) == 2
    assert result.page == 1
    assert result.total_pages == 1


@pytest.mark.asyncio
async def test_list_proposals_lista_vazia(mock_user, mock_db):
    """list_proposals → retorna lista vazia com total 0."""
    with patch(PATCHER) as MockRepo:
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
    assert result.items == []


@pytest.mark.asyncio
async def test_list_proposals_paginacao(mock_user, mock_db):
    """list_proposals → total_pages calculado corretamente."""
    props = [_make_proposal()]
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.list = AsyncMock(return_value=(props, 5))
        result = await list_proposals(
            current_user=mock_user,
            db=mock_db,
            page=1,
            page_size=2,
            status_filter=None,
            proposal_type=None,
            opportunity_id=None,
            is_expired=None,
            min_value=None,
            max_value=None,
            client_name=None,
            search=None,
        )
    assert result.total == 5
    assert result.total_pages == 3


@pytest.mark.asyncio
async def test_list_proposals_com_filtro_status(mock_user, mock_db):
    """list_proposals com status_filter=DRAFT → repassa filtro ao repositorio."""
    props = [_make_proposal(status="draft")]
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.list = AsyncMock(return_value=(props, 1))
        result = await list_proposals(
            current_user=mock_user,
            db=mock_db,
            page=1,
            page_size=20,
            status_filter=ProposalStatus.DRAFT,
            proposal_type=None,
            opportunity_id=None,
            is_expired=None,
            min_value=None,
            max_value=None,
            client_name=None,
            search=None,
        )
    assert result.total == 1
    repo.list.assert_awaited_once()


# ===========================================================================
# 4. get_proposal_stats
# ===========================================================================


@pytest.mark.asyncio
async def test_get_proposal_stats_sucesso(mock_user, mock_db):
    """get_proposal_stats → retorna ProposalStats do repositorio."""
    stats = _make_stats()
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_stats = AsyncMock(return_value=stats)
        result = await get_proposal_stats(current_user=mock_user, db=mock_db)
    assert result.total_proposals == 10
    assert result.acceptance_rate == 50.0
    assert result.draft_count == 3


@pytest.mark.asyncio
async def test_get_proposal_stats_com_filtro_usuario(mock_user, mock_db):
    """get_proposal_stats com created_by_id → repassa filtro ao repositorio."""
    stats = _make_stats()
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_stats = AsyncMock(return_value=stats)
        result = await get_proposal_stats(current_user=mock_user, db=mock_db, created_by_id="test-user-id")
    assert result == stats
    repo.get_stats.assert_awaited_once_with(created_by_id="test-user-id")


@pytest.mark.asyncio
async def test_get_proposal_stats_campos(mock_user, mock_db):
    """get_proposal_stats → todos os campos de ProposalStats presentes."""
    stats = _make_stats()
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_stats = AsyncMock(return_value=stats)
        result = await get_proposal_stats(current_user=mock_user, db=mock_db)
    assert isinstance(result.by_status, dict)
    assert isinstance(result.by_type, dict)
    assert result.accepted_value == 20000.0
    assert result.pending_value == 15000.0


# ===========================================================================
# 5. get_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_get_proposal_sucesso(mock_user, mock_db):
    """get_proposal → retorna proposta quando encontrada."""
    pid = _uid()
    prop = _make_proposal(id=pid)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_by_id = AsyncMock(return_value=prop)
        result = await get_proposal(proposal_id=pid, current_user=mock_user, db=mock_db)
    assert result.id == pid
    repo.get_by_id.assert_awaited_once_with(pid)


@pytest.mark.asyncio
async def test_get_proposal_404(mock_user, mock_db):
    """get_proposal → HTTPException 404 quando proposta nao encontrada."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_proposal(proposal_id="inexistente", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404
    assert "proposta" in exc.value.detail.lower()


# ===========================================================================
# 6. update_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_update_proposal_sucesso(mock_user, mock_db):
    """update_proposal → retorna proposta atualizada."""
    pid = _uid()
    prop = _make_proposal(id=pid, title="Proposta Atualizada")
    data = ProposalUpdate(title="Proposta Atualizada")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update = AsyncMock(return_value=prop)
        result = await update_proposal(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result.title == "Proposta Atualizada"
    repo.update.assert_awaited_once_with(pid, data)


@pytest.mark.asyncio
async def test_update_proposal_404(mock_user, mock_db):
    """update_proposal → HTTPException 404 quando proposta nao encontrada ou nao editavel."""
    data = ProposalUpdate(title="X")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_proposal(proposal_id="x", data=data, current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_proposal_campos_parciais(mock_user, mock_db):
    """update_proposal com apenas discount_value → repassa ao repositorio."""
    pid = _uid()
    prop = _make_proposal(id=pid, discount_value=500.0)
    data = ProposalUpdate(discount_value=500.0)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update = AsyncMock(return_value=prop)
        result = await update_proposal(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result.discount_value == 500.0


# ===========================================================================
# 7. submit_proposal_for_approval
# ===========================================================================


@pytest.mark.asyncio
async def test_submit_for_approval_sucesso(mock_user, mock_db):
    """submit_proposal_for_approval → retorna proposta em PENDING_APPROVAL."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="pending_approval", is_draft=False, is_pending=True)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.submit_for_approval = AsyncMock(return_value=prop)
        result = await submit_proposal_for_approval(proposal_id=pid, current_user=mock_user, db=mock_db)
    assert result.status == "pending_approval"
    repo.submit_for_approval.assert_awaited_once_with(pid, str(mock_user.id))


@pytest.mark.asyncio
async def test_submit_for_approval_400(mock_user, mock_db):
    """submit_proposal_for_approval → 400 quando proposta nao em rascunho."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.submit_for_approval = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await submit_proposal_for_approval(proposal_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 400


# ===========================================================================
# 8. process_proposal_approval
# ===========================================================================


@pytest.mark.asyncio
async def test_process_approval_approve(mock_user, mock_db):
    """process_proposal_approval com APPROVE → proposta aprovada."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="approved", is_approved=True, is_draft=False)
    data = ProposalApprovalRequest(action=ApprovalAction.APPROVE, comments="Aprovado")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.process_approval = AsyncMock(return_value=prop)
        result = await process_proposal_approval(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result.status == "approved"
    repo.process_approval.assert_awaited_once_with(pid, data, str(mock_user.id))


@pytest.mark.asyncio
async def test_process_approval_reject_action(mock_user, mock_db):
    """process_proposal_approval com REJECT → proposta rejeitada internamente."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="draft")
    data = ProposalApprovalRequest(action=ApprovalAction.REJECT, comments="Nao aprovado")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.process_approval = AsyncMock(return_value=prop)
        result = await process_proposal_approval(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result is not None


@pytest.mark.asyncio
async def test_process_approval_request_changes(mock_user, mock_db):
    """process_proposal_approval com REQUEST_CHANGES → retorna proposta."""
    pid = _uid()
    prop = _make_proposal(id=pid)
    data = ProposalApprovalRequest(action=ApprovalAction.REQUEST_CHANGES, comments="Revisar valores")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.process_approval = AsyncMock(return_value=prop)
        result = await process_proposal_approval(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result is not None


@pytest.mark.asyncio
async def test_process_approval_400(mock_user, mock_db):
    """process_proposal_approval → 400 quando proposta nao encontrada."""
    data = ProposalApprovalRequest(action=ApprovalAction.APPROVE)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.process_approval = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await process_proposal_approval(proposal_id="x", data=data, current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 400


# ===========================================================================
# 9. send_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_send_proposal_sucesso(mock_user, mock_db):
    """send_proposal → proposta marcada como SENT."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="sent", is_sent=True, is_draft=False)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=prop)
        result = await send_proposal(proposal_id=pid, current_user=mock_user, db=mock_db)
    assert result.status == "sent"
    # Verifica que update_status foi chamado com SENT
    call_args = repo.update_status.call_args
    assert call_args[0][1] == ProposalStatus.SENT


@pytest.mark.asyncio
async def test_send_proposal_404(mock_user, mock_db):
    """send_proposal → HTTPException 404 quando proposta nao encontrada."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await send_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# 10. accept_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_accept_proposal_sucesso(mock_user, mock_db):
    """accept_proposal → proposta marcada como ACCEPTED."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="accepted", is_accepted=True, is_closed=True, is_draft=False)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=prop)
        result = await accept_proposal(proposal_id=pid, current_user=mock_user, db=mock_db)
    assert result.status == "accepted"
    assert result.is_accepted is True
    call_args = repo.update_status.call_args
    assert call_args[0][1] == ProposalStatus.ACCEPTED


@pytest.mark.asyncio
async def test_accept_proposal_404(mock_user, mock_db):
    """accept_proposal → HTTPException 404 quando proposta nao encontrada."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await accept_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# 11. reject_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_reject_proposal_sucesso_com_reason(mock_user, mock_db):
    """reject_proposal com reason → proposta rejeitada, reason repassada ao repositorio."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="rejected", is_rejected=True, is_closed=True, is_draft=False)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=prop)
        result = await reject_proposal(
            proposal_id=pid, current_user=mock_user, db=mock_db, reason="Valor acima do orcamento"
        )
    assert result.status == "rejected"
    call_args = repo.update_status.call_args
    assert call_args[0][1] == ProposalStatus.REJECTED
    assert call_args[1].get("notes") == "Valor acima do orcamento"


@pytest.mark.asyncio
async def test_reject_proposal_sem_reason(mock_user, mock_db):
    """reject_proposal sem reason → funciona normalmente (reason e opcional)."""
    pid = _uid()
    prop = _make_proposal(id=pid, status="rejected", is_rejected=True, is_draft=False)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=prop)
        result = await reject_proposal(proposal_id=pid, current_user=mock_user, db=mock_db)
    assert result.status == "rejected"


@pytest.mark.asyncio
async def test_reject_proposal_404(mock_user, mock_db):
    """reject_proposal → HTTPException 404 quando proposta nao encontrada."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await reject_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# 12. create_new_version
# ===========================================================================


@pytest.mark.asyncio
async def test_create_new_version_sucesso(mock_user, mock_db):
    """create_new_version → retorna nova versao da proposta."""
    pid = _uid()
    prop = _make_proposal(id=_uid(), number="PRO-001", version=2)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_new_version = AsyncMock(return_value=prop)
        result = await create_new_version(proposal_id=pid, current_user=mock_user, db=mock_db)
    assert result.version == 2
    assert result.number == "PRO-001"
    repo.create_new_version.assert_awaited_once_with(pid, str(mock_user.id))


@pytest.mark.asyncio
async def test_create_new_version_404(mock_user, mock_db):
    """create_new_version → HTTPException 404 quando proposta nao encontrada."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_new_version = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await create_new_version(proposal_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# 13. delete_proposal
# ===========================================================================


@pytest.mark.asyncio
async def test_delete_proposal_sucesso(mock_user, mock_db):
    """delete_proposal → retorna None (204 No Content)."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.delete = AsyncMock(return_value=True)
        result = await delete_proposal(proposal_id="abc", current_user=mock_user, db=mock_db)
    assert result is None
    repo.delete.assert_awaited_once_with("abc")


@pytest.mark.asyncio
async def test_delete_proposal_404(mock_user, mock_db):
    """delete_proposal → HTTPException 404 quando proposta nao encontrada."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.delete = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await delete_proposal(proposal_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# 14. add_proposal_item
# ===========================================================================


@pytest.mark.asyncio
async def test_add_proposal_item_sucesso(mock_user, mock_db):
    """add_proposal_item → retorna item adicionado."""
    pid = _uid()
    item = _make_proposal_item(proposal_id=pid)
    data = ProposalItemCreate(name="Vigilancia 24h", unit_price=5000.0, quantity=1.0)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.add_item = AsyncMock(return_value=item)
        result = await add_proposal_item(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result.name == "Vigilancia 24h"
    assert result.unit_price == 5000.0
    repo.add_item.assert_awaited_once_with(pid, data)


@pytest.mark.asyncio
async def test_add_proposal_item_400(mock_user, mock_db):
    """add_proposal_item → 400 quando proposta nao encontrada ou nao editavel."""
    data = ProposalItemCreate(name="Item", unit_price=100.0)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.add_item = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await add_proposal_item(proposal_id="x", data=data, current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_add_proposal_item_campos_do_item(mock_user, mock_db):
    """add_proposal_item → resultado contem todos os campos de ProposalItemResponse."""
    pid = _uid()
    item = _make_proposal_item(proposal_id=pid, quantity=3.0, unit_price=2000.0, total=6000.0)
    data = ProposalItemCreate(name="CFTV", unit_price=2000.0, quantity=3.0)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.add_item = AsyncMock(return_value=item)
        result = await add_proposal_item(proposal_id=pid, data=data, current_user=mock_user, db=mock_db)
    assert result.quantity == 3.0
    assert result.total == 6000.0


# ===========================================================================
# 15. remove_proposal_item
# ===========================================================================


@pytest.mark.asyncio
async def test_remove_proposal_item_sucesso(mock_user, mock_db):
    """remove_proposal_item → retorna None (204 No Content)."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.remove_item = AsyncMock(return_value=True)
        result = await remove_proposal_item(proposal_id="pid", item_id="iid", current_user=mock_user, db=mock_db)
    assert result is None
    repo.remove_item.assert_awaited_once_with("pid", "iid")


@pytest.mark.asyncio
async def test_remove_proposal_item_404(mock_user, mock_db):
    """remove_proposal_item → HTTPException 404 quando item ou proposta nao encontrados."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.remove_item = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await remove_proposal_item(proposal_id="pid", item_id="iid", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# 16. create_template
# ===========================================================================


@pytest.mark.asyncio
async def test_create_template_sucesso(mock_user, mock_db):
    """create_template → retorna template criado."""
    tmpl = _make_template(name="Template Seguranca")
    data = ProposalTemplateCreate(
        name="Template Seguranca",
        proposal_type=ProposalType.SERVICE,
        validity_days=30,
    )
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_template = AsyncMock(return_value=tmpl)
        result = await create_template(data=data, current_user=mock_user, db=mock_db)
    assert result.name == "Template Seguranca"
    assert result.validity_days == 30
    repo.create_template.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_create_template_com_html(mock_user, mock_db):
    """create_template com header_html e footer_html → repassa ao repositorio."""
    tmpl = _make_template(header_html="<h1>Header</h1>", footer_html="<p>Footer</p>")
    data = ProposalTemplateCreate(
        name="Template HTML",
        proposal_type=ProposalType.SERVICE,
        header_html="<h1>Header</h1>",
        footer_html="<p>Footer</p>",
    )
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_template = AsyncMock(return_value=tmpl)
        result = await create_template(data=data, current_user=mock_user, db=mock_db)
    assert result.header_html == "<h1>Header</h1>"


# ===========================================================================
# 17. list_templates
# ===========================================================================


@pytest.mark.asyncio
async def test_list_templates_com_resultados(mock_user, mock_db):
    """list_templates → retorna lista de templates."""
    templates = [_make_template(), _make_template(name="Template 2")]
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.list_templates = AsyncMock(return_value=templates)
        result = await list_templates(current_user=mock_user, db=mock_db)
    assert len(result) == 2
    repo.list_templates.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_templates_vazia(mock_user, mock_db):
    """list_templates → retorna lista vazia quando nao ha templates."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.list_templates = AsyncMock(return_value=[])
        result = await list_templates(current_user=mock_user, db=mock_db)
    assert result == []


# ===========================================================================
# 18. get_template
# ===========================================================================


@pytest.mark.asyncio
async def test_get_template_sucesso(mock_user, mock_db):
    """get_template → retorna template quando encontrado."""
    tid = _uid()
    tmpl = _make_template(id=tid)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_template_by_id = AsyncMock(return_value=tmpl)
        result = await get_template(template_id=tid, current_user=mock_user, db=mock_db)
    assert result.id == tid
    assert result.is_active is True
    repo.get_template_by_id.assert_awaited_once_with(tid)


@pytest.mark.asyncio
async def test_get_template_404(mock_user, mock_db):
    """get_template → HTTPException 404 quando template nao encontrado."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_template_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_template(template_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404
    assert "template" in exc.value.detail.lower()


# ===========================================================================
# 19. update_template
# ===========================================================================


@pytest.mark.asyncio
async def test_update_template_sucesso(mock_user, mock_db):
    """update_template → retorna template atualizado."""
    tid = _uid()
    tmpl = _make_template(id=tid, name="Template Atualizado")
    data = ProposalTemplateUpdate(name="Template Atualizado")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_template = AsyncMock(return_value=tmpl)
        result = await update_template(template_id=tid, data=data, current_user=mock_user, db=mock_db)
    assert result.name == "Template Atualizado"
    repo.update_template.assert_awaited_once_with(tid, data)


@pytest.mark.asyncio
async def test_update_template_404(mock_user, mock_db):
    """update_template → HTTPException 404 quando template nao encontrado."""
    data = ProposalTemplateUpdate(name="X")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_template = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await update_template(template_id="x", data=data, current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_template_campos_parciais(mock_user, mock_db):
    """update_template com validity_days → repassa ao repositorio."""
    tid = _uid()
    tmpl = _make_template(id=tid, validity_days=60)
    data = ProposalTemplateUpdate(validity_days=60)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_template = AsyncMock(return_value=tmpl)
        result = await update_template(template_id=tid, data=data, current_user=mock_user, db=mock_db)
    assert result.validity_days == 60


# ===========================================================================
# 20. delete_template
# ===========================================================================


@pytest.mark.asyncio
async def test_delete_template_sucesso(mock_user, mock_db):
    """delete_template → retorna None (204 No Content)."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.delete_template = AsyncMock(return_value=True)
        result = await delete_template(template_id="abc", current_user=mock_user, db=mock_db)
    assert result is None
    repo.delete_template.assert_awaited_once_with("abc")


@pytest.mark.asyncio
async def test_delete_template_404(mock_user, mock_db):
    """delete_template → HTTPException 404 quando template nao encontrado."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.delete_template = AsyncMock(return_value=False)
        with pytest.raises(HTTPException) as exc:
            await delete_template(template_id="x", current_user=mock_user, db=mock_db)
    assert exc.value.status_code == 404


# ===========================================================================
# Testes adicionais de comportamento e contrato de dados
# ===========================================================================


@pytest.mark.asyncio
async def test_create_proposal_loga_email_do_usuario(mock_user, mock_db):
    """create_proposal → chama repo.create com created_by_id do usuario atual."""
    prop = _make_proposal()
    data = ProposalCreate(title="T", client_name="C", client_email="c@c.com.br")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create = AsyncMock(return_value=prop)
        await create_proposal(data=data, current_user=mock_user, db=mock_db)
    repo.create.assert_awaited_once_with(data, created_by_id="test-user-id")


@pytest.mark.asyncio
async def test_create_from_opportunity_passa_created_by_id(mock_user, mock_db):
    """create_proposal_from_opportunity → repassa created_by_id ao repositorio."""
    prop = _make_proposal()
    data = ProposalCreateFromOpportunity(opportunity_id=_uid(), title="T")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_from_opportunity = AsyncMock(return_value=prop)
        await create_proposal_from_opportunity(data=data, current_user=mock_user, db=mock_db)
    call_kwargs = repo.create_from_opportunity.call_args[1]
    assert call_kwargs.get("created_by_id") == "test-user-id"


@pytest.mark.asyncio
async def test_submit_proposal_passa_user_id(mock_user, mock_db):
    """submit_proposal_for_approval → repassa user_id ao repositorio."""
    prop = _make_proposal(status="pending_approval")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.submit_for_approval = AsyncMock(return_value=prop)
        await submit_proposal_for_approval(proposal_id="pid", current_user=mock_user, db=mock_db)
    repo.submit_for_approval.assert_awaited_once_with("pid", "test-user-id")


@pytest.mark.asyncio
async def test_list_proposals_response_tem_campos_de_paginacao(mock_user, mock_db):
    """list_proposals → resposta ProposalListResponse contem todos os campos de paginacao."""
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.list = AsyncMock(return_value=([], 0))
        result = await list_proposals(
            current_user=mock_user,
            db=mock_db,
            page=2,
            page_size=10,
            status_filter=None,
            proposal_type=None,
            opportunity_id=None,
            is_expired=None,
            min_value=None,
            max_value=None,
            client_name=None,
            search=None,
        )
    assert result.page == 2
    assert result.page_size == 10
    assert hasattr(result, "total")
    assert hasattr(result, "total_pages")
    assert hasattr(result, "items")


@pytest.mark.asyncio
async def test_reject_proposal_passes_notes_to_update_status(mock_user, mock_db):
    """reject_proposal → repassa reason como notes para update_status."""
    prop = _make_proposal(status="rejected")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=prop)
        await reject_proposal(proposal_id="pid", current_user=mock_user, db=mock_db, reason="Too expensive")
    repo.update_status.assert_awaited_once_with("pid", ProposalStatus.REJECTED, notes="Too expensive")


@pytest.mark.asyncio
async def test_send_proposal_passes_user_id_to_update_status(mock_user, mock_db):
    """send_proposal → repassa user_id como kwarg para update_status."""
    prop = _make_proposal(status="sent")
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.update_status = AsyncMock(return_value=prop)
        await send_proposal(proposal_id="pid", current_user=mock_user, db=mock_db)
    repo.update_status.assert_awaited_once_with("pid", ProposalStatus.SENT, user_id="test-user-id")


@pytest.mark.asyncio
async def test_create_new_version_passes_user_id(mock_user, mock_db):
    """create_new_version → repassa user_id ao repositorio."""
    prop = _make_proposal(version=3)
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.create_new_version = AsyncMock(return_value=prop)
        await create_new_version(proposal_id="pid", current_user=mock_user, db=mock_db)
    repo.create_new_version.assert_awaited_once_with("pid", "test-user-id")


@pytest.mark.asyncio
async def test_list_proposals_total_pages_arredondamento(mock_user, mock_db):
    """list_proposals → total_pages usa ceil (arredondamento para cima)."""
    props = [_make_proposal()]
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.list = AsyncMock(return_value=(props, 7))
        result = await list_proposals(
            current_user=mock_user,
            db=mock_db,
            page=1,
            page_size=3,
            status_filter=None,
            proposal_type=None,
            opportunity_id=None,
            is_expired=None,
            min_value=None,
            max_value=None,
            client_name=None,
            search=None,
        )
    # 7 itens / 3 por pagina = 2.33 → 3 paginas
    assert result.total_pages == 3


@pytest.mark.asyncio
async def test_get_proposal_stats_valores_numericos(mock_user, mock_db):
    """get_proposal_stats → valores numericos sao do tipo correto."""
    stats = _make_stats()
    with patch(PATCHER) as MockRepo:
        repo = MockRepo.return_value
        repo.get_stats = AsyncMock(return_value=stats)
        result = await get_proposal_stats(current_user=mock_user, db=mock_db)
    assert isinstance(result.total_value, float)
    assert isinstance(result.avg_proposal_value, float)
    assert isinstance(result.avg_response_time_days, float)
    assert result.avg_proposal_value == 10000.0

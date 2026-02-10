"""Testes para Proposal model."""

from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest

from modules.crm.models.proposal import (
    ApprovalAction,
    DiscountType,
    Proposal,
    ProposalApproval,
    ProposalItem,
    ProposalStatus,
    ProposalTemplate,
    ProposalType,
)
from tests.factories import ProposalFactory, ProposalItemFactory, ProposalTemplateFactory


class TestProposalModel:
    """Testes para o modelo Proposal."""

    def test_create_proposal_basic(self):
        """Testa criacao basica de proposal."""
        proposal = Proposal(
            id=str(uuid4()),
            number="PROP-20241230-000001",
            version=1,
            title="Proposta Teste",
            client_name="Cliente",
            client_email="cliente@test.com",
            proposal_type=ProposalType.SERVICE.value,
            status=ProposalStatus.DRAFT.value,
            subtotal=10000.0,
            total=10000.0,
            issue_date=date.today(),
        )

        assert proposal.title == "Proposta Teste"
        assert proposal.client_email == "cliente@test.com"
        assert proposal.status == "draft"
        assert proposal.proposal_type == "service"

    def test_proposal_with_all_fields(self):
        """Testa proposal com todos os campos."""
        proposal = ProposalFactory.build(
            title="Proposta Completa",
            client_name="Cliente Completo",
            client_email="completo@test.com",
            client_phone="11999999999",
            client_company="Empresa",
            description="Descricao da proposta",
            proposal_type="project",
            status="draft",
            subtotal=50000.0,
            total=50000.0,
            notes="Notas importantes",
        )

        assert proposal.title == "Proposta Completa"
        assert proposal.client_company == "Empresa"
        assert proposal.description == "Descricao da proposta"
        assert proposal.proposal_type == "project"

    def test_proposal_default_values(self):
        """Testa valores padrao."""
        proposal = ProposalFactory.build()

        assert proposal.is_active is True
        assert proposal.created_at is not None
        assert proposal.updated_at is not None
        assert proposal.version == 1


class TestProposalProperties:
    """Testes para propriedades calculadas do Proposal."""

    def test_is_draft_true(self):
        """Testa is_draft quando em rascunho."""
        proposal = ProposalFactory.build(status="draft")
        assert proposal.is_draft is True

    def test_is_draft_false(self):
        """Testa is_draft para outros status."""
        proposal = ProposalFactory.build(status="approved")
        assert proposal.is_draft is False

    def test_is_pending_true(self):
        """Testa is_pending para status pendentes."""
        pending_statuses = [
            ProposalStatus.DRAFT.value,
            ProposalStatus.DRAFT.value,
        ]

        for status in pending_statuses:
            proposal = ProposalFactory.build(status=status)
            assert proposal.is_pending is True, f"Status {status} should be pending"

    def test_is_pending_false(self):
        """Testa is_pending para outros status."""
        proposal = ProposalFactory.build(status="draft")
        assert proposal.is_pending is False

    def test_is_approved_true(self):
        """Testa is_approved quando aprovada."""
        proposal = ProposalFactory.build(status="approved")
        assert proposal.is_approved is True

    def test_is_approved_false(self):
        """Testa is_approved para outros status."""
        proposal = ProposalFactory.build(status="draft")
        assert proposal.is_approved is False

    def test_is_sent_true(self):
        """Testa is_sent quando enviada."""
        proposal = ProposalFactory.build(status="sent")
        assert proposal.is_sent is True

    def test_is_sent_false(self):
        """Testa is_sent para outros status."""
        proposal = ProposalFactory.build(status="draft")
        assert proposal.is_sent is False

    def test_is_closed_true_for_final_statuses(self):
        """Testa is_closed para status finais."""
        closed_statuses = [
            ProposalStatus.DRAFT.value,
            ProposalStatus.DRAFT.value,
            ProposalStatus.DRAFT.value,
        ]

        for status in closed_statuses:
            proposal = ProposalFactory.build(status=status)
            assert proposal.is_closed is True, f"Status {status} should be closed"

    def test_is_closed_false(self):
        """Testa is_closed para status abertos."""
        proposal = ProposalFactory.build(status="draft")
        assert proposal.is_closed is False

    def test_is_accepted_true(self):
        """Testa is_accepted quando aceita."""
        proposal = ProposalFactory.build_accepted()
        assert proposal.is_accepted is True

    def test_is_accepted_false(self):
        """Testa is_accepted para outros status."""
        proposal = ProposalFactory.build(status="rejected")
        assert proposal.is_accepted is False

    def test_is_expired_true(self):
        """Testa is_expired quando expirada."""
        past_date = date.today() - timedelta(days=5)
        proposal = ProposalFactory.build(
            status="sent",
            valid_until=past_date,
        )
        assert proposal.is_expired is True

    def test_is_expired_false_future(self):
        """Testa is_expired com data futura."""
        future_date = date.today() + timedelta(days=30)
        proposal = ProposalFactory.build(
            status="sent",
            valid_until=future_date,
        )
        assert proposal.is_expired is False

    def test_is_expired_false_closed(self):
        """Testa is_expired para proposal fechada."""
        past_date = date.today() - timedelta(days=5)
        proposal = ProposalFactory.build(
            status="accepted",
            valid_until=past_date,
        )
        # Nao esta expirada pois ja foi aceita
        assert proposal.is_expired is False

    def test_days_until_expiry_positive(self):
        """Testa dias ate expirar com data futura."""
        future_date = date.today() + timedelta(days=15)
        proposal = ProposalFactory.build(valid_until=future_date)

        assert proposal.days_until_expiry == 15

    def test_days_until_expiry_negative(self):
        """Testa dias ate expirar com data passada."""
        past_date = date.today() - timedelta(days=5)
        proposal = ProposalFactory.build(valid_until=past_date)

        assert proposal.days_until_expiry == -5

    def test_days_until_expiry_none(self):
        """Testa dias ate expirar sem data."""
        proposal = ProposalFactory.build(valid_until=None)
        assert proposal.days_until_expiry is None

    def test_discount_amount_percentage(self):
        """Testa calculo de desconto percentual."""
        proposal = ProposalFactory.build(
            subtotal=10000.0,
            discount_type="percentage",
            discount_value=10.0,
        )

        # 10% de 10000 = 1000
        assert proposal.discount_amount == 1000.0

    def test_discount_amount_fixed(self):
        """Testa calculo de desconto fixo."""
        proposal = ProposalFactory.build(
            subtotal=10000.0,
            discount_type="fixed",
            discount_value=500.0,
        )

        # Desconto fixo de 500
        assert proposal.discount_amount == 500.0

    def test_discount_amount_none(self):
        """Testa calculo sem desconto."""
        proposal = ProposalFactory.build(
            subtotal=10000.0,
            discount_type=None,
            discount_value=0.0,
        )

        assert proposal.discount_amount == 0.0

    def test_item_count_empty(self):
        """Testa contagem de itens vazia."""
        proposal = ProposalFactory.build()
        # items e uma lista vazia por padrao (relacionamento nao carregado)
        assert proposal.item_count == 0


class TestProposalStatus:
    """Testes para ProposalStatus enum."""

    def test_all_statuses_exist(self):
        """Testa que todos os status existem."""
        expected = [
            "draft",
            "pending_review",
            "pending_approval",
            "approved",
            "sent",
            "viewed",
            "accepted",
            "rejected",
            "expired",
            "cancelled",
        ]

        for status in expected:
            assert hasattr(ProposalStatus, status.upper())
            assert ProposalStatus[status.upper()].value == status

    def test_status_values(self):
        """Testa valores dos status."""
        assert ProposalStatus.DRAFT.value == "draft"
        assert ProposalStatus.DRAFT.value == "pending_review"
        assert ProposalStatus.DRAFT.value == "pending_approval"
        assert ProposalStatus.DRAFT.value == "approved"
        assert ProposalStatus.DRAFT.value == "sent"
        assert ProposalStatus.DRAFT.value == "viewed"
        assert ProposalStatus.DRAFT.value == "accepted"
        assert ProposalStatus.DRAFT.value == "rejected"
        assert ProposalStatus.DRAFT.value == "expired"
        assert ProposalStatus.DRAFT.value == "cancelled"


class TestProposalType:
    """Testes para ProposalType enum."""

    def test_all_types_exist(self):
        """Testa que todos os tipos existem."""
        expected = ["product", "service", "project", "subscription", "mixed"]

        for ptype in expected:
            assert hasattr(ProposalType, ptype.upper())
            assert ProposalType[ptype.upper()].value == ptype

    def test_type_values(self):
        """Testa valores dos tipos."""
        assert ProposalType.PRODUCT.value == "product"
        assert ProposalType.SERVICE.value == "service"
        assert ProposalType.PROJECT.value == "project"
        assert ProposalType.SUBSCRIPTION.value == "subscription"
        assert ProposalType.MIXED.value == "mixed"


class TestDiscountType:
    """Testes para DiscountType enum."""

    def test_discount_types_exist(self):
        """Testa que os tipos de desconto existem."""
        expected = ["percentage", "fixed"]

        for dtype in expected:
            assert hasattr(DiscountType, dtype.upper())
            assert DiscountType[dtype.upper()].value == dtype


class TestApprovalAction:
    """Testes para ApprovalAction enum."""

    def test_approval_actions_exist(self):
        """Testa que as acoes de aprovacao existem."""
        expected = ["approve", "reject", "request_changes"]

        for action in expected:
            assert hasattr(ApprovalAction, action.upper())
            assert ApprovalAction[action.upper()].value == action


class TestProposalItem:
    """Testes para ProposalItem model."""

    def test_create_item_basic(self):
        """Testa criacao basica de item."""
        item = ProposalItemFactory.build(
            name="Servico A",
            quantity=2.0,
            unit_price=500.0,
            discount_percent=0.0,
        )

        assert item.name == "Servico A"
        assert item.quantity == 2.0
        assert item.unit_price == 500.0
        assert item.subtotal == 1000.0
        assert item.total == 1000.0

    def test_create_item_with_discount(self):
        """Testa criacao de item com desconto."""
        item = ProposalItemFactory.build(
            name="Produto B",
            quantity=1.0,
            unit_price=1000.0,
            discount_percent=10.0,
        )

        assert item.subtotal == 1000.0
        assert item.discount_amount == 100.0
        assert item.total == 900.0

    def test_create_optional_item(self):
        """Testa criacao de item opcional."""
        item = ProposalItemFactory.build(is_optional=True)
        assert item.is_optional is True


class TestProposalTemplate:
    """Testes para ProposalTemplate model."""

    def test_create_template_basic(self):
        """Testa criacao basica de template."""
        template = ProposalTemplateFactory.build(
            name="Template Padrao",
            validity_days=30,
            proposal_type="service",
        )

        assert template.name == "Template Padrao"
        assert template.validity_days == 30
        assert template.proposal_type == "service"

    def test_create_default_template(self):
        """Testa criacao de template padrao."""
        template = ProposalTemplateFactory.build_default()
        assert template.is_default is True


class TestProposalFactory:
    """Testes para ProposalFactory."""

    def test_build_creates_proposal(self):
        """Testa que build cria proposal valida."""
        proposal = ProposalFactory.build()

        assert proposal.id is not None
        assert proposal.title is not None
        assert proposal.client_email is not None
        assert proposal.number is not None

    def test_build_approved(self):
        """Testa criacao de proposal aprovada."""
        proposal = ProposalFactory.build_approved()

        assert proposal.status == "approved"
        assert proposal.approved_at is not None
        assert proposal.approved_by_id is not None

    def test_build_sent(self):
        """Testa criacao de proposal enviada."""
        proposal = ProposalFactory.build_sent()

        assert proposal.status == "sent"
        assert proposal.sent_at is not None

    def test_build_accepted(self):
        """Testa criacao de proposal aceita."""
        proposal = ProposalFactory.build_accepted()

        assert proposal.status == "accepted"
        assert proposal.responded_at is not None
        assert proposal.is_accepted is True

    def test_build_rejected(self):
        """Testa criacao de proposal rejeitada."""
        proposal = ProposalFactory.build_rejected()

        assert proposal.status == "rejected"
        assert proposal.rejection_reason is not None

    def test_build_expired(self):
        """Testa criacao de proposal expirada."""
        proposal = ProposalFactory.build_expired()

        assert proposal.status == "expired"
        assert proposal.valid_until < date.today()

    def test_build_high_value(self):
        """Testa criacao de proposal de alto valor."""
        proposal = ProposalFactory.build_high_value()

        assert proposal.total == 100000.0
        assert proposal.proposal_type == "project"

    def test_build_batch(self):
        """Testa criacao de lote de proposals."""
        proposals = ProposalFactory.build_batch(5)

        assert len(proposals) == 5
        for proposal in proposals:
            assert proposal.id is not None

    def test_build_with_custom_values(self):
        """Testa criacao com valores customizados."""
        proposal = ProposalFactory.build(
            title="Custom Proposal",
            client_email="custom@test.com",
            total=99999.0,
        )

        assert proposal.title == "Custom Proposal"
        assert proposal.client_email == "custom@test.com"
        assert proposal.total == 99999.0


class TestProposalItemFactory:
    """Testes para ProposalItemFactory."""

    def test_build_creates_item(self):
        """Testa que build cria item valido."""
        item = ProposalItemFactory.build()

        assert item.id is not None
        assert item.name is not None
        assert item.code is not None

    def test_build_batch(self):
        """Testa criacao de lote de items."""
        proposal_id = str(uuid4())
        items = ProposalItemFactory.build_batch(3, proposal_id=proposal_id)

        assert len(items) == 3
        for i, item in enumerate(items):
            assert item.proposal_id == proposal_id
            assert item.sort_order == i


class TestProposalTemplateFactory:
    """Testes para ProposalTemplateFactory."""

    def test_build_creates_template(self):
        """Testa que build cria template valido."""
        template = ProposalTemplateFactory.build()

        assert template.id is not None
        assert template.name is not None

    def test_build_default(self):
        """Testa criacao de template padrao."""
        template = ProposalTemplateFactory.build_default()
        assert template.is_default is True

    def test_build_batch(self):
        """Testa criacao de lote de templates."""
        templates = ProposalTemplateFactory.build_batch(3)

        assert len(templates) == 3
        for template in templates:
            assert template.id is not None

"""
Testes do Model Proposal.

Testes para Proposal, ProposalItem, ProposalTemplate e ProposalApproval.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

from modules.crm.models.proposal import (
    Proposal,
    ProposalItem,
    ProposalTemplate,
    ProposalApproval,
    ProposalStatus,
    ProposalType,
    DiscountType,
    ApprovalAction,
)


class TestProposal:
    """Testes do modelo Proposal."""

    def test_criar_proposal(self):
        """Testa criacao de proposal."""
        proposal = Proposal(
            id="prop-001",
            number="PRO-2026-00001",
            client_name="Empresa Teste",
            client_email="contato@empresa.com.br",
            title="Proposta de Servicos",
        )

        assert proposal.id == "prop-001"
        assert proposal.number == "PRO-2026-00001"
        assert proposal.client_name == "Empresa Teste"
        assert proposal.status == ProposalStatus.DRAFT.value
        assert proposal.version == 1

    def test_proposal_status_checks(self):
        """Testa verificacoes de status."""
        proposal = Proposal(
            id="prop-002",
            number="PRO-2026-00002",
            client_name="Cliente",
            client_email="cliente@test.com",
            title="Proposta",
        )

        # Draft
        proposal.status = ProposalStatus.DRAFT.value
        assert proposal.is_draft is True
        assert proposal.is_pending is False
        assert proposal.is_closed is False

        # Pending approval
        proposal.status = ProposalStatus.PENDING_APPROVAL.value
        assert proposal.is_draft is False
        assert proposal.is_pending is True

        # Approved
        proposal.status = ProposalStatus.APPROVED.value
        assert proposal.is_approved is True
        assert proposal.is_closed is False

        # Sent
        proposal.status = ProposalStatus.SENT.value
        assert proposal.is_sent is True

        # Accepted (closed)
        proposal.status = ProposalStatus.ACCEPTED.value
        assert proposal.is_accepted is True
        assert proposal.is_closed is True

    def test_proposal_expiration(self):
        """Testa verificacao de expiracao."""
        proposal = Proposal(
            id="prop-003",
            number="PRO-2026-00003",
            client_name="Cliente",
            client_email="cliente@test.com",
            title="Proposta",
        )

        # Validade futura
        proposal.valid_until = date.today() + timedelta(days=10)
        assert proposal.is_expired is False
        assert proposal.days_until_expiry == 10

        # Validade passada
        proposal.valid_until = date.today() - timedelta(days=5)
        assert proposal.is_expired is True
        assert proposal.days_until_expiry == -5

    def test_proposal_discount_calculation(self):
        """Testa calculo de desconto."""
        proposal = Proposal(
            id="prop-004",
            number="PRO-2026-00004",
            client_name="Cliente",
            client_email="cliente@test.com",
            title="Proposta",
            subtotal=Decimal("1000.00"),
        )

        # Desconto percentual
        proposal.discount_type = DiscountType.PERCENTAGE.value
        proposal.discount_value = Decimal("10.00")
        assert proposal.discount_amount == Decimal("100.00")

        # Desconto fixo
        proposal.discount_type = DiscountType.FIXED.value
        proposal.discount_value = Decimal("150.00")
        assert proposal.discount_amount == Decimal("150.00")

    def test_proposal_calculate_totals(self):
        """Testa recalculo de totais."""
        proposal = Proposal(
            id="prop-005",
            number="PRO-2026-00005",
            client_name="Cliente",
            client_email="cliente@test.com",
            title="Proposta",
        )

        # Adicionar items mock
        item1 = ProposalItem(
            id="item-001",
            proposal_id="prop-005",
            name="Servico 1",
            quantity=Decimal("2"),
            unit_price=Decimal("500.00"),
            total=Decimal("1000.00"),
        )
        item2 = ProposalItem(
            id="item-002",
            proposal_id="prop-005",
            name="Servico 2",
            quantity=Decimal("1"),
            unit_price=Decimal("300.00"),
            total=Decimal("300.00"),
        )

        proposal.items = [item1, item2]
        proposal.discount_type = DiscountType.PERCENTAGE.value
        proposal.discount_value = Decimal("10.00")
        proposal.taxes = Decimal("130.00")

        proposal.calculate_totals()

        assert proposal.subtotal == Decimal("1300.00")
        # Total = subtotal - desconto + impostos
        # 1300 - 130 + 130 = 1300
        assert proposal.total == Decimal("1300.00")


class TestProposalItem:
    """Testes do modelo ProposalItem."""

    def test_criar_item(self):
        """Testa criacao de item."""
        item = ProposalItem(
            id="item-001",
            proposal_id="prop-001",
            name="Servico de Limpeza",
            quantity=Decimal("10"),
            unit_price=Decimal("150.00"),
            unit="hr",
        )

        assert item.name == "Servico de Limpeza"
        assert item.unit == "hr"
        assert item.is_optional is False

    def test_item_subtotal(self):
        """Testa calculo de subtotal."""
        item = ProposalItem(
            id="item-002",
            proposal_id="prop-001",
            name="Servico",
            quantity=Decimal("5"),
            unit_price=Decimal("200.00"),
        )

        assert item.subtotal == Decimal("1000.00")

    def test_item_discount_amount(self):
        """Testa calculo de desconto do item."""
        item = ProposalItem(
            id="item-003",
            proposal_id="prop-001",
            name="Servico",
            quantity=Decimal("10"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("15.00"),
        )

        # Subtotal = 10 * 100 = 1000
        # Desconto = 1000 * 0.15 = 150
        assert item.subtotal == Decimal("1000.00")
        assert item.discount_amount == Decimal("150.00")

    def test_item_calculate_total(self):
        """Testa calculo de total do item."""
        item = ProposalItem(
            id="item-004",
            proposal_id="prop-001",
            name="Servico",
            quantity=Decimal("4"),
            unit_price=Decimal("250.00"),
            discount_percent=Decimal("10.00"),
        )

        item.calculate_total()

        # Subtotal = 4 * 250 = 1000
        # Desconto = 1000 * 0.10 = 100
        # Total = 1000 - 100 = 900
        assert item.total == Decimal("900.00")


class TestProposalTemplate:
    """Testes do modelo ProposalTemplate."""

    def test_criar_template(self):
        """Testa criacao de template."""
        template = ProposalTemplate(
            id="tpl-001",
            name="Template Padrao",
            description="Template para servicos gerais",
            validity_days=30,
        )

        assert template.name == "Template Padrao"
        assert template.validity_days == 30
        assert template.is_default is False
        assert template.is_active is True


class TestProposalApproval:
    """Testes do modelo ProposalApproval."""

    def test_criar_approval(self):
        """Testa criacao de registro de aprovacao."""
        approval = ProposalApproval(
            id="apr-001",
            proposal_id="prop-001",
            user_id="user-001",
            action=ApprovalAction.APPROVE.value,
            comments="Aprovado conforme politica",
        )

        assert approval.action == ApprovalAction.APPROVE.value
        assert approval.comments == "Aprovado conforme politica"

    def test_approval_actions(self):
        """Testa diferentes acoes de aprovacao."""
        # Aprovar
        approval_ok = ProposalApproval(
            id="apr-002",
            proposal_id="prop-001",
            action=ApprovalAction.APPROVE.value,
        )
        assert approval_ok.action == "approve"

        # Rejeitar
        approval_reject = ProposalApproval(
            id="apr-003",
            proposal_id="prop-001",
            action=ApprovalAction.REJECT.value,
            comments="Margem abaixo do minimo",
        )
        assert approval_reject.action == "reject"

        # Solicitar mudancas
        approval_changes = ProposalApproval(
            id="apr-004",
            proposal_id="prop-001",
            action=ApprovalAction.REQUEST_CHANGES.value,
            comments="Revisar itens 3 e 5",
        )
        assert approval_changes.action == "request_changes"


class TestProposalEnums:
    """Testes dos enums de Proposal."""

    def test_proposal_status_values(self):
        """Testa valores dos status."""
        assert ProposalStatus.DRAFT.value == "draft"
        assert ProposalStatus.PENDING_APPROVAL.value == "pending_approval"
        assert ProposalStatus.APPROVED.value == "approved"
        assert ProposalStatus.SENT.value == "sent"
        assert ProposalStatus.ACCEPTED.value == "accepted"
        assert ProposalStatus.REJECTED.value == "rejected"
        assert ProposalStatus.EXPIRED.value == "expired"
        assert ProposalStatus.CANCELLED.value == "cancelled"

    def test_proposal_type_values(self):
        """Testa valores dos tipos."""
        assert ProposalType.PRODUCT.value == "product"
        assert ProposalType.SERVICE.value == "service"
        assert ProposalType.PROJECT.value == "project"
        assert ProposalType.SUBSCRIPTION.value == "subscription"
        assert ProposalType.MIXED.value == "mixed"

    def test_discount_type_values(self):
        """Testa valores dos tipos de desconto."""
        assert DiscountType.PERCENTAGE.value == "percentage"
        assert DiscountType.FIXED.value == "fixed"

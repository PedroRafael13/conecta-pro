"""
Testes do ProposalService.

Testes para workflow de aprovacao, precificacao e validacoes.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from modules.crm.models.proposal import (
    ApprovalAction,
    ProposalStatus,
    ProposalType,
)
from modules.crm.services.proposal_service import ProposalService


class TestProposalService:
    """Testes do servico de propostas."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service."""
        return ProposalService()

    def test_generate_proposal_number(self, service):
        """Testa geracao de numero de proposta."""
        # Servico
        number = service.generate_proposal_number(ProposalType.SERVICE, 1)
        assert number == f"PRO-{date.today().year}-00001"

        # Produto
        number = service.generate_proposal_number(ProposalType.PRODUCT, 42)
        assert number == f"PRP-{date.today().year}-00042"

        # Misto
        number = service.generate_proposal_number(ProposalType.MIXED, 100)
        assert number == f"PRM-{date.today().year}-00100"

    def test_calculate_validity_date_default(self, service):
        """Testa data de validade padrao."""
        validity = service.calculate_validity_date()

        expected = date.today() + timedelta(days=30)
        assert validity == expected

    def test_calculate_validity_date_custom(self, service):
        """Testa data de validade customizada."""
        validity = service.calculate_validity_date(days=15)

        expected = date.today() + timedelta(days=15)
        assert validity == expected

    def test_calculate_proposal_pricing(self, service):
        """Testa calculo de precificacao."""
        result = service.calculate_proposal_pricing(
            base_salary=Decimal("2000.00"),
            headcount=5,
            contract_months=12,
            service_type="limpeza",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        assert result.base_cost > 0
        assert result.total_contract > result.total_cost
        assert result.margin_percent > 0

    def test_can_apply_discount_vendedor(self, service):
        """Testa limite de desconto para vendedor."""
        # Desconto dentro do limite (5%)
        allowed, msg = service.can_apply_discount(Decimal("3.00"), "vendedor")
        assert allowed is True
        assert "aprovado" in msg.lower()

        # Desconto acima do limite
        allowed, msg = service.can_apply_discount(Decimal("10.00"), "vendedor")
        assert allowed is False
        assert "aprovacao" in msg.lower()

    def test_can_apply_discount_gerente(self, service):
        """Testa limite de desconto para gerente."""
        # Desconto dentro do limite (15%)
        allowed, msg = service.can_apply_discount(Decimal("12.00"), "gerente")
        assert allowed is True

        # Desconto acima do limite
        allowed, msg = service.can_apply_discount(Decimal("20.00"), "gerente")
        assert allowed is False

    def test_can_apply_discount_diretor(self, service):
        """Testa limite de desconto para diretor."""
        # Desconto dentro do limite (25%)
        allowed, msg = service.can_apply_discount(Decimal("25.00"), "diretor")
        assert allowed is True

        # Desconto acima do limite
        allowed, msg = service.can_apply_discount(Decimal("30.00"), "diretor")
        assert allowed is False

    def test_can_apply_discount_admin(self, service):
        """Testa limite de desconto para admin."""
        # Admin pode aplicar qualquer desconto
        allowed, msg = service.can_apply_discount(Decimal("50.00"), "admin")
        assert allowed is True

    def test_can_transition_status_valid(self, service):
        """Testa transicoes de status validas."""
        # Draft -> Pending Approval
        valid, msg = service.can_transition_status(
            ProposalStatus.DRAFT,
            ProposalStatus.PENDING_APPROVAL,
        )
        assert valid is True

        # Pending -> Approved
        valid, msg = service.can_transition_status(
            ProposalStatus.PENDING_APPROVAL,
            ProposalStatus.APPROVED,
        )
        assert valid is True

        # Approved -> Sent
        valid, msg = service.can_transition_status(
            ProposalStatus.APPROVED,
            ProposalStatus.SENT,
        )
        assert valid is True

        # Sent -> Accepted
        valid, msg = service.can_transition_status(
            ProposalStatus.SENT,
            ProposalStatus.ACCEPTED,
        )
        assert valid is True

    def test_can_transition_status_invalid(self, service):
        """Testa transicoes de status invalidas."""
        # Draft -> Sent (pula aprovacao)
        valid, msg = service.can_transition_status(
            ProposalStatus.DRAFT,
            ProposalStatus.SENT,
        )
        assert valid is False
        assert "nao permitida" in msg.lower()

        # Accepted -> Draft (estado final)
        valid, msg = service.can_transition_status(
            ProposalStatus.ACCEPTED,
            ProposalStatus.DRAFT,
        )
        assert valid is False

    def test_process_approval_approve(self, service):
        """Testa aprovacao de proposta."""
        new_status, msg = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.APPROVE,
            "gerente",
        )

        assert new_status == ProposalStatus.APPROVED
        assert "aprovada" in msg.lower()

    def test_process_approval_reject(self, service):
        """Testa rejeicao de proposta."""
        new_status, msg = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.REJECT,
            "diretor",
        )

        assert new_status == ProposalStatus.REJECTED
        assert "rejeitada" in msg.lower()

    def test_process_approval_request_changes(self, service):
        """Testa solicitacao de mudancas."""
        new_status, msg = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.REQUEST_CHANGES,
            "gerente",
        )

        assert new_status == ProposalStatus.DRAFT
        assert "ajustes" in msg.lower()

    def test_process_approval_wrong_status(self, service):
        """Testa aprovacao em status errado."""
        new_status, msg = service.process_approval(
            ProposalStatus.DRAFT,  # Nao esta pendente
            ApprovalAction.APPROVE,
            "gerente",
        )

        assert new_status == ProposalStatus.DRAFT
        assert "pendente" in msg.lower()

    def test_process_approval_insufficient_permission(self, service):
        """Testa aprovacao sem permissao."""
        new_status, msg = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.APPROVE,
            "vendedor",  # Nao pode aprovar
        )

        assert new_status == ProposalStatus.PENDING_APPROVAL
        assert "permissao" in msg.lower()

    def test_calculate_items_totals(self, service):
        """Testa calculo de totais dos itens."""
        items = [
            {"quantity": 5, "unit_price": 100, "discount_percent": 0},
            {"quantity": 10, "unit_price": 50, "discount_percent": 10},
            {"quantity": 2, "unit_price": 200, "discount_percent": 5},
        ]

        subtotal, discount, total = service.calculate_items_totals(items)

        # Item 1: 5 * 100 = 500, desconto 0 = 500
        # Item 2: 10 * 50 = 500, desconto 50 = 450
        # Item 3: 2 * 200 = 400, desconto 20 = 380
        # Subtotal = 500 + 500 + 400 = 1400
        # Desconto = 0 + 50 + 20 = 70
        # Total = 1400 - 70 = 1330

        assert subtotal == Decimal("1400.00")
        assert discount == Decimal("70.00")
        assert total == Decimal("1330.00")

    def test_check_expiration_not_expired(self, service):
        """Testa proposta nao expirada."""
        valid_until = date.today() + timedelta(days=10)
        expired, days = service.check_expiration(valid_until)

        assert expired is False
        assert days == 10

    def test_check_expiration_expired(self, service):
        """Testa proposta expirada."""
        valid_until = date.today() - timedelta(days=5)
        expired, days = service.check_expiration(valid_until)

        assert expired is True
        assert days == -5

    def test_check_expiration_today(self, service):
        """Testa proposta expirando hoje."""
        valid_until = date.today()
        expired, days = service.check_expiration(valid_until)

        assert expired is False
        assert days == 0

    def test_generate_version(self, service):
        """Testa geracao de versao."""
        assert service.generate_version(1) == 2
        assert service.generate_version(5) == 6
        assert service.generate_version(10) == 11

    def test_format_currency(self, service):
        """Testa formatacao de moeda."""
        # Valor simples
        assert service.format_currency(Decimal("100.00")) == "R$ 100,00"

        # Valor com milhares
        assert service.format_currency(Decimal("1234.56")) == "R$ 1.234,56"

        # Valor grande
        assert service.format_currency(Decimal("1234567.89")) == "R$ 1.234.567,89"

    def test_calculate_commission(self, service):
        """Testa calculo de comissao."""
        # 3% sobre 100000
        commission = service.calculate_commission(
            Decimal("100000.00"),
            Decimal("3.00"),
        )
        assert commission == Decimal("3000.00")

        # 5% sobre 50000
        commission = service.calculate_commission(
            Decimal("50000.00"),
            Decimal("5.00"),
        )
        assert commission == Decimal("2500.00")


class TestProposalServiceIntegration:
    """Testes de integracao do ProposalService."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service."""
        return ProposalService()

    def test_full_workflow(self, service):
        """Testa workflow completo de proposta."""
        # 1. Criar proposta (simula numero)
        number = service.generate_proposal_number(ProposalType.SERVICE, 1)
        assert "PRO" in number

        # 2. Calcular validade
        validity = service.calculate_validity_date(days=30)
        assert validity > date.today()

        # 3. Calcular preco
        pricing = service.calculate_proposal_pricing(
            base_salary=Decimal("2500.00"),
            headcount=10,
            contract_months=12,
            margin_target=Decimal("15.00"),
        )
        assert pricing.total_contract > 0

        # 4. Tentar aplicar desconto (vendedor)
        allowed, _ = service.can_apply_discount(Decimal("8.00"), "vendedor")
        assert allowed is False  # Precisa aprovacao

        # 5. Aprovar (gerente)
        new_status, _ = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.APPROVE,
            "gerente",
        )
        assert new_status == ProposalStatus.APPROVED

        # 6. Verificar expiracao
        expired, days = service.check_expiration(validity)
        assert expired is False
        assert days == 30

        # 7. Calcular comissao (3%)
        commission = service.calculate_commission(
            pricing.total_contract,
            Decimal("3.00"),
        )
        assert commission > 0

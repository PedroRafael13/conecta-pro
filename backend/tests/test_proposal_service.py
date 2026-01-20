"""
Testes do ProposalService.

Testa gerenciamento de propostas comerciais, workflow
de aprovacao, calculo de valores e validacoes.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from modules.crm.models.proposal import ApprovalAction, ProposalStatus, ProposalType
from modules.crm.services.proposal_service import ProposalService


class TestProposalServiceBasic:
    """Testes basicos do ProposalService."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_instance_creation(self, service: ProposalService) -> None:
        """Testa criacao de instancia."""
        assert service is not None
        assert service.pricing_engine is not None

    def test_generate_proposal_number_service(self, service: ProposalService) -> None:
        """Testa geracao de numero para servico."""
        number = service.generate_proposal_number(ProposalType.SERVICE, 1)

        assert number.startswith("PRO-")
        assert str(date.today().year) in number
        assert number.endswith("-00001")

    def test_generate_proposal_number_product(self, service: ProposalService) -> None:
        """Testa geracao de numero para produto."""
        number = service.generate_proposal_number(ProposalType.PRODUCT, 123)

        assert number.startswith("PRP-")
        assert number.endswith("-00123")

    def test_generate_proposal_number_mixed(self, service: ProposalService) -> None:
        """Testa geracao de numero para misto."""
        number = service.generate_proposal_number(ProposalType.MIXED, 99999)

        assert number.startswith("PRM-")
        assert number.endswith("-99999")

    def test_calculate_validity_date_default(self, service: ProposalService) -> None:
        """Testa calculo de validade padrao."""
        validity = service.calculate_validity_date()
        expected = date.today() + timedelta(days=30)

        assert validity == expected

    def test_calculate_validity_date_custom(self, service: ProposalService) -> None:
        """Testa calculo de validade customizada."""
        validity = service.calculate_validity_date(days=60)
        expected = date.today() + timedelta(days=60)

        assert validity == expected


class TestProposalServicePricing:
    """Testes de precificacao."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_calculate_proposal_pricing(self, service: ProposalService) -> None:
        """Testa calculo de precificacao."""
        result = service.calculate_proposal_pricing(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        assert result is not None
        assert result.total_contract > Decimal("0")
        assert result.margin_percent > Decimal("0")

    def test_calculate_proposal_pricing_with_benefits(self, service: ProposalService) -> None:
        """Testa precificacao com beneficios."""
        result = service.calculate_proposal_pricing(
            base_salary=Decimal("2500.00"),
            headcount=5,
            contract_months=24,
            benefits_value=Decimal("800.00"),
        )

        # Benefits = valor * headcount * meses = 800 * 5 * 24 = 96000
        assert result.benefits_cost == Decimal("96000.00")

    def test_calculate_proposal_pricing_with_equipment(self, service: ProposalService) -> None:
        """Testa precificacao com equipamentos."""
        result = service.calculate_proposal_pricing(
            base_salary=Decimal("1500.00"),
            headcount=3,
            contract_months=12,
            equipment_value=Decimal("5000.00"),
        )

        assert result.equipment_cost == Decimal("5000.00")


class TestProposalServiceDiscount:
    """Testes de validacao de desconto."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_discount_allowed_vendedor(self, service: ProposalService) -> None:
        """Testa desconto permitido para vendedor."""
        allowed, message = service.can_apply_discount(Decimal("5.00"), "vendedor")

        assert allowed is True
        assert "aprovado automaticamente" in message

    def test_discount_denied_vendedor_high(self, service: ProposalService) -> None:
        """Testa desconto negado para vendedor (muito alto)."""
        allowed, message = service.can_apply_discount(Decimal("10.00"), "vendedor")

        assert allowed is False
        assert "gerente" in message

    def test_discount_allowed_gerente(self, service: ProposalService) -> None:
        """Testa desconto permitido para gerente."""
        allowed, _ = service.can_apply_discount(Decimal("15.00"), "gerente")

        assert allowed is True

    def test_discount_requires_diretor(self, service: ProposalService) -> None:
        """Testa desconto que requer diretor."""
        allowed, message = service.can_apply_discount(Decimal("20.00"), "gerente")

        assert allowed is False
        assert "diretor" in message

    def test_discount_allowed_admin(self, service: ProposalService) -> None:
        """Testa que admin pode aplicar qualquer desconto."""
        allowed, _ = service.can_apply_discount(Decimal("50.00"), "admin")

        assert allowed is True

    def test_discount_exceeds_max(self, service: ProposalService) -> None:
        """Testa desconto que excede limite maximo."""
        allowed, msg = service.can_apply_discount(Decimal("150.00"), "admin")

        # Admin pode dar ate 100%, 150% nao existe
        assert allowed is False
        assert "limite maximo" in msg


class TestProposalServiceStatusTransition:
    """Testes de transicao de status."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_draft_to_pending_allowed(self, service: ProposalService) -> None:
        """Testa transicao DRAFT -> PENDING_APPROVAL."""
        valid, _ = service.can_transition_status(
            ProposalStatus.DRAFT,
            ProposalStatus.PENDING_APPROVAL,
        )

        assert valid is True

    def test_draft_to_cancelled_allowed(self, service: ProposalService) -> None:
        """Testa transicao DRAFT -> CANCELLED."""
        valid, _ = service.can_transition_status(
            ProposalStatus.DRAFT,
            ProposalStatus.CANCELLED,
        )

        assert valid is True

    def test_draft_to_sent_denied(self, service: ProposalService) -> None:
        """Testa transicao DRAFT -> SENT (nao permitida)."""
        valid, message = service.can_transition_status(
            ProposalStatus.DRAFT,
            ProposalStatus.SENT,
        )

        assert valid is False
        assert "nao permitida" in message

    def test_pending_to_approved_allowed(self, service: ProposalService) -> None:
        """Testa transicao PENDING_APPROVAL -> APPROVED."""
        valid, _ = service.can_transition_status(
            ProposalStatus.PENDING_APPROVAL,
            ProposalStatus.APPROVED,
        )

        assert valid is True

    def test_approved_to_sent_allowed(self, service: ProposalService) -> None:
        """Testa transicao APPROVED -> SENT."""
        valid, _ = service.can_transition_status(
            ProposalStatus.APPROVED,
            ProposalStatus.SENT,
        )

        assert valid is True

    def test_sent_to_accepted_allowed(self, service: ProposalService) -> None:
        """Testa transicao SENT -> ACCEPTED."""
        valid, _ = service.can_transition_status(
            ProposalStatus.SENT,
            ProposalStatus.ACCEPTED,
        )

        assert valid is True

    def test_accepted_is_final(self, service: ProposalService) -> None:
        """Testa que ACCEPTED e estado final."""
        valid, _ = service.can_transition_status(
            ProposalStatus.ACCEPTED,
            ProposalStatus.DRAFT,
        )

        assert valid is False

    def test_rejected_can_return_to_draft(self, service: ProposalService) -> None:
        """Testa que REJECTED pode voltar para DRAFT."""
        valid, _ = service.can_transition_status(
            ProposalStatus.REJECTED,
            ProposalStatus.DRAFT,
        )

        assert valid is True


class TestProposalServiceApproval:
    """Testes de processamento de aprovacao."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_approve_by_gerente(self, service: ProposalService) -> None:
        """Testa aprovacao por gerente."""
        new_status, message = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.APPROVE,
            "gerente",
        )

        assert new_status == ProposalStatus.APPROVED
        assert "aprovada" in message

    def test_approve_by_diretor(self, service: ProposalService) -> None:
        """Testa aprovacao por diretor."""
        new_status, _ = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.APPROVE,
            "diretor",
        )

        assert new_status == ProposalStatus.APPROVED

    def test_reject_proposal(self, service: ProposalService) -> None:
        """Testa rejeicao de proposta."""
        new_status, message = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.REJECT,
            "gerente",
        )

        assert new_status == ProposalStatus.REJECTED
        assert "rejeitada" in message

    def test_request_changes(self, service: ProposalService) -> None:
        """Testa solicitacao de alteracoes."""
        new_status, message = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.REQUEST_CHANGES,
            "gerente",
        )

        assert new_status == ProposalStatus.DRAFT
        assert "ajustes" in message

    def test_vendedor_cannot_approve(self, service: ProposalService) -> None:
        """Testa que vendedor nao pode aprovar."""
        new_status, message = service.process_approval(
            ProposalStatus.PENDING_APPROVAL,
            ApprovalAction.APPROVE,
            "vendedor",
        )

        assert new_status == ProposalStatus.PENDING_APPROVAL
        assert "permissao" in message

    def test_cannot_approve_draft(self, service: ProposalService) -> None:
        """Testa que nao pode aprovar proposta em DRAFT."""
        new_status, message = service.process_approval(
            ProposalStatus.DRAFT,
            ApprovalAction.APPROVE,
            "gerente",
        )

        assert new_status == ProposalStatus.DRAFT
        assert "pendente" in message


class TestProposalServiceItemsCalculation:
    """Testes de calculo de itens."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_calculate_items_simple(self, service: ProposalService) -> None:
        """Testa calculo de itens simples."""
        items = [
            {"quantity": 10, "unit_price": "100.00", "discount_percent": "0"},
        ]

        subtotal, discount, total = service.calculate_items_totals(items)

        assert subtotal == Decimal("1000.00")
        assert discount == Decimal("0.00")
        assert total == Decimal("1000.00")

    def test_calculate_items_with_discount(self, service: ProposalService) -> None:
        """Testa calculo de itens com desconto."""
        items = [
            {"quantity": 10, "unit_price": "100.00", "discount_percent": "10"},
        ]

        subtotal, discount, total = service.calculate_items_totals(items)

        assert subtotal == Decimal("1000.00")
        assert discount == Decimal("100.00")
        assert total == Decimal("900.00")

    def test_calculate_items_multiple(self, service: ProposalService) -> None:
        """Testa calculo de multiplos itens."""
        items = [
            {"quantity": 5, "unit_price": "200.00", "discount_percent": "5"},
            {"quantity": 10, "unit_price": "50.00", "discount_percent": "10"},
        ]

        subtotal, discount, total = service.calculate_items_totals(items)

        # Item 1: 5 * 200 = 1000, desconto 5% = 50
        # Item 2: 10 * 50 = 500, desconto 10% = 50
        assert subtotal == Decimal("1500.00")
        assert discount == Decimal("100.00")
        assert total == Decimal("1400.00")

    def test_calculate_items_empty(self, service: ProposalService) -> None:
        """Testa calculo de lista vazia."""
        items: list[dict] = []

        subtotal, discount, total = service.calculate_items_totals(items)

        assert subtotal == Decimal("0.00")
        assert discount == Decimal("0.00")
        assert total == Decimal("0.00")


class TestProposalServiceExpiration:
    """Testes de verificacao de expiracao."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_not_expired(self, service: ProposalService) -> None:
        """Testa proposta nao expirada."""
        future_date = date.today() + timedelta(days=10)

        expired, days = service.check_expiration(future_date)

        assert expired is False
        assert days == 10

    def test_expired(self, service: ProposalService) -> None:
        """Testa proposta expirada."""
        past_date = date.today() - timedelta(days=5)

        expired, days = service.check_expiration(past_date)

        assert expired is True
        assert days == -5

    def test_expires_today(self, service: ProposalService) -> None:
        """Testa proposta que expira hoje."""
        today = date.today()

        expired, days = service.check_expiration(today)

        assert expired is False
        assert days == 0


class TestProposalServiceVersioning:
    """Testes de versionamento."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_generate_version_from_1(self, service: ProposalService) -> None:
        """Testa geracao de versao 2."""
        new_version = service.generate_version(1)
        assert new_version == 2

    def test_generate_version_from_5(self, service: ProposalService) -> None:
        """Testa geracao de versao 6."""
        new_version = service.generate_version(5)
        assert new_version == 6


class TestProposalServiceFormatting:
    """Testes de formatacao."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_format_currency_simple(self, service: ProposalService) -> None:
        """Testa formatacao simples."""
        formatted = service.format_currency(Decimal("1234.56"))
        assert formatted == "R$ 1.234,56"

    def test_format_currency_large(self, service: ProposalService) -> None:
        """Testa formatacao de valor grande."""
        formatted = service.format_currency(Decimal("1234567.89"))
        assert formatted == "R$ 1.234.567,89"

    def test_format_currency_small(self, service: ProposalService) -> None:
        """Testa formatacao de valor pequeno."""
        formatted = service.format_currency(Decimal("99.00"))
        assert formatted == "R$ 99,00"


class TestProposalServiceCommission:
    """Testes de calculo de comissao."""

    @pytest.fixture
    def service(self) -> ProposalService:
        """Fixture do service."""
        return ProposalService()

    def test_calculate_commission(self, service: ProposalService) -> None:
        """Testa calculo de comissao."""
        commission = service.calculate_commission(
            total_value=Decimal("100000.00"),
            commission_rate=Decimal("5.00"),
        )

        assert commission == Decimal("5000.00")

    def test_calculate_commission_decimal_precision(self, service: ProposalService) -> None:
        """Testa precisao decimal da comissao."""
        commission = service.calculate_commission(
            total_value=Decimal("123456.78"),
            commission_rate=Decimal("3.50"),
        )

        # 123456.78 * 0.035 = 4320.9873
        assert commission == Decimal("4320.99")

    def test_calculate_commission_zero_rate(self, service: ProposalService) -> None:
        """Testa comissao com taxa zero."""
        commission = service.calculate_commission(
            total_value=Decimal("50000.00"),
            commission_rate=Decimal("0.00"),
        )

        assert commission == Decimal("0.00")

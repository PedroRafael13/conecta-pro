"""
Servico de Propostas Comerciais.

Orquestra a criacao, precificacao, aprovacao e envio
de propostas comerciais no sistema CPQ.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from core.logging import logger
from modules.crm.models.proposal import ApprovalAction, ProposalStatus, ProposalType
from modules.crm.services.pricing_engine import PricingEngine, PricingInput, PricingResult


class ProposalService:
    """
    Servico para gerenciamento de propostas comerciais.

    Responsabilidades:
    - Criar propostas com numeracao automatica
    - Calcular valores usando PricingEngine
    - Gerenciar workflow de aprovacao
    - Controlar envio e resposta do cliente
    - Gerar versoes e historico
    """

    # Prefixos por tipo de proposta
    NUMBER_PREFIXES: dict[ProposalType, str] = {
        ProposalType.SERVICE: "PRO",
        ProposalType.PRODUCT: "PRP",
        ProposalType.MIXED: "PRM",
    }

    # Dias padrao de validade
    DEFAULT_VALIDITY_DAYS = 30

    # Limites de desconto por nivel
    DISCOUNT_LIMITS: dict[str, Decimal] = {
        "vendedor": Decimal("5.00"),
        "gerente": Decimal("15.00"),
        "diretor": Decimal("25.00"),
        "admin": Decimal("100.00"),
    }

    def __init__(self, pricing_engine: Optional[PricingEngine] = None) -> None:
        """
        Inicializa o servico.

        Args:
            pricing_engine: Motor de precificacao (opcional)
        """
        self.pricing_engine = pricing_engine or PricingEngine()

    def generate_proposal_number(self, proposal_type: ProposalType, sequence: int) -> str:
        """
        Gera numero unico da proposta.

        Formato: {PREFIX}-{ANO}-{SEQUENCIAL:05d}
        Exemplo: PRO-2026-00001

        Args:
            proposal_type: Tipo da proposta
            sequence: Numero sequencial

        Returns:
            Numero formatado da proposta
        """
        prefix = self.NUMBER_PREFIXES.get(proposal_type, "PRO")
        year = datetime.now().year
        return f"{prefix}-{year}-{sequence:05d}"

    def calculate_validity_date(self, days: Optional[int] = None) -> date:
        """
        Calcula data de validade da proposta.

        Args:
            days: Dias de validade (opcional)

        Returns:
            Data de validade
        """
        validity_days = days or self.DEFAULT_VALIDITY_DAYS
        return date.today() + timedelta(days=validity_days)

    def calculate_proposal_pricing(
        self,
        base_salary: Decimal,
        headcount: int,
        contract_months: int,
        service_type: str = "default",
        client_state: str = "SP",
        margin_target: Decimal = Decimal("15.00"),
        benefits_value: Decimal = Decimal("0.00"),
        equipment_value: Decimal = Decimal("0.00"),
    ) -> PricingResult:
        """
        Calcula precificacao completa para proposta.

        Args:
            base_salary: Salario base mensal
            headcount: Numero de funcionarios
            contract_months: Duracao do contrato
            service_type: Tipo de servico
            client_state: Estado do cliente
            margin_target: Margem alvo
            benefits_value: Valor de beneficios
            equipment_value: Valor de equipamentos

        Returns:
            Resultado do calculo de precos
        """
        pricing_input = PricingInput(
            base_salary=base_salary,
            headcount=headcount,
            contract_months=contract_months,
            service_type=service_type,
            client_state=client_state,
            margin_target=margin_target,
            benefits_value=benefits_value,
            equipment_value=equipment_value,
        )

        result = self.pricing_engine.calculate(pricing_input)

        logger.info(
            "Precificacao calculada para proposta",
            extra={
                "headcount": headcount,
                "months": contract_months,
                "total": str(result.total_contract),
                "margin": str(result.margin_percent),
            },
        )

        return result

    def can_apply_discount(self, discount_percent: Decimal, user_role: str) -> tuple[bool, str]:
        """
        Verifica se usuario pode aplicar desconto.

        Args:
            discount_percent: Percentual de desconto
            user_role: Role do usuario

        Returns:
            Tupla (permitido, mensagem)
        """
        limit = self.DISCOUNT_LIMITS.get(user_role.lower(), Decimal("0.00"))

        if discount_percent <= limit:
            return True, f"Desconto de {discount_percent}% aprovado automaticamente"

        # Verificar se precisa aprovacao de nivel superior
        for role, role_limit in self.DISCOUNT_LIMITS.items():
            if discount_percent <= role_limit:
                return False, f"Desconto requer aprovacao de {role}"

        return False, "Desconto excede limite maximo permitido"

    def can_transition_status(
        self, current_status: ProposalStatus, new_status: ProposalStatus
    ) -> tuple[bool, str]:
        """
        Verifica se transicao de status e valida.

        Args:
            current_status: Status atual
            new_status: Novo status

        Returns:
            Tupla (valido, mensagem)
        """
        valid_transitions: dict[ProposalStatus, list[ProposalStatus]] = {
            ProposalStatus.DRAFT: [
                ProposalStatus.PENDING_APPROVAL,
                ProposalStatus.CANCELLED,
            ],
            ProposalStatus.PENDING_APPROVAL: [
                ProposalStatus.APPROVED,
                ProposalStatus.REJECTED,
                ProposalStatus.DRAFT,
            ],
            ProposalStatus.APPROVED: [
                ProposalStatus.SENT,
                ProposalStatus.CANCELLED,
            ],
            ProposalStatus.SENT: [
                ProposalStatus.ACCEPTED,
                ProposalStatus.REJECTED,
                ProposalStatus.EXPIRED,
            ],
            ProposalStatus.ACCEPTED: [],  # Estado final
            ProposalStatus.REJECTED: [
                ProposalStatus.DRAFT,  # Pode criar nova versao
            ],
            ProposalStatus.EXPIRED: [
                ProposalStatus.DRAFT,  # Pode renovar
            ],
            ProposalStatus.CANCELLED: [],  # Estado final
        }

        allowed = valid_transitions.get(current_status, [])

        if new_status in allowed:
            return True, f"Transicao {current_status.value} -> {new_status.value} permitida"

        return False, f"Transicao {current_status.value} -> {new_status.value} nao permitida"

    def process_approval(
        self,
        current_status: ProposalStatus,
        action: ApprovalAction,
        user_role: str,
    ) -> tuple[ProposalStatus, str]:
        """
        Processa acao de aprovacao.

        Args:
            current_status: Status atual da proposta
            action: Acao de aprovacao
            user_role: Role do usuario

        Returns:
            Tupla (novo_status, mensagem)
        """
        if current_status != ProposalStatus.PENDING_APPROVAL:
            return current_status, "Proposta nao esta pendente de aprovacao"

        # Validar permissao do usuario
        approval_roles = ["gerente", "diretor", "admin"]
        if user_role.lower() not in approval_roles:
            return current_status, "Usuario nao tem permissao para aprovar"

        if action == ApprovalAction.APPROVE:
            return ProposalStatus.APPROVED, "Proposta aprovada com sucesso"

        if action == ApprovalAction.REJECT:
            return ProposalStatus.REJECTED, "Proposta rejeitada"

        if action == ApprovalAction.REQUEST_CHANGES:
            return ProposalStatus.DRAFT, "Proposta devolvida para ajustes"

        return current_status, "Acao nao reconhecida"

    def calculate_items_totals(
        self,
        items: list[dict],
    ) -> tuple[Decimal, Decimal, Decimal]:
        """
        Calcula totais dos itens da proposta.

        Args:
            items: Lista de itens com quantity, unit_price, discount_percent

        Returns:
            Tupla (subtotal, desconto_total, total)
        """
        subtotal = Decimal("0.00")
        total_discount = Decimal("0.00")

        for item in items:
            quantity = Decimal(str(item.get("quantity", 1)))
            unit_price = Decimal(str(item.get("unit_price", 0)))
            discount_pct = Decimal(str(item.get("discount_percent", 0)))

            item_subtotal = quantity * unit_price
            item_discount = item_subtotal * (discount_pct / Decimal("100"))

            subtotal += item_subtotal
            total_discount += item_discount

        total = subtotal - total_discount
        return subtotal, total_discount, total

    def check_expiration(self, valid_until: date) -> tuple[bool, int]:
        """
        Verifica se proposta esta expirada.

        Args:
            valid_until: Data de validade

        Returns:
            Tupla (expirada, dias_restantes)
        """
        today = date.today()
        days_remaining = (valid_until - today).days

        return days_remaining < 0, days_remaining

    def generate_version(self, current_version: int) -> int:
        """
        Gera nova versao da proposta.

        Args:
            current_version: Versao atual

        Returns:
            Nova versao
        """
        return current_version + 1

    def format_currency(self, value: Decimal) -> str:
        """
        Formata valor monetario para exibicao.

        Args:
            value: Valor decimal

        Returns:
            String formatada (ex: R$ 1.234,56)
        """
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"

    def calculate_commission(self, total_value: Decimal, commission_rate: Decimal) -> Decimal:
        """
        Calcula comissao sobre valor da proposta.

        Args:
            total_value: Valor total da proposta
            commission_rate: Taxa de comissao

        Returns:
            Valor da comissao
        """
        commission = total_value * (commission_rate / Decimal("100"))
        return commission.quantize(Decimal("0.01"))


# Instancia global
proposal_service = ProposalService()

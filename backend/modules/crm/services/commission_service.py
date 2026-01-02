"""
Service para Comissões de Vendedores.
Gerencia cálculo, aprovação e processamento de comissões.
"""

import json
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from core.logging import logger
from modules.crm.models.commission import (
    Commission,
    CommissionRule,
    CommissionStatus,
    CommissionSummary,
    CommissionTrigger,
    CommissionType,
)
from modules.crm.models.proposal import Proposal
from modules.crm.schemas.commission import (
    CommissionRanking,
    CommissionStats,
    SellerCommissionStats,
)


class CommissionService:
    """Service para cálculo e gestão de comissões."""

    # Formato do número de referência
    REFERENCE_FORMAT = "COM-{year}-{sequence:05d}"

    def generate_reference_number(self, sequence: int) -> str:
        """
        Gera número de referência único para comissão.

        Args:
            sequence: Número sequencial

        Returns:
            Número de referência formatado
        """
        return self.REFERENCE_FORMAT.format(
            year=date.today().year,
            sequence=sequence,
        )

    def find_applicable_rule(  # pylint: disable=too-many-branches
        self,
        rules: list[CommissionRule],
        sale_value: float,
        product_category: Optional[str] = None,
        service_type: Optional[str] = None,
    ) -> Optional[CommissionRule]:
        """
        Encontra a regra de comissão aplicável.

        Args:
            rules: Lista de regras disponíveis
            sale_value: Valor da venda
            product_category: Categoria do produto (opcional)
            service_type: Tipo de serviço (opcional)

        Returns:
            Regra aplicável ou None
        """
        applicable_rules = []

        for rule in rules:
            # Verificar se está vigente
            if not rule.is_valid:
                continue

            # Verificar valor mínimo/máximo
            if rule.min_sale_value and sale_value < rule.min_sale_value:
                continue
            if rule.max_sale_value and sale_value > rule.max_sale_value:
                continue

            # Se não aplica a todos, verificar categorias/tipos
            if not rule.applies_to_all:
                matches = False

                if rule.product_categories and product_category:
                    try:
                        categories = json.loads(rule.product_categories)
                        if product_category in categories:
                            matches = True
                    except json.JSONDecodeError:
                        pass

                if rule.service_types and service_type:
                    try:
                        types = json.loads(rule.service_types)
                        if service_type in types:
                            matches = True
                    except json.JSONDecodeError:
                        pass

                if not matches:
                    continue

            applicable_rules.append(rule)

        if not applicable_rules:
            return None

        # Retornar regra com maior prioridade
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        return applicable_rules[0]

    def calculate_commission(
        self,
        rule: CommissionRule,
        sale_value: float,
        sale_margin: float = 0.0,
        custom_rate: Optional[float] = None,
    ) -> dict:
        """
        Calcula o valor da comissão baseado na regra.

        Args:
            rule: Regra de comissão
            sale_value: Valor total da venda
            sale_margin: Margem da venda (para tipo MARGIN)
            custom_rate: Taxa customizada (override)

        Returns:
            Dict com detalhes do cálculo
        """
        rate = custom_rate if custom_rate is not None else rule.base_value
        commission_type = rule.commission_type

        base_commission = 0.0

        if commission_type == CommissionType.FIXED.value:
            base_commission = rate
        elif commission_type == CommissionType.PERCENTAGE.value:
            base_commission = sale_value * (rate / 100)
        elif commission_type == CommissionType.MARGIN.value:
            base_commission = sale_margin * (rate / 100)
        elif commission_type == CommissionType.PROGRESSIVE.value:
            base_commission = self._calculate_progressive(
                rule.progressive_scale, sale_value, rate
            )
        elif commission_type == CommissionType.BONUS.value:
            # Bônus é fixo quando critérios são atingidos
            base_commission = rate

        # Aplicar limites
        if rule.min_value and base_commission < rule.min_value:
            base_commission = rule.min_value
        if rule.max_value and base_commission > rule.max_value:
            base_commission = rule.max_value

        base_commission = round(base_commission, 2)

        # Calcular data de pagamento
        trigger_date = self._calculate_trigger_date(rule.trigger)
        due_date = trigger_date + timedelta(days=rule.trigger_delay_days)

        return {
            "commission_type": commission_type,
            "commission_rate": rate,
            "base_commission": base_commission,
            "trigger": rule.trigger,
            "trigger_date": trigger_date,
            "due_date": due_date,
        }

    def _calculate_progressive(
        self, scale_json: Optional[str], sale_value: float, default_rate: float
    ) -> float:
        """Calcula comissão com escala progressiva."""
        if not scale_json:
            return sale_value * (default_rate / 100)

        try:
            scale = json.loads(scale_json)
            for tier in scale:
                tier_min = tier.get("min", 0)
                tier_max = tier.get("max", float("inf"))
                rate = tier.get("rate", 0)

                if tier_min <= sale_value <= tier_max:
                    return sale_value * (rate / 100)

            return sale_value * (default_rate / 100)

        except (json.JSONDecodeError, KeyError):
            logger.warning("Erro ao processar escala progressiva")
            return sale_value * (default_rate / 100)

    def _calculate_trigger_date(self, trigger: str) -> date:
        """Calcula a data do gatilho."""
        today = date.today()

        if trigger == CommissionTrigger.ON_SIGNATURE.value:
            return today
        elif trigger == CommissionTrigger.MONTHLY.value:
            # Próximo dia 1
            if today.month == 12:
                return date(today.year + 1, 1, 1)
            return date(today.year, today.month + 1, 1)
        else:
            # Para outros gatilhos, data atual (será atualizado quando evento ocorrer)
            return today

    def create_commission_from_proposal(
        self,
        proposal: Proposal,
        rule: CommissionRule,
        seller_id: str,
        sale_margin: float = 0.0,
        custom_rate: Optional[float] = None,
    ) -> dict:
        """
        Cria dados de comissão a partir de proposta aceita.

        Args:
            proposal: Proposta aceita
            rule: Regra de comissão
            seller_id: ID do vendedor
            sale_margin: Margem da venda
            custom_rate: Taxa customizada

        Returns:
            Dict com dados para criar Commission
        """
        calculation = self.calculate_commission(
            rule=rule,
            sale_value=proposal.total,
            sale_margin=sale_margin,
            custom_rate=custom_rate,
        )

        return {
            "id": str(uuid.uuid4()),
            "seller_id": seller_id,
            "proposal_id": str(proposal.id),
            "rule_id": str(rule.id),
            "sale_value": proposal.total,
            "sale_margin": sale_margin,
            "commission_type": calculation["commission_type"],
            "commission_rate": calculation["commission_rate"],
            "base_commission": calculation["base_commission"],
            "adjustments": 0.0,
            "final_commission": calculation["base_commission"],
            "status": CommissionStatus.PENDING.value,
            "trigger": calculation["trigger"],
            "trigger_date": calculation["trigger_date"],
            "due_date": calculation["due_date"],
            "description": f"Comissão - Proposta {proposal.number}",
        }

    def apply_adjustment(
        self,
        commission: Commission,
        adjustment: float,
        reason: str,
    ) -> float:
        """
        Aplica ajuste na comissão.

        Args:
            commission: Comissão
            adjustment: Valor do ajuste (+/-)
            reason: Motivo do ajuste

        Returns:
            Novo valor final
        """
        new_adjustments = commission.adjustments + adjustment
        new_final = commission.base_commission + new_adjustments

        logger.info(
            f"Ajuste na comissão {commission.reference_number}: "
            f"{adjustment:+.2f} ({reason}). Novo total: {new_final:.2f}"
        )

        return max(0.0, new_final)  # Não permite comissão negativa

    def calculate_stats(  # pylint: disable=too-many-locals
        self,
        commissions: list[Commission],
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> CommissionStats:
        """
        Calcula estatísticas de comissões.

        Args:
            commissions: Lista de comissões
            date_from: Data inicial
            date_to: Data final

        Returns:
            Estatísticas calculadas
        """
        # Filtrar por período se especificado
        filtered = commissions
        if date_from:
            filtered = [c for c in filtered if c.created_at.date() >= date_from]
        if date_to:
            filtered = [c for c in filtered if c.created_at.date() <= date_to]

        # Contagens por status
        pending_count = sum(1 for c in filtered if c.status == CommissionStatus.PENDING.value)
        approved_count = sum(1 for c in filtered if c.status == CommissionStatus.APPROVED.value)
        paid_count = sum(1 for c in filtered if c.status == CommissionStatus.PAID.value)
        cancelled_count = sum(1 for c in filtered if c.status == CommissionStatus.CANCELLED.value)

        # Valores por status
        pending_value = sum(
            c.final_commission for c in filtered if c.status == CommissionStatus.PENDING.value
        )
        approved_value = sum(
            c.final_commission for c in filtered if c.status == CommissionStatus.APPROVED.value
        )
        paid_value = sum(
            c.final_commission for c in filtered if c.status == CommissionStatus.PAID.value
        )
        total_value = sum(c.final_commission for c in filtered)

        # Comissões atrasadas
        overdue = [c for c in filtered if c.is_overdue]
        overdue_count = len(overdue)
        overdue_value = sum(c.pending_amount for c in overdue)

        # Média de valor
        avg_commission = total_value / len(filtered) if filtered else 0.0

        # Média de dias até pagamento
        paid_with_dates = [c for c in filtered if c.is_paid and c.paid_date and c.trigger_date]
        if paid_with_dates:
            total_days = sum((c.paid_date - c.trigger_date).days for c in paid_with_dates)
            avg_days = total_days / len(paid_with_dates)
        else:
            avg_days = 0.0

        # Agrupar por status
        by_status = {}
        for c in filtered:
            by_status[c.status] = by_status.get(c.status, 0) + 1

        # Agrupar por trigger
        by_trigger = {}
        for c in filtered:
            by_trigger[c.trigger] = by_trigger.get(c.trigger, 0) + 1

        # Agrupar por mês
        by_month = {}
        for c in filtered:
            month_key = c.created_at.strftime("%Y-%m")
            by_month[month_key] = by_month.get(month_key, 0) + c.final_commission

        return CommissionStats(
            total_commissions=len(filtered),
            pending_count=pending_count,
            approved_count=approved_count,
            paid_count=paid_count,
            cancelled_count=cancelled_count,
            total_value=round(total_value, 2),
            pending_value=round(pending_value, 2),
            approved_value=round(approved_value, 2),
            paid_value=round(paid_value, 2),
            overdue_count=overdue_count,
            overdue_value=round(overdue_value, 2),
            avg_commission_value=round(avg_commission, 2),
            avg_days_to_payment=round(avg_days, 1),
            by_status=by_status,
            by_trigger=by_trigger,
            by_month=by_month,
        )

    def calculate_seller_stats(  # pylint: disable=too-many-locals
        self,
        commissions: list[Commission],
        seller_id: str,
        seller_name: Optional[str] = None,
        target: Optional[float] = None,
    ) -> SellerCommissionStats:
        """
        Calcula estatísticas de comissões por vendedor.

        Args:
            commissions: Comissões do vendedor
            seller_id: ID do vendedor
            seller_name: Nome do vendedor
            target: Meta de vendas

        Returns:
            Estatísticas do vendedor
        """
        seller_commissions = [c for c in commissions if c.seller_id == seller_id]

        total_sales = sum(c.sale_value for c in seller_commissions)
        total_commissions = sum(c.final_commission for c in seller_commissions)
        pending_commissions = sum(
            c.final_commission for c in seller_commissions if c.is_pending
        )
        paid_commissions = sum(
            c.final_commission for c in seller_commissions if c.is_paid
        )

        # Taxa média de comissão
        if total_sales > 0:
            commission_rate_avg = (total_commissions / total_sales) * 100
        else:
            commission_rate_avg = 0.0

        # Vendas do mês atual
        today = date.today()
        current_month = [
            c for c in seller_commissions
            if c.created_at.year == today.year and c.created_at.month == today.month
        ]
        current_month_sales = sum(c.sale_value for c in current_month)
        current_month_commissions = sum(c.final_commission for c in current_month)

        # Percentual da meta
        target_percentage = None
        if target and target > 0:
            target_percentage = (current_month_sales / target) * 100

        return SellerCommissionStats(
            seller_id=seller_id,
            seller_name=seller_name,
            total_sales=round(total_sales, 2),
            total_commissions=round(total_commissions, 2),
            pending_commissions=round(pending_commissions, 2),
            paid_commissions=round(paid_commissions, 2),
            commission_rate_avg=round(commission_rate_avg, 2),
            sales_count=len(seller_commissions),
            current_month_sales=round(current_month_sales, 2),
            current_month_commissions=round(current_month_commissions, 2),
            target=target,
            target_percentage=round(target_percentage, 1) if target_percentage else None,
        )

    def generate_ranking(
        self,
        commissions: list[Commission],
        sellers: dict[str, str],  # {seller_id: seller_name}
        period_start: date,
        period_end: date,
    ) -> CommissionRanking:
        """
        Gera ranking de vendedores por comissão.

        Args:
            commissions: Todas as comissões
            sellers: Dict de vendedores {id: nome}
            period_start: Início do período
            period_end: Fim do período

        Returns:
            Ranking de vendedores
        """
        # Filtrar por período
        period_commissions = [
            c for c in commissions
            if period_start <= c.created_at.date() <= period_end
        ]

        # Calcular stats por vendedor
        seller_stats = []
        for seller_id, seller_name in sellers.items():
            stats = self.calculate_seller_stats(
                commissions=period_commissions,
                seller_id=seller_id,
                seller_name=seller_name,
            )
            seller_stats.append(stats)

        # Ordenar por total de comissões (decrescente)
        seller_stats.sort(key=lambda s: s.total_commissions, reverse=True)

        # Totais
        total_commissions = sum(s.total_commissions for s in seller_stats)
        total_sales = sum(s.total_sales for s in seller_stats)

        return CommissionRanking(
            sellers=seller_stats,
            period_start=period_start,
            period_end=period_end,
            total_commissions=round(total_commissions, 2),
            total_sales=round(total_sales, 2),
        )

    def update_summary(
        self,
        summary: CommissionSummary,
        commissions: list[Commission],
    ) -> CommissionSummary:
        """
        Atualiza resumo mensal com base nas comissões.

        Args:
            summary: Resumo a atualizar
            commissions: Comissões do período

        Returns:
            Resumo atualizado
        """
        # Filtrar comissões do período
        period_commissions = [
            c for c in commissions
            if c.seller_id == summary.seller_id
            and c.created_at.year == summary.year
            and c.created_at.month == summary.month
        ]

        summary.total_sales = sum(c.sale_value for c in period_commissions)
        summary.total_sales_count = len(period_commissions)
        summary.total_commissions = sum(c.final_commission for c in period_commissions)
        summary.total_paid = sum(c.final_commission for c in period_commissions if c.is_paid)
        summary.total_pending = summary.total_commissions - summary.total_paid

        # Calcular percentual da meta
        if summary.sales_target and summary.sales_target > 0:
            summary.target_percentage = (summary.total_sales / summary.sales_target) * 100
        else:
            summary.target_percentage = None

        summary.updated_at = datetime.utcnow()

        return summary

    def should_process_trigger(
        self,
        commission: Commission,
        event: str,
        event_date: Optional[date] = None,  # pylint: disable=unused-argument
    ) -> bool:
        """
        Verifica se o gatilho da comissão deve ser processado.

        Args:
            commission: Comissão
            event: Tipo de evento (signature, payment, etc)
            event_date: Data do evento

        Returns:
            True se deve processar
        """
        if commission.status != CommissionStatus.PENDING.value:
            return False

        trigger_map = {
            "signature": CommissionTrigger.ON_SIGNATURE.value,
            "first_payment": CommissionTrigger.ON_FIRST_PAYMENT.value,
            "payment": CommissionTrigger.ON_EACH_PAYMENT.value,
            "full_payment": CommissionTrigger.ON_FULL_PAYMENT.value,
        }

        expected_trigger = trigger_map.get(event)
        return commission.trigger == expected_trigger

    def process_trigger(
        self,
        commission: Commission,
        event_date: Optional[date] = None,
    ) -> Commission:
        """
        Processa gatilho e atualiza comissão para aprovação.

        Args:
            commission: Comissão
            event_date: Data do evento

        Returns:
            Comissão atualizada
        """
        commission.trigger_date = event_date or date.today()
        commission.status = CommissionStatus.APPROVED.value

        # Recalcular data de vencimento se necessário
        if hasattr(commission, 'rule') and commission.rule:
            delay = commission.rule.trigger_delay_days
            commission.due_date = commission.trigger_date + timedelta(days=delay)

        commission.updated_at = datetime.utcnow()

        logger.info(
            f"Comissão {commission.reference_number} aprovada para pagamento. "
            f"Vencimento: {commission.due_date}"
        )

        return commission

"""Service de IA para analise de contas a receber."""

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.customer import Customer, CustomerStatus
from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus
from modules.financial.models.receivable_installment import (
    InstallmentStatus,
    ReceivableInstallment,
)
from modules.financial.models.receivable_payment import ReceivablePayment

logger = logging.getLogger(__name__)


@dataclass
class CustomerRiskScore:
    """Score de risco do cliente."""

    customer_id: UUID
    customer_name: str
    risk_score: float  # 0-100
    risk_level: str  # baixo, medio, alto, critico
    total_debt: Decimal
    overdue_debt: Decimal
    overdue_days_avg: float
    payment_history_score: float
    recommendations: List[str]


@dataclass
class CollectionPriority:
    """Prioridade de cobranca."""

    account_id: UUID
    customer_name: str
    value: Decimal
    days_overdue: int
    priority_score: float
    recommended_action: str
    contact_info: Dict[str, str]


@dataclass
class CashFlowForecast:
    """Previsao de fluxo de caixa."""

    period_start: date
    period_end: date
    expected_receipts: Decimal
    probable_receipts: Decimal  # Considerando inadimplencia
    historical_collection_rate: float
    by_day: List[Dict]


@dataclass
class DelinquencyAnalysis:
    """Analise de inadimplencia."""

    total_customers: int
    delinquent_customers: int
    delinquency_rate: float
    total_overdue: Decimal
    aging_buckets: Dict[str, Dict]
    trend: str  # melhorando, estavel, piorando
    projected_losses: Decimal


class ReceivableAIService:
    """Service de IA para analise de recebiveis."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session

    async def calculate_customer_risk(
        self,
        customer_id: UUID,
    ) -> CustomerRiskScore:
        """Calcula score de risco do cliente."""
        # Busca dados do cliente
        customer_result = await self.session.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise ValueError("Cliente nao encontrado")

        # Busca historico de pagamentos
        payments_result = await self.session.execute(
            select(ReceivablePayment)
            .join(
                ReceivableInstallment,
                ReceivablePayment.installment_id == ReceivableInstallment.id,
            )
            .join(
                ReceivableAccount,
                ReceivableInstallment.receivable_account_id == ReceivableAccount.id,
            )
            .where(ReceivableAccount.customer_id == customer_id)
            .order_by(ReceivablePayment.payment_date.desc())
            .limit(50)
        )
        payments = list(payments_result.scalars().all())

        # Busca parcelas vencidas
        today = date.today()
        overdue_result = await self.session.execute(
            select(ReceivableInstallment)
            .join(ReceivableAccount)
            .where(
                and_(
                    ReceivableAccount.customer_id == customer_id,
                    ReceivableInstallment.due_date < today,
                    ReceivableInstallment.status.notin_(
                        [InstallmentStatus.PAGA.value, InstallmentStatus.CANCELADA.value]
                    ),
                )
            )
        )
        overdue_installments = list(overdue_result.scalars().all())

        # Calcula metricas
        total_overdue_days = sum(
            (today - inst.due_date).days for inst in overdue_installments
        )
        avg_overdue_days = (
            total_overdue_days / len(overdue_installments)
            if overdue_installments
            else 0
        )

        # Score de historico de pagamento (0-100)
        payment_score = 100.0
        if payments:
            late_payments = sum(
                1 for p in payments
                if p.payment_date and hasattr(p, 'installment') and
                p.installment and p.installment.due_date and
                p.payment_date > p.installment.due_date
            )
            payment_score = max(0, 100 - (late_payments / len(payments) * 100))

        # Calcula risk score
        risk_factors = []

        # Fator: divida vencida
        if customer.overdue_debt > 0:
            overdue_ratio = float(customer.overdue_debt / customer.total_debt) if customer.total_debt > 0 else 0
            risk_factors.append(overdue_ratio * 40)

        # Fator: dias de atraso medio
        if avg_overdue_days > 0:
            days_factor = min(avg_overdue_days / 90, 1) * 30
            risk_factors.append(days_factor)

        # Fator: historico de pagamentos
        risk_factors.append((100 - payment_score) * 0.3)

        risk_score = sum(risk_factors)
        risk_score = min(max(risk_score, 0), 100)

        # Determina nivel de risco
        if risk_score < 25:
            risk_level = "baixo"
        elif risk_score < 50:
            risk_level = "medio"
        elif risk_score < 75:
            risk_level = "alto"
        else:
            risk_level = "critico"

        # Gera recomendacoes
        recommendations = self._generate_risk_recommendations(
            risk_level, avg_overdue_days, customer.overdue_debt
        )

        return CustomerRiskScore(
            customer_id=customer_id,
            customer_name=customer.name,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            total_debt=customer.total_debt,
            overdue_debt=customer.overdue_debt,
            overdue_days_avg=round(avg_overdue_days, 1),
            payment_history_score=round(payment_score, 2),
            recommendations=recommendations,
        )

    def _generate_risk_recommendations(
        self,
        risk_level: str,
        avg_overdue_days: float,
        overdue_debt: Decimal,
    ) -> List[str]:
        """Gera recomendacoes baseadas no risco."""
        recommendations = []

        if risk_level == "baixo":
            recommendations.append("Manter monitoramento regular")
            recommendations.append("Cliente elegivel para beneficios de pontualidade")

        elif risk_level == "medio":
            recommendations.append("Enviar lembretes de pagamento antecipados")
            recommendations.append("Considerar contato preventivo proximo ao vencimento")

        elif risk_level == "alto":
            recommendations.append("Priorizar contato de cobranca")
            recommendations.append("Oferecer renegociacao de divida")
            if avg_overdue_days > 30:
                recommendations.append("Considerar restricao de credito")

        else:  # critico
            recommendations.append("Acao de cobranca imediata necessaria")
            if overdue_debt > 1000:
                recommendations.append("Avaliar envio para protesto")
            recommendations.append("Bloquear novas operacoes")
            recommendations.append("Considerar cobranca judicial")

        return recommendations

    async def get_collection_priorities(
        self,
        condominio_id: UUID,
        limit: int = 20,
    ) -> List[CollectionPriority]:
        """Retorna lista priorizada de cobrancas."""
        today = date.today()

        # Busca contas vencidas com informacoes do cliente
        result = await self.session.execute(
            select(ReceivableAccount, Customer)
            .outerjoin(Customer, ReceivableAccount.customer_id == Customer.id)
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.ativo == True,  # noqa: E712
                    ReceivableAccount.due_date < today,
                    ReceivableAccount.status.notin_(
                        [
                            ReceivableStatus.PAGA.value,
                            ReceivableStatus.CANCELADA.value,
                        ]
                    ),
                )
            )
            .order_by(ReceivableAccount.due_date)
        )

        priorities = []
        for account, customer in result:
            days_overdue = (today - account.due_date).days
            remaining_value = account.net_value - account.paid_value

            # Calcula score de prioridade
            priority_score = self._calculate_priority_score(
                remaining_value, days_overdue
            )

            # Determina acao recomendada
            action = self._get_recommended_action(days_overdue, remaining_value)

            # Informacoes de contato
            contact_info = {}
            if customer:
                if customer.phone:
                    contact_info["telefone"] = customer.phone
                if customer.whatsapp:
                    contact_info["whatsapp"] = customer.whatsapp
                if customer.email:
                    contact_info["email"] = customer.email

            priorities.append(
                CollectionPriority(
                    account_id=account.id,
                    customer_name=customer.name if customer else "N/A",
                    value=remaining_value,
                    days_overdue=days_overdue,
                    priority_score=round(priority_score, 2),
                    recommended_action=action,
                    contact_info=contact_info,
                )
            )

        # Ordena por score de prioridade
        priorities.sort(key=lambda x: x.priority_score, reverse=True)
        return priorities[:limit]

    def _calculate_priority_score(
        self,
        value: Decimal,
        days_overdue: int,
    ) -> float:
        """Calcula score de prioridade para cobranca."""
        # Normalizacao do valor (assume max 10000)
        value_score = min(float(value) / 10000, 1) * 50

        # Normalizacao dos dias (assume max 90 dias)
        days_score = min(days_overdue / 90, 1) * 50

        return value_score + days_score

    def _get_recommended_action(
        self,
        days_overdue: int,
        value: Decimal,
    ) -> str:
        """Retorna acao recomendada baseada no atraso."""
        if days_overdue <= 7:
            return "Enviar lembrete por email/WhatsApp"
        elif days_overdue <= 15:
            return "Contato telefonico amigavel"
        elif days_overdue <= 30:
            return "Negociacao de pagamento"
        elif days_overdue <= 60:
            if value > 500:
                return "Notificacao extrajudicial"
            return "Intensificar cobranca"
        elif days_overdue <= 90:
            if value > 1000:
                return "Considerar protesto"
            return "Ultima tentativa de negociacao"
        else:
            if value > 2000:
                return "Protesto ou cobranca judicial"
            return "Avaliar baixa por perda"

    async def forecast_cash_flow(
        self,
        condominio_id: UUID,
        days_ahead: int = 30,
    ) -> CashFlowForecast:
        """Preve fluxo de caixa de recebiveis."""
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        # Busca parcelas a vencer no periodo
        result = await self.session.execute(
            select(ReceivableInstallment)
            .join(ReceivableAccount)
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableInstallment.ativo == True,  # noqa: E712
                    ReceivableInstallment.due_date >= today,
                    ReceivableInstallment.due_date <= end_date,
                    ReceivableInstallment.status.in_(
                        [InstallmentStatus.PENDENTE.value, InstallmentStatus.AGENDADA.value]
                    ),
                )
            )
            .order_by(ReceivableInstallment.due_date)
        )
        installments = list(result.scalars().all())

        # Calcula taxa historica de recebimento
        collection_rate = await self._calculate_historical_collection_rate(condominio_id)

        # Totaliza por dia
        by_day = []
        total_expected = Decimal("0")
        current_date = today

        while current_date <= end_date:
            day_total = sum(
                inst.current_value for inst in installments
                if inst.due_date == current_date
            )
            total_expected += day_total

            by_day.append({
                "date": current_date.isoformat(),
                "expected": float(day_total),
                "probable": float(day_total * Decimal(str(collection_rate))),
            })
            current_date += timedelta(days=1)

        probable_total = total_expected * Decimal(str(collection_rate))

        return CashFlowForecast(
            period_start=today,
            period_end=end_date,
            expected_receipts=total_expected,
            probable_receipts=probable_total,
            historical_collection_rate=round(collection_rate, 4),
            by_day=by_day,
        )

    async def _calculate_historical_collection_rate(
        self,
        condominio_id: UUID,
    ) -> float:
        """Calcula taxa historica de recebimento."""
        # Ultimos 90 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=90)

        # Total faturado no periodo
        billed_result = await self.session.execute(
            select(func.sum(ReceivableInstallment.original_value))
            .join(ReceivableAccount)
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableInstallment.due_date >= start_date,
                    ReceivableInstallment.due_date <= end_date,
                )
            )
        )
        total_billed = billed_result.scalar_one() or Decimal("0")

        # Total recebido no periodo
        received_result = await self.session.execute(
            select(func.sum(ReceivablePayment.paid_value))
            .where(
                and_(
                    ReceivablePayment.condominio_id == condominio_id,
                    ReceivablePayment.payment_date >= start_date,
                    ReceivablePayment.payment_date <= end_date,
                )
            )
        )
        total_received = received_result.scalar_one() or Decimal("0")

        if total_billed == 0:
            return 0.95  # Taxa padrao se nao houver historico

        rate = float(total_received / total_billed)
        return min(max(rate, 0.5), 1.0)  # Entre 50% e 100%

    async def analyze_delinquency(
        self,
        condominio_id: UUID,
    ) -> DelinquencyAnalysis:
        """Analisa inadimplencia do condominio."""
        today = date.today()

        # Total de clientes
        total_customers_result = await self.session.execute(
            select(func.count(Customer.id)).where(
                and_(
                    Customer.condominio_id == condominio_id,
                    Customer.ativo == True,  # noqa: E712
                    Customer.status != CustomerStatus.INATIVO.value,
                )
            )
        )
        total_customers = total_customers_result.scalar_one() or 0

        # Clientes inadimplentes
        delinquent_result = await self.session.execute(
            select(func.count(Customer.id)).where(
                and_(
                    Customer.condominio_id == condominio_id,
                    Customer.ativo == True,  # noqa: E712
                    Customer.overdue_debt > 0,
                )
            )
        )
        delinquent_customers = delinquent_result.scalar_one() or 0

        # Total vencido
        overdue_result = await self.session.execute(
            select(func.sum(ReceivableAccount.net_value - ReceivableAccount.paid_value))
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.ativo == True,  # noqa: E712
                    ReceivableAccount.due_date < today,
                    ReceivableAccount.status.notin_(
                        [ReceivableStatus.PAGA.value, ReceivableStatus.CANCELADA.value]
                    ),
                )
            )
        )
        total_overdue = overdue_result.scalar_one() or Decimal("0")

        # Aging buckets
        aging_buckets = await self._calculate_aging_buckets(condominio_id, today)

        # Taxa de inadimplencia
        delinquency_rate = (
            delinquent_customers / total_customers if total_customers > 0 else 0
        )

        # Tendencia (comparando com mes anterior)
        trend = await self._calculate_trend(condominio_id)

        # Projecao de perdas (30% do vencido >90 dias)
        over_90_value = Decimal(str(aging_buckets.get(">90", {}).get("value", 0)))
        projected_losses = over_90_value * Decimal("0.3")

        return DelinquencyAnalysis(
            total_customers=total_customers,
            delinquent_customers=delinquent_customers,
            delinquency_rate=round(delinquency_rate, 4),
            total_overdue=total_overdue,
            aging_buckets=aging_buckets,
            trend=trend,
            projected_losses=projected_losses,
        )

    async def _calculate_aging_buckets(
        self,
        condominio_id: UUID,
        reference_date: date,
    ) -> Dict[str, Dict]:
        """Calcula distribuicao de aging."""
        buckets = {
            "1-7": {"count": 0, "value": 0},
            "8-15": {"count": 0, "value": 0},
            "16-30": {"count": 0, "value": 0},
            "31-60": {"count": 0, "value": 0},
            "61-90": {"count": 0, "value": 0},
            ">90": {"count": 0, "value": 0},
        }

        result = await self.session.execute(
            select(ReceivableAccount)
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.ativo == True,  # noqa: E712
                    ReceivableAccount.due_date < reference_date,
                    ReceivableAccount.status.notin_(
                        [ReceivableStatus.PAGA.value, ReceivableStatus.CANCELADA.value]
                    ),
                )
            )
        )

        for account in result.scalars():
            days = (reference_date - account.due_date).days
            value = float(account.net_value - account.paid_value)

            if days <= 7:
                bucket = "1-7"
            elif days <= 15:
                bucket = "8-15"
            elif days <= 30:
                bucket = "16-30"
            elif days <= 60:
                bucket = "31-60"
            elif days <= 90:
                bucket = "61-90"
            else:
                bucket = ">90"

            buckets[bucket]["count"] += 1
            buckets[bucket]["value"] += value

        return buckets

    async def _calculate_trend(self, condominio_id: UUID) -> str:
        """Calcula tendencia de inadimplencia."""
        today = date.today()

        # Mes atual
        current_month_start = today.replace(day=1)
        current_result = await self.session.execute(
            select(func.sum(ReceivableAccount.net_value - ReceivableAccount.paid_value))
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.ativo == True,  # noqa: E712
                    ReceivableAccount.due_date < today,
                    ReceivableAccount.due_date >= current_month_start,
                    ReceivableAccount.status.notin_(
                        [ReceivableStatus.PAGA.value, ReceivableStatus.CANCELADA.value]
                    ),
                )
            )
        )
        current_overdue = current_result.scalar_one() or Decimal("0")

        # Mes anterior
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        prev_result = await self.session.execute(
            select(func.sum(ReceivableAccount.net_value - ReceivableAccount.paid_value))
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.ativo == True,  # noqa: E712
                    ReceivableAccount.due_date < prev_month_end,
                    ReceivableAccount.due_date >= prev_month_start,
                    ReceivableAccount.status.notin_(
                        [ReceivableStatus.PAGA.value, ReceivableStatus.CANCELADA.value]
                    ),
                )
            )
        )
        prev_overdue = prev_result.scalar_one() or Decimal("0")

        if prev_overdue == 0:
            return "estavel"

        variation = (current_overdue - prev_overdue) / prev_overdue

        if variation < -0.1:
            return "melhorando"
        elif variation > 0.1:
            return "piorando"
        return "estavel"

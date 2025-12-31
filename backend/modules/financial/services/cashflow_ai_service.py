"""Service de IA para Fluxo de Caixa."""

import logging
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.bank_account import BankAccount
from modules.financial.models.bank_transaction import BankTransaction, TransactionType
from modules.financial.models.cashflow_entry import CashFlowEntry, CashFlowEntryType
from modules.financial.models.cashflow_forecast import (
    CashFlowForecast,
    ForecastConfidence,
    ForecastPeriodType,
    ForecastStatus,
)
from modules.financial.models.payable_account import PayableAccount, PayableStatus
from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus
from modules.financial.repositories.cashflow_repository import (
    BankAccountRepository,
    BankTransactionRepository,
    CashFlowEntryRepository,
    CashFlowForecastRepository,
)

logger = logging.getLogger(__name__)


class CashFlowAIService:
    """Service de IA para analise e previsao de fluxo de caixa."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.account_repo = BankAccountRepository(session)
        self.transaction_repo = BankTransactionRepository(session)
        self.entry_repo = CashFlowEntryRepository(session)
        self.forecast_repo = CashFlowForecastRepository(session)

    async def generate_forecast(
        self,
        condominio_id: UUID,
        months_ahead: int = 3,
        include_scenarios: bool = True,
    ) -> CashFlowForecast:
        """Gera previsao de fluxo de caixa usando IA."""
        logger.info(f"Gerando previsao IA para {condominio_id} - {months_ahead} meses")

        today = date.today()

        # Define periodo
        period_start = today.replace(day=1)
        if today.month + months_ahead > 12:
            period_end = date(
                today.year + 1,
                (today.month + months_ahead - 1) % 12 + 1,
                1,
            ) - timedelta(days=1)
        else:
            period_end = date(today.year, today.month + months_ahead, 1) - timedelta(days=1)

        # Coleta dados historicos
        historical_data = await self._collect_historical_data(condominio_id, months=12)

        # Analisa padroes
        patterns = await self._analyze_patterns(historical_data)

        # Calcula previsoes
        expected_receivables = await self._forecast_receivables(condominio_id, months_ahead)
        expected_payables = await self._forecast_payables(condominio_id, months_ahead)

        # Obtem saldo atual
        current_balance = await self.account_repo.get_total_balance(condominio_id)

        # Cria previsao
        forecast = CashFlowForecast(
            condominio_id=condominio_id,
            name=f"Previsao {period_start.strftime('%m/%Y')} - {period_end.strftime('%m/%Y')}",
            reference=f"{period_start.year}/{period_start.month:02d}",
            period_type=ForecastPeriodType.MENSAL.value,
            period_start=period_start,
            period_end=period_end,
            forecast_date=today,
            status=ForecastStatus.ATIVA.value,
            expected_opening_balance=current_balance,
            expected_receivables=expected_receivables,
            expected_payables=expected_payables,
            expected_other_income=Decimal("0"),
            expected_other_expenses=Decimal("0"),
        )

        # Calcula valores derivados
        forecast.calculate_expected_values()

        # Calcula nivel de confianca
        confidence = self._calculate_confidence(historical_data, patterns)
        forecast.update_confidence(confidence)

        # Gera breakdown
        forecast.inflows_breakdown = await self._generate_inflows_breakdown(
            condominio_id, months_ahead
        )
        forecast.outflows_breakdown = await self._generate_outflows_breakdown(
            condominio_id, months_ahead
        )

        # Gera cenarios
        if include_scenarios:
            forecast.scenarios = self._generate_scenarios(forecast)

        # Identifica riscos e oportunidades
        risks = self._identify_risks(forecast, patterns)
        for risk in risks:
            forecast.add_risk(**risk)

        opportunities = self._identify_opportunities(forecast, patterns)
        for opp in opportunities:
            forecast.add_opportunity(**opp)

        # Gera alertas
        await self._generate_alerts(forecast)

        # Marca como gerada por IA
        forecast.mark_as_ai_generated("cashflow-ai-v1.0")

        # Fatores de confianca
        forecast.ai_factors = {
            "historical_data_months": len(historical_data.get("months", [])),
            "payment_regularity": patterns.get("payment_regularity", 0),
            "collection_rate": patterns.get("collection_rate", 0),
            "seasonality_factor": patterns.get("seasonality", 0),
            "trend_stability": patterns.get("trend_stability", 0),
        }

        return forecast

    async def _collect_historical_data(
        self,
        condominio_id: UUID,
        months: int = 12,
    ) -> Dict[str, Any]:
        """Coleta dados historicos para analise."""
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        # Busca contas a pagar historicas
        payables_query = select(PayableAccount).where(
            and_(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.due_date >= start_date,
                PayableAccount.due_date <= end_date,
            )
        )
        result = await self.session.execute(payables_query)
        payables = list(result.scalars().all())

        # Busca contas a receber historicas
        receivables_query = select(ReceivableAccount).where(
            and_(
                ReceivableAccount.condominio_id == condominio_id,
                ReceivableAccount.due_date >= start_date,
                ReceivableAccount.due_date <= end_date,
            )
        )
        result = await self.session.execute(receivables_query)
        receivables = list(result.scalars().all())

        # Agrupa por mes
        monthly_data = {}
        for p in payables:
            month_key = p.due_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "payables": Decimal("0"),
                    "receivables": Decimal("0"),
                    "paid_payables": Decimal("0"),
                    "collected_receivables": Decimal("0"),
                }
            monthly_data[month_key]["payables"] += p.net_value or Decimal("0")
            if p.status == PayableStatus.PAGA.value:
                monthly_data[month_key]["paid_payables"] += p.paid_amount or Decimal("0")

        for r in receivables:
            month_key = r.due_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "payables": Decimal("0"),
                    "receivables": Decimal("0"),
                    "paid_payables": Decimal("0"),
                    "collected_receivables": Decimal("0"),
                }
            monthly_data[month_key]["receivables"] += r.net_value or Decimal("0")
            if r.status == ReceivableStatus.PAGA.value:
                monthly_data[month_key]["collected_receivables"] += r.paid_value or Decimal("0")

        return {
            "months": list(monthly_data.keys()),
            "monthly_data": monthly_data,
            "total_payables": sum(p.net_value or Decimal("0") for p in payables),
            "total_receivables": sum(r.net_value or Decimal("0") for r in receivables),
            "total_paid": sum(
                p.paid_amount or Decimal("0")
                for p in payables
                if p.status == PayableStatus.PAGA.value
            ),
            "total_collected": sum(
                r.paid_value or Decimal("0")
                for r in receivables
                if r.status == ReceivableStatus.PAGA.value
            ),
        }

    async def _analyze_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, float]:
        """Analisa padroes nos dados historicos."""
        patterns = {
            "payment_regularity": 0.0,
            "collection_rate": 0.0,
            "seasonality": 0.0,
            "trend_stability": 0.0,
            "average_monthly_inflow": 0.0,
            "average_monthly_outflow": 0.0,
        }

        monthly_data = historical_data.get("monthly_data", {})
        if not monthly_data:
            return patterns

        # Calcula taxa de pagamento
        total_payables = historical_data.get("total_payables", Decimal("0"))
        total_paid = historical_data.get("total_paid", Decimal("0"))
        if total_payables > 0:
            patterns["payment_regularity"] = float(total_paid / total_payables * 100)

        # Calcula taxa de arrecadacao
        total_receivables = historical_data.get("total_receivables", Decimal("0"))
        total_collected = historical_data.get("total_collected", Decimal("0"))
        if total_receivables > 0:
            patterns["collection_rate"] = float(total_collected / total_receivables * 100)

        # Calcula medias mensais
        months_count = len(monthly_data)
        if months_count > 0:
            total_inflows = sum(d.get("receivables", Decimal("0")) for d in monthly_data.values())
            total_outflows = sum(d.get("payables", Decimal("0")) for d in monthly_data.values())
            patterns["average_monthly_inflow"] = float(total_inflows / months_count)
            patterns["average_monthly_outflow"] = float(total_outflows / months_count)

        # Analisa sazonalidade (simplificado)
        if months_count >= 6:
            inflows = [float(d.get("receivables", Decimal("0"))) for d in monthly_data.values()]
            if inflows:
                avg = sum(inflows) / len(inflows)
                variance = sum((x - avg) ** 2 for x in inflows) / len(inflows)
                std_dev = variance**0.5
                if avg > 0:
                    cv = std_dev / avg  # Coeficiente de variacao
                    patterns["seasonality"] = min(100, cv * 100)
                    patterns["trend_stability"] = max(0, 100 - cv * 100)

        return patterns

    async def _forecast_receivables(
        self,
        condominio_id: UUID,
        months_ahead: int,
    ) -> Decimal:
        """Preve receitas futuras."""
        today = date.today()
        future_date = today + timedelta(days=months_ahead * 30)

        # Busca contas a receber pendentes
        query = select(func.sum(ReceivableAccount.net_value)).where(
            and_(
                ReceivableAccount.condominio_id == condominio_id,
                ReceivableAccount.due_date >= today,
                ReceivableAccount.due_date <= future_date,
                ReceivableAccount.status.in_(
                    [
                        ReceivableStatus.PENDENTE.value,
                        ReceivableStatus.VENCIDA.value,
                    ]
                ),
                ReceivableAccount.ativo == True,  # noqa: E712
            )
        )

        result = await self.session.execute(query)
        total = result.scalar_one() or Decimal("0")

        # Aplica fator de inadimplencia (baseado em historico)
        # Por padrao, considera 95% de arrecadacao
        return total * Decimal("0.95")

    async def _forecast_payables(
        self,
        condominio_id: UUID,
        months_ahead: int,
    ) -> Decimal:
        """Preve despesas futuras."""
        today = date.today()
        future_date = today + timedelta(days=months_ahead * 30)

        # Busca contas a pagar pendentes
        query = select(func.sum(PayableAccount.net_value)).where(
            and_(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.due_date >= today,
                PayableAccount.due_date <= future_date,
                PayableAccount.status.in_(
                    [
                        PayableStatus.PENDENTE.value,
                        PayableStatus.APROVADA.value,
                        PayableStatus.VENCIDA.value,
                    ]
                ),
                PayableAccount.ativo == True,  # noqa: E712
            )
        )

        result = await self.session.execute(query)
        total = result.scalar_one() or Decimal("0")

        return total

    async def _generate_inflows_breakdown(
        self,
        condominio_id: UUID,
        months_ahead: int,
    ) -> Dict[str, float]:
        """Gera breakdown de entradas previstas."""
        today = date.today()
        future_date = today + timedelta(days=months_ahead * 30)

        # Agrupa por tipo/categoria
        query = (
            select(
                ReceivableAccount.account_type,
                func.sum(ReceivableAccount.net_value).label("total"),
            )
            .where(
                and_(
                    ReceivableAccount.condominio_id == condominio_id,
                    ReceivableAccount.due_date >= today,
                    ReceivableAccount.due_date <= future_date,
                    ReceivableAccount.status.in_(
                        [
                            ReceivableStatus.PENDENTE.value,
                            ReceivableStatus.VENCIDA.value,
                        ]
                    ),
                    ReceivableAccount.ativo == True,  # noqa: E712
                )
            )
            .group_by(ReceivableAccount.account_type)
        )

        result = await self.session.execute(query)
        return {row.account_type or "outros": float(row.total or 0) for row in result}

    async def _generate_outflows_breakdown(
        self,
        condominio_id: UUID,
        months_ahead: int,
    ) -> Dict[str, float]:
        """Gera breakdown de saidas previstas."""
        today = date.today()
        future_date = today + timedelta(days=months_ahead * 30)

        # Agrupa por tipo
        query = (
            select(
                PayableAccount.account_type,
                func.sum(PayableAccount.net_value).label("total"),
            )
            .where(
                and_(
                    PayableAccount.condominio_id == condominio_id,
                    PayableAccount.due_date >= today,
                    PayableAccount.due_date <= future_date,
                    PayableAccount.status.in_(
                        [
                            PayableStatus.PENDENTE.value,
                            PayableStatus.APROVADA.value,
                        ]
                    ),
                    PayableAccount.ativo == True,  # noqa: E712
                )
            )
            .group_by(PayableAccount.account_type)
        )

        result = await self.session.execute(query)
        return {row.account_type or "outros": float(row.total or 0) for row in result}

    def _calculate_confidence(
        self,
        historical_data: Dict[str, Any],
        patterns: Dict[str, float],
    ) -> int:
        """Calcula nivel de confianca da previsao."""
        confidence = 50  # Base

        # Mais dados historicos = mais confianca
        months = len(historical_data.get("months", []))
        if months >= 12:
            confidence += 20
        elif months >= 6:
            confidence += 10
        elif months >= 3:
            confidence += 5

        # Taxa de arrecadacao alta = mais confianca
        collection_rate = patterns.get("collection_rate", 0)
        if collection_rate >= 90:
            confidence += 15
        elif collection_rate >= 80:
            confidence += 10
        elif collection_rate >= 70:
            confidence += 5

        # Estabilidade de tendencia = mais confianca
        trend_stability = patterns.get("trend_stability", 0)
        if trend_stability >= 80:
            confidence += 10
        elif trend_stability >= 60:
            confidence += 5

        return min(100, max(0, confidence))

    def _generate_scenarios(self, forecast: CashFlowForecast) -> Dict[str, Dict[str, float]]:
        """Gera cenarios pessimista, realista e otimista."""
        expected_inflows = float(forecast.expected_inflows)
        expected_outflows = float(forecast.expected_outflows)
        opening_balance = float(forecast.expected_opening_balance)

        return {
            "pessimista": {
                "inflows": expected_inflows * 0.8,  # 80% das receitas
                "outflows": expected_outflows * 1.1,  # 110% das despesas
                "closing_balance": opening_balance
                + (expected_inflows * 0.8)
                - (expected_outflows * 1.1),
            },
            "realista": {
                "inflows": expected_inflows,
                "outflows": expected_outflows,
                "closing_balance": opening_balance + expected_inflows - expected_outflows,
            },
            "otimista": {
                "inflows": expected_inflows * 1.1,  # 110% das receitas
                "outflows": expected_outflows * 0.95,  # 95% das despesas
                "closing_balance": opening_balance
                + (expected_inflows * 1.1)
                - (expected_outflows * 0.95),
            },
        }

    def _identify_risks(
        self,
        forecast: CashFlowForecast,
        patterns: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Identifica riscos no fluxo de caixa."""
        risks = []

        # Risco de saldo negativo
        if forecast.expected_closing_balance < 0:
            risks.append(
                {
                    "risk_type": "saldo_negativo",
                    "probability": 0.8,
                    "impact": abs(forecast.expected_closing_balance),
                    "mitigation": "Antecipar recebimentos ou postergar pagamentos nao essenciais",
                }
            )

        # Risco de inadimplencia
        collection_rate = patterns.get("collection_rate", 100)
        if collection_rate < 85:
            expected_loss = forecast.expected_inflows * Decimal(str((100 - collection_rate) / 100))
            risks.append(
                {
                    "risk_type": "inadimplencia",
                    "probability": (100 - collection_rate) / 100,
                    "impact": expected_loss,
                    "mitigation": "Intensificar cobranca e oferecer acordos de pagamento",
                }
            )

        # Risco de sazonalidade
        seasonality = patterns.get("seasonality", 0)
        if seasonality > 30:
            risks.append(
                {
                    "risk_type": "sazonalidade",
                    "probability": 0.5,
                    "impact": forecast.expected_inflows * Decimal("0.15"),
                    "mitigation": "Manter reserva de contingencia para periodos de baixa",
                }
            )

        # Risco de concentracao de despesas
        if forecast.expected_outflows > forecast.expected_inflows * Decimal("1.2"):
            risks.append(
                {
                    "risk_type": "despesas_elevadas",
                    "probability": 0.6,
                    "impact": forecast.expected_outflows - forecast.expected_inflows,
                    "mitigation": "Revisar contratos e buscar reducao de custos",
                }
            )

        return risks

    def _identify_opportunities(
        self,
        forecast: CashFlowForecast,
        patterns: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades de otimizacao."""
        opportunities = []

        # Oportunidade de aplicacao financeira
        if forecast.expected_closing_balance > forecast.expected_outflows * Decimal("0.3"):
            excess = forecast.expected_closing_balance - (
                forecast.expected_outflows * Decimal("0.3")
            )
            opportunities.append(
                {
                    "opportunity_type": "aplicacao_financeira",
                    "probability": 0.9,
                    "value": excess * Decimal("0.01"),  # ~1% ao mes
                    "action": "Aplicar excedente em CDB ou fundo de liquidez diaria",
                }
            )

        # Oportunidade de desconto por antecipacao
        if forecast.expected_opening_balance > forecast.expected_payables * Decimal("0.5"):
            potential_savings = forecast.expected_payables * Decimal("0.02")  # 2% desconto
            opportunities.append(
                {
                    "opportunity_type": "desconto_antecipacao",
                    "probability": 0.7,
                    "value": potential_savings,
                    "action": "Negociar descontos para pagamento antecipado com fornecedores",
                }
            )

        # Oportunidade de reducao de inadimplencia
        collection_rate = patterns.get("collection_rate", 100)
        if collection_rate < 95:
            potential_recovery = forecast.expected_receivables * Decimal(
                str((95 - collection_rate) / 100)
            )
            opportunities.append(
                {
                    "opportunity_type": "recuperacao_credito",
                    "probability": 0.5,
                    "value": potential_recovery,
                    "action": "Implementar programa de cobranca preventiva",
                }
            )

        return opportunities

    async def _generate_alerts(self, forecast: CashFlowForecast) -> None:
        """Gera alertas para a previsao."""
        # Alerta de saldo negativo
        if forecast.expected_closing_balance < 0:
            forecast.add_alert(
                alert_type="saldo_negativo",
                alert_date=forecast.period_end,
                amount=abs(forecast.expected_closing_balance),
                severity="high",
                message="Previsao de saldo negativo ao final do periodo",
            )

        # Alerta de saidas altas
        if forecast.expected_outflows > forecast.expected_inflows * Decimal("1.3"):
            forecast.add_alert(
                alert_type="saida_alta",
                alert_date=forecast.period_start,
                amount=forecast.expected_outflows - forecast.expected_inflows,
                severity="medium",
                message="Despesas previstas excedem receitas em mais de 30%",
            )

        # Alerta de entradas baixas
        avg_inflows = await self._get_average_monthly_inflows(forecast.condominio_id)
        if forecast.expected_inflows < avg_inflows * Decimal("0.8"):
            forecast.add_alert(
                alert_type="entrada_baixa",
                alert_date=forecast.period_start,
                amount=avg_inflows - forecast.expected_inflows,
                severity="medium",
                message="Receitas previstas abaixo da media historica",
            )

    async def _get_average_monthly_inflows(self, condominio_id: UUID) -> Decimal:
        """Retorna media de receitas mensais."""
        end_date = date.today()
        start_date = end_date - timedelta(days=180)  # 6 meses

        query = select(func.avg(ReceivableAccount.net_value)).where(
            and_(
                ReceivableAccount.condominio_id == condominio_id,
                ReceivableAccount.due_date >= start_date,
                ReceivableAccount.due_date <= end_date,
                ReceivableAccount.status == ReceivableStatus.PAGA.value,
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one() or Decimal("0")

    async def detect_anomalies(
        self,
        condominio_id: UUID,
        period_months: int = 6,
        sensitivity: str = "medium",
    ) -> List[Dict[str, Any]]:
        """Detecta anomalias no fluxo de caixa."""
        logger.info(f"Detectando anomalias para {condominio_id}")
        anomalies = []

        # Coleta dados historicos
        historical_data = await self._collect_historical_data(condominio_id, period_months)
        monthly_data = historical_data.get("monthly_data", {})

        if len(monthly_data) < 3:
            return anomalies

        # Calcula limites baseados em sensibilidade
        thresholds = {
            "low": 2.5,
            "medium": 2.0,
            "high": 1.5,
        }
        threshold = thresholds.get(sensitivity, 2.0)

        # Analisa anomalias em receitas
        receivables = [float(d.get("receivables", Decimal("0"))) for d in monthly_data.values()]
        if receivables:
            avg_recv = sum(receivables) / len(receivables)
            std_recv = (sum((x - avg_recv) ** 2 for x in receivables) / len(receivables)) ** 0.5

            for month, data in monthly_data.items():
                value = float(data.get("receivables", Decimal("0")))
                if std_recv > 0:
                    z_score = abs(value - avg_recv) / std_recv
                    if z_score > threshold:
                        anomalies.append(
                            {
                                "type": "receita_anomala",
                                "month": month,
                                "value": value,
                                "expected": avg_recv,
                                "deviation": value - avg_recv,
                                "severity": "high" if z_score > 3 else "medium",
                                "description": (
                                    f"Receita de {month} fora do padrao "
                                    f"(desvio de {z_score:.1f} desvios padrao)"
                                ),
                            }
                        )

        # Analisa anomalias em despesas
        payables = [float(d.get("payables", Decimal("0"))) for d in monthly_data.values()]
        if payables:
            avg_pay = sum(payables) / len(payables)
            std_pay = (sum((x - avg_pay) ** 2 for x in payables) / len(payables)) ** 0.5

            for month, data in monthly_data.items():
                value = float(data.get("payables", Decimal("0")))
                if std_pay > 0:
                    z_score = abs(value - avg_pay) / std_pay
                    if z_score > threshold:
                        anomalies.append(
                            {
                                "type": "despesa_anomala",
                                "month": month,
                                "value": value,
                                "expected": avg_pay,
                                "deviation": value - avg_pay,
                                "severity": "high" if z_score > 3 else "medium",
                                "description": (
                                    f"Despesa de {month} fora do padrao "
                                    f"(desvio de {z_score:.1f} desvios padrao)"
                                ),
                            }
                        )

        return sorted(anomalies, key=lambda x: x.get("severity", "low"), reverse=True)

    async def suggest_optimizations(
        self,
        condominio_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Sugere otimizacoes para o fluxo de caixa."""
        logger.info(f"Gerando sugestoes de otimizacao para {condominio_id}")
        suggestions = []

        # Coleta dados
        historical_data = await self._collect_historical_data(condominio_id, months=6)
        patterns = await self._analyze_patterns(historical_data)

        # Sugestao: Melhorar arrecadacao
        collection_rate = patterns.get("collection_rate", 100)
        if collection_rate < 90:
            potential_improvement = historical_data.get(
                "total_receivables", Decimal("0")
            ) * Decimal(str((90 - collection_rate) / 100))
            suggestions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "melhoria_arrecadacao",
                    "title": "Aumentar taxa de arrecadacao",
                    "description": (
                        f"Taxa atual de {collection_rate:.1f}%. "
                        "Implementar cobranca preventiva pode aumentar para 90%+"
                    ),
                    "potential_savings": potential_improvement,
                    "implementation_effort": "medio",
                    "priority": "alta" if collection_rate < 80 else "media",
                    "action_items": [
                        "Enviar lembretes 7 dias antes do vencimento",
                        "Oferecer desconto para pagamento antecipado",
                        "Implementar cobranca via WhatsApp",
                        "Negociar acordos para inadimplentes",
                    ],
                }
            )

        # Sugestao: Renegociar contratos
        avg_outflow = patterns.get("average_monthly_outflow", 0)
        if avg_outflow > 0:
            potential_reduction = Decimal(str(avg_outflow * 0.05))  # 5% de reducao
            suggestions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "renegociacao_contratos",
                    "title": "Renegociar contratos com fornecedores",
                    "description": (
                        "Revisar contratos de servicos recorrentes pode gerar "
                        "economia de 5-10% nos custos fixos"
                    ),
                    "potential_savings": potential_reduction * 12,  # Anual
                    "implementation_effort": "alto",
                    "priority": "media",
                    "action_items": [
                        "Listar todos os contratos de servicos",
                        "Pesquisar alternativas no mercado",
                        "Negociar renovacao com descontos",
                        "Consolidar servicos quando possivel",
                    ],
                }
            )

        # Sugestao: Aplicacao de reservas
        current_balance = await self.account_repo.get_total_balance(condominio_id)
        if current_balance > Decimal(str(avg_outflow * 2)):
            excess = current_balance - Decimal(str(avg_outflow * 2))
            potential_yield = excess * Decimal("0.12")  # 12% ao ano
            suggestions.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "aplicacao_financeira",
                    "title": "Aplicar reservas excedentes",
                    "description": (
                        f"Saldo excedente de R$ {float(excess):.2f} pode ser "
                        "aplicado em investimentos de baixo risco"
                    ),
                    "potential_savings": potential_yield,
                    "implementation_effort": "baixo",
                    "priority": "alta",
                    "action_items": [
                        "Definir politica de reserva minima",
                        "Abrir conta em corretora",
                        "Aplicar em CDB de liquidez diaria",
                        "Monitorar rendimentos mensalmente",
                    ],
                }
            )

        return sorted(
            suggestions,
            key=lambda x: float(x.get("potential_savings", 0)),
            reverse=True,
        )

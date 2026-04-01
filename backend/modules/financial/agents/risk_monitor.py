"""RiskMonitorAgent — Monitora riscos financeiros e calcula health score."""

from datetime import date, timedelta

from sqlalchemy import and_, func, select

from modules.financial.agents.base_agent import BaseAgent
from modules.financial.models.payable_account import PayableAccount, PayableStatus
from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus


class RiskAlert:
    """Alerta de risco financeiro."""

    def __init__(
        self,
        level: str,
        category: str,
        title: str,
        description: str,
        value: float | None = None,
        action: str | None = None,
    ):
        self.level = level
        self.category = category
        self.title = title
        self.description = description
        self.value = value
        self.action = action

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "value": self.value,
            "action": self.action,
        }


class RiskMonitorAgent(BaseAgent):
    """Agente de monitoramento de riscos financeiros."""

    name = "risk_monitor"

    async def scan(self) -> list[dict]:
        """Executa varredura de riscos e retorna lista de alertas."""
        return await self.execute()

    async def health_check(self) -> dict:
        """Calcula o health score financeiro (0-100)."""
        today = date.today()
        past_90 = today - timedelta(days=90)

        try:
            # Taxa de inadimplência
            total_recv_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                and_(
                    ReceivableAccount.due_date >= past_90,
                    ReceivableAccount.due_date <= today,
                    ReceivableAccount.status != ReceivableStatus.CANCELADA.value,
                )
            )
            total_recv = float((await self.session.execute(total_recv_q)).scalar_one() or 0)

            overdue_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                and_(
                    ReceivableAccount.due_date < today,
                    ReceivableAccount.status.notin_(
                        [
                            ReceivableStatus.PAGA.value,
                            ReceivableStatus.CANCELADA.value,
                        ]
                    ),
                )
            )
            overdue = float((await self.session.execute(overdue_q)).scalar_one() or 0)

            default_rate = (overdue / total_recv * 100) if total_recv > 0 else 0.0

            # Tendência: comparar receita dos últimos 30d com 30d anteriores
            past_30 = today - timedelta(days=30)
            past_60 = today - timedelta(days=60)

            recv_recent_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                and_(
                    ReceivableAccount.payment_date >= past_30,
                    ReceivableAccount.payment_date <= today,
                    ReceivableAccount.status == ReceivableStatus.PAGA.value,
                )
            )
            recv_recent = float((await self.session.execute(recv_recent_q)).scalar_one() or 0)

            recv_prev_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                and_(
                    ReceivableAccount.payment_date >= past_60,
                    ReceivableAccount.payment_date < past_30,
                    ReceivableAccount.status == ReceivableStatus.PAGA.value,
                )
            )
            recv_prev = float((await self.session.execute(recv_prev_q)).scalar_one() or 0)

            if recv_recent > recv_prev * 1.02:
                trend = "positivo"
            elif recv_recent < recv_prev * 0.98:
                trend = "negativo"
            else:
                trend = "estavel"

            # Margem geral (últimos 30 dias)
            pay_recent_q = select(func.coalesce(func.sum(PayableAccount.net_value), 0)).where(
                and_(
                    PayableAccount.payment_date >= past_30,
                    PayableAccount.payment_date <= today,
                    PayableAccount.status == PayableStatus.PAGA.value,
                )
            )
            pay_recent = float((await self.session.execute(pay_recent_q)).scalar_one() or 0)

            margin = (recv_recent - pay_recent) / recv_recent * 100 if recv_recent > 0 else 0.0

            # Busca alertas críticos
            alerts_raw = await self._execute()
            critical_count = sum(1 for a in alerts_raw if isinstance(a, dict) and a.get("level") == "critico")

            # Pontuação
            score = 0

            # Inadimplência (25 pts)
            if default_rate < 2:
                score += 25
            elif default_rate < 5:
                score += 15

            # Tendência (25 pts)
            if trend == "positivo":
                score += 25
            elif trend == "estavel":
                score += 15

            # Margem (25 pts)
            if margin > 20:
                score += 25
            elif margin > 10:
                score += 15
            else:
                score += 5

            # Alertas críticos (25 pts)
            if critical_count == 0:
                score += 25
            elif critical_count == 1:
                score += 10

            if score >= 80:
                classification = "excelente"
            elif score >= 60:
                classification = "bom"
            elif score >= 40:
                classification = "atencao"
            else:
                classification = "critico"

            return {
                "score": score,
                "classification": classification,
                "default_rate": round(default_rate, 2),
                "trend": trend,
                "margin_avg": round(margin, 2),
                "alerts_count": len(alerts_raw),
                "critical_alerts": critical_count,
                "liquidity": round(total_recv - overdue, 2),
            }

        except Exception as exc:
            self.logger.warning(f"[{self.name}] Erro no health_check: {exc}")
            return {
                "score": 50,
                "classification": "atencao",
                "default_rate": 0.0,
                "trend": "estavel",
                "margin_avg": 0.0,
                "alerts_count": 0,
                "critical_alerts": 0,
                "liquidity": 0.0,
            }

    async def _execute(self, **kwargs) -> list[dict]:
        today = date.today()
        alerts: list[dict] = []

        # ----------------------------------------------------------------
        # 1. Alertas de inadimplência por faixa de atraso
        # ----------------------------------------------------------------
        try:
            overdue_q = select(
                ReceivableAccount.id,
                ReceivableAccount.net_value,
                ReceivableAccount.due_date,
                ReceivableAccount.customer_id,
            ).where(
                and_(
                    ReceivableAccount.due_date < today,
                    ReceivableAccount.status.notin_(
                        [
                            ReceivableStatus.PAGA.value,
                            ReceivableStatus.CANCELADA.value,
                            ReceivableStatus.BAIXADA.value,
                        ]
                    ),
                )
            )
            overdue_rows = (await self.session.execute(overdue_q)).all()

            buckets = {
                "amarelo": {"days": (5, 15), "total": 0.0, "count": 0},
                "laranja": {"days": (15, 30), "total": 0.0, "count": 0},
                "vermelho": {"days": (30, 60), "total": 0.0, "count": 0},
                "critico": {"days": (60, 99999), "total": 0.0, "count": 0},
            }

            for row in overdue_rows:
                days_late = (today - row.due_date).days
                value = float(row.net_value or 0)
                if days_late > 60:
                    buckets["critico"]["total"] += value
                    buckets["critico"]["count"] += 1
                elif days_late > 30:
                    buckets["vermelho"]["total"] += value
                    buckets["vermelho"]["count"] += 1
                elif days_late > 15:
                    buckets["laranja"]["total"] += value
                    buckets["laranja"]["count"] += 1
                elif days_late > 5:
                    buckets["amarelo"]["total"] += value
                    buckets["amarelo"]["count"] += 1

            label_map = {
                "amarelo": ("5 a 15 dias", "Enviar lembrete de cobrança"),
                "laranja": ("16 a 30 dias", "Acionar cobrança personalizada"),
                "vermelho": ("31 a 60 dias", "Negociar acordo de pagamento"),
                "critico": ("acima de 60 dias", "Considerar protesto ou baixa"),
            }
            for level, data in buckets.items():
                if data["count"] > 0:
                    label, action = label_map[level]
                    alerts.append(
                        RiskAlert(
                            level=level,
                            category="inadimplencia",
                            title=f"{data['count']} conta(s) em atraso ({label})",
                            description=(f"R$ {data['total']:,.2f} em recebíveis com atraso de {label}."),
                            value=round(data["total"], 2),
                            action=action,
                        ).to_dict()
                    )
        except Exception as exc:
            self.logger.debug(f"Erro ao calcular inadimplência: {exc}")

        # ----------------------------------------------------------------
        # 2. Alertas de liquidez (saldo projetado 7 dias vs despesas semanais)
        # ----------------------------------------------------------------
        try:
            week_ahead = today + timedelta(days=7)

            upcoming_pay_q = select(func.coalesce(func.sum(PayableAccount.net_value), 0)).where(
                and_(
                    PayableAccount.due_date >= today,
                    PayableAccount.due_date <= week_ahead,
                    PayableAccount.status.notin_(
                        [
                            PayableStatus.PAGA.value,
                            PayableStatus.CANCELADA.value,
                        ]
                    ),
                )
            )
            upcoming_pay = float((await self.session.execute(upcoming_pay_q)).scalar_one() or 0)

            # Receita prevista para os próximos 7 dias
            upcoming_recv_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                and_(
                    ReceivableAccount.due_date >= today,
                    ReceivableAccount.due_date <= week_ahead,
                    ReceivableAccount.status.notin_(
                        [
                            ReceivableStatus.PAGA.value,
                            ReceivableStatus.CANCELADA.value,
                        ]
                    ),
                )
            )
            upcoming_recv = float((await self.session.execute(upcoming_recv_q)).scalar_one() or 0)

            net_7d = upcoming_recv - upcoming_pay
            if net_7d < 0:
                alerts.append(
                    RiskAlert(
                        level="vermelho",
                        category="liquidez",
                        title=f"Déficit projetado em 7 dias: R$ {abs(net_7d):,.2f}",
                        description=(
                            f"Despesas de R$ {upcoming_pay:,.2f} superam receitas previstas "
                            f"de R$ {upcoming_recv:,.2f} nos próximos 7 dias."
                        ),
                        value=round(net_7d, 2),
                        action="Antecipar recebimentos ou postergar pagamentos não críticos",
                    ).to_dict()
                )
            elif upcoming_pay > 50000:
                alerts.append(
                    RiskAlert(
                        level="amarelo",
                        category="liquidez",
                        title=f"Vencimentos próximos: R$ {upcoming_pay:,.2f}",
                        description=("Concentração de pagamentos nos próximos 7 dias. Verifique o saldo disponível."),
                        value=round(upcoming_pay, 2),
                        action="Verificar saldo bancário e garantir liquidez",
                    ).to_dict()
                )
        except Exception as exc:
            self.logger.debug(f"Erro ao calcular liquidez: {exc}")

        # ----------------------------------------------------------------
        # 3. Alertas de concentração (cliente > 20% da receita)
        # ----------------------------------------------------------------
        try:
            total_recv_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                ReceivableAccount.status != ReceivableStatus.CANCELADA.value
            )
            total_recv = float((await self.session.execute(total_recv_q)).scalar_one() or 0)

            if total_recv > 0:
                top_q = (
                    select(
                        ReceivableAccount.customer_id,
                        func.sum(ReceivableAccount.net_value).label("total"),
                    )
                    .where(ReceivableAccount.status != ReceivableStatus.CANCELADA.value)
                    .where(ReceivableAccount.customer_id.isnot(None))
                    .group_by(ReceivableAccount.customer_id)
                    .order_by(func.sum(ReceivableAccount.net_value).desc())
                    .limit(1)
                )
                top_result = (await self.session.execute(top_q)).first()
                if top_result and top_result.total:
                    concentration = float(top_result.total / total_recv * 100)
                    if concentration > 20:
                        level = "vermelho" if concentration > 40 else "amarelo"
                        alerts.append(
                            RiskAlert(
                                level=level,
                                category="concentracao",
                                title=f"Concentração de receita: {concentration:.0f}% em 1 cliente",
                                description=(
                                    "Alto risco de dependência de um único cliente. "
                                    "Diversifique a base de clientes para reduzir exposição."
                                ),
                                value=round(float(top_result.total), 2),
                                action="Prospectar novos clientes para diluir concentração",
                            ).to_dict()
                        )
        except Exception as exc:
            self.logger.debug(f"Erro ao calcular concentração: {exc}")

        # ----------------------------------------------------------------
        # 4. Alertas de margem (receita - despesa / receita nos últimos 30d)
        # ----------------------------------------------------------------
        try:
            past_30 = today - timedelta(days=30)

            recv_30_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
                and_(
                    ReceivableAccount.payment_date >= past_30,
                    ReceivableAccount.payment_date <= today,
                    ReceivableAccount.status == ReceivableStatus.PAGA.value,
                )
            )
            recv_30 = float((await self.session.execute(recv_30_q)).scalar_one() or 0)

            pay_30_q = select(func.coalesce(func.sum(PayableAccount.net_value), 0)).where(
                and_(
                    PayableAccount.payment_date >= past_30,
                    PayableAccount.payment_date <= today,
                    PayableAccount.status == PayableStatus.PAGA.value,
                )
            )
            pay_30 = float((await self.session.execute(pay_30_q)).scalar_one() or 0)

            if recv_30 > 0:
                margin = (recv_30 - pay_30) / recv_30 * 100
                if margin < 5:
                    alerts.append(
                        RiskAlert(
                            level="vermelho",
                            category="margem",
                            title=f"Margem operacional crítica: {margin:.1f}%",
                            description=(
                                f"Receita de R$ {recv_30:,.2f} e despesas de R$ {pay_30:,.2f} "
                                "nos últimos 30 dias resultam em margem abaixo do mínimo recomendado."
                            ),
                            value=round(margin, 2),
                            action="Revisar custos operacionais e estratégia de precificação",
                        ).to_dict()
                    )
                elif margin < 10:
                    alerts.append(
                        RiskAlert(
                            level="laranja",
                            category="margem",
                            title=f"Margem operacional baixa: {margin:.1f}%",
                            description=(
                                f"Margem de {margin:.1f}% está abaixo do ideal (>10%). Monitore a evolução dos custos."
                            ),
                            value=round(margin, 2),
                            action="Analisar contratos com margem negativa ou baixa",
                        ).to_dict()
                    )
        except Exception as exc:
            self.logger.debug(f"Erro ao calcular margem: {exc}")

        return alerts

    async def _fallback(self, **kwargs) -> list[dict]:
        """Retorna lista vazia em caso de falha."""
        return []

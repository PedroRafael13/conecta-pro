"""CashflowPredictorAgent — Projeção de fluxo de caixa com dados históricos."""

from datetime import date, timedelta

from sqlalchemy import and_, func, select

from modules.financial.agents.base_agent import BaseAgent
from modules.financial.agents.skill_loader import SkillLoader
from modules.financial.models.payable_account import PayableAccount, PayableStatus
from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus


class CashflowPredictorAgent(BaseAgent):
    """Agente de projeção de fluxo de caixa."""

    name = "cashflow_predictor"

    def _load_skills(self) -> str:
        """Carrega skills de projeção e análise cashflow."""
        return SkillLoader.load_multiple(
            [
                "projecao-fluxo-caixa-12-meses",
                "analise-fluxo-caixa-real",
                "metas-smart-financeiras",
            ]
        )

    def _get_enriched_system_prompt(self, base_prompt: str = "") -> str:
        """System prompt com contexto real de caixa Conecta Mais."""
        skills = self._load_skills()
        return f"""Você é o CashflowPredictorAgent da Conecta Mais.

ESTADO ATUAL DO CAIXA (dados reais):
- Saldo Inter: R$88.684,29 (🔴 CRÍTICO — runway ~12 dias)
- MRR garantido: R$270.586,96 (contratos recorrentes)
- MRR líquido: R$243.241,98 (entra no banco após retenções)
- Custo fixo mensal: ~R$88.360,22
- Semáforo: 🔴 VERMELHO (saldo < 1x custo fixo)

HISTÓRICO REAL (jan-abr/2026):
Jan: entradas R$237k, saídas R$245k → -R$7.4k
Fev: entradas R$247k, saídas R$258k → -R$10.6k
Mar: entradas R$495k, saídas R$439k → +R$56.9k (atípico)
Abr (13d): entradas R$150k, saídas R$124k → +R$26.2k

SKILLS DE PROJEÇÃO:
{skills}

{base_prompt}

Sempre retorne 3 cenários (pessimista/esperado/otimista).
Sinalize meses com saldo projetado < R$88k com ALERTA VERMELHO."""

    async def predict(self, days: int = 90) -> dict:
        """Gera projeção de fluxo de caixa para os próximos N dias."""
        return await self.execute(days=days)

    async def _execute(self, days: int = 90, **kwargs) -> dict:
        today = date.today()
        past_90 = today - timedelta(days=90)

        # ----------------------------------------------------------------
        # 1. Receita histórica dos últimos 90 dias (recebíveis pagos)
        # ----------------------------------------------------------------
        recv_hist_q = select(func.coalesce(func.sum(ReceivableAccount.net_value), 0)).where(
            and_(
                ReceivableAccount.payment_date >= past_90,
                ReceivableAccount.payment_date <= today,
                ReceivableAccount.status == ReceivableStatus.PAGA.value,
            )
        )
        total_recv_hist = float((await self.session.execute(recv_hist_q)).scalar_one() or 0)

        # ----------------------------------------------------------------
        # 2. Despesa histórica dos últimos 90 dias (pagáveis pagos)
        # ----------------------------------------------------------------
        pay_hist_q = select(func.coalesce(func.sum(PayableAccount.net_value), 0)).where(
            and_(
                PayableAccount.payment_date >= past_90,
                PayableAccount.payment_date <= today,
                PayableAccount.status == PayableStatus.PAGA.value,
            )
        )
        total_pay_hist = float((await self.session.execute(pay_hist_q)).scalar_one() or 0)

        has_history = total_recv_hist > 0 or total_pay_hist > 0
        daily_recv = total_recv_hist / 90 if has_history else 0.0
        daily_pay = total_pay_hist / 90 if has_history else 0.0

        # ----------------------------------------------------------------
        # 3. Taxa de inadimplência histórica (recebíveis que atrasaram)
        # ----------------------------------------------------------------
        total_recv_due_q = select(func.coalesce(func.count(ReceivableAccount.id), 0)).where(
            and_(
                ReceivableAccount.due_date >= past_90,
                ReceivableAccount.due_date <= today,
            )
        )
        total_due_count = float((await self.session.execute(total_recv_due_q)).scalar_one() or 0)

        late_recv_q = select(func.coalesce(func.count(ReceivableAccount.id), 0)).where(
            and_(
                ReceivableAccount.due_date >= past_90,
                ReceivableAccount.due_date <= today,
                ReceivableAccount.status.notin_(
                    [
                        ReceivableStatus.PAGA.value,
                        ReceivableStatus.CANCELADA.value,
                    ]
                ),
                ReceivableAccount.due_date < today,
            )
        )
        late_count = float((await self.session.execute(late_recv_q)).scalar_one() or 0)

        default_rate = (late_count / total_due_count) if total_due_count > 0 else 0.0

        # ----------------------------------------------------------------
        # 4. Recebíveis PENDENTES futuros
        # ----------------------------------------------------------------
        pending_recv_q = select(
            ReceivableAccount.due_date,
            ReceivableAccount.net_value,
        ).where(
            and_(
                ReceivableAccount.due_date >= today,
                ReceivableAccount.status.notin_(
                    [
                        ReceivableStatus.PAGA.value,
                        ReceivableStatus.CANCELADA.value,
                        ReceivableStatus.BAIXADA.value,
                    ]
                ),
            )
        )
        pending_recv_rows = (await self.session.execute(pending_recv_q)).all()

        # Mapa: dia -> valor esperado (ajustado pela taxa de inadimplência)
        recv_by_day: dict[date, float] = {}
        for row in pending_recv_rows:
            d = row.due_date
            v = float(row.net_value or 0) * (1.0 - default_rate)
            recv_by_day[d] = recv_by_day.get(d, 0.0) + v

        # ----------------------------------------------------------------
        # 5. Pagáveis PENDENTES futuros
        # ----------------------------------------------------------------
        pending_pay_q = select(
            PayableAccount.due_date,
            PayableAccount.net_value,
        ).where(
            and_(
                PayableAccount.due_date >= today,
                PayableAccount.status.notin_(
                    [
                        PayableStatus.PAGA.value,
                        PayableStatus.CANCELADA.value,
                    ]
                ),
            )
        )
        pending_pay_rows = (await self.session.execute(pending_pay_q)).all()

        pay_by_day: dict[date, float] = {}
        for row in pending_pay_rows:
            d = row.due_date
            v = float(row.net_value or 0)
            pay_by_day[d] = pay_by_day.get(d, 0.0) + v

        # ----------------------------------------------------------------
        # 6. Saldo atual estimado (net histórico dos últimos 30d)
        # ----------------------------------------------------------------
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

        current_balance = recv_30 - pay_30

        # ----------------------------------------------------------------
        # 7. Projeção diária acumulada por N dias
        # ----------------------------------------------------------------
        running_balance = current_balance
        balance_by_day: dict[int, float] = {0: current_balance}

        for offset in range(1, days + 1):
            d = today + timedelta(days=offset)
            daily_in = recv_by_day.get(d, daily_recv)
            daily_out = pay_by_day.get(d, daily_pay)
            running_balance += daily_in - daily_out
            balance_by_day[offset] = running_balance

        # ----------------------------------------------------------------
        # 8. Pontos a cada 7 dias
        # ----------------------------------------------------------------
        points = []
        gaps = []
        for offset in range(7, days + 1, 7):
            d = today + timedelta(days=offset)
            expected = balance_by_day.get(offset, current_balance)
            optimistic = expected * 1.10 if expected >= 0 else expected * 0.90
            pessimistic = expected * 0.90 if expected >= 0 else expected * 1.10
            points.append(
                {
                    "date": d.isoformat(),
                    "expected_balance": round(expected, 2),
                    "optimistic_balance": round(optimistic, 2),
                    "pessimistic_balance": round(pessimistic, 2),
                }
            )
            if pessimistic < 0:
                gaps.append(
                    {
                        "date": d.isoformat(),
                        "projected_balance": round(pessimistic, 2),
                    }
                )

        predicted_30d = balance_by_day.get(30, current_balance)
        predicted_60d = balance_by_day.get(60, current_balance)
        predicted_90d = balance_by_day.get(90, current_balance)

        # Tendência baseada nos primeiros 30 dias
        if predicted_30d > current_balance * 1.02:
            trend = "positivo"
        elif predicted_30d < current_balance * 0.98:
            trend = "negativo"
        else:
            trend = "estavel"

        # Confiança baseada no volume de dados históricos
        if total_recv_hist > 0 and total_pay_hist > 0:
            confidence = 0.80
        elif total_recv_hist > 0 or total_pay_hist > 0:
            confidence = 0.50
        else:
            confidence = 0.30

        return {
            "current_balance": round(current_balance, 2),
            "predicted_30d": round(predicted_30d, 2),
            "predicted_60d": round(predicted_60d, 2),
            "predicted_90d": round(predicted_90d, 2),
            "trend": trend,
            "confidence": confidence,
            "points": points,
            "gaps": gaps,
            "scenario_optimistic": round(predicted_90d * 1.15 if predicted_90d >= 0 else predicted_90d * 0.85, 2),
            "scenario_pessimistic": round(predicted_90d * 0.85 if predicted_90d >= 0 else predicted_90d * 1.15, 2),
        }

    async def _fallback(self, days: int = 90, **kwargs) -> dict:
        """Retorna projeção neutra quando a execução principal falha."""
        today = date.today()
        points = []
        for offset in range(7, days + 1, 7):
            d = today + timedelta(days=offset)
            points.append(
                {
                    "date": d.isoformat(),
                    "expected_balance": 0.0,
                    "optimistic_balance": 0.0,
                    "pessimistic_balance": 0.0,
                }
            )
        return {
            "current_balance": 0.0,
            "predicted_30d": 0.0,
            "predicted_60d": 0.0,
            "predicted_90d": 0.0,
            "trend": "estavel",
            "confidence": 0.30,
            "points": points,
            "gaps": [],
            "scenario_optimistic": 0.0,
            "scenario_pessimistic": 0.0,
        }

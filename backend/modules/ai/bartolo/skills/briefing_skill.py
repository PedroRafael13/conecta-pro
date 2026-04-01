"""
BriefingSkill — Briefing Executivo Diario para Jordan Jesus (CEO).

Consulta dados reais do banco e gera resumo executivo.
Tabelas consultadas: bank_accounts, bank_transactions, nfses,
receivable_accounts, payable_accounts, employees, contracts, billing_rules.
"""

import logging
from datetime import date, datetime
from typing import Any

from modules.ai.bartolo.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class BriefingSkill(BaseSkill):
    """Gera briefing executivo diario."""

    name = "briefing"
    description = "Briefing executivo diario do CEO"
    commands = ["briefing", "resumo", "bom dia"]

    MRR_REF = 272086.96

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Executa o briefing."""
        db = context.get("db")
        if not db:
            return {"response": self._fallback(), "tipo": "briefing_fallback"}

        dados = await self._coletar_dados(db)
        texto = self._formatar(dados)
        return {"response": texto, "dados": dados, "tipo": "briefing"}

    def get_help(self) -> str:
        return "/briefing — Briefing executivo do dia"

    async def _coletar_dados(self, db: Any) -> dict:
        """Coleta dados de todas as areas."""
        from sqlalchemy import text

        hoje = date.today()
        mes_inicio = hoje.replace(day=1)
        d: dict[str, Any] = {}

        # Saldo bancario
        try:
            r = (
                await db.execute(text("SELECT SUM(current_balance) as total FROM bank_accounts WHERE ativo = true"))
            ).fetchone()
            d["saldo"] = float(r.total or 0) if r else 0
        except Exception:
            d["saldo"] = 0

        # NFS-e do mes
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT COUNT(*) as qtd, COALESCE(SUM(valor_servicos),0) as total "
                        "FROM nfses WHERE data_emissao >= :ini"
                    ),
                    {"ini": mes_inicio},
                )
            ).fetchone()
            d["nfse_qtd"] = int(r.qtd) if r else 0
            d["nfse_total"] = float(r.total) if r else 0
        except Exception:
            d["nfse_qtd"] = 0
            d["nfse_total"] = 0

        # Receivables vencidos
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT COUNT(*) as vencidos, "
                        "COALESCE(SUM(gross_value),0) as valor "
                        "FROM receivable_accounts "
                        "WHERE due_date < :hoje AND status = 'pendente'"
                    ),
                    {"hoje": hoje},
                )
            ).fetchone()
            d["vencidos"] = int(r.vencidos) if r else 0
            d["valor_vencido"] = float(r.valor) if r else 0
        except Exception:
            d["vencidos"] = 0
            d["valor_vencido"] = 0

        # Receivables vencendo em 3 dias
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT COUNT(*) as qtd, COALESCE(SUM(gross_value),0) as valor "
                        "FROM receivable_accounts "
                        "WHERE due_date BETWEEN :hoje AND :fim AND status = 'pendente'"
                    ),
                    {"hoje": hoje, "fim": date(hoje.year, hoje.month, min(hoje.day + 3, 28))},
                )
            ).fetchone()
            d["vencendo_3d"] = int(r.qtd) if r else 0
            d["valor_vencendo"] = float(r.valor) if r else 0
        except Exception:
            d["vencendo_3d"] = 0
            d["valor_vencendo"] = 0

        # Funcionarios
        try:
            r = (await db.execute(text("SELECT COUNT(*) as total FROM employees WHERE status = 'ativo'"))).fetchone()
            d["funcionarios"] = int(r.total) if r else 0
        except Exception:
            d["funcionarios"] = 0

        # Contratos ativos
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT COUNT(*) as total, COALESCE(SUM(monthly_value),0) as mrr "
                        "FROM contracts WHERE status = 'ativo'"
                    )
                )
            ).fetchone()
            d["contratos"] = int(r.total) if r else 0
            d["mrr"] = float(r.mrr) if r else 0
        except Exception:
            d["contratos"] = 0
            d["mrr"] = self.MRR_REF

        # Transacoes bancarias recentes (ultimos 7 dias)
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT COUNT(*) as qtd, COALESCE(SUM(amount),0) as total "
                        "FROM bank_transactions "
                        "WHERE transaction_date >= :ini AND transaction_type = 'credit'"
                    ),
                    {"ini": date(hoje.year, hoje.month, max(hoje.day - 7, 1))},
                )
            ).fetchone()
            d["tx_7d_qtd"] = int(r.qtd) if r else 0
            d["tx_7d_total"] = float(r.total) if r else 0
        except Exception:
            d["tx_7d_qtd"] = 0
            d["tx_7d_total"] = 0

        # Conciliacao
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT "
                        "COUNT(*) FILTER (WHERE reconciliation_status='conciliado') as ok, "
                        "COUNT(*) FILTER (WHERE reconciliation_status='pendente') as pend "
                        "FROM bank_transactions"
                    )
                )
            ).fetchone()
            d["conc_ok"] = int(r.ok) if r else 0
            d["conc_pend"] = int(r.pend) if r else 0
        except Exception:
            d["conc_ok"] = 0
            d["conc_pend"] = 0

        # Payables proximos
        try:
            r = (
                await db.execute(
                    text(
                        "SELECT COUNT(*) as qtd, COALESCE(SUM(gross_value),0) as total "
                        "FROM payable_accounts "
                        "WHERE due_date BETWEEN :hoje AND :fim AND status = 'pendente'"
                    ),
                    {"hoje": hoje, "fim": date(hoje.year, hoje.month, min(hoje.day + 7, 28))},
                )
            ).fetchone()
            d["pagar_7d"] = int(r.qtd) if r else 0
            d["pagar_7d_valor"] = float(r.total) if r else 0
        except Exception:
            d["pagar_7d"] = 0
            d["pagar_7d_valor"] = 0

        return d

    def _formatar(self, d: dict) -> str:
        """Formata o briefing em texto."""
        hoje = datetime.now()
        dias = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
        dia = dias[hoje.weekday()]

        def fmt(v: float) -> str:
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        linhas = [
            f"Bom dia, Jordan. {dia}, {hoje.strftime('%d/%m/%Y')}.",
            "",
            "FINANCEIRO",
            f"  Saldo bancario: {fmt(d['saldo'])}",
            f"  MRR: {fmt(d['mrr'])} ({d['contratos']} contratos)",
            f"  NFS-e mes: {d['nfse_qtd']} notas ({fmt(d['nfse_total'])})",
            f"  Recebimentos 7d: {d['tx_7d_qtd']} creditos ({fmt(d['tx_7d_total'])})",
        ]

        if d["vencidos"] > 0:
            linhas.append(f"  ALERTA: {d['vencidos']} receivable(s) VENCIDO(S) ({fmt(d['valor_vencido'])})")
        if d["vencendo_3d"] > 0:
            linhas.append(f"  Vencendo em 3 dias: {d['vencendo_3d']} ({fmt(d['valor_vencendo'])})")
        if d["pagar_7d"] > 0:
            linhas.append(f"  A pagar 7 dias: {d['pagar_7d']} ({fmt(d['pagar_7d_valor'])})")

        linhas.extend(
            [
                "",
                "EQUIPE",
                f"  Funcionarios ativos: {d['funcionarios']}",
                "",
                "CONCILIACAO",
                f"  Conciliados: {d['conc_ok']} | Pendentes: {d['conc_pend']}",
                "",
                "O que priorizo primeiro?",
            ]
        )

        return "\n".join(linhas)

    def _fallback(self) -> str:
        return (
            f"Bom dia, Jordan. {datetime.now().strftime('%d/%m/%Y')}.\n"
            "Briefing indisponivel — banco de dados nao acessivel.\n"
            "O que priorizo primeiro?"
        )

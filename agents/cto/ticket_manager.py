"""
TicketManager — Gerenciador de tickets do CTO.
Formato profissional com histórico, SLA e relatórios.

Estrutura do ticket:
CTO-XXXX | Severidade | Categoria | Status
Timeline de ações | Causa raiz | Solução | Lição aprendida
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


TICKETS_DIR = Path("/opt/conecta-pro/agents/cto/tickets")

# SLA por severidade (horas para resolução)
SLA = {
    "critica": 1,
    "alta": 4,
    "media": 24,
    "baixa": 72,
    "info": 168,
}


class TicketManager:
    """Gerenciador profissional de tickets do CTO."""

    def __init__(self):
        TICKETS_DIR.mkdir(parents=True, exist_ok=True)

    def criar(
        self,
        titulo: str,
        descricao: str,
        severidade: str,
        categoria: str,
        causa_raiz: str = "",
        solucao_proposta: str = "",
        auto_resolvido: bool = False,
        requer_jordan: bool = False,
        componente: str = "",
    ) -> dict:
        """Cria ticket numerado com SLA."""
        existentes = list(TICKETS_DIR.glob("CTO-*.json"))
        numero = len(existentes) + 1
        ticket_id = f"CTO-{numero:04d}"

        sla_horas = SLA.get(severidade, 24)
        prazo = datetime.now() + timedelta(hours=sla_horas)

        ticket = {
            "numero": ticket_id,
            "titulo": titulo,
            "descricao": descricao,
            "severidade": severidade,
            "categoria": categoria,
            "componente": componente,
            "causa_raiz": causa_raiz,
            "solucao_proposta": solucao_proposta,
            "solucao_aplicada": "",
            "licao_aprendida": "",
            "status": "resolvido" if auto_resolvido else "aberto",
            "auto_resolvido": auto_resolvido,
            "requer_jordan": requer_jordan,
            "sla_horas": sla_horas,
            "prazo_resolucao": prazo.isoformat(),
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat(),
            "resolvido_em": (
                datetime.now().isoformat() if auto_resolvido else None
            ),
            "timeline": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "acao": "Ticket criado",
                    "autor": "CTO_Autonomo",
                    "detalhe": descricao[:100],
                }
            ],
        }

        f = TICKETS_DIR / f"{ticket_id}.json"
        f.write_text(
            json.dumps(ticket, indent=2, ensure_ascii=False, default=str)
        )

        print(
            f"[TicketManager] {ticket_id} criado "
            f"[{severidade.upper()}] {titulo[:40]}"
        )
        return ticket

    def atualizar(
        self,
        numero: str,
        acao: str,
        status: str = None,
        solucao_aplicada: str = "",
        licao: str = "",
        autor: str = "CTO_Autonomo",
    ) -> dict:
        """Atualiza ticket com nova ação na timeline."""
        f = TICKETS_DIR / f"{numero}.json"
        if not f.exists():
            return {"erro": f"{numero} não encontrado"}

        ticket = json.loads(f.read_text())

        ticket["timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "acao": acao,
            "autor": autor,
            "detalhe": solucao_aplicada[:100] if solucao_aplicada else "",
        })

        if status:
            ticket["status"] = status
            ticket["atualizado_em"] = datetime.now().isoformat()
            if status == "resolvido":
                ticket["resolvido_em"] = datetime.now().isoformat()
                if solucao_aplicada:
                    ticket["solucao_aplicada"] = solucao_aplicada
                if licao:
                    ticket["licao_aprendida"] = licao
                # Gerar pós-mortem automaticamente
                try:
                    import sys
                    sys.path.insert(0, "/opt/conecta-pro/agents/cto")
                    from pos_mortem import PósMortem
                    PósMortem().gerar(ticket)
                except Exception as e:
                    print(f"[PM] {e}")

        f.write_text(
            json.dumps(ticket, indent=2, ensure_ascii=False, default=str)
        )
        return ticket

    def formatar_telegram(self, ticket: dict) -> str:
        """Formata ticket para envio no Telegram."""
        sev_emoji = {
            "critica": "🔴", "alta": "🟠",
            "media": "🟡", "baixa": "🟢", "info": "ℹ️",
        }.get(ticket["severidade"], "⚪")

        status_emoji = (
            "✅" if ticket["status"] == "resolvido"
            else "🔄" if ticket["status"] == "em_progresso"
            else "⏳"
        )

        msg = (
            f"{sev_emoji} *{ticket['numero']}* "
            f"{status_emoji}\n"
            f"*{ticket['titulo']}*\n\n"
            f"📂 {ticket['categoria']} | "
            f"⚡ {ticket['severidade'].upper()}\n"
        )

        if ticket.get("componente"):
            msg += f"🔧 Componente: `{ticket['componente']}`\n"

        msg += f"\n📝 _{ticket['descricao'][:150]}_\n"

        if ticket.get("causa_raiz"):
            msg += (
                f"\n🔍 *Causa raiz:*\n"
                f"_{ticket['causa_raiz'][:120]}_\n"
            )

        if ticket.get("solucao_aplicada"):
            msg += (
                f"\n💡 *Solução aplicada:*\n"
                f"_{ticket['solucao_aplicada'][:100]}_\n"
            )

        if ticket.get("licao_aprendida"):
            msg += (
                f"\n📚 *Lição:* "
                f"_{ticket['licao_aprendida'][:80]}_\n"
            )

        # Timeline (últimas 3)
        timeline = ticket.get("timeline", [])[-3:]
        if timeline:
            msg += "\n📜 *Timeline:*\n"
            for t in timeline:
                ts = t["timestamp"][:16]
                msg += f"  `{ts}` {t['acao']}\n"

        if ticket.get("requer_jordan"):
            msg += "\n📋 _Requer atenção de Jordan_"

        return msg

    def listar(
        self,
        status: str = None,
        severidade: str = None,
        limit: int = 10,
    ) -> list:
        """Lista tickets com filtros."""
        tickets = []
        for f in sorted(TICKETS_DIR.glob("CTO-*.json"), reverse=True):
            try:
                t = json.loads(f.read_text())
                if status and t.get("status") != status:
                    continue
                if severidade and t.get("severidade") != severidade:
                    continue
                tickets.append(t)
            except Exception:
                pass
        return tickets[:limit]

    def relatorio_periodo(self, dias: int = 7) -> str:
        """Relatório de tickets dos últimos N dias."""
        cutoff = datetime.now() - timedelta(days=dias)

        todos = self.listar(limit=200)
        periodo = [
            t for t in todos
            if datetime.fromisoformat(
                t["criado_em"].replace("Z", "")
            ) > cutoff
        ]

        resolvidos = [t for t in periodo if t["status"] == "resolvido"]
        abertos = [t for t in periodo if t["status"] == "aberto"]
        auto = [t for t in resolvidos if t.get("auto_resolvido")]

        por_sev: dict = {}
        for t in periodo:
            s = t["severidade"]
            por_sev[s] = por_sev.get(s, 0) + 1

        _ordem = ["critica", "alta", "media", "baixa", "info"]
        msg = (
            f"📊 *Relatório CTO — últimos {dias} dias*\n\n"
            f"Total: {len(periodo)} tickets\n"
            f"✅ Resolvidos: {len(resolvidos)} "
            f"({len(auto)} automáticos)\n"
            f"⏳ Abertos: {len(abertos)}\n\n"
            f"*Por severidade:*\n"
        )
        for sev, count in sorted(
            por_sev.items(),
            key=lambda x: _ordem.index(x[0]) if x[0] in _ordem else 99,
        ):
            emoji = {
                "critica": "🔴", "alta": "🟠",
                "media": "🟡", "baixa": "🟢", "info": "ℹ️",
            }.get(sev, "⚪")
            msg += f"  {emoji} {sev}: {count}\n"

        return msg

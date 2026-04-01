"""
CTO Brain — Cérebro do CTO Autônomo da Conecta Mais.
Centraliza conhecimento, raciocínio e memória de negócio.

Schema real do banco (descoberto durante Sprint 1):
- clients: status='active', colunas: name, trading_name, document_number, client_type
- employees: status='ativo', colunas: nome, cargo, salario_base
- posts: status='active', client_id
- allocations: status='active', post_id, employee_id
- gp_clock_punches: punch_timestamp (não punch_time!)
- payable_accounts: status='pendente', net_value
- receivable_accounts: status='pendente', net_value
- bidding_opportunities: objeto, valor_estimado, data_abertura
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

CTO_DIR = Path("/opt/conecta-pro/agents/cto")
KNOWLEDGE_DIR = CTO_DIR / "knowledge"
TICKETS_DIR = CTO_DIR / "tickets"
MEMORY_DIR = CTO_DIR / "memory"

for d in [KNOWLEDGE_DIR, TICKETS_DIR, MEMORY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Credenciais do banco (lidas do .env em runtime)
_PG_PASS = None
_PG_IP = None


def _get_pg_conn():
    """Abre conexão com PostgreSQL usando psycopg2."""
    global _PG_PASS, _PG_IP
    if not _PG_PASS:
        env = Path("/opt/conecta-pro/.env")
        for line in env.read_text().splitlines():
            if line.startswith("POSTGRES_PASSWORD=") and "STAGING" not in line:
                _PG_PASS = line.split("=", 1)[1].strip()
    if not _PG_IP:
        r = subprocess.run(
            "docker inspect conecta-pro-postgres "
            "--format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'",
            shell=True, capture_output=True, text=True,
        )
        _PG_IP = r.stdout.strip().split("\n")[0]

    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(
        host=_PG_IP, port="5432", dbname="conecta_pro",
        user="postgres", password=_PG_PASS, connect_timeout=5,
    )
    return conn, conn.cursor(cursor_factory=RealDictCursor)


class CTOBrain:
    """Cérebro do CTO — conhecimento + raciocínio + memória."""

    def __init__(self):
        self.conhecimento = self._carregar_conhecimento()
        self.memoria = self._carregar_memoria()
        self.proximo_ticket = self.memoria.get("total_tickets", 0) + 1

    # ─── PERSISTÊNCIA ─────────────────────────────────

    def _carregar_conhecimento(self) -> dict:
        conhecimento = {}
        for f in KNOWLEDGE_DIR.glob("*.json"):
            try:
                conhecimento[f.stem] = json.loads(f.read_text())
            except Exception:
                pass
        return conhecimento

    def _carregar_memoria(self) -> dict:
        mem_file = MEMORY_DIR / "memoria.json"
        if mem_file.exists():
            try:
                return json.loads(mem_file.read_text())
            except Exception:
                pass
        return {
            "total_tickets": 0,
            "incidentes_resolvidos": 0,
            "problemas_recorrentes": {},
            "solucoes_aprovadas": {},
            "aprendizados": [],
        }

    def _salvar_memoria(self):
        (MEMORY_DIR / "memoria.json").write_text(
            json.dumps(self.memoria, indent=2, ensure_ascii=False, default=str)
        )

    def _q(self, sql: str) -> list:
        """Executa query no banco e retorna lista de dicts."""
        try:
            conn, cur = _get_pg_conn()
            cur.execute(sql)
            rows = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            return []

    def _q1(self, sql: str) -> dict:
        r = self._q(sql)
        return r[0] if r else {}

    # ─── TICKETS ──────────────────────────────────────

    def criar_ticket(
        self,
        titulo: str,
        descricao: str,
        severidade: str,
        categoria: str,
        causa_raiz: str = "",
        solucao_proposta: str = "",
        auto_resolvido: bool = False,
        requer_jordan: bool = False,
    ) -> dict:
        """Cria ticket numerado com histórico completo."""
        numero = self.proximo_ticket
        self.proximo_ticket += 1
        self.memoria["total_tickets"] = numero

        ticket = {
            "numero": f"CTO-{numero:04d}",
            "titulo": titulo,
            "descricao": descricao,
            "severidade": severidade,
            "categoria": categoria,
            "causa_raiz": causa_raiz,
            "solucao_proposta": solucao_proposta,
            "auto_resolvido": auto_resolvido,
            "requer_jordan": requer_jordan,
            "status": "resolvido" if auto_resolvido else "aberto",
            "criado_em": datetime.now().isoformat(),
            "resolvido_em": datetime.now().isoformat() if auto_resolvido else None,
            "historico": [{
                "timestamp": datetime.now().isoformat(),
                "acao": "Ticket criado pelo CTO Autônomo",
                "autor": "CTO_Autonomo",
            }],
        }

        (TICKETS_DIR / f"{ticket['numero']}.json").write_text(
            json.dumps(ticket, indent=2, ensure_ascii=False, default=str)
        )

        if auto_resolvido:
            self.memoria["incidentes_resolvidos"] += 1

        key = f"{categoria}:{titulo[:30]}"
        self.memoria["problemas_recorrentes"][key] = (
            self.memoria["problemas_recorrentes"].get(key, 0) + 1
        )
        self._salvar_memoria()
        return ticket

    def atualizar_ticket(
        self,
        numero: str,
        acao: str,
        status: str = None,
        resultado: str = "",
    ) -> dict:
        ticket_file = TICKETS_DIR / f"{numero}.json"
        if not ticket_file.exists():
            return {"erro": f"Ticket {numero} não encontrado"}

        ticket = json.loads(ticket_file.read_text())
        ticket["historico"].append({
            "timestamp": datetime.now().isoformat(),
            "acao": acao,
            "resultado": resultado,
            "autor": "CTO_Autonomo",
        })
        if status:
            ticket["status"] = status
            if status == "resolvido":
                ticket["resolvido_em"] = datetime.now().isoformat()
                self.memoria["incidentes_resolvidos"] += 1
                self._salvar_memoria()

        ticket_file.write_text(
            json.dumps(ticket, indent=2, ensure_ascii=False, default=str)
        )
        return ticket

    def listar_tickets(self, status: str = None, limit: int = 10) -> list:
        tickets = []
        for f in sorted(TICKETS_DIR.glob("*.json"), reverse=True)[:50]:
            try:
                t = json.loads(f.read_text())
                if status is None or t.get("status") == status:
                    tickets.append(t)
            except Exception:
                pass
        return tickets[:limit]

    # ─── DIAGNÓSTICO INTELIGENTE ──────────────────────

    def diagnosticar(self, problema: str, contexto: dict = None) -> dict:
        """
        Diagnóstico com contexto do negócio.
        Correlaciona problema técnico com impacto real.
        """
        negocio = self.conhecimento.get("negocio", {})
        n_clientes = negocio.get("clientes", {}).get("total_ativos", 13)
        n_func = negocio.get("funcionarios", {}).get("total_ativos", 41)

        diag = {
            "problema": problema,
            "timestamp": datetime.now().isoformat(),
            "causa_raiz": "",
            "contexto_negocio": "",
            "solucao_recomendada": "",
            "urgencia": "media",
            "requer_jordan": False,
            "acoes_possiveis": [],
        }

        p = problema.lower()

        if "redis" in p:
            diag.update({
                "causa_raiz": "Redis indisponível — possível OOM ou restart do container",
                "solucao_recomendada": "Reiniciar container Redis e verificar swap",
                "contexto_negocio": (
                    f"Cache offline impacta portal de {n_clientes} clientes e "
                    f"ponto eletrônico de {n_func} funcionários"
                ),
                "acoes_possiveis": ["docker restart conecta-pro-redis"],
                "urgencia": "alta",
            })

        elif any(k in p for k in ["swap", "memoria", "memory", "oom"]):
            diag.update({
                "causa_raiz": "Swap saturado — VPS KV4 com 4GB swap a 100%",
                "solucao_recomendada": "swapoff -a && swapon -a para resetar swap",
                "contexto_negocio": "Sistema degradado. Todos os {n_func} funcionários afetados no ponto.",
                "urgencia": "critica",
                "acoes_possiveis": ["swapoff -a && swapon -a", "Verificar processos com alto uso de RAM"],
            })

        elif "celery" in p:
            diag.update({
                "causa_raiz": "Worker Celery com falha — tarefas assíncronas paradas",
                "solucao_recomendada": "Reiniciar celery-integrations",
                "contexto_negocio": "NFS-e, eSocial e integrações Sólides paralisadas",
                "acoes_possiveis": ["docker restart conecta-pro-celery-integrations"],
            })

        elif "ponto" in p or "clock" in p or "batida" in p:
            batidas = negocio.get("operacional", {}).get("batidas_hoje", 0)
            diag.update({
                "causa_raiz": "Endpoint de ponto eletrônico com falha",
                "contexto_negocio": f"{batidas} batidas registradas hoje. {n_func} funcionários ativos.",
                "solucao_recomendada": "Verificar gp_clock_punches e container backend",
                "urgencia": "alta",
            })

        elif any(k in p for k in ["regressão", "regress", "deploy", "quebrou"]):
            r = subprocess.run(
                "cd /opt/conecta-pro && git log --oneline -3",
                shell=True, capture_output=True, text=True,
            )
            diag.update({
                "causa_raiz": "Possível regressão por deploy recente",
                "contexto_negocio": f"Últimos commits:\n{r.stdout.strip()}",
                "solucao_recomendada": "Revisar último commit e rollback se necessário",
                "urgencia": "critica",
                "requer_jordan": True,
            })

        elif any(k in p for k in ["financeiro", "pagar", "receber", "nfe", "nfse"]):
            cp = negocio.get("financeiro", {}).get("valor_pagar", 0)
            cr = negocio.get("financeiro", {}).get("valor_receber", 0)
            diag.update({
                "causa_raiz": "Módulo financeiro ou fiscal com falha",
                "contexto_negocio": (
                    f"R$ {cp:,.2f} em contas a pagar | R$ {cr:,.2f} a receber"
                ),
                "solucao_recomendada": "Verificar endpoints do módulo financeiro",
                "urgencia": "alta",
                "requer_jordan": True,
            })

        # Verificar recorrência
        key = problema[:30]
        rec = self.memoria["problemas_recorrentes"].get(key, 0)
        if rec > 2:
            diag["contexto_negocio"] += f" [RECORRENTE: {rec}x anteriores]"
            diag["urgencia"] = "critica"
            diag["requer_jordan"] = True

        return diag

    # ─── ATUALIZAÇÃO DE CONHECIMENTO ──────────────────

    def atualizar_conhecimento(self) -> list:
        """
        Atualiza snapshot do negócio lendo o banco.
        Executado a cada 6h pelo heartbeat.
        """
        alertas = []

        # Postos sem cobertura
        sem_cob = self._q("""
            SELECT p.name as posto, c.name as cliente
            FROM posts p
            LEFT JOIN clients c ON c.id = p.client_id
            LEFT JOIN allocations a ON a.post_id = p.id AND a.status='active'
            WHERE a.id IS NULL AND p.status = 'active'
        """)
        if sem_cob:
            alertas.append({
                "tipo": "postos_sem_cobertura", "urgencia": "alta",
                "quantidade": len(sem_cob), "dados": sem_cob[:3],
                "mensagem": f"{len(sem_cob)} postos ativos sem cobertura",
            })

        # Contas vencidas
        vencidas = self._q1(
            "SELECT COUNT(*) as total FROM payable_accounts "
            "WHERE status='pendente' AND due_date < CURRENT_DATE"
        )
        if int(vencidas.get("total", 0) or 0) > 0:
            alertas.append({
                "tipo": "contas_vencidas", "urgencia": "media",
                "quantidade": vencidas["total"],
                "mensagem": f"{vencidas['total']} contas a pagar vencidas",
            })

        self.conhecimento["alertas_ativos"] = alertas
        (KNOWLEDGE_DIR / "alertas_ativos.json").write_text(
            json.dumps(alertas, indent=2, ensure_ascii=False, default=str)
        )
        return alertas

    # ─── TELEGRAM ─────────────────────────────────────

    def resumo_para_telegram(self) -> str:
        """Resumo executivo diário — tom de CTO."""
        now = datetime.now()
        negocio = self.conhecimento.get("negocio", {})

        clientes = negocio.get("clientes", {}).get("total_ativos", 13)
        func = negocio.get("funcionarios", {}).get("total_ativos", 41)
        valor_pagar = negocio.get("financeiro", {}).get("valor_pagar", 0)
        valor_receber = negocio.get("financeiro", {}).get("valor_receber", 0)
        batidas_hoje = negocio.get("operacional", {}).get("batidas_hoje", 0)

        alertas = self.conhecimento.get("alertas_ativos", [])
        tickets_abertos = sum(
            1 for f in TICKETS_DIR.glob("*.json")
            if json.loads(f.read_text()).get("status") == "aberto"
        )

        linhas = [
            f"📊 *Conecta Mais — {now.strftime('%d/%m %H:%M')}*\n",
            f"👥 {clientes} clientes | {func} funcionários",
            f"💰 A pagar: R$ {valor_pagar:,.0f} | A receber: R$ {valor_receber:,.0f}",
            f"🕐 Batidas hoje: {batidas_hoje}",
        ]

        if alertas:
            criticos = [a for a in alertas if a["urgencia"] == "critica"]
            altos = [a for a in alertas if a["urgencia"] == "alta"]
            if criticos:
                linhas.append(f"\n🔴 *Crítico ({len(criticos)}):*")
                for a in criticos:
                    linhas.append(f"  • {a['mensagem']}")
            if altos:
                linhas.append(f"⚠️ *Atenção ({len(altos)}):*")
                for a in altos:
                    linhas.append(f"  • {a['mensagem']}")
        else:
            linhas.append("\n✅ Sem alertas ativos")

        if tickets_abertos:
            linhas.append(f"\n📋 {tickets_abertos} ticket(s) aberto(s)")

        return "\n".join(linhas)

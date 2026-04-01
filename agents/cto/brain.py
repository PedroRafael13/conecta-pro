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

        # Preferir TicketManager (Sprint 3) se disponível
        tm = CTOBrain._get_ticket_mgr()
        if tm:
            result = tm.criar(
                titulo=titulo,
                descricao=descricao,
                severidade=severidade,
                categoria=categoria,
                causa_raiz=causa_raiz,
                solucao_proposta=solucao_proposta,
                auto_resolvido=auto_resolvido,
                requer_jordan=requer_jordan,
            )
            # Sincronizar contador local
            self.proximo_ticket += 1
            self.memoria["total_tickets"] = self.proximo_ticket - 1
            if auto_resolvido:
                self.memoria["incidentes_resolvidos"] += 1
            self._salvar_memoria()
            return result

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

        # Consultar memória de longo prazo
        mem = CTOBrain._get_memoria_longa()
        solucao_conhecida = mem.consultar_solucao(problema) if mem else None

        diag = {
            "problema": problema,
            "timestamp": datetime.now().isoformat(),
            "causa_raiz": "",
            "contexto_negocio": "",
            "solucao_recomendada": solucao_conhecida or "",
            "urgencia": "media",
            "requer_jordan": False,
            "acoes_possiveis": [],
            "solucao_da_memoria": solucao_conhecida is not None,
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
        """
        Resumo TÉCNICO para o Telegram.
        CTO = suporte técnico. NÃO envia dados de negócio.
        Dados de negócio ficam no Assistente Pessoal.
        """
        import urllib.request
        import urllib.error

        now = datetime.now()
        hora = now.strftime("%H:%M")
        data = now.strftime("%d/%m")

        # Containers
        r = subprocess.run(
            "docker ps --filter status=running --format '{{.Names}}' | wc -l",
            shell=True, capture_output=True, text=True,
        )
        containers_ativos = r.stdout.strip()

        # Backend health
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                health = json.loads(resp.read())
            status_backend = health.get("status", "?")
        except Exception:
            status_backend = "offline"

        # Swap
        r2 = subprocess.run(
            "free -m | awk 'NR==3{print $3}'",
            shell=True, capture_output=True, text=True,
        )
        swap_mb = int(r2.stdout.strip() or 0)

        # CPU load
        r3 = subprocess.run(
            "cat /proc/loadavg | awk '{print $1}'",
            shell=True, capture_output=True, text=True,
        )
        cpu_load = r3.stdout.strip() or "0"

        # Tickets abertos
        tickets_abertos = 0
        for f in TICKETS_DIR.glob("*.json"):
            try:
                if json.loads(f.read_text()).get("status") == "aberto":
                    tickets_abertos += 1
            except Exception:
                pass

        # Último score do monitor
        monitor_state_file = Path("/opt/conecta-pro/reports/monitor_state.json")
        score = "?"
        ciclos = "?"
        correcoes = "?"
        if monitor_state_file.exists():
            try:
                ms = json.loads(monitor_state_file.read_text())
                score = ms.get("score_anterior", "?")
                ciclos = ms.get("ciclos", "?")
                correcoes = ms.get("correcoes_totais", "?")
            except Exception:
                pass

        emoji_backend = "✅" if status_backend == "healthy" else "🔴"
        try:
            cpu_f = float(cpu_load)
            emoji_cpu = "🔴" if cpu_f > 7 else ("⚠️" if cpu_f > 5 else "✅")
        except ValueError:
            emoji_cpu = "❓"
        emoji_swap = "🔴" if swap_mb > 3000 else ("⚠️" if swap_mb > 2000 else "✅")

        linhas = [
            f"🤖 *CTO — {data} {hora}*\n",
            f"─────────────────",
            f"{emoji_backend} Backend: `{status_backend}`",
            f"🐳 Containers: `{containers_ativos}` ativos",
            f"{emoji_cpu} CPU load: `{cpu_load}`",
            f"{emoji_swap} Swap: `{swap_mb}MB`",
            f"",
            f"📊 Monitor:",
            f"  Score: `{score}/10`",
            f"  Ciclos: `{ciclos}`",
            f"  Autocorreções: `{correcoes}`",
        ]

        if tickets_abertos:
            linhas.append("")
            linhas.append(f"🎫 Tickets abertos: `{tickets_abertos}`")
            linhas.append("_Use /tickets para ver detalhes_")
        else:
            linhas.append("")
            linhas.append("✅ Sem tickets abertos")

        linhas.append("")

        # Team support — resumo dos 80 agentes
        try:
            bridge = self._get_team_bridge()
            if bridge:
                linhas.append(bridge.resumo_para_cto())
        except Exception:
            pass

        linhas.append("")
        linhas.append("_/ajuda para comandos_")

        return "\n".join(linhas)

    # ─── SPRINT 3 — MEMÓRIA LONGA + TICKET MANAGER ───────────────────────────

    _memoria_longa_instance = None
    _ticket_mgr_instance = None

    @classmethod
    def _get_memoria_longa(cls):
        if cls._memoria_longa_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from memoria_longa import MemóriaLonga
                cls._memoria_longa_instance = MemóriaLonga()
            except Exception:
                pass
        return cls._memoria_longa_instance

    @classmethod
    def _get_ticket_mgr(cls):
        if cls._ticket_mgr_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from ticket_manager import TicketManager
                cls._ticket_mgr_instance = TicketManager()
            except Exception:
                pass
        return cls._ticket_mgr_instance

    # ─── SPRINT 2 — DIAGNÓSTICO AVANÇADO + APRENDIZADO ────────────────────────

    # Instâncias lazy (carregadas só quando necessário)
    _diagnostico_instance = None
    _aprendizado_instance = None

    def diagnosticar_avancado(
        self, tipo: str, contexto: dict = None
    ) -> dict:
        """
        Diagnóstico avançado usando logs reais, commits e banco.
        Sprint 2 — correlaciona evidências reais antes de recomendar ação.
        """
        if CTOBrain._diagnostico_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from diagnostico import DiagnosticoAvancado
                CTOBrain._diagnostico_instance = DiagnosticoAvancado()
            except Exception:
                return self.diagnosticar(tipo, contexto or {})

        d = CTOBrain._diagnostico_instance
        ctx = contexto or {}

        if tipo == "regressao":
            return d.investigar_regressao(
                score_antes=ctx.get("score_antes", 10.0),
                score_depois=ctx.get("score_depois", 0.0),
                endpoints_afetados=ctx.get("erros", []),
            )
        elif tipo == "performance":
            return d.investigar_performance(
                endpoint=ctx.get("endpoint", ""),
                tempo_ms=ctx.get("tempo_ms", 0),
            )
        else:
            return self.diagnosticar(tipo, ctx)

    def executar_aprendizado(self) -> dict:
        """Executa ciclo de aprendizado contínuo (Sprint 2)."""
        if CTOBrain._aprendizado_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from aprendizado import AprendizadoContinuo
                CTOBrain._aprendizado_instance = AprendizadoContinuo()
            except Exception as e:
                return {"erro": str(e), "mudancas": []}
        return CTOBrain._aprendizado_instance.executar()

    # ─── SPRINT 5 — TEAM BRIDGE (CTO ↔ 80 agentes) ───────────────────────────

    _team_bridge_instance = None

    @classmethod
    def _get_team_bridge(cls):
        if cls._team_bridge_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from team_bridge import TeamBridge
                cls._team_bridge_instance = TeamBridge()
            except Exception:
                pass
        return cls._team_bridge_instance

    def status_modulo(self, nome: str) -> str:
        """Status detalhado de um módulo por nome (Sprint 5)."""
        bridge = self._get_team_bridge()
        if bridge:
            return bridge.status_modulo(nome)
        return f"❌ TeamBridge indisponível"

    def resumo_team_support(self) -> str:
        """Resumo dos 80 agentes em 13 módulos (Sprint 5)."""
        bridge = self._get_team_bridge()
        if bridge:
            return bridge.resumo_para_cto()
        return "⚠️ TeamBridge indisponível"

    # ─── SPRINT 6 — RUNBOOKS + ESCALADA AUTOMÁTICA ────────────────────────────

    _runbook_executor_instance = None
    _escalada_instance = None

    @classmethod
    def _get_runbook_executor(cls):
        if cls._runbook_executor_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from runbook import RunbookExecutor
                cls._runbook_executor_instance = RunbookExecutor()
            except Exception:
                pass
        return cls._runbook_executor_instance

    @classmethod
    def _get_escalada(cls):
        if cls._escalada_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from escalada import Escalada
                cls._escalada_instance = Escalada()
            except Exception:
                pass
        return cls._escalada_instance

    def tentar_resolver(
        self,
        ticket_num: str,
        tipo: str,
        severidade: str,
        descricao: str,
    ) -> dict:
        """
        Sprint 6 — Tenta resolver autonomamente antes de apenas notificar.
        1. Executa runbook adequado
        2. Se falhar, abre escalada temporal
        3. Retorna resultado consolidado
        """
        rb = self._get_runbook_executor()
        resultado = {
            "ticket": ticket_num,
            "tipo": tipo,
            "resolvido": False,
            "requer_jordan": False,
            "runbook_executado": False,
            "escalada_aberta": False,
            "mensagem": "",
        }

        if rb and rb.pode_executar(tipo):
            resultado["runbook_executado"] = True
            res_rb = rb.executar(tipo)
            resultado["resolvido"] = res_rb.resolvido
            resultado["requer_jordan"] = res_rb.requer_jordan
            resultado["mensagem"] = res_rb.mensagem

            if res_rb.resolvido:
                # Atualizar ticket como resolvido automaticamente
                self.atualizar_ticket(
                    ticket_num,
                    f"Runbook {tipo} executado com sucesso",
                    "resolvido",
                    resultado=res_rb.mensagem,
                )
                return resultado

        # Runbook falhou ou não existe — abrir escalada
        esc = self._get_escalada()
        if esc:
            esc.abrir(ticket_num, tipo, severidade, descricao)
            resultado["escalada_aberta"] = True

        if not resultado["resolvido"]:
            resultado["requer_jordan"] = True

        return resultado

    def verificar_escaladas(self) -> list:
        """
        Sprint 6 — Verifica escaladas ativas e dispara próximo nível se necessário.
        Chamado a cada 5 minutos pelo cron.
        """
        esc = self._get_escalada()
        if not esc:
            return []
        # Recarregar estado do disco (pode ter sido modificado por outro processo)
        esc.escaladas = esc._carregar()
        return esc.verificar_todas()

    def listar_escaladas(self) -> list:
        """Sprint 6 — Lista escaladas ativas."""
        esc = self._get_escalada()
        if not esc:
            return []
        esc.escaladas = esc._carregar()
        return esc.listar_ativas()

    def fechar_escalada(self, ticket_num: str, motivo: str = "resolvido"):
        """Sprint 6 — Fecha escalada de um ticket."""
        esc = self._get_escalada()
        if esc:
            esc.escaladas = esc._carregar()
            esc.fechar(ticket_num, motivo)

    def resumo_runbooks(self, limit: int = 5) -> str:
        """Sprint 6 — Resumo dos últimos runbooks executados."""
        rb = self._get_runbook_executor()
        if not rb:
            return "⚠️ RunbookExecutor indisponível"
        historico = rb.historico(limit)
        if not historico:
            return "📭 Nenhum runbook executado ainda."
        linhas = [f"🔧 *Últimos {len(historico)} runbook(s):*\n"]
        for r in historico:
            emoji = "✅" if r["resolvido"] else ("🔴" if r.get("requer_jordan") else "⚠️")
            ts = r.get("inicio", "")[:16].replace("T", " ")
            linhas.append(
                f"{emoji} `{r['tipo']}` — {ts}\n"
                f"   {r['mensagem'][:80]}"
            )
        return "\n".join(linhas)

    # ─── SPRINT 9 — AUTO-EVOLUÇÃO ─────────────────────────────────────────────

    _auto_evolucao_instance = None

    @classmethod
    def _get_auto_evolucao(cls):
        if cls._auto_evolucao_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from auto_evolucao import AutoEvolução
                cls._auto_evolucao_instance = AutoEvolução()
            except Exception:
                pass
        return cls._auto_evolucao_instance

    def auditoria_completa(self) -> str:
        """Executa auditoria completa do sistema (Sprint 9)."""
        ae = self._get_auto_evolucao()
        if not ae:
            return "❌ AutoEvolução não disponível"
        return ae.executar_auditoria_completa()

    def relatorio_evolucao(self) -> str:
        """Relatório de auto-evolução do sistema (Sprint 9)."""
        ae = self._get_auto_evolucao()
        if not ae:
            return "❌ AutoEvolução não disponível"
        return ae.relatorio_evolucao()

    # ─── SPRINT 0 — CONHECIMENTO TOTAL ────────────────────────────────────────

    _conhecimento_total_instance = None

    @classmethod
    def _get_conhecimento_total(cls):
        if cls._conhecimento_total_instance is None:
            try:
                import sys as _sys
                _sys.path.insert(0, str(CTO_DIR))
                from conhecimento_total import ConhecimentoTotal
                cls._conhecimento_total_instance = ConhecimentoTotal()
            except Exception as e:
                print(f"[CTOBrain] ConhecimentoTotal erro: {e}")
        return cls._conhecimento_total_instance

    def diagnosticar_com_conhecimento_total(self, problema: str) -> dict:
        """
        Diagnóstico usando TODO o conhecimento do sistema.
        Sabe onde está o código, qual tabela, qual integração.
        """
        diag = self.diagnosticar_avancado(
            problema.split()[0].lower() if problema.split() else "geral",
            {"descricao": problema}
        )
        ct = self._get_conhecimento_total()
        if ct:
            ctx = ct.diagnosticar_com_contexto(problema)
            diag["codigo_relacionado"]  = ctx.get("codigo_relacionado", [])
            diag["tabelas_relacionadas"] = ctx.get("tabelas_relacionadas", [])
            diag["integracao_relacionada"] = ctx.get("integracao_relacionada")
            diag["onde_corrigir"]       = ctx.get("onde_corrigir", [])
            if ctx.get("causa_provavel"):
                diag["causa_raiz"] = ctx["causa_provavel"]
        return diag

    def buscar_no_sistema(self, termo: str) -> dict:
        """
        Busca qualquer coisa no sistema.
        Retorna código, tabelas, endpoints, integrações.
        """
        ct = self._get_conhecimento_total()
        if not ct:
            return {"erro": "Conhecimento não disponível — execute Sprint 0"}
        return {
            "codigo":    ct.buscar_codigo(termo),
            "endpoints": ct.buscar_endpoint(termo),
            "tabela":    ct.buscar_tabela(termo),
            "grep":      ct.buscar_no_codigo_real(termo),
        }

    def resumo_conhecimento(self) -> str:
        """Resumo do que o CTO conhece sobre o sistema."""
        ct = self._get_conhecimento_total()
        if not ct:
            return "❌ Conhecimento não indexado — execute Sprint 0"
        r = ct.resumo_conhecimento()
        return (
            f"🧠 *Conhecimento do CTO:*\n\n"
            f"*Backend:*\n"
            f"  📁 {r['backend']['arquivos']:,} arquivos\n"
            f"  📝 {r['backend']['linhas']:,} linhas\n"
            f"  🔗 {r['backend']['endpoints']:,} endpoints\n"
            f"  ⚙️ {r['backend']['funcoes']:,} funções\n\n"
            f"*Banco:*\n"
            f"  🗄️ {r['banco']['tabelas']} tabelas\n"
            f"  🔑 {r['banco']['fks']} FKs | "
            f"{r['banco']['indices']} índices | "
            f"{r['banco']['enums']} enums\n\n"
            f"*Frontend:*\n"
            f"  📄 {r['frontend']['paginas']} páginas / {r['frontend']['rotas']} rotas\n"
            f"  🧩 {r['frontend']['componentes']} componentes | "
            f"{r['frontend']['hooks']} hooks\n\n"
            f"*Integrações:* {r['integracoes']} "
            f"(Cora, Inter, Sólides, eSocial, NFS-e...)\n\n"
            f"*Infraestrutura:*\n"
            f"  🐳 {r['infra']['containers']} containers | "
            f"⏰ {r['infra']['crons']} crons | "
            f"🔧 {r['infra']['vars_env']} vars env\n\n"
            f"*Agents:*\n"
            f"  🤖 {r['agents']['modulos']} módulos | "
            f"🧠 {r['agents']['cto_arquivos']} CTO | "
            f"📜 {r['agents']['migrations']} migrations\n\n"
            f"_O CTO conhece cada linha do Conecta PRO_"
        )

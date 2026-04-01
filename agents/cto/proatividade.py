"""
Proatividade — CTO propõe antes de ser perguntado.

Executa a cada 4h via cron. Verifica tendências silenciosas:
- Disco crescendo > 2%/dia → propor limpeza
- Swap persistente > 3000MB → propor aumento de RAM virtual
- CPU load médio > 5.0 nas últimas 2h → investigar processo
- Contas a pagar vencidas > 5 → alertar financeiro
- Nenhum commit nos últimos 3 dias → dev pipeline parado?
- Tickets abertos há > 7 dias sem resolução → escalar

Anti-spam: 1 alerta por tipo por dia (controle em proatividade_state.json).
"""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

CTO_DIR    = Path("/opt/conecta-pro/agents/cto")
MEMORY_DIR = CTO_DIR / "memory"
STATE_FILE = MEMORY_DIR / "proatividade_state.json"

# ─── DB access ───────────────────────────────────────────────────────────────
_PG_PASS: Optional[str] = None
_PG_IP:   Optional[str] = None


def _get_pg_conn():
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
        _PG_IP = r.stdout.strip().split()[0]
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(
        host=_PG_IP, port="5432", dbname="conecta_pro",
        user="postgres", password=_PG_PASS, connect_timeout=5,
    )
    return conn, conn.cursor(cursor_factory=RealDictCursor)


def _q(sql: str) -> list:
    try:
        conn, cur = _get_pg_conn()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ─── Anti-spam ───────────────────────────────────────────────────────────────

def _carregar_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"alertas_hoje": {}, "data": ""}


def _salvar_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def _pode_alertar(tipo: str) -> bool:
    """Retorna True se ainda não alertou sobre este tipo hoje."""
    state = _carregar_state()
    hoje = datetime.now().strftime("%Y-%m-%d")
    # Reset diário
    if state.get("data") != hoje:
        state = {"alertas_hoje": {}, "data": hoje}
        _salvar_state(state)
    return tipo not in state["alertas_hoje"]


def _registrar_alerta(tipo: str):
    state = _carregar_state()
    hoje = datetime.now().strftime("%Y-%m-%d")
    if state.get("data") != hoje:
        state = {"alertas_hoje": {}, "data": hoje}
    state["alertas_hoje"][tipo] = datetime.now().isoformat()
    _salvar_state(state)


# ─── Verificações proativas ──────────────────────────────────────────────────

def _verificar_disco() -> Optional[dict]:
    """Disco > 85% → alerta."""
    try:
        out = subprocess.run(
            "df /opt --output=pcent | tail -1",
            shell=True, capture_output=True, text=True,
        ).stdout.strip().replace("%", "")
        pct = int(out) if out.isdigit() else 0
        if pct > 85:
            return {
                "tipo": "disco_critico",
                "gravidade": "alta",
                "titulo": f"Disco {pct}% — risco de escrita",
                "acao": (
                    "Executar: `docker system prune -f` "
                    "+ limpar /opt/conecta-pro/logs/*.log antigos"
                ),
            }
    except Exception:
        pass
    return None


def _verificar_swap() -> Optional[dict]:
    """Swap persistente > 3000MB."""
    try:
        mem = Path("/proc/meminfo").read_text()
        swap_total = swap_free = 0
        for line in mem.splitlines():
            if line.startswith("SwapTotal:"):
                swap_total = int(line.split()[1])
            elif line.startswith("SwapFree:"):
                swap_free = int(line.split()[1])
        swap_used_mb = (swap_total - swap_free) // 1024
        if swap_used_mb > 3000:
            return {
                "tipo": "swap_persistente",
                "gravidade": "alta",
                "titulo": f"Swap persistente: {swap_used_mb}MB",
                "acao": (
                    "Verificar processo com mais RSS: `ps aux --sort=-%mem | head -10`. "
                    "Considerar `sudo sysctl vm.swappiness=10` para reduzir swap."
                ),
            }
    except Exception:
        pass
    return None


def _verificar_cpu() -> Optional[dict]:
    """CPU load > 7.0."""
    try:
        load = float(open("/proc/loadavg").read().split()[0])
        if load > 7.0:
            return {
                "tipo": "cpu_carga_alta",
                "gravidade": "media",
                "titulo": f"CPU load alto: {load:.1f}",
                "acao": (
                    "Verificar: `top -b -n1 | head -20`. "
                    "Se for Celery, verificar tarefas presas na fila."
                ),
            }
    except Exception:
        pass
    return None


def _verificar_contas_vencidas() -> Optional[dict]:
    """Contas a pagar vencidas há > 2 dias."""
    rows = _q(
        "SELECT COUNT(*) AS n, COALESCE(SUM(net_value),0) AS total "
        "FROM payable_accounts "
        "WHERE status='pendente' AND due_date < CURRENT_DATE - interval '2 days'"
    )
    if rows and rows[0]["n"] > 3:
        n = rows[0]["n"]
        total = float(rows[0]["total"])
        return {
            "tipo": "contas_vencidas",
            "gravidade": "alta",
            "titulo": f"{n} contas a pagar vencidas (R${total:,.2f})",
            "acao": (
                "Acessar módulo Financeiro → Contas a Pagar "
                "para negociar ou quitar obrigações em atraso."
            ),
        }
    return None


def _verificar_git_inatividade() -> Optional[dict]:
    """Nenhum commit nos últimos 3 dias → pipeline dev parado."""
    try:
        r = subprocess.run(
            "git -C /opt/conecta-pro log --oneline --since='3 days ago' | wc -l",
            shell=True, capture_output=True, text=True,
        )
        n = int(r.stdout.strip())
        if n == 0:
            return {
                "tipo": "git_inativo",
                "gravidade": "baixa",
                "titulo": "Nenhum commit nos últimos 3 dias",
                "acao": (
                    "Pipeline de desenvolvimento parado. "
                    "Verificar se há bloqueadores técnicos ou pendências de review."
                ),
            }
    except Exception:
        pass
    return None


def _verificar_tickets_antigos() -> Optional[dict]:
    """Tickets abertos há mais de 7 dias."""
    tickets_dir = CTO_DIR / "tickets"
    limite = datetime.now() - timedelta(days=7)
    antigos = []
    for f in sorted(tickets_dir.glob("*.json")):
        try:
            t = json.loads(f.read_text())
            if t.get("status") == "aberto":
                criado = datetime.fromisoformat(t["criado_em"])
                if criado < limite:
                    antigos.append(t["numero"])
        except Exception:
            pass
    if antigos:
        return {
            "tipo": "tickets_antigos",
            "gravidade": "media",
            "titulo": f"{len(antigos)} ticket(s) aberto(s) há +7 dias",
            "acao": (
                f"Tickets: {', '.join(antigos[:5])}. "
                "Revisar e escalar ou fechar os não-acionáveis."
            ),
        }
    return None


def _verificar_containers_unhealthy() -> Optional[dict]:
    """Containers em estado unhealthy/exited."""
    r = subprocess.run(
        "docker ps --filter 'health=unhealthy' --format '{{.Names}}' 2>/dev/null; "
        "docker ps -a --filter 'status=exited' --format '{{.Names}}' 2>/dev/null | head -5",
        shell=True, capture_output=True, text=True,
    )
    names = [n.strip() for n in r.stdout.strip().splitlines() if n.strip()]
    # Filtrar containers de run-once
    names = [n for n in names if "conecta-pro" in n and "migration" not in n]
    if names:
        return {
            "tipo": "containers_degradados",
            "gravidade": "alta",
            "titulo": f"{len(names)} container(s) degradado(s)",
            "acao": (
                f"Afetados: {', '.join(names[:4])}. "
                "Verificar logs: `docker logs <nome> --tail 50`."
            ),
        }
    return None


# ─── Executor principal ──────────────────────────────────────────────────────

def verificar_e_gerar_propostas() -> list[dict]:
    """
    Executa todas as verificações proativas.
    Retorna lista de propostas filtradas pelo anti-spam.
    """
    checks = [
        _verificar_swap,
        _verificar_disco,
        _verificar_cpu,
        _verificar_containers_unhealthy,
        _verificar_contas_vencidas,
        _verificar_tickets_antigos,
        _verificar_git_inatividade,
    ]

    propostas = []
    for check in checks:
        try:
            resultado = check()
            if resultado and _pode_alertar(resultado["tipo"]):
                propostas.append(resultado)
                _registrar_alerta(resultado["tipo"])
        except Exception:
            pass

    return propostas


def formatar_propostas_telegram(propostas: list[dict]) -> str:
    """Formata propostas para envio no Telegram."""
    if not propostas:
        return ""

    now = datetime.now().strftime("%d/%m %H:%M")
    emoji_grav = {"critica": "🔴", "alta": "🟠", "media": "🟡", "baixa": "🟢"}

    linhas = [f"💡 *CTO Proativo — {now}*\n"]
    linhas.append(f"_{len(propostas)} proposta(s) de melhoria:_\n")

    for i, p in enumerate(propostas, 1):
        em = emoji_grav.get(p["gravidade"], "⚪")
        linhas.append(f"{em} *{i}. {p['titulo']}*")
        linhas.append(f"   ➤ {p['acao']}\n")

    return "\n".join(linhas)


def gerar_listagem_propostas() -> str:
    """
    Gera listagem on-demand para o comando /propostas.
    NÃO respeita anti-spam (usuário pediu explicitamente).
    """
    checks = [
        _verificar_swap,
        _verificar_disco,
        _verificar_cpu,
        _verificar_containers_unhealthy,
        _verificar_contas_vencidas,
        _verificar_tickets_antigos,
        _verificar_git_inatividade,
    ]

    propostas = []
    for check in checks:
        try:
            resultado = check()
            if resultado:
                propostas.append(resultado)
        except Exception:
            pass

    return formatar_propostas_telegram(propostas) or (
        "✅ *Nenhuma proposta proativa no momento.*\n"
        "_Sistema dentro dos parâmetros normais._"
    )

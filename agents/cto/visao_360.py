"""
Visão 360° — CTO conecta dots entre módulos.

Correlaciona eventos técnicos com impacto de negócio:
- Deploy + queda de score → regressão funcional
- Swap alto + endpoints lentos → degradação silenciosa
- Celery unhealthy + eSocial pendente → obrigação fiscal em risco
- Tickets concentrados → componente frágil emergindo

Sprint 4: gerado automaticamente, chamado via /visao360 no Telegram.
"""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

CTO_DIR    = Path("/opt/conecta-pro/agents/cto")
MEMORY_DIR = CTO_DIR / "memory"

# ─── DB access (mesmo padrão de brain.py / diagnostico.py) ──────────────────
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


# ─── Coleta de dados ─────────────────────────────────────────────────────────

def _dados_infra() -> dict:
    """Métricas do servidor: swap, CPU load, disco."""
    try:
        mem = Path("/proc/meminfo").read_text()
        swap_total = swap_free = 0
        for line in mem.splitlines():
            if line.startswith("SwapTotal:"):
                swap_total = int(line.split()[1])
            elif line.startswith("SwapFree:"):
                swap_free = int(line.split()[1])
        swap_used_mb = (swap_total - swap_free) // 1024

        load = float(open("/proc/loadavg").read().split()[0])
        disk = subprocess.run(
            "df /opt --output=pcent | tail -1",
            shell=True, capture_output=True, text=True,
        ).stdout.strip().replace("%", "")
        disk_pct = int(disk) if disk.isdigit() else 0
        return {"swap_mb": swap_used_mb, "cpu_load": load, "disk_pct": disk_pct}
    except Exception:
        return {"swap_mb": 0, "cpu_load": 0.0, "disk_pct": 0}


def _dados_containers() -> dict:
    """Estado dos containers Docker."""
    r = subprocess.run(
        "docker ps --format '{{.Names}}|{{.Status}}'",
        shell=True, capture_output=True, text=True,
    )
    containers = {}
    for line in r.stdout.strip().splitlines():
        if "|" in line:
            name, status = line.split("|", 1)
            containers[name.strip()] = status.strip()
    return containers


def _dados_negocio() -> dict:
    """Dados de negócio: contas pendentes, funcionários, clientes ativos."""
    contas_pagar = _q(
        "SELECT COUNT(*) AS n, COALESCE(SUM(net_value),0) AS total "
        "FROM payable_accounts WHERE status='pendente'"
    )
    contas_receber = _q(
        "SELECT COUNT(*) AS n, COALESCE(SUM(net_value),0) AS total "
        "FROM receivable_accounts WHERE status='pendente'"
    )
    funcionarios = _q("SELECT COUNT(*) AS n FROM employees WHERE status='ativo'")
    clientes = _q("SELECT COUNT(*) AS n FROM clients WHERE status='active'")
    licitacoes = _q(
        "SELECT COUNT(*) AS n FROM bidding_opportunities "
        "WHERE data_abertura >= CURRENT_DATE AND data_abertura <= CURRENT_DATE + interval '7 days'"
    )
    return {
        "contas_pagar_n": contas_pagar[0]["n"] if contas_pagar else 0,
        "contas_pagar_total": float(contas_receber[0]["total"]) if contas_pagar else 0,
        "contas_receber_n": contas_receber[0]["n"] if contas_receber else 0,
        "contas_receber_total": float(contas_receber[0]["total"]) if contas_receber else 0,
        "funcionarios": funcionarios[0]["n"] if funcionarios else 0,
        "clientes": clientes[0]["n"] if clientes else 0,
        "licitacoes_proximas_7d": licitacoes[0]["n"] if licitacoes else 0,
    }


def _tickets_recentes() -> list:
    """Últimos 5 tickets abertos dos arquivos JSON."""
    tickets_dir = CTO_DIR / "tickets"
    tickets = []
    for f in sorted(tickets_dir.glob("*.json"), reverse=True)[:10]:
        try:
            t = json.loads(f.read_text())
            if t.get("status") == "aberto":
                tickets.append(t)
                if len(tickets) >= 5:
                    break
        except Exception:
            pass
    return tickets


def _memoria_longa() -> dict:
    ml = MEMORY_DIR / "memoria_longa.json"
    if ml.exists():
        try:
            return json.loads(ml.read_text())
        except Exception:
            pass
    return {}


def _mudancas_recentes() -> list:
    mf = MEMORY_DIR / "mudancas_detectadas.json"
    if mf.exists():
        try:
            return json.loads(mf.read_text())
        except Exception:
            pass
    return []


# ─── Correlações ─────────────────────────────────────────────────────────────

def _correlacionar(infra: dict, containers: dict, negocio: dict,
                   tickets: list, mem_longa: dict, mudancas: list) -> list:
    """Conecta dots entre eventos técnicos e contexto de negócio."""
    alertas = []

    # Correlação 1: Swap alto + containers degradados
    if infra["swap_mb"] > 2000:
        unhealthy = [k for k, v in containers.items() if "unhealthy" in v.lower()]
        degraded  = [k for k, v in containers.items() if "exited" in v.lower()]
        if unhealthy or degraded:
            affected = unhealthy + degraded
            alertas.append({
                "tipo": "swap_containers",
                "gravidade": "critica",
                "titulo": "Swap alto degradando containers",
                "detalhe": (
                    f"Swap {infra['swap_mb']}MB + containers afetados: "
                    f"{', '.join(affected[:3])}. "
                    f"Redis/Celery em risco — logout de usuários possível."
                ),
            })
        else:
            alertas.append({
                "tipo": "swap_alto_isolado",
                "gravidade": "alta",
                "titulo": f"Swap alto: {infra['swap_mb']}MB",
                "detalhe": (
                    "Sistema sob pressão de memória. "
                    "Risco de OOM se carga aumentar."
                ),
            })

    # Correlação 2: Celery unhealthy + obrigações fiscais
    celery_ok = all(
        "unhealthy" not in v.lower() and "exited" not in v.lower()
        for k, v in containers.items() if "celery" in k
    )
    if not celery_ok and negocio["licitacoes_proximas_7d"] > 0:
        alertas.append({
            "tipo": "celery_licitacoes",
            "gravidade": "alta",
            "titulo": "Celery degradado + licitações nos próximos 7 dias",
            "detalhe": (
                f"{negocio['licitacoes_proximas_7d']} licitação(ões) abertura próxima. "
                "Celery com problema pode atrasar geração automática de propostas."
            ),
        })

    # Correlação 3: CPU alto + contas a receber elevadas
    if infra["cpu_load"] > 6.0 and negocio["contas_receber_total"] > 100000:
        alertas.append({
            "tipo": "cpu_financeiro",
            "gravidade": "media",
            "titulo": "CPU alto com R$" + f"{negocio['contas_receber_total']:,.2f} a receber",
            "detalhe": (
                "Processamento intenso pode atrasar geração de boletos/NFSe. "
                "Monitorar antes do fechamento do mês."
            ),
        })

    # Correlação 4: Tickets concentrados em um componente
    categorias: dict = {}
    for t in tickets:
        cat = t.get("categoria", "desconhecido")
        categorias[cat] = categorias.get(cat, 0) + 1
    hot_cat = max(categorias, key=lambda c: categorias[c]) if categorias else None
    if hot_cat and categorias.get(hot_cat, 0) >= 2:
        alertas.append({
            "tipo": "tickets_concentrados",
            "gravidade": "media",
            "titulo": f"Tickets concentrados: {hot_cat} ({categorias[hot_cat]}x)",
            "detalhe": (
                f"Módulo '{hot_cat}' com múltiplos tickets abertos indica "
                "componente frágil emergindo. Considerar refactoring preventivo."
            ),
        })

    # Correlação 5: Componentes frágeis com falhas recentes
    frageis = mem_longa.get("componentes_frageis", {})
    for comp, dados in frageis.items():
        if dados.get("total", 0) >= 2:
            cont_status = containers.get(f"conecta-pro-{comp}", "")
            if "unhealthy" in cont_status or "exited" in cont_status:
                alertas.append({
                    "tipo": "fragil_ativo",
                    "gravidade": "alta",
                    "titulo": f"{comp} frágil está em estado degradado",
                    "detalhe": (
                        f"{comp} tem {dados['total']} falhas históricas "
                        f"(último: {dados.get('ultimo_incidente','?')[:10]}) "
                        f"e status atual: {cont_status[:40]}."
                    ),
                })

    # Correlação 6: Mudanças recentes do tipo crítico
    for entrada in mudancas[-3:]:
        for m in entrada.get("mudancas", []):
            if m.get("urgencia") == "critica":
                already = any(a["tipo"] == m["tipo"] for a in alertas)
                if not already:
                    alertas.append({
                        "tipo": m["tipo"],
                        "gravidade": "critica",
                        "titulo": m["mensagem"],
                        "detalhe": f"Detectado em {entrada['timestamp'][:16]}.",
                    })

    # Correlação 7: Disco alto
    if infra["disk_pct"] > 85:
        alertas.append({
            "tipo": "disco_alto",
            "gravidade": "alta",
            "titulo": f"Disco {infra['disk_pct']}% — risco de falha de escrita",
            "detalhe": (
                "PostgreSQL e logs em risco. Limpar Docker images antigas "
                "(`docker system prune -f`) e logs de /var/log."
            ),
        })

    return alertas


# ─── Relatório Visão 360° ────────────────────────────────────────────────────

def gerar_visao_360() -> str:
    """Gera texto resumido da Visão 360° para o Telegram."""
    now = datetime.now().strftime("%d/%m %H:%M")

    infra       = _dados_infra()
    containers  = _dados_containers()
    negocio     = _dados_negocio()
    tickets     = _tickets_recentes()
    mem_longa   = _memoria_longa()
    mudancas    = _mudancas_recentes()

    alertas = _correlacionar(infra, containers, negocio, tickets, mem_longa, mudancas)

    emoji_grav = {"critica": "🔴", "alta": "🟠", "media": "🟡", "baixa": "🟢"}

    linhas = [f"🔭 *Visão 360° — {now}*\n"]

    # Painel de negócio
    linhas.append(
        f"💼 *Negócio:* {negocio['clientes']} clientes | "
        f"{negocio['funcionarios']} func | "
        f"R${negocio['contas_receber_total']:,.0f} a receber"
    )
    if negocio["licitacoes_proximas_7d"] > 0:
        linhas.append(
            f"📋 {negocio['licitacoes_proximas_7d']} licitação(ões) nos próximos 7 dias"
        )

    # Painel de infra
    linhas.append(
        f"\n⚙️ *Infra:* CPU {infra['cpu_load']:.1f} | "
        f"Swap {infra['swap_mb']}MB | "
        f"Disco {infra['disk_pct']}%"
    )

    # Correlações
    if alertas:
        linhas.append(f"\n🔗 *Correlações detectadas ({len(alertas)}):*")
        for a in alertas:
            em = emoji_grav.get(a["gravidade"], "⚪")
            linhas.append(f"\n{em} *{a['titulo']}*\n   _{a['detalhe']}_")
    else:
        linhas.append("\n✅ *Nenhuma correlação crítica detectada.* Sistema saudável.")

    # Tickets abertos
    if tickets:
        linhas.append(f"\n📌 *{len(tickets)} ticket(s) aberto(s) recentes:*")
        for t in tickets[:3]:
            sev = {"critica": "🔴", "alta": "🟠", "media": "🟡"}.get(
                t.get("severidade", "media"), "⚪"
            )
            linhas.append(f"  {sev} `{t['numero']}` {t['titulo'][:45]}")

    return "\n".join(linhas)

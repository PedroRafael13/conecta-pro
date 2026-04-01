"""
AprendizadoContinuo — O CTO aprende com o banco a cada 6h.
Detecta mudanças, tendências e anomalias no negócio.

Schema real (descoberto Sprint 1):
- employees:     status='ativo'   | nome, cargo, salario_base, created_at
- clients:       status='active'  | name, contract_end_date
- posts:         status='active'  | client_id, name
- allocations:   status='active'  | post_id, employee_id
- occurrences:   status='aberta'  | severity, created_at
- payable_accounts: status='pendente' | net_value, due_date
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

CTO_DIR       = Path("/opt/conecta-pro/agents/cto")
MEMORY_DIR    = CTO_DIR / "memory"
SNAPSHOTS_DIR = MEMORY_DIR / "snapshots"

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
        rows = [dict(r) for r in cur.fetchall()]
        cur.close(); conn.close()
        return rows
    except Exception:
        return []


def _q1(sql: str) -> dict:
    r = _q(sql)
    return r[0] if r else {}


class AprendizadoContinuo:
    """Aprende continuamente com o estado do banco."""

    def __init__(self):
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        self.snapshot_anterior = self._carregar_ultimo_snapshot()

    def _carregar_ultimo_snapshot(self) -> dict:
        snapshots = sorted(SNAPSHOTS_DIR.glob("snapshot_*.json"))
        if snapshots:
            try:
                return json.loads(snapshots[-1].read_text())
            except Exception:
                pass
        return {}

    def _salvar_snapshot(self, snapshot: dict):
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        f = SNAPSHOTS_DIR / f"snapshot_{ts}.json"
        f.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False, default=str))
        # Manter apenas últimos 30 snapshots (~1 semana a 6h)
        todos = sorted(SNAPSHOTS_DIR.glob("snapshot_*.json"))
        for antigo in todos[:-30]:
            antigo.unlink()

    # ─── Snapshot ─────────────────────────────────────────────────────────────

    def tirar_snapshot(self) -> dict:
        """Coleta estado atual do negócio."""
        print("[Aprendizado] Tirando snapshot...")
        snapshot: dict = {
            "timestamp": datetime.now().isoformat(),
            "metricas": {},
        }
        m = snapshot["metricas"]

        # Funcionários
        try:
            r = _q1("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'ativo')    AS ativos,
                    COUNT(*) FILTER (WHERE status = 'inativo')  AS inativos,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') AS novos_7dias
                FROM employees
            """)
            m["funcionarios"] = {k: int(v or 0) for k, v in r.items()}
        except Exception as e:
            print(f"  ⚠️ Funcionários: {e}")

        # Clientes + contratos vencendo
        try:
            r = _q1("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'active') AS ativos,
                    COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelados,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') AS novos_7dias,
                    COUNT(*) FILTER (
                        WHERE contract_end_date IS NOT NULL
                          AND contract_end_date BETWEEN NOW() AND NOW() + INTERVAL '30 days'
                          AND status = 'active'
                    ) AS contratos_vencendo_30d
                FROM clients
            """)
            m["clientes"] = {k: int(v or 0) for k, v in r.items()}
        except Exception as e:
            print(f"  ⚠️ Clientes: {e}")

        # Financeiro — contas a pagar
        try:
            r = _q1("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'pendente' AND due_date < NOW())     AS vencidas,
                    COUNT(*) FILTER (WHERE status = 'pendente' AND due_date BETWEEN NOW()
                                      AND NOW() + INTERVAL '7 days')                     AS vencendo_7d,
                    COALESCE(SUM(net_value) FILTER (WHERE status = 'pendente'), 0)::numeric(12,2)
                                                                                          AS total_pendente
                FROM payable_accounts
            """)
            m["financeiro_pagar"] = {k: float(v or 0) for k, v in r.items()}
        except Exception as e:
            print(f"  ⚠️ Financeiro: {e}")

        # Operacional — postos sem cobertura
        try:
            r = _q1("""
                SELECT COUNT(*) AS postos_sem_cobertura
                FROM posts p
                LEFT JOIN allocations a ON a.post_id = p.id AND a.status = 'active'
                WHERE p.status = 'active' AND a.id IS NULL
            """)
            m["postos_sem_cobertura"] = int(r.get("postos_sem_cobertura", 0) or 0)
        except Exception as e:
            print(f"  ⚠️ Postos: {e}")

        # Operacional — ocorrências abertas
        try:
            r = _q1("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'aberta')                        AS abertas,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') AS ultimas_24h
                FROM occurrences
            """)
            m["ocorrencias"] = {k: int(v or 0) for k, v in r.items()}
        except Exception as e:
            print(f"  ⚠️ Ocorrências: {e}")

        # Performance do sistema
        try:
            load  = subprocess.run("awk '{print $1}' /proc/loadavg", shell=True, capture_output=True, text=True)
            ram   = subprocess.run("free -m | awk 'NR==2{printf \"%.1f\",$3/$2*100}'", shell=True, capture_output=True, text=True)
            swap  = subprocess.run("free -m | awk 'NR==3{print $3}'", shell=True, capture_output=True, text=True)
            m["cpu_load_1m"] = float(load.stdout.strip() or 0)
            m["ram_pct"]     = float(ram.stdout.strip() or 0)
            m["swap_mb"]     = int(swap.stdout.strip() or 0)
        except Exception:
            pass

        return snapshot

    # ─── Comparação ───────────────────────────────────────────────────────────

    def comparar_snapshots(self, atual: dict, anterior: dict) -> list:
        """Detecta mudanças significativas entre dois snapshots."""
        if not anterior:
            return []

        mudancas = []
        ma = atual.get("metricas", {})
        mp = anterior.get("metricas", {})

        def _int(d, *keys):
            v = d
            for k in keys:
                v = (v or {}).get(k, 0)
            return int(v or 0)

        # Funcionários
        func_ant = _int(mp, "funcionarios", "ativos")
        func_atu = _int(ma, "funcionarios", "ativos")
        if func_ant and func_atu != func_ant:
            delta = func_atu - func_ant
            mudancas.append({
                "tipo": "mudanca_funcionarios",
                "urgencia": "media",
                "mensagem": (
                    f"Funcionários ativos: {func_ant} → {func_atu} "
                    f"({'admissão' if delta > 0 else 'demissão/afastamento'})"
                ),
            })

        # Postos sem cobertura
        post_ant = _int(mp, "postos_sem_cobertura")
        post_atu = _int(ma, "postos_sem_cobertura")
        if post_atu > post_ant:
            mudancas.append({
                "tipo": "postos_descobertos",
                "urgencia": "alta",
                "mensagem": f"Postos sem cobertura: {post_ant} → {post_atu} (+{post_atu - post_ant})",
            })

        # Contas vencidas
        venc_ant = _int(mp, "financeiro_pagar", "vencidas")
        venc_atu = _int(ma, "financeiro_pagar", "vencidas")
        if venc_atu > venc_ant:
            mudancas.append({
                "tipo": "contas_vencidas_aumentou",
                "urgencia": "alta",
                "mensagem": (
                    f"Contas vencidas: {venc_ant} → {venc_atu} (+{venc_atu - venc_ant})"
                ),
            })

        # Contratos vencendo
        contrat_atu = _int(ma, "clientes", "contratos_vencendo_30d")
        if contrat_atu > 0:
            mudancas.append({
                "tipo": "contratos_vencendo",
                "urgencia": "media",
                "mensagem": f"{contrat_atu} contrato(s) de cliente vencendo nos próximos 30 dias",
            })

        # CPU alto
        cpu = float(ma.get("cpu_load_1m", 0) or 0)
        if cpu > 7.0:
            mudancas.append({
                "tipo": "cpu_alto",
                "urgencia": "alta",
                "mensagem": f"CPU load alto: {cpu:.1f} (limite: 7.0)",
            })

        # Swap crítico
        swap_mb = int(ma.get("swap_mb", 0) or 0)
        if swap_mb > 3000:
            mudancas.append({
                "tipo": "swap_alto",
                "urgencia": "critica",
                "mensagem": f"Swap crítico: {swap_mb}MB — sistema degradando",
            })

        return mudancas

    # ─── Ciclo completo ───────────────────────────────────────────────────────

    def executar(self) -> dict:
        """Executa ciclo completo de aprendizado."""
        print(f"[Aprendizado] Ciclo {datetime.now().strftime('%d/%m %H:%M')}...")

        snapshot_atual = self.tirar_snapshot()
        mudancas = self.comparar_snapshots(snapshot_atual, self.snapshot_anterior)

        self._salvar_snapshot(snapshot_atual)
        self.snapshot_anterior = snapshot_atual

        # Persistir mudanças detectadas
        if mudancas:
            f = MEMORY_DIR / "mudancas_detectadas.json"
            historico: list = []
            if f.exists():
                try:
                    historico = json.loads(f.read_text())
                except Exception:
                    pass
            historico.append({
                "timestamp": datetime.now().isoformat(),
                "mudancas": mudancas,
            })
            f.write_text(
                json.dumps(historico[-50:], indent=2, ensure_ascii=False, default=str)
            )

        print(f"  Snapshot salvo | {len(mudancas)} mudança(s) detectada(s)")
        return {"snapshot": snapshot_atual, "mudancas": mudancas}

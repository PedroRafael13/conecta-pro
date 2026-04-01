"""
DiagnosticoAvancado — Motor de diagnóstico do CTO Autônomo.
Investiga causa raiz real lendo logs, banco e histórico.

Sprint 2:
- Lê logs reais do container para contexto
- Correlaciona com commits recentes do git
- Analisa métricas do banco para entender impacto
- Detecta anomalias estatísticas (z-score)
- Aprende com cada diagnóstico resolvido
"""
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

CTO_DIR    = Path("/opt/conecta-pro/agents/cto")
MEMORY_DIR = CTO_DIR / "memory"

# ─── Acesso ao banco (mesma lógica do brain.py) ───────────────────────────────
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


# ─── Classe principal ─────────────────────────────────────────────────────────

class DiagnosticoAvancado:
    """Motor de diagnóstico inteligente do CTO."""

    def __init__(self):
        self.historico = self._carregar_historico()

    def _carregar_historico(self) -> list:
        f = MEMORY_DIR / "diagnosticos.json"
        if f.exists():
            try:
                return json.loads(f.read_text())
            except Exception:
                pass
        return []

    def _salvar_historico(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        f = MEMORY_DIR / "diagnosticos.json"
        f.write_text(
            json.dumps(self.historico[-200:], indent=2,
                       ensure_ascii=False, default=str)
        )

    # ─── Coleta de evidências ─────────────────────────────────────────────────

    def _ler_logs_container(self, container: str, linhas: int = 150) -> list:
        """Lê logs reais do container das últimas 2h."""
        r = subprocess.run(
            f"docker logs {container} --since 2h --tail {linhas} --timestamps",
            shell=True, capture_output=True, text=True,
        )
        return [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]

    def _ultimos_commits(self, n: int = 5) -> list:
        r = subprocess.run(
            f"cd /opt/conecta-pro && git log --oneline -{n} "
            "--format='%H|%s|%ai'",
            shell=True, capture_output=True, text=True,
        )
        commits = []
        for linha in r.stdout.strip().splitlines():
            if "|" in linha:
                parts = linha.split("|", 2)
                commits.append({
                    "hash": parts[0][:8],
                    "mensagem": parts[1] if len(parts) > 1 else "",
                    "data": parts[2][:19] if len(parts) > 2 else "",
                })
        return commits

    def _detectar_erros_logs(self, logs: list) -> dict:
        """Classifica erros encontrados nos logs por categoria."""
        padroes = {
            "banco":       re.compile(r'IntegrityError|OperationalError|ProgrammingError|deadlock', re.I),
            "memoria":     re.compile(r'MemoryError|OOM|killed|out of memory', re.I),
            "timeout":     re.compile(r'TimeoutError|timeout|timed out', re.I),
            "autenticacao":re.compile(r'\b401\b|\b403\b|unauthorized|forbidden', re.I),
            "importacao":  re.compile(r'ImportError|ModuleNotFoundError|cannot import', re.I),
            "conexao":     re.compile(r'Connection refused|ECONNREFUSED|ConnectionError|ConnectionRefused', re.I),
        }
        encontrados: dict = {k: [] for k in padroes}
        for linha in logs:
            for tipo, padrao in padroes.items():
                if padrao.search(linha):
                    encontrados[tipo].append(linha[-120:])
        return {k: v[:3] for k, v in encontrados.items() if v}

    def _conexoes_idle_banco(self) -> int:
        """Conta conexões idle in transaction — indicador de lock."""
        try:
            r = _q1(
                "SELECT COUNT(*) AS total FROM pg_stat_activity "
                "WHERE datname = 'conecta_pro' "
                "  AND state = 'idle in transaction' "
                "  AND state_change < now() - interval '5 minutes'"
            )
            return int(r.get("total", 0) or 0)
        except Exception:
            return 0

    # ─── Diagnósticos ─────────────────────────────────────────────────────────

    def investigar_regressao(
        self,
        score_antes: float,
        score_depois: float,
        endpoints_afetados: list,
    ) -> dict:
        """Investiga causa raiz de uma regressão. Correlaciona commits + logs + banco."""
        investigacao: dict = {
            "tipo": "regressao",
            "score": f"{score_antes} → {score_depois}",
            "timestamp": datetime.now().isoformat(),
            "endpoints_afetados": endpoints_afetados,
            "causa_raiz": "",
            "evidencias": [],
            "requer_jordan": False,
            "acao_recomendada": "",
            "confianca": 0,
        }

        # 1. Commits recentes
        commits = self._ultimos_commits(3)
        investigacao["commits_recentes"] = commits
        if commits:
            investigacao["evidencias"].append(
                f"Último deploy: {commits[0]['hash']} — {commits[0]['mensagem'][:60]}"
            )

        # 2. Logs backend
        logs  = self._ler_logs_container("conecta-pro-backend", 200)
        erros = self._detectar_erros_logs(logs)
        for tipo, exemplos in erros.items():
            investigacao["evidencias"].append(
                f"Logs: {len(exemplos)} erro(s) de {tipo}"
            )

        # 3. Banco — conexões idle
        idle_tx = self._conexoes_idle_banco()
        if idle_tx > 5:
            investigacao["evidencias"].append(
                f"Banco: {idle_tx} conexões 'idle in transaction' — possível lock"
            )

        # 4. Causa raiz (por prioridade de evidências)
        if erros.get("importacao"):
            investigacao.update(
                causa_raiz="Erro de importação Python — possível dependência quebrada no último deploy",
                acao_recomendada="Verificar requirements.txt e reiniciar backend",
                confianca=85, requer_jordan=True,
            )
        elif erros.get("banco"):
            investigacao.update(
                causa_raiz="Erro no banco — migration incompleta ou query inválida",
                acao_recomendada="Verificar migrations e logs do PostgreSQL",
                confianca=80, requer_jordan=True,
            )
        elif idle_tx > 5:
            investigacao.update(
                causa_raiz=f"Lock no banco — {idle_tx} conexões presas em transação",
                acao_recomendada="Terminar conexões idle in transaction",
                confianca=75,
            )
        elif erros.get("conexao"):
            investigacao.update(
                causa_raiz="Serviço dependente indisponível — Redis ou serviço externo offline",
                acao_recomendada="Verificar containers e reiniciar serviços",
                confianca=75,
            )
        elif commits:
            investigacao.update(
                causa_raiz=(
                    f"Possível regressão pelo commit {commits[0]['hash']}: "
                    f"{commits[0]['mensagem'][:50]}"
                ),
                acao_recomendada="Analisar diff do último commit, considerar rollback",
                confianca=60, requer_jordan=True,
            )
        else:
            investigacao.update(
                causa_raiz="Causa não identificada automaticamente",
                confianca=0, requer_jordan=True,
            )

        self.historico.append(investigacao)
        self._salvar_historico()
        return investigacao

    def investigar_performance(
        self, endpoint: str, tempo_ms: int
    ) -> dict:
        """Investiga causa de endpoint lento."""
        investigacao: dict = {
            "tipo": "performance",
            "endpoint": endpoint,
            "tempo_ms": tempo_ms,
            "timestamp": datetime.now().isoformat(),
            "causa_raiz": "",
            "evidencias": [],
        }

        # Swap
        r = subprocess.run(
            "free -m | awk 'NR==3{print $3}'",
            shell=True, capture_output=True, text=True,
        )
        swap_mb = int(r.stdout.strip() or 0)
        if swap_mb > 2000:
            investigacao["evidencias"].append(
                f"Swap: {swap_mb}MB — sistema usando disco como RAM"
            )
            investigacao["causa_raiz"] = (
                f"Swap alto ({swap_mb}MB) causando degradação de performance"
            )

        # Conexões abertas
        r2 = _q1(
            "SELECT COUNT(*) AS total FROM pg_stat_activity "
            "WHERE datname = 'conecta_pro' AND state = 'active'"
        )
        conn_ativas = int(r2.get("total", 0) or 0)
        if conn_ativas > 30:
            investigacao["evidencias"].append(
                f"Banco: {conn_ativas} conexões ativas simultaneamente"
            )
            if not investigacao["causa_raiz"]:
                investigacao["causa_raiz"] = (
                    f"Excesso de conexões abertas no banco ({conn_ativas})"
                )

        if not investigacao["causa_raiz"]:
            investigacao["causa_raiz"] = (
                f"Endpoint {endpoint} lento ({tempo_ms}ms) — causa não identificada"
            )

        self.historico.append(investigacao)
        self._salvar_historico()
        return investigacao

    def investigar_anomalia(
        self, metrica: str, valor: float, historico_valores: list
    ) -> dict:
        """Detecta e investiga anomalias estatísticas (z-score > 2.5σ)."""
        if len(historico_valores) < 5:
            return {"anomalia": False}

        media  = sum(historico_valores) / len(historico_valores)
        variancia = sum((x - media) ** 2 for x in historico_valores) / len(historico_valores)
        desvio = variancia ** 0.5
        z_score = (valor - media) / desvio if desvio > 0 else 0
        is_anomalia = abs(z_score) > 2.5

        return {
            "anomalia": is_anomalia,
            "metrica": metrica,
            "valor": valor,
            "media_historica": round(media, 2),
            "desvio": round(desvio, 2),
            "z_score": round(z_score, 2),
            "descricao": (
                f"{metrica} em {valor} está {abs(z_score):.1f}σ "
                f"{'acima' if z_score > 0 else 'abaixo'} da média ({media:.1f})"
            ) if is_anomalia else "",
        }

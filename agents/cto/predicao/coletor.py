"""
Coletor — Coleta e persiste métricas históricas.
Base de dados para predição de problemas.

Métricas coletadas a cada 5min:
- CPU load, RAM, Swap, Disco
- Tempo de resposta de endpoints críticos
- Tamanho das filas Celery
- Conexões ativas no PostgreSQL
- Contagem de erros nos logs
- Score dos agentes
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


PREDICAO_DIR = Path("/opt/conecta-pro/agents/cto/predicao")
HISTORICO_DIR = PREDICAO_DIR / "historico"
METRICAS_FILE = HISTORICO_DIR / "metricas.json"

# Manter 7 dias de histórico (7*24*12 = 2016 pontos)
MAX_PONTOS = 2016


def run(cmd: str) -> str:
    r = subprocess.run(
        cmd, shell=True,
        capture_output=True, text=True,
        timeout=10,
    )
    return r.stdout.strip()


class Coletor:
    """Coleta métricas para série temporal."""

    def __init__(self):
        HISTORICO_DIR.mkdir(parents=True, exist_ok=True)
        self.historico = self._carregar()

    def _carregar(self) -> list:
        if METRICAS_FILE.exists():
            try:
                return json.loads(METRICAS_FILE.read_text())
            except Exception:
                pass
        return []

    def _salvar(self):
        # Manter apenas últimos MAX_PONTOS
        self.historico = self.historico[-MAX_PONTOS:]
        METRICAS_FILE.write_text(
            json.dumps(self.historico, ensure_ascii=False, default=str)
        )

    def _metrica_float(self, cmd: str, default: float = 0.0) -> float:
        try:
            return float(run(cmd) or default)
        except Exception:
            return default

    def _metrica_int(self, cmd: str, default: int = 0) -> int:
        try:
            return int(run(cmd) or default)
        except Exception:
            return default

    def _tempo_endpoint(self, path: str) -> float:
        """Mede tempo de resposta de endpoint."""
        start = time.time()
        r = subprocess.run(
            f"curl -sf -o /dev/null -w '%{{http_code}}' "
            f"http://127.0.0.1:8080{path}",
            shell=True, capture_output=True,
            text=True, timeout=10,
        )
        elapsed = (time.time() - start) * 1000  # ms
        ok = r.stdout.strip() == "200"
        return round(elapsed, 1) if ok else -1

    def coletar(self) -> dict:
        """Coleta snapshot completo de métricas."""
        ponto = {
            "ts": datetime.now().isoformat(),
            "hora": datetime.now().hour,
            "dia_semana": datetime.now().weekday(),
        }

        # Sistema
        ponto["cpu_1m"] = self._metrica_float(
            "cat /proc/loadavg | awk '{print $1}'"
        )
        ponto["cpu_5m"] = self._metrica_float(
            "cat /proc/loadavg | awk '{print $2}'"
        )
        ponto["ram_pct"] = self._metrica_float(
            "free -m | awk 'NR==2{printf \"%.1f\",$3/$2*100}'"
        )
        ponto["swap_mb"] = self._metrica_int(
            "free -m | awk 'NR==3{print $3}'"
        )
        ponto["swap_pct"] = self._metrica_float(
            "free -m | awk 'NR==3{printf \"%.1f\",$3/$2*100}'"
        )
        ponto["disco_pct"] = self._metrica_float(
            "df -m / | awk 'NR==2{printf \"%.1f\",$3/$2*100}'"
        )

        # Celery
        ponto["celery_queue"] = self._metrica_int(
            "docker exec conecta-pro-redis "
            "redis-cli llen celery 2>/dev/null"
        )

        # PostgreSQL conexões
        ponto["pg_conexoes"] = self._metrica_int(
            "docker exec conecta-pro-postgres psql "
            "-U erp -d erp_db -t -c "
            "'SELECT COUNT(*) FROM pg_stat_activity;' 2>/dev/null"
        )

        # Erros nos logs (últimos 5min)
        ponto["erros_log"] = self._metrica_int(
            "docker logs conecta-pro-backend --since 5m 2>&1 | "
            "grep -ci 'error\\|exception\\|traceback' 2>/dev/null || echo 0"
        )

        # Tempo de resposta endpoints críticos
        ponto["t_health"] = self._tempo_endpoint("/health")
        ponto["t_auth"] = self._tempo_endpoint("/api/v1/auth/login")

        # Containers saudáveis
        ponto["containers_rodando"] = self._metrica_int(
            "docker ps --filter status=running --format '{{.Names}}' | wc -l"
        )

        return ponto

    def executar(self) -> dict:
        """Coleta e persiste ponto."""
        ponto = self.coletar()
        self.historico.append(ponto)
        self._salvar()
        return ponto

    def obter_serie(self, metrica: str, ultimos_n: int = 100) -> list:
        """Retorna série temporal de uma métrica."""
        return [
            {"ts": p["ts"], "valor": p.get(metrica, 0)}
            for p in self.historico[-ultimos_n:]
        ]

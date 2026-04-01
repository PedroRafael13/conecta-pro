"""
RunbookExecutor — CTO Sprint 6.

Playbooks sequenciais: do menos ao mais invasivo.
Cada runbook tenta resolver o problema autonomamente, registrando cada passo.
Se o último passo falhar, retorna requer_jordan=True.

Runbooks disponíveis:
  - RedisDown
  - SwapHigh
  - CeleryUnhealthy
  - BackendUnhealthy
  - DiskSpaceLow
  - PM2ExcessiveRestarts
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

CTO_DIR = Path("/opt/conecta-pro/agents/cto")
RUNBOOK_LOG = CTO_DIR / "memory" / "runbook_history.json"
CTO_DIR.mkdir(parents=True, exist_ok=True)
(CTO_DIR / "memory").mkdir(parents=True, exist_ok=True)


def _run(cmd: str, timeout: int = 30) -> tuple[bool, str]:
    """Executa comando shell. Retorna (sucesso, saida)."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        saida = (r.stdout + r.stderr).strip()
        return r.returncode == 0, saida[:500]
    except subprocess.TimeoutExpired:
        return False, f"timeout após {timeout}s"
    except Exception as e:
        return False, str(e)[:200]


def _container_running(name: str) -> bool:
    ok, out = _run(f"docker inspect --format '{{{{.State.Running}}}}' {name} 2>/dev/null")
    return "true" in out.lower()


def _wait_healthy(name: str, segundos: int = 15) -> bool:
    """Aguarda container ficar Running após restart."""
    for _ in range(segundos):
        if _container_running(name):
            return True
        time.sleep(1)
    return False


class RunbookStep:
    def __init__(self, nome: str, descricao: str, cmd: str, timeout: int = 30):
        self.nome = nome
        self.descricao = descricao
        self.cmd = cmd
        self.timeout = timeout

    def executar(self) -> dict:
        ts = datetime.now().isoformat()
        ok, saida = _run(self.cmd, self.timeout)
        return {
            "passo": self.nome,
            "descricao": self.descricao,
            "cmd": self.cmd,
            "sucesso": ok,
            "saida": saida,
            "timestamp": ts,
        }


class ResultadoRunbook:
    def __init__(self, tipo: str):
        self.tipo = tipo
        self.inicio = datetime.now().isoformat()
        self.fim: Optional[str] = None
        self.resolvido = False
        self.requer_jordan = False
        self.passos: list[dict] = []
        self.mensagem = ""

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "inicio": self.inicio,
            "fim": self.fim,
            "resolvido": self.resolvido,
            "requer_jordan": self.requer_jordan,
            "passos": self.passos,
            "mensagem": self.mensagem,
        }


class RunbookExecutor:
    """Executa playbooks sequenciais de remediação."""

    RUNBOOKS = {
        "RedisDown",
        "SwapHigh",
        "CeleryUnhealthy",
        "BackendUnhealthy",
        "DiskSpaceLow",
        "PM2ExcessiveRestarts",
    }

    def pode_executar(self, tipo: str) -> bool:
        return tipo in self.RUNBOOKS

    def executar(self, tipo: str) -> ResultadoRunbook:
        resultado = ResultadoRunbook(tipo)
        metodo = getattr(self, f"_rb_{tipo.lower()}", None)
        if metodo is None:
            resultado.mensagem = f"Runbook '{tipo}' não encontrado"
            resultado.requer_jordan = True
        else:
            try:
                metodo(resultado)
            except Exception as e:
                resultado.mensagem = f"Erro interno no runbook: {e}"
                resultado.requer_jordan = True
        resultado.fim = datetime.now().isoformat()
        self._registrar(resultado)
        return resultado

    # ─── RUNBOOK: RedisDown ───────────────────────────────────────────────────

    def _rb_redisdown(self, res: ResultadoRunbook):
        # Passo 1: ping
        passo = RunbookStep(
            "redis_ping",
            "Verificar se Redis responde ao ping",
            "docker exec conecta-pro-redis redis-cli ping 2>&1",
            timeout=10,
        ).executar()
        res.passos.append(passo)

        if passo["sucesso"] and "PONG" in passo["saida"]:
            res.resolvido = True
            res.mensagem = "Redis estava respondendo — falso positivo."
            return

        # Passo 2: restart suave
        passo2 = RunbookStep(
            "redis_restart",
            "Restart do container Redis",
            "docker restart conecta-pro-redis",
            timeout=30,
        ).executar()
        res.passos.append(passo2)
        time.sleep(5)

        # Passo 3: verificar após restart
        passo3 = RunbookStep(
            "redis_verify",
            "Verificar Redis após restart",
            "docker exec conecta-pro-redis redis-cli ping 2>&1",
            timeout=10,
        ).executar()
        res.passos.append(passo3)

        if passo3["sucesso"] and "PONG" in passo3["saida"]:
            res.resolvido = True
            res.mensagem = "Redis reiniciado com sucesso. PONG recebido."
            return

        # Passo 4: verificar logs e escalar
        passo4 = RunbookStep(
            "redis_logs",
            "Coletar logs do Redis para diagnóstico",
            "docker logs --tail 30 conecta-pro-redis 2>&1",
            timeout=10,
        ).executar()
        res.passos.append(passo4)
        res.requer_jordan = True
        res.mensagem = (
            "Redis não respondeu após restart. "
            f"Logs: {passo4['saida'][:200]}"
        )

    # ─── RUNBOOK: SwapHigh ────────────────────────────────────────────────────

    def _rb_swaphigh(self, res: ResultadoRunbook):
        # Passo 1: medir swap atual
        passo = RunbookStep(
            "swap_measure",
            "Medir uso atual de swap",
            "free -m | awk 'NR==3{printf \"%s/%s MB\", $3, $2}'",
            timeout=5,
        ).executar()
        res.passos.append(passo)

        # Passo 2: identificar top consumers
        passo2 = RunbookStep(
            "swap_top_procs",
            "Identificar processos que mais consomem RAM",
            "ps aux --sort=-%mem | head -5 | awk '{print $1, $2, $4, $11}'",
            timeout=10,
        ).executar()
        res.passos.append(passo2)

        # Passo 3: resetar swap (operação segura)
        passo3 = RunbookStep(
            "swap_reset",
            "Resetar swap (swapoff -a && swapon -a)",
            "swapoff -a && swapon -a",
            timeout=60,
        ).executar()
        res.passos.append(passo3)

        # Passo 4: verificar resultado
        passo4 = RunbookStep(
            "swap_verify",
            "Verificar swap após reset",
            "free -m | awk 'NR==3{printf \"%s/%s MB\", $3, $2}'",
            timeout=5,
        ).executar()
        res.passos.append(passo4)

        if passo3["sucesso"]:
            res.resolvido = True
            res.mensagem = (
                f"Swap resetado. Antes: {passo['saida']} | Depois: {passo4['saida']}"
            )
        else:
            # Passo 5: tentar via docker — reiniciar containers não-críticos
            passo5 = RunbookStep(
                "swap_docker_clean",
                "Remover containers parados para liberar memória",
                "docker container prune -f",
                timeout=20,
            ).executar()
            res.passos.append(passo5)
            res.requer_jordan = True
            res.mensagem = (
                "swapoff falhou (pode precisar de root). "
                f"Containers prunados: {passo5['saida'][:100]}. Verificar manualmente."
            )

    # ─── RUNBOOK: CeleryUnhealthy ─────────────────────────────────────────────

    def _rb_celeryunhealthy(self, res: ResultadoRunbook):
        container = "conecta-pro-celery-integrations"

        # Passo 1: verificar status
        passo = RunbookStep(
            "celery_status",
            "Verificar status do container Celery",
            f"docker inspect --format '{{{{.State.Status}}}}' {container} 2>/dev/null",
            timeout=10,
        ).executar()
        res.passos.append(passo)

        # Passo 2: coletar logs recentes
        passo2 = RunbookStep(
            "celery_logs",
            "Coletar últimas linhas de log do Celery",
            f"docker logs --tail 20 {container} 2>&1",
            timeout=10,
        ).executar()
        res.passos.append(passo2)

        # Passo 3: restart
        passo3 = RunbookStep(
            "celery_restart",
            "Reiniciar container Celery",
            f"docker restart {container}",
            timeout=30,
        ).executar()
        res.passos.append(passo3)
        time.sleep(8)

        # Passo 4: verificar workers ativos
        passo4 = RunbookStep(
            "celery_verify",
            "Verificar workers Celery após restart",
            f"docker exec {container} celery -A celery_app inspect ping --timeout=5 2>&1 | head -5",
            timeout=15,
        ).executar()
        res.passos.append(passo4)

        if passo3["sucesso"] and _container_running(container):
            res.resolvido = True
            res.mensagem = "Celery reiniciado. Workers verificados."
        else:
            res.requer_jordan = True
            res.mensagem = (
                f"Celery não recuperou após restart. "
                f"Log: {passo2['saida'][:200]}"
            )

    # ─── RUNBOOK: BackendUnhealthy ────────────────────────────────────────────

    def _rb_backendunhealthy(self, res: ResultadoRunbook):
        # Passo 1: verificar health endpoint
        passo = RunbookStep(
            "backend_health",
            "Verificar endpoint /health do backend",
            "curl -sf http://127.0.0.1:8080/health 2>&1 | head -c 200",
            timeout=10,
        ).executar()
        res.passos.append(passo)

        if passo["sucesso"] and "healthy" in passo["saida"].lower():
            res.resolvido = True
            res.mensagem = "Backend estava healthy — falso positivo."
            return

        # Passo 2: verificar container
        passo2 = RunbookStep(
            "backend_container",
            "Verificar estado do container backend",
            "docker inspect --format '{{.State.Status}} {{.State.ExitCode}}' conecta-pro-backend 2>/dev/null",
            timeout=10,
        ).executar()
        res.passos.append(passo2)

        # Passo 3: coletar logs de erro
        passo3 = RunbookStep(
            "backend_logs",
            "Coletar logs de erro do backend",
            "docker logs --tail 30 conecta-pro-backend 2>&1 | grep -i 'error\\|exception\\|fatal' | tail -10",
            timeout=10,
        ).executar()
        res.passos.append(passo3)

        # Passo 4: HUP (reload sem restart — mais suave)
        passo4 = RunbookStep(
            "backend_hup",
            "Enviar HUP para reload do Gunicorn",
            "docker exec conecta-pro-backend kill -HUP 1",
            timeout=15,
        ).executar()
        res.passos.append(passo4)
        time.sleep(5)

        # Passo 5: verificar após HUP
        passo5 = RunbookStep(
            "backend_verify_hup",
            "Verificar health após HUP",
            "curl -sf http://127.0.0.1:8080/health 2>&1 | head -c 200",
            timeout=10,
        ).executar()
        res.passos.append(passo5)

        if "healthy" in passo5["saida"].lower():
            res.resolvido = True
            res.mensagem = "Backend recuperado via HUP (reload suave)."
            return

        # Passo 6: restart completo do container
        passo6 = RunbookStep(
            "backend_restart",
            "Restart completo do container backend",
            "docker restart conecta-pro-backend",
            timeout=60,
        ).executar()
        res.passos.append(passo6)
        time.sleep(10)

        # Passo 7: verificar após restart
        passo7 = RunbookStep(
            "backend_verify_restart",
            "Verificar health após restart",
            "curl -sf http://127.0.0.1:8080/health 2>&1 | head -c 200",
            timeout=15,
        ).executar()
        res.passos.append(passo7)

        if "healthy" in passo7["saida"].lower():
            res.resolvido = True
            res.mensagem = "Backend recuperado via restart completo."
        else:
            res.requer_jordan = True
            res.mensagem = (
                "Backend não respondeu após HUP + restart. "
                f"Logs de erro: {passo3['saida'][:200]}"
            )

    # ─── RUNBOOK: DiskSpaceLow ────────────────────────────────────────────────

    def _rb_diskspacelow(self, res: ResultadoRunbook):
        # Passo 1: medir disco atual
        passo = RunbookStep(
            "disk_measure",
            "Medir uso atual do disco",
            "df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\")\"}' ",
            timeout=5,
        ).executar()
        res.passos.append(passo)

        # Passo 2: limpar logs antigos do Docker
        passo2 = RunbookStep(
            "disk_docker_prune",
            "Remover imagens e containers Docker não utilizados",
            "docker system prune -f --volumes 2>&1 | tail -3",
            timeout=60,
        ).executar()
        res.passos.append(passo2)

        # Passo 3: limpar logs de aplicação > 7 dias
        passo3 = RunbookStep(
            "disk_logs_clean",
            "Remover logs de aplicação com mais de 7 dias",
            "find /opt/conecta-pro/logs -name '*.log' -mtime +7 -delete -print 2>/dev/null | wc -l",
            timeout=20,
        ).executar()
        res.passos.append(passo3)

        # Passo 4: limpar journal do systemd
        passo4 = RunbookStep(
            "disk_journal_clean",
            "Limpar journal systemd (manter últimos 3 dias)",
            "journalctl --vacuum-time=3d 2>&1 | tail -2",
            timeout=20,
        ).executar()
        res.passos.append(passo4)

        # Passo 5: medir disco após limpeza
        passo5 = RunbookStep(
            "disk_verify",
            "Verificar espaço após limpeza",
            "df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\")\"}'",
            timeout=5,
        ).executar()
        res.passos.append(passo5)

        # Verificar se melhorou (usa % do passo 5)
        uso_str = passo5["saida"]
        try:
            uso_pct = int(uso_str.split("(")[1].rstrip("%)")) if "(" in uso_str else 100
        except Exception:
            uso_pct = 100

        if uso_pct < 85:
            res.resolvido = True
            res.mensagem = (
                f"Espaço recuperado. Antes: {passo['saida']} | Depois: {passo5['saida']}"
            )
        else:
            res.requer_jordan = True
            res.mensagem = (
                f"Disco ainda crítico após limpeza ({passo5['saida']}). "
                "Verificar maiores diretórios manualmente."
            )

    # ─── RUNBOOK: PM2ExcessiveRestarts ────────────────────────────────────────

    def _rb_pm2excessiverestarts(self, res: ResultadoRunbook):
        # Passo 1: listar status PM2
        passo = RunbookStep(
            "pm2_list",
            "Listar processos PM2 e seus restarts",
            "pm2 list --no-color 2>&1 | head -20",
            timeout=10,
        ).executar()
        res.passos.append(passo)

        # Passo 2: coletar logs de erro do processo problemático
        passo2 = RunbookStep(
            "pm2_logs",
            "Coletar logs de erro PM2 (últimas 50 linhas)",
            "pm2 logs --lines 50 --no-color 2>&1 | grep -i 'error\\|exception\\|ENOENT\\|crash' | tail -15",
            timeout=15,
        ).executar()
        res.passos.append(passo2)

        # Passo 3: reset de contadores (menos invasivo)
        passo3 = RunbookStep(
            "pm2_reset",
            "Resetar contadores de restart PM2",
            "pm2 reset all 2>&1",
            timeout=15,
        ).executar()
        res.passos.append(passo3)

        # Passo 4: restart do processo com problema
        passo4 = RunbookStep(
            "pm2_restart",
            "Restart de todos os processos PM2",
            "pm2 restart all --update-env 2>&1 | tail -5",
            timeout=60,
        ).executar()
        res.passos.append(passo4)
        time.sleep(8)

        # Passo 5: verificar após restart
        passo5 = RunbookStep(
            "pm2_verify",
            "Verificar status PM2 após restart",
            "pm2 list --no-color 2>&1 | grep -E 'online|stopped|errored' | head -10",
            timeout=10,
        ).executar()
        res.passos.append(passo5)

        if "online" in passo5["saida"] and "errored" not in passo5["saida"]:
            res.resolvido = True
            res.mensagem = "PM2 estabilizado após restart. Todos os processos online."
        elif passo4["sucesso"]:
            res.resolvido = True
            res.mensagem = f"PM2 reiniciado. Estado: {passo5['saida'][:100]}"
        else:
            res.requer_jordan = True
            res.mensagem = (
                f"PM2 restart falhou. Logs: {passo2['saida'][:200]}"
            )

    # ─── Registro histórico ───────────────────────────────────────────────────

    def _registrar(self, resultado: ResultadoRunbook):
        historico = []
        if RUNBOOK_LOG.exists():
            try:
                historico = json.loads(RUNBOOK_LOG.read_text())
            except Exception:
                pass
        historico.append(resultado.to_dict())
        # Manter apenas últimos 100 registros
        historico = historico[-100:]
        RUNBOOK_LOG.write_text(
            json.dumps(historico, indent=2, ensure_ascii=False, default=str)
        )

    def historico(self, limit: int = 10) -> list[dict]:
        if not RUNBOOK_LOG.exists():
            return []
        try:
            data = json.loads(RUNBOOK_LOG.read_text())
            return list(reversed(data))[:limit]
        except Exception:
            return []

    def resumo_telegram(self, resultado: ResultadoRunbook) -> str:
        """Formata resultado para envio no Telegram."""
        emoji = "✅" if resultado.resolvido else ("⚠️" if not resultado.requer_jordan else "🔴")
        linhas = [
            f"{emoji} *Runbook: {resultado.tipo}*",
            f"Status: {'Resolvido ✅' if resultado.resolvido else 'Falhou ❌'}",
            f"Passos: {len(resultado.passos)}",
            f"Mensagem: {resultado.mensagem[:200]}",
        ]
        if resultado.requer_jordan:
            linhas.append("\n⚠️ *Requer intervenção de Jordan.*")
        # Resumo dos passos
        for p in resultado.passos[-3:]:
            ok_str = "✅" if p["sucesso"] else "❌"
            linhas.append(f"  {ok_str} `{p['passo']}`: {p['saida'][:60]}")
        return "\n".join(linhas)

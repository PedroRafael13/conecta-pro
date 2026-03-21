"""
Serviço de remediação automática v2.

Proteções contra falsos positivos:
- Validação de ferramentas antes de diagnosticar
- Threshold de confirmação (3 checks em 30s antes de agir)
- Distinção de tipos de falha (PONG/NOAUTH/refused/timeout)
"""

import asyncio
import shutil
import subprocess
import time


def _run(cmd: str, timeout: int = 30) -> tuple[int, str]:
    """Executa comando shell e retorna (returncode, output)."""
    try:
        result = subprocess.run(  # noqa: S602, S603  # nosec B602
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output[:2000]
    except subprocess.TimeoutExpired:
        return -1, f"Timeout apos {timeout}s"
    except Exception as e:
        return -1, str(e)[:500]


# =========================================================================
# TIPOS DE FALHA — para classificação precisa
# =========================================================================


class FailureType:
    HEALTHY = "healthy"  # Serviço respondendo normalmente
    AUTH_ERROR = "auth_error"  # NOAUTH / credencial errada
    CONNECTION_REFUSED = "refused"  # Serviço não está escutando
    TIMEOUT = "timeout"  # Serviço lento / sobrecarregado
    TOOL_MISSING = "tool_missing"  # Ferramenta de diagnóstico indisponível
    UNKNOWN = "unknown"


ACTIONABLE_FAILURES = {FailureType.CONNECTION_REFUSED}
NON_ACTIONABLE_FAILURES = {FailureType.AUTH_ERROR, FailureType.TIMEOUT, FailureType.TOOL_MISSING}


class RemediationService:
    """Executa diagnóstico e ações corretivas por tipo de alerta."""

    HANDLERS: dict[str, str] = {
        "PostgresDown": "_handle_postgres",
        "PostgresConnectionLost": "_handle_postgres",
        "ERPAPIDown": "_handle_erp_api",
        "RedisDown": "_handle_redis",
        "CeleryDown": "_handle_celery",
        "DiskSpaceLow": "_handle_disk",
        "DiskSpaceCritical": "_handle_disk",
        "HighMemoryUsage": "_handle_memory",
        "HighLoadAverage": "_handle_load",
    }

    # Ferramentas requeridas por handler
    REQUIRED_TOOLS: dict[str, list[str]] = {
        "_handle_redis": ["redis-cli", "docker"],
        "_handle_postgres": ["docker"],
        "_handle_erp_api": ["curl", "docker"],
        "_handle_celery": ["docker"],
        "_handle_disk": ["df", "docker"],
        "_handle_memory": ["free", "ps"],
        "_handle_load": ["ps"],
    }

    async def diagnose_and_act(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        handler_name = self.HANDLERS.get(alert_name)
        if not handler_name:
            return (
                f"Alerta '{alert_name}' recebido mas sem handler de remediacao configurado.",
                [{"step": "skip", "detail": "Sem handler mapeado"}],
            )

        # 1. Validar ferramentas necessárias
        missing = self._check_tools(handler_name)
        if missing:
            diag = (
                f"DIAGNOSTIC_ERROR: ferramentas indisponíveis para diagnosticar {alert_name}: "
                f"{', '.join(missing)}. Diagnóstico abortado — NÃO é uma queda do serviço."
            )
            return diag, [
                {"step": "tool_validation", "result": "FAILED", "missing": missing},
                {"step": "false_positive", "reason": "tool_missing"},
            ]

        handler = getattr(self, handler_name)
        return await asyncio.to_thread(handler, alert_name, severity, annotations)

    def _check_tools(self, handler_name: str) -> list[str]:
        """Verifica se as ferramentas necessárias estão disponíveis."""
        required = self.REQUIRED_TOOLS.get(handler_name, [])
        missing = []
        for tool in required:
            if not shutil.which(tool):
                # Também verificar via _run para binários em paths não-standard
                rc, _ = _run(f"which {tool} 2>/dev/null")
                if rc != 0:
                    missing.append(tool)
        return missing

    # =========================================================================
    # THRESHOLD DE CONFIRMAÇÃO — 3 checks em 30s antes de agir
    # =========================================================================

    def _confirm_down(self, check_fn, interval: int = 10, attempts: int = 3) -> tuple[bool, list[dict]]:
        """
        Confirma que um serviço está realmente down antes de agir.

        Executa check_fn 3 vezes com 10s de intervalo.
        Retorna (confirmed_down, confirmation_steps).
        Se resolver sozinho em qualquer tentativa, retorna (False, steps).
        """
        steps = []
        for i in range(attempts):
            if i > 0:
                time.sleep(interval)
            failure_type, detail = check_fn()
            steps.append(
                {
                    "step": f"confirmation_{i + 1}",
                    "failure_type": failure_type,
                    "detail": detail,
                    "elapsed_seconds": i * interval,
                }
            )
            if failure_type == FailureType.HEALTHY:
                # Serviço voltou sozinho — falso positivo
                steps.append({"step": "false_positive", "reason": f"auto_recovered_at_check_{i + 1}"})
                return False, steps
            if failure_type in NON_ACTIONABLE_FAILURES:
                # Problema de config/ferramenta, não de infra
                steps.append({"step": "false_positive", "reason": failure_type})
                return False, steps
        return True, steps

    # =========================================================================
    # CLASSIFICADOR DE FALHA REDIS
    # =========================================================================

    def _classify_redis_failure(self) -> tuple[str, str]:
        """
        Classifica o tipo de falha do Redis.

        Returns:
            (FailureType, detail_string)
        """
        pw = self._get_redis_password()
        auth = f"-a '{pw}'" if pw else ""

        # Tentar ping com autenticação
        rc, out = _run(f"redis-cli -h redis -p 6379 {auth} ping 2>&1", timeout=5)

        if "PONG" in out:
            return FailureType.HEALTHY, "PONG"
        if "NOAUTH" in out or "AUTH" in out:
            return FailureType.AUTH_ERROR, f"Erro de autenticação: {out[:100]}"
        if "Connection refused" in out or "Could not connect" in out:
            return FailureType.CONNECTION_REFUSED, "Conexão recusada — Redis não está respondendo"
        if "Timeout" in out.lower() or rc == -1:
            return FailureType.TIMEOUT, f"Timeout na conexão: {out[:100]}"
        if not out.strip():
            # redis-cli retornou vazio — possível problema de ferramenta
            rc2, which_out = _run("which redis-cli 2>/dev/null")
            if rc2 != 0:
                return FailureType.TOOL_MISSING, "redis-cli não encontrado"
            return FailureType.UNKNOWN, "Resposta vazia do redis-cli"

        return FailureType.UNKNOWN, f"Resposta não reconhecida: {out[:100]}"

    # =========================================================================
    # REDIS PASSWORD
    # =========================================================================

    def _get_redis_password(self) -> str:
        """Lê a senha do Redis (REDIS_PASSWORD ou extraída de REDIS_URL)."""
        import os
        import re

        pw = os.getenv("REDIS_PASSWORD", "")
        if not pw:
            redis_url = os.getenv("REDIS_URL", "")
            m = re.search(r"://:(.*?)@", redis_url)
            if m:
                pw = m.group(1)
        return pw

    def _redis_cli(self, cmd: str = "ping") -> tuple[int, str]:
        """Executa redis-cli com autenticação."""
        pw = self._get_redis_password()
        auth = f"-a '{pw}'" if pw else ""
        return _run(f"redis-cli -h redis -p 6379 {auth} {cmd} 2>/dev/null")

    # =========================================================================
    # HANDLERS POR TIPO DE ALERTA
    # =========================================================================

    def _handle_redis(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        # 1. Container status
        rc, out = _run("docker inspect --format='{{.State.Status}}' conecta-pro-redis 2>/dev/null")
        container_status = out.strip().strip("'")
        actions.append({"step": "check_container", "result": container_status})
        diag_parts.append(f"Container Redis: {container_status}")

        # 2. Classificar tipo de falha
        failure_type, detail = self._classify_redis_failure()
        actions.append({"step": "classify_failure", "failure_type": failure_type, "detail": detail})
        diag_parts.append(f"Classificacao: {failure_type} ({detail})")

        # 3. Se saudável ou não-acionável → falso positivo
        if failure_type == FailureType.HEALTHY:
            diag_parts.append("Redis respondendo normalmente — alerta era falso positivo")
            actions.append({"step": "false_positive", "reason": "healthy_on_first_check"})
            return "DIAGNOSTICO Redis:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        if failure_type in NON_ACTIONABLE_FAILURES:
            diag_parts.append(f"Problema de {failure_type} — NÃO é queda do serviço, não reiniciar")
            actions.append({"step": "false_positive", "reason": failure_type})
            return "DIAGNOSTICO Redis:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        # 4. Threshold de confirmação (3 checks em 30s)
        diag_parts.append("Iniciando confirmacao (3 checks em 30s)...")
        confirmed, confirm_steps = self._confirm_down(self._classify_redis_failure)
        actions.extend(confirm_steps)

        if not confirmed:
            reason = next(
                (s.get("reason", "auto_recovered") for s in confirm_steps if s.get("step") == "false_positive"),
                "auto_recovered",
            )
            diag_parts.append(f"Redis recuperou sozinho durante confirmacao — falso positivo ({reason})")
            return "DIAGNOSTICO Redis:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        # 5. CONFIRMADO DOWN — agir
        diag_parts.append("CONFIRMADO: Redis down apos 3 verificacoes")

        # Memória
        rc, out = self._redis_cli("info memory")
        mem_line = ""
        for line in out.split("\n"):
            if "used_memory_human" in line:
                mem_line = line.strip()
                break
        actions.append({"step": "memory_usage", "result": mem_line})
        if mem_line:
            diag_parts.append(f"Memoria: {mem_line}")

        # Restart
        rc, out = _run("docker restart conecta-pro-redis 2>/dev/null", timeout=30)
        actions.append({"step": "restart_container", "result": "executed"})
        diag_parts.append("Acao: container Redis reiniciado")

        time.sleep(5)

        failure_type_post, detail_post = self._classify_redis_failure()
        post_ok = failure_type_post == FailureType.HEALTHY
        actions.append(
            {
                "step": "post_restart_check",
                "result": "OK" if post_ok else "FALHA",
                "failure_type": failure_type_post,
                "detail": detail_post,
            }
        )
        diag_parts.append(
            f"Pos-restart: {'recuperado' if post_ok else 'ainda com problemas (' + failure_type_post + ')'}"
        )

        return "DIAGNOSTICO Redis:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

    def _handle_postgres(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        rc, out = _run("docker inspect --format='{{.State.Status}}' conecta-pro-postgres 2>/dev/null")
        container_status = out.strip().strip("'")
        actions.append({"step": "check_container", "result": container_status})
        diag_parts.append(f"Container PostgreSQL: {container_status}")

        rc, out = _run("docker exec conecta-pro-postgres pg_isready -U postgres 2>/dev/null")
        pg_ready = rc == 0
        actions.append({"step": "pg_isready", "result": out})
        diag_parts.append(f"pg_isready: {'OK' if pg_ready else 'FALHA'}")

        if pg_ready:
            diag_parts.append("PostgreSQL respondendo normalmente — alerta era falso positivo")
            actions.append({"step": "false_positive", "reason": "healthy_on_first_check"})
            return "DIAGNOSTICO PostgreSQL:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        # Confirmar 3 vezes
        def check_pg():
            rc2, _ = _run("docker exec conecta-pro-postgres pg_isready -U postgres 2>/dev/null")
            return (
                (FailureType.HEALTHY, "accepting connections")
                if rc2 == 0
                else (FailureType.CONNECTION_REFUSED, "pg_isready failed")
            )

        confirmed, steps = self._confirm_down(check_pg)
        actions.extend(steps)

        if not confirmed:
            diag_parts.append("PostgreSQL recuperou durante confirmacao — falso positivo")
            return "DIAGNOSTICO PostgreSQL:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        # Confirmado down — restart
        rc, out = _run(
            "docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t -c 'SELECT count(*) FROM pg_stat_activity' 2>/dev/null"
        )
        actions.append({"step": "active_connections", "result": out.strip()})
        diag_parts.append(f"Conexoes ativas: {out.strip()}")

        if container_status != "running":
            rc, out = _run("docker restart conecta-pro-postgres 2>/dev/null", timeout=60)
            actions.append({"step": "restart_container", "result": "executed"})
            diag_parts.append("Acao: container reiniciado")

            time.sleep(10)
            rc, out = _run("docker exec conecta-pro-postgres pg_isready -U postgres 2>/dev/null")
            actions.append({"step": "post_restart_check", "result": "OK" if rc == 0 else "FALHA"})
            diag_parts.append(f"Pos-restart: {'recuperado' if rc == 0 else 'ainda com problemas'}")

        return "DIAGNOSTICO PostgreSQL:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

    def _handle_erp_api(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        rc, out = _run("docker inspect --format='{{.State.Status}}' conecta-pro-backend 2>/dev/null")
        container_status = out.strip().strip("'")
        actions.append({"step": "check_container", "result": container_status})
        diag_parts.append(f"Container backend: {container_status}")

        rc, out = _run("curl -sf http://localhost:8080/health 2>/dev/null")
        health_ok = rc == 0
        actions.append({"step": "health_check", "result": out[:500] if health_ok else "FALHA"})
        diag_parts.append(f"Health check: {'OK' if health_ok else 'FALHA'}")

        if health_ok:
            diag_parts.append("Backend respondendo normalmente — falso positivo")
            actions.append({"step": "false_positive", "reason": "healthy_on_first_check"})
            return "DIAGNOSTICO ERP API:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        # Confirmar
        def check_api():
            rc2, _ = _run("curl -sf http://localhost:8080/health 2>/dev/null")
            return (
                (FailureType.HEALTHY, "200 OK") if rc2 == 0 else (FailureType.CONNECTION_REFUSED, "health check failed")
            )

        confirmed, steps = self._confirm_down(check_api)
        actions.extend(steps)

        if not confirmed:
            diag_parts.append("Backend recuperou durante confirmacao — falso positivo")
            return "DIAGNOSTICO ERP API:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

        rc, out = _run(
            "docker logs --tail 20 conecta-pro-backend 2>&1 | grep -i 'error\\|exception\\|traceback' | tail -5"
        )
        actions.append({"step": "check_logs", "result": out[:1000]})
        if out:
            diag_parts.append(f"Erros nos logs: {out[:200]}")

        rc, out = _run("docker restart conecta-pro-backend 2>/dev/null", timeout=120)
        actions.append({"step": "restart_container", "result": "executed"})
        diag_parts.append("Acao: container backend reiniciado")

        time.sleep(30)
        rc, out = _run("curl -sf http://localhost:8080/health 2>/dev/null")
        actions.append({"step": "post_restart_health", "result": "OK" if rc == 0 else "FALHA"})
        diag_parts.append(f"Pos-restart: {'recuperado' if rc == 0 else 'ainda com problemas'}")

        return "DIAGNOSTICO ERP API:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

    def _handle_celery(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        workers = [
            "conecta-pro-celery-priority",
            "conecta-pro-celery-sefaz",
            "conecta-pro-celery-nfse",
            "conecta-pro-celery-operacional",
            "conecta-pro-celery-batch",
            "conecta-pro-celery-integrations",
        ]

        down_workers = []
        for worker in workers:
            rc, out = _run(f"docker inspect --format='{{{{.State.Status}}}}' {worker} 2>/dev/null")
            status = out.strip().strip("'")
            actions.append({"step": f"check_{worker.split('-')[-1]}", "result": status})
            if status != "running":
                down_workers.append(worker)

        diag_parts.append(f"Workers verificados: {len(workers)}, down: {len(down_workers)}")

        for worker in down_workers:
            rc, out = _run(f"docker restart {worker} 2>/dev/null", timeout=60)
            actions.append({"step": f"restart_{worker.split('-')[-1]}", "result": "executed"})
            diag_parts.append(f"Reiniciado: {worker}")

        if not down_workers:
            diag_parts.append("Todos os workers ativos — falso positivo")
            actions.append({"step": "false_positive", "reason": "all_workers_running"})

        return "DIAGNOSTICO Celery:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

    def _handle_disk(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        rc, out = _run("df -h / | tail -1")
        actions.append({"step": "disk_usage", "result": out})
        diag_parts.append(f"Disco: {out}")

        rc, out = _run("du -sh /opt/conecta-pro/logs/ /opt/conecta-pro/uploads/ /opt/conecta-pro/backups/ 2>/dev/null")
        actions.append({"step": "large_dirs", "result": out})
        diag_parts.append(f"Diretorios grandes:\n{out}")

        rc, out = _run(
            "find /opt/conecta-pro/logs/ -name '*.log' -mtime +7 -delete 2>/dev/null && echo 'Logs antigos removidos'"
        )
        actions.append({"step": "cleanup_old_logs", "result": out})
        diag_parts.append(f"Limpeza: {out}")

        rc, out = _run("docker system prune -f 2>/dev/null | tail -1")
        actions.append({"step": "docker_prune", "result": out})
        diag_parts.append(f"Docker prune: {out}")

        return "DIAGNOSTICO Disco:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

    def _handle_memory(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        rc, out = _run("free -h")
        actions.append({"step": "memory_info", "result": out})
        diag_parts.append(f"Memoria:\n{out}")

        rc, out2 = _run("ps aux --sort=-%mem | head -6")
        actions.append({"step": "top_memory_procs", "result": out2})
        diag_parts.append(f"Top processos:\n{out2}")

        rc, mem_pct = _run("free | awk '/^Mem:/ {printf \"%.0f\", $3/$2*100}'")
        try:
            pct = int(mem_pct.strip())
        except (ValueError, AttributeError):
            pct = 0

        if pct > 90:
            _, flush_out = self._redis_cli("FLUSHDB")
            actions.append({"step": "redis_flush", "result": flush_out})
            diag_parts.append(f"Acao: Redis FLUSHDB executado (RAM em {pct}%)")

            _run("sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null")
            actions.append({"step": "drop_caches", "result": "executed"})
            diag_parts.append("Acao: drop_caches executado")
        elif pct < 85:
            diag_parts.append(f"RAM em {pct}% — abaixo do threshold, alerta pode ser falso positivo")
            actions.append({"step": "false_positive", "reason": f"memory_at_{pct}_percent"})

        return "DIAGNOSTICO Memoria:\n" + "\n".join(f"  - {p}" for p in diag_parts), actions

    def _handle_load(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        rc, out = _run("uptime")
        actions.append({"step": "uptime", "result": out})
        rc, out2 = _run("ps aux --sort=-%cpu | head -6")
        actions.append({"step": "top_cpu_procs", "result": out2})

        return f"DIAGNOSTICO Load:\n  - {out}\n  - Top processos:\n{out2}", actions

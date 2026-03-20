"""
Serviço de remediação automática.

Mapeia alertas para ações de diagnóstico e recuperação.
Executa comandos no host via subprocess (dentro do container Docker).
"""

import asyncio
import subprocess


def _run(cmd: str, timeout: int = 30) -> tuple[int, str]:
    """Executa comando shell e retorna (returncode, output)."""
    try:
        result = subprocess.run(  # noqa: S602, S603  # nosec B602
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output[:2000]  # limita tamanho
    except subprocess.TimeoutExpired:
        return -1, f"Timeout apos {timeout}s"
    except Exception as e:
        return -1, str(e)[:500]


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

    async def diagnose_and_act(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        """
        Executa diagnóstico e ações para um alerta.

        Returns:
            (diagnosis_text, actions_list)
        """
        handler_name = self.HANDLERS.get(alert_name)
        if not handler_name:
            diagnosis = f"Alerta '{alert_name}' recebido mas sem handler de remediacao configurado."
            return diagnosis, [{"step": "skip", "detail": "Sem handler mapeado"}]

        handler = getattr(self, handler_name)
        return await asyncio.to_thread(handler, alert_name, severity, annotations)

    # =========================================================================
    # HANDLERS POR TIPO DE ALERTA
    # =========================================================================

    def _handle_postgres(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        # 1. Verificar container
        rc, out = _run("docker inspect --format='{{.State.Status}}' conecta-pro-postgres 2>/dev/null")
        container_status = out.strip().strip("'")
        actions.append({"step": "check_container", "result": container_status})
        diag_parts.append(f"Container PostgreSQL: {container_status}")

        # 2. Verificar conexões
        rc, out = _run("docker exec conecta-pro-postgres pg_isready -U postgres 2>/dev/null")
        pg_ready = rc == 0
        actions.append({"step": "pg_isready", "result": out})
        diag_parts.append(f"pg_isready: {'OK' if pg_ready else 'FALHA'}")

        # 3. Verificar disco do volume
        rc, out = _run("df -h /opt/conecta-pro/data/ 2>/dev/null | tail -1")
        actions.append({"step": "check_disk", "result": out})
        diag_parts.append(f"Disco: {out}")

        # 4. Verificar conexões ativas
        rc, out = _run(
            "docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t "
            "-c 'SELECT count(*) FROM pg_stat_activity' 2>/dev/null"
        )
        actions.append({"step": "active_connections", "result": out.strip()})
        diag_parts.append(f"Conexoes ativas: {out.strip()}")

        # 5. Restart se não está respondendo
        if not pg_ready and container_status != "running":
            rc, out = _run("docker restart conecta-pro-postgres 2>/dev/null", timeout=60)
            actions.append({"step": "restart_container", "result": "executed", "output": out})
            diag_parts.append("Acao: container reiniciado")

            # Aguardar e re-testar
            import time

            time.sleep(10)
            rc, out = _run("docker exec conecta-pro-postgres pg_isready -U postgres 2>/dev/null")
            actions.append({"step": "post_restart_check", "result": "OK" if rc == 0 else "AINDA FALHA"})
            diag_parts.append(f"Pos-restart: {'recuperado' if rc == 0 else 'ainda com problemas'}")

        diagnosis = "DIAGNOSTICO PostgreSQL:\n" + "\n".join(f"  - {p}" for p in diag_parts)
        return diagnosis, actions

    def _handle_erp_api(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        # 1. Verificar container backend
        rc, out = _run("docker inspect --format='{{.State.Status}}' conecta-pro-backend 2>/dev/null")
        container_status = out.strip().strip("'")
        actions.append({"step": "check_container", "result": container_status})
        diag_parts.append(f"Container backend: {container_status}")

        # 2. Health check
        rc, out = _run("curl -sf http://localhost:8080/health 2>/dev/null")
        health_ok = rc == 0
        actions.append({"step": "health_check", "result": out[:500] if health_ok else "FALHA"})
        diag_parts.append(f"Health check: {'OK' if health_ok else 'FALHA'}")

        # 3. Verificar logs recentes
        rc, out = _run(
            "docker logs --tail 20 conecta-pro-backend 2>&1 | grep -i 'error\\|exception\\|traceback' | tail -5"
        )
        actions.append({"step": "check_logs", "result": out[:1000]})
        if out:
            diag_parts.append(f"Erros nos logs: {out[:200]}")

        # 4. Restart se health falhou
        if not health_ok:
            rc, out = _run("docker restart conecta-pro-backend 2>/dev/null", timeout=120)
            actions.append({"step": "restart_container", "result": "executed"})
            diag_parts.append("Acao: container backend reiniciado")

            import time

            time.sleep(30)
            rc, out = _run("curl -sf http://localhost:8080/health 2>/dev/null")
            actions.append({"step": "post_restart_health", "result": "OK" if rc == 0 else "AINDA FALHA"})
            diag_parts.append(f"Pos-restart: {'recuperado' if rc == 0 else 'ainda com problemas'}")

        diagnosis = "DIAGNOSTICO ERP API:\n" + "\n".join(f"  - {p}" for p in diag_parts)
        return diagnosis, actions

    def _handle_redis(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        # 1. Container status
        rc, out = _run("docker inspect --format='{{.State.Status}}' conecta-pro-redis 2>/dev/null")
        container_status = out.strip().strip("'")
        actions.append({"step": "check_container", "result": container_status})
        diag_parts.append(f"Container Redis: {container_status}")

        # 2. Redis ping
        rc, out = _run("docker exec conecta-pro-redis redis-cli ping 2>/dev/null")
        redis_ok = "PONG" in out
        actions.append({"step": "redis_ping", "result": out})
        diag_parts.append(f"Redis PING: {'PONG' if redis_ok else 'FALHA'}")

        # 3. Memoria usada
        rc, out = _run("docker exec conecta-pro-redis redis-cli info memory 2>/dev/null | grep used_memory_human")
        actions.append({"step": "memory_usage", "result": out.strip()})
        diag_parts.append(f"Memoria: {out.strip()}")

        # 4. Restart se não responde
        if not redis_ok:
            rc, out = _run("docker restart conecta-pro-redis 2>/dev/null", timeout=30)
            actions.append({"step": "restart_container", "result": "executed"})
            diag_parts.append("Acao: container Redis reiniciado")

            import time

            time.sleep(5)
            rc, out = _run("docker exec conecta-pro-redis redis-cli ping 2>/dev/null")
            actions.append({"step": "post_restart_ping", "result": out})
            diag_parts.append(f"Pos-restart: {'recuperado' if 'PONG' in out else 'ainda com problemas'}")

        diagnosis = "DIAGNOSTICO Redis:\n" + "\n".join(f"  - {p}" for p in diag_parts)
        return diagnosis, actions

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
            actions.append({"step": f"check_{worker}", "result": status})
            if status != "running":
                down_workers.append(worker)

        diag_parts.append(f"Workers verificados: {len(workers)}")
        diag_parts.append(f"Workers down: {len(down_workers)}")

        # Restart workers que estão down
        for worker in down_workers:
            rc, out = _run(f"docker restart {worker} 2>/dev/null", timeout=60)
            actions.append({"step": f"restart_{worker}", "result": "executed"})
            diag_parts.append(f"Acao: reiniciado {worker}")

        diagnosis = "DIAGNOSTICO Celery Workers:\n" + "\n".join(f"  - {p}" for p in diag_parts)
        return diagnosis, actions

    def _handle_disk(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        diag_parts = []

        # 1. Espaço atual
        rc, out = _run("df -h / | tail -1")
        actions.append({"step": "disk_usage", "result": out})
        diag_parts.append(f"Disco: {out}")

        # 2. Maiores diretórios
        rc, out = _run("du -sh /opt/conecta-pro/logs/ /opt/conecta-pro/uploads/ /opt/conecta-pro/backups/ 2>/dev/null")
        actions.append({"step": "large_dirs", "result": out})
        diag_parts.append(f"Diretorios grandes:\n{out}")

        # 3. Limpar logs antigos (> 7 dias)
        rc, out = _run(
            "find /opt/conecta-pro/logs/ -name '*.log' -mtime +7 -delete 2>/dev/null && echo 'Logs antigos removidos'"
        )
        actions.append({"step": "cleanup_old_logs", "result": out})
        diag_parts.append(f"Limpeza: {out}")

        # 4. Docker prune (imagens não usadas)
        rc, out = _run("docker system prune -f 2>/dev/null | tail -1")
        actions.append({"step": "docker_prune", "result": out})
        diag_parts.append(f"Docker prune: {out}")

        diagnosis = "DIAGNOSTICO Disco:\n" + "\n".join(f"  - {p}" for p in diag_parts)
        return diagnosis, actions

    def _handle_memory(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        rc, out = _run("free -h | head -2")
        actions.append({"step": "memory_info", "result": out})
        rc, out2 = _run("ps aux --sort=-%mem | head -6")
        actions.append({"step": "top_memory_procs", "result": out2})

        diagnosis = f"DIAGNOSTICO Memoria:\n  - {out}\n  - Top processos:\n{out2}"
        return diagnosis, actions

    def _handle_load(self, alert_name: str, severity: str, annotations: dict) -> tuple[str, list[dict]]:
        actions = []
        rc, out = _run("uptime")
        actions.append({"step": "uptime", "result": out})
        rc, out2 = _run("ps aux --sort=-%cpu | head -6")
        actions.append({"step": "top_cpu_procs", "result": out2})

        diagnosis = f"DIAGNOSTICO Load:\n  - {out}\n  - Top processos:\n{out2}"
        return diagnosis, actions

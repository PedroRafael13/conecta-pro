#!/usr/bin/env python3
"""
Context Builder — Gera snapshot completo do sistema para o assistente Telegram.

Coleta métricas de containers, servidor, OpenClaw, Prometheus, logs, knowledge base,
crons e eventos em um único JSON estruturado.

Cron: */2 * * * * (a cada 2 minutos)
Output: /opt/conecta-pro/agents/system_context.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = Path("/opt/conecta-pro")
KB_FILE = PROJECT_DIR / "agent_knowledge_base.json"
OUTPUT = PROJECT_DIR / "agents" / "system_context.json"

BRT_OFFSET = -4


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def get_pg_ip():
    try:
        out = subprocess.run("docker inspect conecta-pro-postgres",
                             shell=True, capture_output=True, text=True, timeout=10).stdout
        data = json.loads(out)
        for info in data[0]["NetworkSettings"]["Networks"].values():
            if info.get("IPAddress"):
                return info["IPAddress"]
    except Exception:
        pass
    return None


def get_db_password():
    env = PROJECT_DIR / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD=") and "STAGING" not in line:
            return line.split("=", 1)[1]
    return ""


def get_redis_password():
    env = PROJECT_DIR / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("REDIS_PASSWORD=") and "STAGING" not in line:
            return line.split("=", 1)[1]
    return ""


def query_db(sql, params=None):
    ip = get_pg_ip()
    pw = get_db_password()
    if not ip or not pw:
        return []
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(host=ip, port="5432", dbname="conecta_pro",
                                user="postgres", password=pw, connect_timeout=5)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for row in rows:
            for k, v in row.items():
                if isinstance(v, datetime):
                    row[k] = v.isoformat()
        return rows
    except Exception as e:
        return [{"error": str(e)[:200]}]


# =============================================================================
# COLLECTORS
# =============================================================================

def collect_containers():
    raw = run("docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}'")
    stats = {}
    for line in raw.splitlines():
        parts = line.split("|")
        if len(parts) >= 4:
            stats[parts[0]] = {"cpu": parts[1], "mem_usage": parts[2], "mem_pct": parts[3]}

    raw2 = run("docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}'")
    containers = []
    for line in raw2.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        name, status, image = parts[0], parts[1], parts[2]
        sl = status.lower()
        health = "unknown"
        if "(healthy)" in sl:
            health = "healthy"
        elif "(unhealthy)" in sl:
            health = "unhealthy"
        elif "up" in sl:
            health = "running"
        elif "created" in sl:
            health = "created"
        elif "exited" in sl:
            health = "stopped"

        st = stats.get(name, {})
        containers.append({
            "name": name,
            "image": image.split(":")[0],
            "status": status,
            "health": health,
            "cpu": st.get("cpu", "0%"),
            "mem_usage": st.get("mem_usage", "0B / 0B"),
            "mem_pct": st.get("mem_pct", "0%"),
        })
    return containers


def collect_server_metrics():
    load = run("cat /proc/loadavg").split()
    mem_raw = run("free -b | awk '/^Mem:/ {print $2, $3, $7}'").split()
    disk_raw = run("df / | tail -1 | awk '{print $2, $3, $5}'").split()
    swap_raw = run("free -b | awk '/^Swap:/ {print $2, $3}'").split()
    mem_total = int(mem_raw[0]) if len(mem_raw) >= 3 else 0
    mem_used = int(mem_raw[1]) if len(mem_raw) >= 3 else 0

    return {
        "load_1m": float(load[0]) if load else 0,
        "load_5m": float(load[1]) if len(load) > 1 else 0,
        "load_15m": float(load[2]) if len(load) > 2 else 0,
        "cpu_cores": int(run("nproc") or "1"),
        "mem_total_gb": round(mem_total / (1024**3), 1),
        "mem_used_gb": round(mem_used / (1024**3), 1),
        "mem_percent": round(mem_used / mem_total * 100, 1) if mem_total else 0,
        "disk_total_gb": round(int(disk_raw[0]) / (1024**2), 0) if disk_raw else 0,
        "disk_used_gb": round(int(disk_raw[1]) / (1024**2), 0) if len(disk_raw) > 1 else 0,
        "disk_percent": int(disk_raw[2].replace("%", "")) if len(disk_raw) > 2 else 0,
        "swap_total_gb": round(int(swap_raw[0]) / (1024**3), 1) if swap_raw and int(swap_raw[0]) > 0 else 0,
        "swap_used_gb": round(int(swap_raw[1]) / (1024**3), 1) if len(swap_raw) > 1 else 0,
        "uptime_days": round(float(run("awk '{print $1/86400}' /proc/uptime").split()[0]), 1) if run("cat /proc/uptime") else 0,
    }


def collect_interventions():
    return query_db(
        "SELECT alert_name, severity, status, diagnosis, resolution, "
        "response_time_seconds, false_positive, false_positive_reason, "
        "created_at, resolved_at "
        "FROM openclaw_interventions ORDER BY created_at DESC LIMIT 10"
    )


def collect_patterns():
    return query_db(
        "SELECT alert_name, description, confidence_score, frequency, "
        "prevention_count, last_prevented_at, preventive_command, conditions "
        "FROM openclaw_patterns WHERE is_active = true ORDER BY confidence_score DESC LIMIT 8"
    )


def collect_prometheus_alerts():
    try:
        import urllib.request
        r = urllib.request.urlopen("http://localhost:9090/api/v1/rules", timeout=5)
        data = json.loads(r.read())
        alerts = []
        for g in data.get("data", {}).get("groups", []):
            for rule in g["rules"]:
                alerts.append({
                    "name": rule.get("name"),
                    "state": rule.get("state"),
                    "active_alerts": len(rule.get("alerts", [])),
                })
        return alerts
    except Exception as e:
        return [{"error": str(e)[:100]}]


def collect_error_logs():
    critical = ["conecta-pro-backend", "conecta-pro-postgres", "conecta-pro-redis"]
    logs = {}
    for c in critical:
        out = run(f"docker logs {c} --tail 5 2>&1 | grep -iE 'error|exception|warning|critical' | tail -3")
        logs[c] = out.splitlines() if out else ["(sem erros recentes)"]
    return logs


def collect_knowledge_base():
    try:
        kb = json.loads(KB_FILE.read_text())
        modules = kb.get("modules", {})
        summary = {}
        for name, mod in modules.items():
            summary[name] = {
                "endpoints": mod.get("endpoints", 0),
                "criticality": mod.get("criticality", "unknown"),
                "lines": mod.get("lines", 0),
                "models": mod.get("models", 0),
                "dependencies": mod.get("internal_dependencies", []),
                "infra": mod.get("infrastructure", []),
            }
        return {
            "total_modules": kb.get("system", {}).get("total_modules", 0),
            "total_endpoints": kb.get("system", {}).get("total_endpoints", 0),
            "modules": summary,
            "peak_hours": kb.get("peak_hours", {}),
            "operational_rules": kb.get("operational_rules", []),
        }
    except Exception:
        return {"error": "knowledge base not found"}


def collect_cron_status():
    backup_dir = PROJECT_DIR / "backups" / "postgresql"
    latest_backup = None
    try:
        files = sorted(backup_dir.glob("backup_*.sql.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
        if files:
            st = files[0].stat()
            latest_backup = {
                "file": files[0].name,
                "size_kb": round(st.st_size / 1024),
                "age_hours": round((datetime.now().timestamp() - st.st_mtime) / 3600, 1),
            }
    except Exception:
        pass

    pattern_log = PROJECT_DIR / "logs" / "pattern_learner.log"
    pattern_last = None
    try:
        if pattern_log.exists():
            lines = pattern_log.read_text().strip().splitlines()
            if lines:
                pattern_last = lines[-1][:80]
    except Exception:
        pass

    preventive_log = PROJECT_DIR / "logs" / "preventive_action.log"
    preventive_last = None
    try:
        if preventive_log.exists():
            lines = preventive_log.read_text().strip().splitlines()
            if lines:
                preventive_last = lines[-1][:80]
    except Exception:
        pass

    return {
        "latest_backup": latest_backup,
        "pattern_learner_last": pattern_last,
        "preventive_action_last": preventive_last,
    }


def collect_recent_events():
    """Combina intervenções, alertas e ações em timeline cronológica."""
    events = []

    # Intervenções das últimas 24h
    rows = query_db(
        "SELECT alert_name, status, false_positive, created_at "
        "FROM openclaw_interventions "
        "WHERE created_at >= NOW() - INTERVAL '24 hours' "
        "ORDER BY created_at DESC"
    )
    for r in rows:
        if isinstance(r, dict) and "error" not in r:
            fp = " (falso positivo)" if r.get("false_positive") else ""
            events.append({
                "time": r.get("created_at", ""),
                "type": "intervention",
                "summary": f"{r['alert_name']}: {r['status']}{fp}",
            })

    # Backup mais recente
    cron = collect_cron_status()
    if cron.get("latest_backup"):
        events.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "type": "backup",
            "summary": f"Último backup: {cron['latest_backup']['file']} ({cron['latest_backup']['size_kb']}KB, {cron['latest_backup']['age_hours']}h atrás)",
        })

    events.sort(key=lambda e: e.get("time", ""), reverse=True)
    return events[:20]


def collect_celery_status():
    redis_pw = get_redis_password()
    queues = ["celery", "operacional", "gov.batch", "integrations", "webhooks"]
    result = {}
    for q in queues:
        out = run(f"docker exec conecta-pro-redis redis-cli -a '{redis_pw}' llen {q} 2>/dev/null")
        try:
            result[q] = int(out)
        except ValueError:
            result[q] = 0
    return result


# =============================================================================
# MAIN
# =============================================================================

def build_context():
    now = datetime.now(timezone.utc)
    brt = now + timedelta(hours=BRT_OFFSET)

    ctx = {
        "generated_at": now.isoformat(),
        "generated_at_brt": brt.strftime("%d/%m/%Y %H:%M AMT"),
        "containers": collect_containers(),
        "server": collect_server_metrics(),
        "interventions": collect_interventions(),
        "patterns": collect_patterns(),
        "prometheus_alerts": collect_prometheus_alerts(),
        "error_logs": collect_error_logs(),
        "knowledge_base": collect_knowledge_base(),
        "cron_status": collect_cron_status(),
        "celery_queues": collect_celery_status(),
        "recent_events": collect_recent_events(),
    }

    OUTPUT.write_text(json.dumps(ctx, indent=2, ensure_ascii=False, default=str))
    return ctx


if __name__ == "__main__":
    ctx = build_context()
    containers = len(ctx["containers"])
    interventions = len(ctx["interventions"])
    modules = len(ctx.get("knowledge_base", {}).get("modules", {}))
    print(f"Context built: {containers} containers, {interventions} interventions, {modules} modules")

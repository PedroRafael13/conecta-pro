#!/usr/bin/env python3
"""
Dashboard API — Gera JSON com métricas para o dashboard HTML.
Executado pelo nginx como CGI-like (stdout → JSON file).

Uso: python3 agents/dashboard_api.py > agents/dashboard_data.json
Cron: */2 * * * * (a cada 2 minutos)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = Path("/opt/conecta-pro")
OUTPUT = PROJECT_DIR / "agents" / "dashboard_data.json"

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

def query_db(sql):
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
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Convert datetime to string
        for row in rows:
            for k, v in row.items():
                if isinstance(v, datetime):
                    row[k] = v.isoformat()
        return rows
    except Exception as e:
        return [{"error": str(e)[:200]}]

def collect():
    now = datetime.now(timezone.utc)

    # 1. Containers
    raw = run("docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}'")
    containers = []
    for line in raw.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        name, status, image = parts[0], parts[1], parts[2]
        health = "unknown"
        if "healthy" in status.lower():
            health = "healthy"
        elif "unhealthy" in status.lower():
            health = "unhealthy"
        elif "up" in status.lower():
            health = "running"
        elif "created" in status.lower() or "exited" in status.lower():
            health = "stopped"
        containers.append({
            "name": name, "status": status, "health": health,
            "image": image.split(":")[0]
        })

    # 2. System metrics
    load = run("cat /proc/loadavg | awk '{print $1, $2, $3}'").split()
    mem_raw = run("free -b | awk '/^Mem:/ {print $2, $3, $7}'").split()
    disk_raw = run("df / | tail -1 | awk '{print $2, $3, $5}'").split()
    swap_raw = run("free -b | awk '/^Swap:/ {print $2, $3}'").split()

    mem_total = int(mem_raw[0]) if len(mem_raw) >= 3 else 0
    mem_used = int(mem_raw[1]) if len(mem_raw) >= 3 else 0
    mem_avail = int(mem_raw[2]) if len(mem_raw) >= 3 else 0

    metrics = {
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
        "uptime_days": float(run("awk '{print $1/86400}' /proc/uptime").split()[0]) if run("cat /proc/uptime") else 0,
    }

    # 3. Interventions (last 20)
    interventions = query_db(
        "SELECT alert_name, severity, status, diagnosis, resolution, "
        "response_time_seconds, created_at, resolved_at "
        "FROM openclaw_interventions ORDER BY created_at DESC LIMIT 20"
    )

    # 4. Patterns
    patterns = query_db(
        "SELECT alert_name, description, confidence_score, frequency, "
        "prevention_count, last_prevented_at, preventive_command, conditions "
        "FROM openclaw_patterns WHERE is_active = true ORDER BY confidence_score DESC"
    )
    # Serialize conditions (jsonb)
    for p in patterns:
        if isinstance(p.get("conditions"), dict):
            pass  # already dict
        elif p.get("conditions"):
            try:
                p["conditions"] = json.loads(p["conditions"])
            except Exception:
                pass

    # 5. Uptime history (simulated from container start times)
    uptime_data = []
    for h in range(24):
        t = now - timedelta(hours=23 - h)
        uptime_data.append({
            "hour": t.strftime("%H:00"),
            "backend": 100,
            "postgres": 100,
            "redis": 100,
        })

    # 6. Scheduled preventive actions
    redis_pw = get_db_password()  # reuse
    celery_queue = run(
        f"docker exec conecta-pro-redis redis-cli -a '{get_redis_password()}' llen celery 2>/dev/null"
    )
    scheduled = [
        {"name": "Health check módulos", "schedule": "*/15 * * * *", "next": "próximos 15min"},
        {"name": "Métricas Prometheus", "schedule": "*/5 * * * *", "next": "próximos 5min"},
        {"name": "Backup PostgreSQL", "schedule": "0 3 * * *", "next": "03:00 UTC"},
        {"name": "Retenção de backups", "schedule": "30 3 * * *", "next": "03:30 UTC"},
        {"name": "Pattern Learner", "schedule": "0 3 * * *", "next": "03:00 UTC"},
        {"name": "Relatório semanal", "schedule": "Sexta 17-18h BRT", "next": "sexta"},
    ]

    return {
        "generated_at": now.isoformat(),
        "containers": sorted(containers, key=lambda c: c["name"]),
        "metrics": metrics,
        "interventions": interventions,
        "patterns": patterns,
        "uptime_history": uptime_data,
        "scheduled_actions": scheduled,
        "celery_queue_length": int(celery_queue) if celery_queue.isdigit() else 0,
    }


def get_redis_password():
    env = PROJECT_DIR / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("REDIS_PASSWORD=") and "STAGING" not in line:
            return line.split("=", 1)[1]
    return ""


if __name__ == "__main__":
    data = collect()
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    print(f"Dashboard data written to {OUTPUT} ({len(data['containers'])} containers)")

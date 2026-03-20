#!/usr/bin/env python3
"""
OpenClaw Preventive Action — Age antes dos problemas acontecerem.

Lê openclaw_patterns com confidence > 70%, verifica condições de gatilho,
e executa ações preventivas quando detecta condições pré-falha.

Agendado: a cada 15 minutos via cron.
"""

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("POSTGRES_HOST", "conecta-pro-postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "conecta_pro")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")

CONFIDENCE_THRESHOLD = 70.0

if not DB_PASS:
    env_file = "/opt/conecta-pro/.env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("POSTGRES_PASSWORD=") and "STAGING" not in line:
                    DB_PASS = line.strip().split("=", 1)[1]
                    break


def get_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] preventive_action: {msg}", flush=True)


def run_cmd(cmd: str, timeout: int = 30) -> tuple[int, str]:
    """Executa comando e retorna (returncode, output)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, (result.stdout + result.stderr).strip()[:2000]
    except subprocess.TimeoutExpired:
        return -1, f"Timeout apos {timeout}s"
    except Exception as e:
        return -1, str(e)[:500]


# =============================================================================
# COLETORES DE MÉTRICAS
# =============================================================================


def get_disk_usage_percent() -> float | None:
    """Retorna % de uso do disco /."""
    rc, out = run_cmd("df / | tail -1 | awk '{print $5}' | tr -d '%'")
    if rc == 0 and out.strip().isdigit():
        return float(out.strip())
    return None


def get_memory_usage_percent() -> float | None:
    """Retorna % de uso da memória."""
    rc, out = run_cmd("free | awk '/^Mem:/ {printf \"%.1f\", $3/$2*100}'")
    if rc == 0:
        try:
            return float(out.strip())
        except ValueError:
            pass
    return None


def get_pg_active_connections() -> int | None:
    """Retorna número de conexões ativas no PostgreSQL."""
    rc, out = run_cmd(
        "docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t "
        "-c 'SELECT count(*) FROM pg_stat_activity' 2>/dev/null"
    )
    if rc == 0:
        try:
            return int(out.strip())
        except ValueError:
            pass
    return None


def get_redis_memory_mb() -> float | None:
    """Retorna memória usada pelo Redis em MB."""
    rc, out = run_cmd(
        "docker exec conecta-pro-redis redis-cli info memory 2>/dev/null "
        "| grep 'used_memory:' | cut -d: -f2 | tr -d '\\r'"
    )
    if rc == 0:
        try:
            return float(out.strip()) / (1024 * 1024)
        except ValueError:
            pass
    return None


METRIC_COLLECTORS = {
    "disk_usage_percent": get_disk_usage_percent,
    "memory_usage_percent": get_memory_usage_percent,
    "pg_active_connections": get_pg_active_connections,
    "redis_memory_mb": get_redis_memory_mb,
}


# =============================================================================
# AVALIAÇÃO E EXECUÇÃO
# =============================================================================


def evaluate_condition(conditions: dict, current_value: float | int | None) -> bool:
    """Avalia se a condição de gatilho é verdadeira."""
    if current_value is None:
        return False

    threshold = conditions.get("threshold")
    operator = conditions.get("operator", ">")

    if threshold is None:
        return False

    if operator == ">":
        return current_value > threshold
    elif operator == ">=":
        return current_value >= threshold
    elif operator == "<":
        return current_value < threshold
    elif operator == "<=":
        return current_value <= threshold
    elif operator == "==":
        return current_value == threshold
    return False


def execute_prevention(pattern: dict, current_value: float | int) -> dict:
    """Executa ação preventiva e retorna resultado."""
    cmd = pattern.get("preventive_command")
    if not cmd:
        return {"executed": False, "reason": "Sem comando preventivo configurado"}

    log(f"  Executando acao preventiva: {cmd[:100]}...")
    rc, output = run_cmd(cmd, timeout=60)

    return {
        "executed": True,
        "return_code": rc,
        "output": output[:500],
        "trigger_value": current_value,
        "threshold": pattern["conditions"].get("threshold"),
    }


def record_prevention(conn, pattern: dict, result: dict, current_value: float | int):
    """Registra intervenção preventiva na memória episódica."""
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    # Registrar na tabela de intervenções
    cursor.execute(
        """INSERT INTO openclaw_interventions
        (id, alert_name, alert_fingerprint, severity, status,
         diagnosis, actions_taken, resolution, resolved_at,
         response_time_seconds, raw_payload, telegram_sent, is_active,
         created_at, updated_at)
        VALUES (%s, %s, %s, 'info', 'resolved', %s, %s, %s, %s, 0, %s, false, true, %s, %s)""",
        (
            str(uuid.uuid4()),
            f"PREVENTIVE_{pattern['alert_name']}",
            f"preventive-{pattern['id']}",
            f"Acao preventiva: {pattern['description']}. Valor atual: {current_value}",
            json.dumps([{"step": "preventive_action", "result": result}]),
            "Prevenido automaticamente pelo OpenClaw" if result.get("return_code") == 0 else None,
            now if result.get("return_code") == 0 else None,
            json.dumps({"pattern_id": str(pattern["id"]), "trigger_value": current_value}),
            now, now,
        ),
    )

    # Atualizar contagem no padrão
    cursor.execute(
        """UPDATE openclaw_patterns SET
            prevention_count = prevention_count + 1,
            last_prevented_at = %s,
            updated_at = %s
        WHERE id = %s""",
        (now, now, pattern["id"]),
    )

    conn.commit()
    cursor.close()


# =============================================================================
# MAIN
# =============================================================================


def main():
    log("Verificando condicoes preventivas...")

    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Buscar padrões preventivos com confidence acima do threshold
    cursor.execute(
        """SELECT * FROM openclaw_patterns
        WHERE is_active = true
          AND confidence_score >= %s
          AND preventive_command IS NOT NULL
        ORDER BY confidence_score DESC""",
        (CONFIDENCE_THRESHOLD,),
    )
    patterns = cursor.fetchall()
    cursor.close()

    log(f"Encontrados {len(patterns)} padroes preventivos ativos (confidence >= {CONFIDENCE_THRESHOLD}%)")

    if not patterns:
        log("Nenhum padrao preventivo configurado. Execute pattern_learner.py primeiro.")
        conn.close()
        return

    actions_taken = 0

    for pattern in patterns:
        conditions = pattern["conditions"]
        metric_name = conditions.get("metric")

        if not metric_name:
            continue

        # Coletar métrica
        collector = METRIC_COLLECTORS.get(metric_name)
        if not collector:
            log(f"  Metrica '{metric_name}' sem coletor configurado")
            continue

        current_value = collector()
        if current_value is None:
            log(f"  Metrica '{metric_name}' indisponivel")
            continue

        threshold = conditions.get("threshold", "?")
        operator = conditions.get("operator", ">")

        # Avaliar condição
        triggered = evaluate_condition(conditions, current_value)

        if triggered:
            log(f"  GATILHO: {pattern['alert_name']} — "
                f"{metric_name}={current_value} {operator} {threshold}")

            result = execute_prevention(pattern, current_value)
            record_prevention(conn, pattern, result, current_value)

            if result.get("return_code") == 0:
                log(f"  PREVENIDO: {pattern['alert_name']} — acao executada com sucesso")
            else:
                log(f"  FALHA: {pattern['alert_name']} — rc={result.get('return_code')}")

            actions_taken += 1
        else:
            log(f"  OK: {pattern['alert_name']} — "
                f"{metric_name}={current_value} (threshold: {operator}{threshold})")

    conn.close()
    log(f"Concluido. Acoes preventivas executadas: {actions_taken}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERRO: {e}")
        sys.exit(1)

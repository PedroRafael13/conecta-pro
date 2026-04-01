#!/usr/bin/env python3
"""
OpenClaw Pattern Learner — Aprende padrões a partir da memória episódica.

Lê openclaw_interventions, identifica padrões recorrentes, correlações
temporais e sequências de eventos, e atualiza openclaw_patterns.

Agendado: diariamente às 03:00 UTC via cron.
"""

import json
import os
import sys
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("POSTGRES_HOST", "conecta-pro-postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "conecta_pro")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")

# Ler password do .env se não estiver no ambiente
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
    print(f"[{ts}] pattern_learner: {msg}", flush=True)


# =============================================================================
# ANÁLISE DE PADRÕES
# =============================================================================


def analyze_recurrence(interventions: list[dict]) -> list[dict]:
    """Identifica alertas recorrentes e calcula frequência."""
    patterns = []
    counter = Counter(i["alert_name"] for i in interventions)

    for alert_name, count in counter.items():
        if count < 2:
            continue

        # Filtrar intervenções deste alerta
        alert_interventions = [i for i in interventions if i["alert_name"] == alert_name]
        resolved = [i for i in alert_interventions if i["status"] == "resolved"]
        failed = [i for i in alert_interventions if i["status"] in ("failed", "escalated")]

        resolution_rate = len(resolved) / len(alert_interventions) if alert_interventions else 0

        # Tempo médio de resposta
        response_times = [i["response_time_seconds"] for i in alert_interventions if i["response_time_seconds"]]
        avg_response = sum(response_times) / len(response_times) if response_times else 0

        # Confidence baseada em frequência e taxa de resolução
        confidence = min(95.0, (count / 3) * 30 + resolution_rate * 50 + (20 if avg_response < 10 else 0))

        patterns.append({
            "pattern_type": "recurrence",
            "alert_name": alert_name,
            "description": (
                f"Alerta '{alert_name}' ocorreu {count}x nos ultimos 30 dias. "
                f"Taxa resolucao: {resolution_rate:.0%}. "
                f"Tempo medio resposta: {avg_response:.1f}s."
            ),
            "conditions": {
                "total_occurrences": count,
                "resolution_rate": round(resolution_rate, 3),
                "avg_response_seconds": round(avg_response, 1),
                "failed_count": len(failed),
            },
            "recommended_action": _recommend_action_for_recurrence(alert_name, count, resolution_rate),
            "confidence_score": round(confidence, 1),
            "occurrences": count,
        })

    return patterns


def analyze_temporal_correlation(interventions: list[dict]) -> list[dict]:
    """Identifica correlações temporais entre alertas diferentes."""
    patterns = []

    # Agrupar por janela de 10 minutos
    windows: dict[str, list[str]] = defaultdict(list)
    for i in interventions:
        if i["created_at"]:
            # Arredondar para janela de 10 min
            ts = i["created_at"]
            window_key = ts.strftime("%Y-%m-%d %H:") + str(ts.minute // 10 * 10).zfill(2)
            windows[window_key].append(i["alert_name"])

    # Encontrar co-ocorrências
    pair_counter: Counter = Counter()
    for window_key, alerts in windows.items():
        unique_alerts = set(alerts)
        if len(unique_alerts) >= 2:
            for a1 in unique_alerts:
                for a2 in unique_alerts:
                    if a1 < a2:  # evitar duplicatas
                        pair_counter[(a1, a2)] += 1

    for (a1, a2), count in pair_counter.items():
        if count < 2:
            continue

        confidence = min(90.0, count * 25)
        patterns.append({
            "pattern_type": "temporal_correlation",
            "alert_name": f"{a1}+{a2}",
            "description": (
                f"Alertas '{a1}' e '{a2}' co-ocorreram {count}x "
                f"dentro de janelas de 10 minutos. Possivel causa raiz comum."
            ),
            "conditions": {
                "alert_a": a1,
                "alert_b": a2,
                "co_occurrences": count,
                "window_minutes": 10,
            },
            "recommended_action": (
                f"Quando '{a1}' disparar, verificar proativamente '{a2}' "
                f"e vice-versa. Investigar causa raiz compartilhada."
            ),
            "confidence_score": round(confidence, 1),
            "occurrences": count,
        })

    return patterns


def analyze_time_of_day(interventions: list[dict]) -> list[dict]:
    """Identifica horários com mais incidentes."""
    patterns = []
    hour_counter: dict[str, Counter] = defaultdict(Counter)

    for i in interventions:
        if i["created_at"]:
            hour = i["created_at"].hour
            hour_counter[i["alert_name"]][hour] += 1

    for alert_name, hours in hour_counter.items():
        total = sum(hours.values())
        if total < 3:
            continue

        # Encontrar pico
        peak_hour, peak_count = hours.most_common(1)[0]
        peak_ratio = peak_count / total

        if peak_ratio < 0.4:  # Pelo menos 40% concentrado em 1 hora
            continue

        confidence = min(85.0, peak_ratio * 80 + total * 3)
        patterns.append({
            "pattern_type": "time_of_day",
            "alert_name": alert_name,
            "description": (
                f"Alerta '{alert_name}' concentra {peak_ratio:.0%} das ocorrencias "
                f"por volta das {peak_hour:02d}:00 UTC. Total: {total} incidentes."
            ),
            "conditions": {
                "peak_hour_utc": peak_hour,
                "peak_ratio": round(peak_ratio, 3),
                "total_incidents": total,
            },
            "recommended_action": (
                f"Agendar verificacao preventiva de '{alert_name}' "
                f"para {(peak_hour - 1) % 24:02d}:30 UTC (30min antes do pico)."
            ),
            "confidence_score": round(confidence, 1),
            "occurrences": total,
        })

    return patterns


def analyze_escalation_sequences(interventions: list[dict]) -> list[dict]:
    """Identifica alertas que frequentemente escalam (resolução automática falha)."""
    patterns = []

    by_alert = defaultdict(list)
    for i in interventions:
        by_alert[i["alert_name"]].append(i)

    for alert_name, items in by_alert.items():
        if len(items) < 2:
            continue

        escalated = [i for i in items if i["status"] in ("failed", "escalated")]
        if not escalated:
            continue

        escalation_rate = len(escalated) / len(items)
        if escalation_rate < 0.3:
            continue

        confidence = min(90.0, escalation_rate * 60 + len(items) * 5)
        patterns.append({
            "pattern_type": "escalation_prone",
            "alert_name": alert_name,
            "description": (
                f"Alerta '{alert_name}' escala/falha em {escalation_rate:.0%} dos casos "
                f"({len(escalated)}/{len(items)}). Remediacao automatica insuficiente."
            ),
            "conditions": {
                "escalation_rate": round(escalation_rate, 3),
                "total": len(items),
                "escalated": len(escalated),
            },
            "recommended_action": (
                f"Revisar handler de remediacao para '{alert_name}'. "
                f"Considerar acao preventiva ou notificacao imediata ao admin."
            ),
            "confidence_score": round(confidence, 1),
            "occurrences": len(items),
        })

    return patterns


def _recommend_action_for_recurrence(alert_name: str, count: int, resolution_rate: float) -> str:
    """Gera recomendação baseada no tipo de alerta recorrente."""
    recommendations = {
        "DiskSpaceLow": "Aumentar limpeza preventiva de logs/backups antigos. Considerar aumento de disco.",
        "DiskSpaceCritical": "URGENTE: aumento de disco necessario. Limpar dados temporarios imediatamente.",
        "HighMemoryUsage": "Verificar memory leaks nos containers. Considerar aumento de RAM ou otimizacao.",
        "HighLoadAverage": "Verificar processos com uso excessivo de CPU. Considerar escalar horizontalmente.",
        "PostgresDown": "Verificar estabilidade do container PostgreSQL. Monitorar conexoes e WAL.",
        "RedisDown": "Verificar se Redis esta com maxmemory configurado. Monitorar evictions.",
        "ERPAPIDown": "Verificar logs do backend por OOM kills ou crashes. Monitorar response times.",
        "CeleryDown": "Verificar filas acumuladas. Workers podem estar crashando por memory ou timeout.",
    }
    base = recommendations.get(alert_name, f"Investigar causa raiz de '{alert_name}' recorrente.")

    if resolution_rate < 0.5:
        base += " ATENCAO: taxa de resolucao automatica baixa — revisar handler."

    return base


# =============================================================================
# PERSISTÊNCIA
# =============================================================================


def upsert_patterns(conn, patterns: list[dict]):
    """Insere ou atualiza padrões no banco."""
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    for p in patterns:
        # Verificar se padrão já existe (mesmo type + alert_name)
        cursor.execute(
            "SELECT id, occurrences, confidence_score FROM openclaw_patterns "
            "WHERE pattern_type = %s AND alert_name = %s AND is_active = true",
            (p["pattern_type"], p["alert_name"]),
        )
        existing = cursor.fetchone()

        if existing:
            # Atualizar
            cursor.execute(
                """UPDATE openclaw_patterns SET
                    description = %s,
                    conditions = %s,
                    recommended_action = %s,
                    confidence_score = %s,
                    occurrences = %s,
                    last_seen_at = %s,
                    updated_at = %s
                WHERE id = %s""",
                (
                    p["description"],
                    json.dumps(p["conditions"]),
                    p["recommended_action"],
                    p["confidence_score"],
                    p["occurrences"],
                    now,
                    now,
                    existing[0],
                ),
            )
            log(f"  Atualizado: {p['pattern_type']}/{p['alert_name']} "
                f"(confidence: {p['confidence_score']}%)")
        else:
            # Inserir
            cursor.execute(
                """INSERT INTO openclaw_patterns
                (id, pattern_type, alert_name, description, conditions,
                 recommended_action, confidence_score, occurrences,
                 last_seen_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(uuid.uuid4()),
                    p["pattern_type"],
                    p["alert_name"],
                    p["description"],
                    json.dumps(p["conditions"]),
                    p.get("recommended_action"),
                    p["confidence_score"],
                    p["occurrences"],
                    now, now, now,
                ),
            )
            log(f"  Novo padrão: {p['pattern_type']}/{p['alert_name']} "
                f"(confidence: {p['confidence_score']}%)")

    conn.commit()
    cursor.close()


def seed_preventive_patterns(conn):
    """Insere padrões preventivos baseados em conhecimento prévio do sistema."""
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM openclaw_patterns WHERE pattern_type = 'preventive'")
    count = cursor.fetchone()[0]

    if count > 0:
        cursor.close()
        return  # Já tem padrões preventivos

    now = datetime.now(timezone.utc)
    seeds = [
        {
            "alert_name": "DiskSpaceLow",
            "description": "Disco acima de 75%: limpar logs e backups antigos preventivamente.",
            "conditions": {"metric": "disk_usage_percent", "threshold": 75, "operator": ">"},
            "recommended_action": "Limpar logs > 7 dias e rodar docker system prune",
            "preventive_command": (
                "find /opt/conecta-pro/logs -name '*.log' -mtime +7 -delete 2>/dev/null; "
                "docker system prune -f 2>/dev/null"
            ),
            "confidence_score": 90.0,
        },
        {
            "alert_name": "HighMemoryUsage",
            "description": "Memoria acima de 85%: limpar caches e verificar processos.",
            "conditions": {"metric": "memory_usage_percent", "threshold": 85, "operator": ">"},
            "recommended_action": "Limpar cache Redis e verificar containers com alto uso de RAM",
            "preventive_command": (
                "docker exec conecta-pro-redis redis-cli FLUSHDB 2>/dev/null; "
                "sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null"
            ),
            "confidence_score": 80.0,
        },
        {
            "alert_name": "PostgresConnectionLost",
            "description": "Conexoes PostgreSQL acima de 80: fechar conexoes idle.",
            "conditions": {"metric": "pg_active_connections", "threshold": 80, "operator": ">"},
            "recommended_action": "Terminar conexoes idle ha mais de 10 minutos",
            "preventive_command": (
                "docker exec conecta-pro-postgres psql -U postgres -d conecta_pro "
                "-c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE state = 'idle' AND state_change < now() - interval '10 minutes' "
                "AND pid <> pg_backend_pid()\" 2>/dev/null"
            ),
            "confidence_score": 85.0,
        },
    ]

    for s in seeds:
        cursor.execute(
            """INSERT INTO openclaw_patterns
            (id, pattern_type, alert_name, description, conditions,
             recommended_action, preventive_command, confidence_score,
             occurrences, created_at, updated_at)
            VALUES (%s, 'preventive', %s, %s, %s, %s, %s, %s, 0, %s, %s)""",
            (
                str(uuid.uuid4()), s["alert_name"], s["description"],
                json.dumps(s["conditions"]), s["recommended_action"],
                s["preventive_command"], s["confidence_score"], now, now,
            ),
        )
        log(f"  Seed preventivo: {s['alert_name']} (confidence: {s['confidence_score']}%)")

    conn.commit()
    cursor.close()


# =============================================================================
# MAIN
# =============================================================================


def main():
    log("Iniciando analise de padroes...")

    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Buscar intervenções dos últimos 30 dias
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    cursor.execute(
        "SELECT * FROM openclaw_interventions WHERE created_at >= %s ORDER BY created_at",
        (cutoff,),
    )
    interventions = cursor.fetchall()
    cursor.close()

    log(f"Encontradas {len(interventions)} intervencoes nos ultimos 30 dias")

    if not interventions:
        log("Sem dados para analise. Inserindo padroes preventivos seed...")
        seed_preventive_patterns(conn)
        conn.close()
        log("Concluido.")
        return

    # Executar análises
    all_patterns = []

    patterns = analyze_recurrence(interventions)
    log(f"Recorrencia: {len(patterns)} padroes")
    all_patterns.extend(patterns)

    patterns = analyze_temporal_correlation(interventions)
    log(f"Correlacao temporal: {len(patterns)} padroes")
    all_patterns.extend(patterns)

    patterns = analyze_time_of_day(interventions)
    log(f"Horario do dia: {len(patterns)} padroes")
    all_patterns.extend(patterns)

    patterns = analyze_escalation_sequences(interventions)
    log(f"Propensos a escalacao: {len(patterns)} padroes")
    all_patterns.extend(patterns)

    # Persistir
    if all_patterns:
        log(f"Persistindo {len(all_patterns)} padroes...")
        upsert_patterns(conn, all_patterns)
    else:
        log("Nenhum padrao significativo encontrado (dados insuficientes)")

    # Garantir que padrões preventivos seed existam
    seed_preventive_patterns(conn)

    conn.close()
    log(f"Concluido. Total padroes processados: {len(all_patterns)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERRO: {e}")
        sys.exit(1)

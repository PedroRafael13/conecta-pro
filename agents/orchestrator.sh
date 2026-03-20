#!/bin/bash
# ============================================================================
# Orchestrator — Conecta PRO Multi-Agent System
#
# Lê AGENT_STATE.json, coleta métricas, atualiza HEALTH_REPORT.md,
# processa MESSAGE_QUEUE.json e coordena agentes.
#
# Uso:
#   ./agents/orchestrator.sh              # Execução única (cron)
#   ./agents/orchestrator.sh --health     # Apenas health report
#   ./agents/orchestrator.sh --daily      # Gera daily report
#   ./agents/orchestrator.sh --status     # Mostra status no terminal
# ============================================================================

set -uo pipefail

PROJECT_DIR="/opt/conecta-pro"
STATE_FILE="$PROJECT_DIR/AGENT_STATE.json"
QUEUE_FILE="$PROJECT_DIR/MESSAGE_QUEUE.json"
HEALTH_FILE="$PROJECT_DIR/HEALTH_REPORT.md"
DAILY_FILE="$PROJECT_DIR/DAILY_REPORT.md"
KB_FILE="$PROJECT_DIR/agent_knowledge_base.json"
LOG_FILE="/var/log/conecta-pro/orchestrator.log"

NOW=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
NOW_BR=$(TZ='America/Manaus' date '+%Y-%m-%d %H:%M AMT')

mkdir -p /var/log/conecta-pro

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

# ============================================================================
# COLETA DE MÉTRICAS
# ============================================================================

collect_metrics() {
    # Backend health
    BACKEND_STATUS="down"
    BACKEND_DETAIL="não respondendo"
    if response=$(curl -sf --max-time 5 http://localhost:8080/health 2>/dev/null); then
        BACKEND_STATUS="up"
        BACKEND_DETAIL=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','ok'))" 2>/dev/null || echo "ok")
    fi

    # Frontend PM2
    PM2_STATUS="down"
    PM2_DETAIL="não respondendo"
    if pm2_json=$(pm2 jlist 2>/dev/null); then
        PM2_STATUS=$(echo "$pm2_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['pm2_env']['status'] if d else 'stopped')" 2>/dev/null || echo "unknown")
        PM2_RESTARTS=$(echo "$pm2_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['pm2_env']['restart_time'] if d else 0)" 2>/dev/null || echo "?")
        PM2_DETAIL="restarts: $PM2_RESTARTS"
    fi

    # PostgreSQL
    PG_STATUS="down"
    PG_DETAIL="não acessível"
    if docker exec conecta-pro-postgres pg_isready -U postgres -q 2>/dev/null; then
        PG_STATUS="up"
        PG_DETAIL="accepting connections"
    fi

    # Redis
    REDIS_STATUS="down"
    REDIS_DETAIL="não acessível"
    REDIS_PW=$(grep "^REDIS_PASSWORD=" "$PROJECT_DIR/.env" 2>/dev/null | head -1 | cut -d= -f2)
    if docker exec conecta-pro-redis redis-cli -a "$REDIS_PW" ping 2>/dev/null | grep -q PONG; then
        REDIS_STATUS="up"
        REDIS_DETAIL="PONG"
    fi

    # Celery workers
    CELERY_HEALTHY=0
    CELERY_TOTAL=0
    for w in batch beat integrations nfse operacional priority sefaz; do
        CELERY_TOTAL=$((CELERY_TOTAL + 1))
        status=$(docker inspect --format='{{.State.Health.Status}}' "conecta-pro-celery-$w" 2>/dev/null || echo "not_found")
        [ "$status" = "healthy" ] && CELERY_HEALTHY=$((CELERY_HEALTHY + 1))
    done
    CELERY_STATUS="up"
    CELERY_DETAIL="$CELERY_HEALTHY/$CELERY_TOTAL healthy"
    [ "$CELERY_HEALTHY" -lt "$CELERY_TOTAL" ] && CELERY_STATUS="degraded"

    # Nginx
    NGINX_STATUS="down"
    NGINX_DETAIL="não ativo"
    if systemctl is-active nginx >/dev/null 2>&1; then
        NGINX_STATUS="up"
        NGINX_DETAIL="active"
    fi

    # Recursos
    CPU_LOAD=$(cat /proc/loadavg | awk '{print $2}')
    RAM_PERCENT=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
    DISK_PERCENT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    SWAP_USED=$(free | awk '/Swap:/ {if($2>0) printf "%.0f", $3/$2*100; else print "0"}')

    # Status geral
    OVERALL="HEALTHY"
    [ "$BACKEND_STATUS" != "up" ] && OVERALL="DEGRADED"
    [ "$PG_STATUS" != "down" ] || OVERALL="CRITICAL"
    [ "$REDIS_STATUS" != "down" ] || OVERALL="CRITICAL"
    [ "$DISK_PERCENT" -gt 80 ] && OVERALL="WARNING"
    [ "$RAM_PERCENT" -gt 90 ] && OVERALL="WARNING"
}

# ============================================================================
# KNOWLEDGE-BASED PRIORITIZATION
# ============================================================================

assess_priority() {
    # Lê knowledge base e retorna prioridade de ação baseada em componentes afetados
    # Saída: PRIORITY_ACTIONS (variável global com ações priorizadas)
    PRIORITY_ACTIONS=$(python3 -c "
import json, sys
from datetime import datetime

kb_path = '$KB_FILE'
try:
    with open(kb_path) as f:
        kb = json.load(f)
except FileNotFoundError:
    print('KB não encontrada — executar: python3 agents/knowledge_builder.py')
    sys.exit(0)

actions = []

# Mapear criticidade dos componentes
crit_map = {}
for level in kb.get('criticality_order', []):
    for comp in level['components']:
        crit_map[comp] = level['level']
    for mod in level['modules']:
        crit_map[mod] = level['level']

# Verificar regras operacionais
now_hour_brt = (datetime.utcnow().hour - 4) % 24
is_peak = 7 <= now_hour_brt <= 9 or 17 <= now_hour_brt <= 19

# Coletar problemas atuais
problems = []

# Backend
if '$BACKEND_STATUS' != 'up':
    problems.append({'component': 'backend', 'criticality': 'critical', 'issue': 'Backend API down'})

# PostgreSQL
if '$PG_STATUS' != 'up':
    problems.append({'component': 'postgres', 'criticality': 'critical', 'issue': 'PostgreSQL down'})

# Redis
if '$REDIS_STATUS' != 'up':
    problems.append({'component': 'redis', 'criticality': 'critical', 'issue': 'Redis down'})

# Celery degraded
if '$CELERY_STATUS' == 'degraded':
    problems.append({'component': 'celery_workers', 'criticality': 'high', 'issue': 'Celery workers degraded: $CELERY_DETAIL'})

# Disco
disk = int('$DISK_PERCENT')
if disk > 80:
    problems.append({'component': 'disk', 'criticality': 'high' if disk < 90 else 'critical', 'issue': f'Disco em {disk}%'})

# RAM
ram = int('$RAM_PERCENT')
if ram > 90:
    problems.append({'component': 'memory', 'criticality': 'high', 'issue': f'RAM em {ram}%'})

# Ordenar por criticidade
order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
problems.sort(key=lambda p: order.get(p['criticality'], 99))

if not problems:
    if is_peak:
        print('PEAK_HOUR: horário de pico BRT — evitar deploys e operações pesadas')
    else:
        print('ALL_CLEAR: nenhum problema detectado')
else:
    for p in problems:
        flag = '🔴' if p['criticality'] == 'critical' else '🟡' if p['criticality'] == 'high' else '🔵'
        print(f'{flag} [{p[\"criticality\"].upper()}] {p[\"issue\"]}')
    if is_peak:
        print('⚠️  PEAK_HOUR: ações corretivas devem ser conservadoras')
" 2>/dev/null || echo "KB assessment falhou")
}

# ============================================================================
# HEALTH REPORT
# ============================================================================

generate_health_report() {
    collect_metrics
    assess_priority

    cat > "$HEALTH_FILE" << REPORT
# Health Report — Conecta PRO

> **Gerado automaticamente pelo orchestrator**
> **Última atualização:** $NOW_BR

---

## Status Geral: $OVERALL

| Componente | Status | Detalhe |
|---|---|---|
| Backend API | $BACKEND_STATUS | $BACKEND_DETAIL |
| Frontend PM2 | $PM2_STATUS | $PM2_DETAIL |
| PostgreSQL | $PG_STATUS | $PG_DETAIL |
| Redis | $REDIS_STATUS | $REDIS_DETAIL |
| Celery Workers | $CELERY_STATUS | $CELERY_DETAIL |
| Nginx | $NGINX_STATUS | $NGINX_DETAIL |

## Recursos

| Recurso | Valor | Threshold |
|---|---|---|
| CPU Load (5min) | $CPU_LOAD | < 8.0 |
| RAM usada | ${RAM_PERCENT}% | < 90% |
| Disco usado | ${DISK_PERCENT}% | < 80% |
| Swap usado | ${SWAP_USED}% | < 50% |

## Priorização (Knowledge Base)

$PRIORITY_ACTIONS

## Alertas Ativos

$(curl -sf http://localhost:9090/api/v1/alerts 2>/dev/null | python3 -c "
import sys,json
data=json.load(sys.stdin)
alerts=data.get('data',{}).get('alerts',[])
if not alerts:
    print('Nenhum.')
else:
    for a in alerts:
        print(f'- **{a[\"labels\"][\"alertname\"]}** [{a[\"labels\"].get(\"severity\",\"?\")}]: {a[\"annotations\"].get(\"summary\",\"\")}')
" 2>/dev/null || echo "Prometheus indisponível.")

## Agentes Ativos

$(python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
agents = state.get('active_agents', [])
if not agents:
    print('Nenhum.')
else:
    for a in agents:
        print(f'- **{a[\"id\"]}** ({a[\"type\"]}): {a[\"task\"]} — desde {a.get(\"started_at\",\"?\")}')
" 2>/dev/null || echo "Erro ao ler AGENT_STATE.json")
REPORT

    log "Health report gerado: $OVERALL"
}

# ============================================================================
# DAILY REPORT
# ============================================================================

generate_daily_report() {
    collect_metrics

    # Contar backups das últimas 24h
    BACKUP_COUNT=$(find "$PROJECT_DIR/backups/postgresql" -name "backup_*.sql.gz" -mtime -1 2>/dev/null | wc -l)

    # Testes (último resultado conhecido)
    TESTS_PASSED=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    print(json.load(f).get('last_build',{}).get('backend',{}).get('tests_passed',0))
" 2>/dev/null || echo "?")
    TESTS_FAILED=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    print(json.load(f).get('last_build',{}).get('backend',{}).get('tests_failed',0))
" 2>/dev/null || echo "?")

    # Issues do dia
    FIXED_TODAY=$(python3 -c "
import json
from datetime import datetime, timedelta
with open('$STATE_FILE') as f:
    state = json.load(f)
cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
fixed = [i for i in state.get('fixed_issues', []) if i.get('fixed_at', '') > cutoff]
if not fixed:
    print('Nenhum problema resolvido nas últimas 24h.')
else:
    for i in fixed:
        print(f'| {i.get(\"severity\",\"?\")} | {i.get(\"description\",\"?\")} | {i.get(\"resolution\",\"?\")} |')
" 2>/dev/null || echo "Erro ao ler state.")

    cat > "$DAILY_FILE" << REPORT
# Relatório Diário — Conecta PRO

> **Para:** Jordan Santos de Jesus
> **Data:** $NOW_BR
> **Período:** últimas 24 horas

---

## Resumo Executivo

Sistema **$OVERALL**. Backend $BACKEND_STATUS, $CELERY_HEALTHY/$CELERY_TOTAL workers Celery healthy, disco ${DISK_PERCENT}%.

## Problemas encontrados

| Severidade | Descrição | Resolução |
|---|---|---|
$FIXED_TODAY

## Métricas do dia

| Métrica | Valor |
|---|---|
| Uptime backend | $BACKEND_STATUS |
| Backups realizados (24h) | $BACKUP_COUNT |
| Testes passando | $TESTS_PASSED |
| Testes falhando | $TESTS_FAILED |

## Infraestrutura

| Recurso | Atual |
|---|---|
| Disco | ${DISK_PERCENT}% |
| RAM | ${RAM_PERCENT}% |
| CPU Load (5min) | $CPU_LOAD |
| Swap | ${SWAP_USED}% |

## Pendências para próxima sessão

$(python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
issues = state.get('current_issues', [])
if not issues:
    print('- [ ] Nenhuma pendência registrada')
else:
    for i in issues:
        print(f'- [ ] [{i.get(\"severity\",\"?\")}] {i.get(\"description\",\"?\")}')
" 2>/dev/null || echo "- [ ] Erro ao ler state")

## Decisões que precisam de aprovação

Nenhuma.
REPORT

    log "Daily report gerado"
}

# ============================================================================
# UPDATE STATE
# ============================================================================

update_state() {
    python3 -c "
import json
from datetime import datetime

with open('$STATE_FILE') as f:
    state = json.load(f)

state['last_updated'] = datetime.utcnow().isoformat() + 'Z'
state['status'] = 'idle'

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
" 2>/dev/null || log "ERRO: falha ao atualizar state"
}

# ============================================================================
# PROCESS MESSAGE QUEUE
# ============================================================================

process_queue() {
    python3 -c "
import json
from datetime import datetime, timedelta

with open('$QUEUE_FILE') as f:
    queue = json.load(f)

now = datetime.utcnow()
messages = queue.get('messages', [])
expired = 0
pending = 0

active = []
for msg in messages:
    ts = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
    ttl = msg.get('ttl_minutes', 60)
    if (now - ts).total_seconds() > ttl * 60:
        expired += 1
        continue
    if msg['status'] == 'pending':
        pending += 1
    active.append(msg)

queue['messages'] = active
queue['last_updated'] = now.isoformat() + 'Z'

with open('$QUEUE_FILE', 'w') as f:
    json.dump(queue, f, indent=2, ensure_ascii=False)

print(f'Queue: {pending} pending, {expired} expired (removed)')
" 2>/dev/null || log "ERRO: falha ao processar queue"
}

# ============================================================================
# STATUS (terminal output)
# ============================================================================

show_status() {
    collect_metrics
    assess_priority
    echo ""
    echo "  Conecta PRO — Status: $OVERALL"
    echo "  ─────────────────────────────────"
    echo "  Backend:  $BACKEND_STATUS ($BACKEND_DETAIL)"
    echo "  Frontend: $PM2_STATUS ($PM2_DETAIL)"
    echo "  Postgres: $PG_STATUS"
    echo "  Redis:    $REDIS_STATUS"
    echo "  Celery:   $CELERY_DETAIL"
    echo "  Nginx:    $NGINX_STATUS"
    echo "  ─────────────────────────────────"
    echo "  CPU: $CPU_LOAD | RAM: ${RAM_PERCENT}% | Disco: ${DISK_PERCENT}% | Swap: ${SWAP_USED}%"
    echo "  ─────────────────────────────────"
    echo "  $PRIORITY_ACTIONS"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

case "${1:-}" in
    --health)
        generate_health_report
        ;;
    --daily)
        generate_daily_report
        ;;
    --status)
        show_status
        ;;
    *)
        # Execução completa (cron)
        log "=== Orchestrator run ==="
        generate_health_report
        process_queue
        update_state
        log "=== Done ==="
        ;;
esac

#!/bin/bash
# =============================================================================
# Audit Watcher - Monitoramento em tempo real de mudanças no codebase
# Uso: ./audit-watcher.sh [diretório] [intervalo_segundos] [log_file]
# =============================================================================

PROJECT_DIR="${1:-/opt/conecta-pro}"
INTERVAL="${2:-30}"
LOG_FILE="${3:-/tmp/audit-watcher.log}"
SNAPSHOT_DIR="/tmp/audit-watcher-snapshots"

mkdir -p "$SNAPSHOT_DIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Snapshot inicial
take_snapshot() {
    local name="$1"
    cd "$PROJECT_DIR" || exit 1

    # Git status
    git diff --name-only > "$SNAPSHOT_DIR/${name}_modified.txt" 2>/dev/null
    git diff --stat > "$SNAPSHOT_DIR/${name}_stats.txt" 2>/dev/null

    # Ruff (backend)
    if [ -d "$PROJECT_DIR/backend" ]; then
        cd "$PROJECT_DIR/backend" || exit 1
        source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
        ruff check . 2>&1 | tail -1 > "$SNAPSHOT_DIR/${name}_ruff.txt"
        deactivate 2>/dev/null
    fi

    # TypeScript (frontend)
    if [ -d "$PROJECT_DIR/frontend" ]; then
        cd "$PROJECT_DIR/frontend" || exit 1
        npx tsc --noEmit 2>&1 | tail -1 > "$SNAPSHOT_DIR/${name}_tsc.txt"
    fi

    cd "$PROJECT_DIR" || exit 1
}

# Comparar snapshots
compare_snapshots() {
    local prev="$1"
    local curr="$2"

    # Arquivos modificados desde último check
    local new_changes
    new_changes=$(diff "$SNAPSHOT_DIR/${prev}_modified.txt" "$SNAPSHOT_DIR/${curr}_modified.txt" 2>/dev/null | grep "^>" | sed 's/^> //')

    if [ -n "$new_changes" ]; then
        log "${YELLOW}[MUDANCAS]${NC} Novos arquivos modificados:"
        echo "$new_changes" | while read -r f; do
            log "  + $f"
        done
    fi

    # Ruff
    local prev_ruff curr_ruff
    prev_ruff=$(cat "$SNAPSHOT_DIR/${prev}_ruff.txt" 2>/dev/null)
    curr_ruff=$(cat "$SNAPSHOT_DIR/${curr}_ruff.txt" 2>/dev/null)
    if [ "$prev_ruff" != "$curr_ruff" ]; then
        log "${BLUE}[RUFF]${NC} $prev_ruff -> $curr_ruff"
    fi

    # TSC
    local prev_tsc curr_tsc
    prev_tsc=$(cat "$SNAPSHOT_DIR/${prev}_tsc.txt" 2>/dev/null)
    curr_tsc=$(cat "$SNAPSHOT_DIR/${curr}_tsc.txt" 2>/dev/null)
    if [ "$prev_tsc" != "$curr_tsc" ]; then
        log "${BLUE}[TSC]${NC} $prev_tsc -> $curr_tsc"
    fi
}

# Verificação completa de qualidade
full_quality_check() {
    log "${GREEN}========== QUALITY CHECK COMPLETO ==========${NC}"
    cd "$PROJECT_DIR" || exit 1

    # 1. Ruff
    log "${BLUE}[1/4] Ruff (Python lint)...${NC}"
    cd "$PROJECT_DIR/backend" || exit 1
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
    local ruff_out
    ruff_out=$(ruff check . 2>&1)
    local ruff_errors
    ruff_errors=$(echo "$ruff_out" | grep -c "^[A-Z]" 2>/dev/null || echo "0")
    if echo "$ruff_out" | grep -q "All checks passed"; then
        log "${GREEN}  Ruff: 0 erros${NC}"
    else
        local ruff_count
        ruff_count=$(echo "$ruff_out" | tail -1)
        log "${RED}  Ruff: $ruff_count${NC}"
    fi

    # 2. Pytest collect
    log "${BLUE}[2/4] Pytest collection...${NC}"
    local pytest_out
    pytest_out=$(python -m pytest --collect-only -q 2>&1 | tail -3)
    log "  $pytest_out"

    # 3. TSC
    log "${BLUE}[3/4] TypeScript check...${NC}"
    cd "$PROJECT_DIR/frontend" || exit 1
    local tsc_out
    tsc_out=$(npx tsc --noEmit 2>&1)
    local tsc_errors
    tsc_errors=$(echo "$tsc_out" | grep -c "error TS" 2>/dev/null || echo "0")
    log "  TSC: $tsc_errors erros"

    # 4. Vitest
    log "${BLUE}[4/4] Frontend tests (vitest)...${NC}"
    local vitest_out
    vitest_out=$(npx vitest run 2>&1 | tail -5)
    log "  $vitest_out"

    deactivate 2>/dev/null
    log "${GREEN}========== FIM DO CHECK ==========${NC}"
}

# Main
log "${GREEN}=== AUDIT WATCHER INICIADO ===${NC}"
log "Projeto: $PROJECT_DIR"
log "Intervalo: ${INTERVAL}s"
log "Log: $LOG_FILE"
log "PID: $$"

# Snapshot inicial
take_snapshot "initial"
log "Snapshot inicial capturado"

iteration=0
while true; do
    sleep "$INTERVAL"
    iteration=$((iteration + 1))

    take_snapshot "current"
    compare_snapshots "previous" "current" 2>/dev/null || compare_snapshots "initial" "current"

    # Rotacionar snapshot
    cp "$SNAPSHOT_DIR/current_modified.txt" "$SNAPSHOT_DIR/previous_modified.txt" 2>/dev/null
    cp "$SNAPSHOT_DIR/current_ruff.txt" "$SNAPSHOT_DIR/previous_ruff.txt" 2>/dev/null
    cp "$SNAPSHOT_DIR/current_tsc.txt" "$SNAPSHOT_DIR/previous_tsc.txt" 2>/dev/null
    cp "$SNAPSHOT_DIR/current_stats.txt" "$SNAPSHOT_DIR/previous_stats.txt" 2>/dev/null

    # Quality check completo a cada 10 iterações (5min com intervalo de 30s)
    if [ $((iteration % 10)) -eq 0 ]; then
        full_quality_check
    fi
done

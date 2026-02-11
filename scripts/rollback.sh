#!/usr/bin/env bash
set -euo pipefail

# rollback.sh — Rollback para versão anterior do Conecta PRO
# Uso: ./scripts/rollback.sh <commit-or-tag>
# Exemplo: ./scripts/rollback.sh v1.0.0
#          ./scripts/rollback.sh HEAD~1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/rollback.log"
TARGET="${1:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
error() { log "ERROR: $*"; exit 1; }

if [ -z "$TARGET" ]; then
  echo "Uso: $0 <commit-or-tag>"
  echo "Exemplo: $0 HEAD~1"
  echo "         $0 v1.0.0"
  exit 1
fi

log "=== ROLLBACK INICIADO para $TARGET ($TIMESTAMP) ==="

cd "$PROJECT_DIR"

# 1. Backup antes do rollback
log "[1/5] Backup antes do rollback..."
if [ -f "$SCRIPT_DIR/backup_database.sh" ]; then
  bash "$SCRIPT_DIR/backup_database.sh" || log "WARN: Backup falhou"
else
  log "WARN: backup_database.sh não encontrado"
fi

# 2. Parar containers
log "[2/5] Parando containers..."
docker compose down || log "WARN: docker compose down falhou"
if [ -f "$PROJECT_DIR/docker-compose.celery.yml" ]; then
  docker compose -f "$PROJECT_DIR/docker-compose.celery.yml" down 2>/dev/null || true
fi

# 3. Checkout para target
log "[3/5] Checkout para $TARGET..."
git fetch --all || log "WARN: git fetch falhou"
git checkout "$TARGET" || error "Falha no checkout para $TARGET"
log "[3/5] Código em $TARGET"

# 4. Rebuild e restart
log "[4/5] Rebuild e restart..."
docker compose build --parallel || error "Build falhou"
docker compose up -d || error "Docker compose up falhou"
if [ -f "$PROJECT_DIR/docker-compose.celery.yml" ]; then
  docker compose -f "$PROJECT_DIR/docker-compose.celery.yml" up -d 2>/dev/null || true
fi
if [ -f "$PROJECT_DIR/monitoring/docker-compose.yml" ]; then
  docker compose -f "$PROJECT_DIR/monitoring/docker-compose.yml" up -d 2>/dev/null || true
fi

# 5. Health check
log "[5/5] Health check..."
MAX_RETRIES=30
RETRY_INTERVAL=2

BACKEND_OK=false
FRONTEND_OK=false

for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
    log "Backend healthy (tentativa $i)"
    BACKEND_OK=true
    break
  fi
  sleep $RETRY_INTERVAL
done

for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf -o /dev/null http://localhost:3001 2>&1; then
    log "Frontend healthy (tentativa $i)"
    FRONTEND_OK=true
    break
  fi
  sleep $RETRY_INTERVAL
done

if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ]; then
  log "=== ROLLBACK PARA $TARGET CONCLUÍDO COM SUCESSO ($TIMESTAMP) ==="
else
  log "=== ROLLBACK CONCLUÍDO COM AVISOS ==="
  [ "$BACKEND_OK" = false ] && log "WARN: Backend não respondeu"
  [ "$FRONTEND_OK" = false ] && log "WARN: Frontend não respondeu"
fi

# Notificar
if [ -n "${DISCORD_WEBHOOK:-}" ]; then
  curl -sf -H "Content-Type: application/json" \
    -d "{\"content\":\"ROLLBACK Conecta PRO para $TARGET ($TIMESTAMP)\"}" \
    "$DISCORD_WEBHOOK" > /dev/null 2>&1 || true
fi

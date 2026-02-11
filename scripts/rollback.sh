#!/usr/bin/env bash
set -euo pipefail

# rollback.sh — Rollback para versão anterior do Conecta PRO
# Uso: ./scripts/rollback.sh [--downgrade <revision>] <commit-or-tag>
# Exemplo: ./scripts/rollback.sh v1.0.0
#          ./scripts/rollback.sh HEAD~1
#          ./scripts/rollback.sh --downgrade abc123 HEAD~1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/rollback.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse flags
DOWNGRADE_REVISION=""
TARGET=""
while [ $# -gt 0 ]; do
  case "$1" in
    --downgrade)
      DOWNGRADE_REVISION="${2:-}"
      [ -z "$DOWNGRADE_REVISION" ] && { echo "ERRO: --downgrade requer uma revision"; exit 1; }
      shift 2
      ;;
    *)
      TARGET="$1"
      shift
      ;;
  esac
done

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
log "[1/6] Backup antes do rollback..."
if [ -f "$SCRIPT_DIR/backup_database.sh" ]; then
  bash "$SCRIPT_DIR/backup_database.sh" || log "WARN: Backup falhou"
else
  log "WARN: backup_database.sh não encontrado"
fi

# 2. Downgrade migrations (se solicitado — ANTES de parar containers)
if [ -n "$DOWNGRADE_REVISION" ]; then
  log "[2/6] Downgrade Alembic para $DOWNGRADE_REVISION..."
  docker compose run --rm backend alembic downgrade "$DOWNGRADE_REVISION" || error "Alembic downgrade falhou"
  log "[2/6] Migration downgrade concluído"
else
  log "[2/6] Downgrade de migration não solicitado, pulando"
fi

# 3. Parar containers
log "[3/6] Parando containers..."
docker compose down || log "WARN: docker compose down falhou"
if [ -f "$PROJECT_DIR/docker-compose.celery.yml" ]; then
  docker compose -f "$PROJECT_DIR/docker-compose.celery.yml" down 2>/dev/null || true
fi

# 4. Checkout para target
log "[4/6] Checkout para $TARGET..."
git fetch --all || log "WARN: git fetch falhou"
git checkout "$TARGET" || error "Falha no checkout para $TARGET"
log "[4/6] Código em $TARGET"

# 5. Rebuild e restart
log "[5/6] Rebuild e restart..."
docker compose build --parallel || error "Build falhou"
docker compose up -d || error "Docker compose up falhou"
if [ -f "$PROJECT_DIR/docker-compose.celery.yml" ]; then
  docker compose -f "$PROJECT_DIR/docker-compose.celery.yml" up -d 2>/dev/null || true
fi
if [ -f "$PROJECT_DIR/monitoring/docker-compose.yml" ]; then
  docker compose -f "$PROJECT_DIR/monitoring/docker-compose.yml" up -d 2>/dev/null || true
fi

# 6. Health check
log "[6/6] Health check..."
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

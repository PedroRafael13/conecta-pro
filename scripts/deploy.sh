#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy automatizado do Conecta PRO
# Uso: ./scripts/deploy.sh [--skip-build] [--skip-migrate]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/deploy.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Criar dir de logs se não existir
mkdir -p "$LOG_DIR"

# Funções auxiliares
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
error() { log "ERROR: $*"; exit 1; }

# Flags
SKIP_BUILD=false
SKIP_MIGRATE=false
for arg in "$@"; do
  case $arg in
    --skip-build) SKIP_BUILD=true ;;
    --skip-migrate) SKIP_MIGRATE=true ;;
    --help) echo "Uso: $0 [--skip-build] [--skip-migrate]"; exit 0 ;;
  esac
done

log "=== DEPLOY INICIADO ($TIMESTAMP) ==="

# 1. Pre-flight checks
log "[1/7] Pre-flight checks..."
cd "$PROJECT_DIR"
if [ ! -f ".env" ]; then
  error ".env não encontrado em $PROJECT_DIR"
fi
source .env 2>/dev/null || error "Falha ao carregar .env"
[ -n "${POSTGRES_PASSWORD:-}" ] || error "POSTGRES_PASSWORD não definido"
[ -n "${JWT_SECRET_KEY:-}" ] || error "JWT_SECRET_KEY não definido"

# Verificar Docker
command -v docker >/dev/null 2>&1 || error "Docker não instalado"
docker info >/dev/null 2>&1 || error "Docker daemon não está rodando"

log "[1/7] Pre-flight OK"

# 2. Git pull
log "[2/7] Atualizando código..."
git pull --ff-only || error "Git pull falhou (conflitos?)"
log "[2/7] Código atualizado"

# 3. Backup database
log "[3/7] Backup do banco antes do deploy..."
if [ -f "$SCRIPT_DIR/backup_database.sh" ]; then
  bash "$SCRIPT_DIR/backup_database.sh" || log "WARN: Backup falhou, continuando..."
else
  log "WARN: backup_database.sh não encontrado, pulando backup"
fi

# 4. Build images
if [ "$SKIP_BUILD" = false ]; then
  log "[4/7] Building Docker images..."
  docker compose build --parallel || error "Build falhou"
  log "[4/7] Build concluído"
else
  log "[4/7] Build pulado (--skip-build)"
fi

# 5. Run migrations
if [ "$SKIP_MIGRATE" = false ]; then
  log "[5/7] Rodando migrações Alembic..."
  docker compose run --rm backend alembic upgrade head || error "Migrações falharam"
  log "[5/7] Migrações aplicadas"
else
  log "[5/7] Migrações puladas (--skip-migrate)"
fi

# 6. Deploy containers
log "[6/7] Iniciando containers..."
docker compose up -d || error "Docker compose up falhou"

# Celery (opcional)
if [ -f "$PROJECT_DIR/docker-compose.celery.yml" ]; then
  docker compose -f "$PROJECT_DIR/docker-compose.celery.yml" up -d 2>/dev/null || log "WARN: Celery compose falhou"
fi

# Monitoring (opcional)
if [ -f "$PROJECT_DIR/monitoring/docker-compose.yml" ]; then
  docker compose -f "$PROJECT_DIR/monitoring/docker-compose.yml" up -d 2>/dev/null || log "WARN: Monitoring compose falhou"
fi

log "[6/7] Containers iniciados"

# 7. Health check com retry
log "[7/7] Verificando saúde dos serviços..."
MAX_RETRIES=30
RETRY_INTERVAL=2

for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
    log "Backend healthy (tentativa $i)"
    break
  fi
  if [ "$i" -eq "$MAX_RETRIES" ]; then
    error "Backend não respondeu após $MAX_RETRIES tentativas"
  fi
  sleep $RETRY_INTERVAL
done

for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf -o /dev/null http://localhost:3001 2>&1; then
    log "Frontend healthy (tentativa $i)"
    break
  fi
  if [ "$i" -eq "$MAX_RETRIES" ]; then
    error "Frontend não respondeu após $MAX_RETRIES tentativas"
  fi
  sleep $RETRY_INTERVAL
done

# Notificar (Discord webhook, se configurado)
if [ -n "${DISCORD_WEBHOOK:-}" ]; then
  curl -sf -H "Content-Type: application/json" \
    -d "{\"content\":\"Deploy Conecta PRO concluído com sucesso ($TIMESTAMP)\"}" \
    "$DISCORD_WEBHOOK" > /dev/null 2>&1 || true
fi

log "=== DEPLOY CONCLUÍDO COM SUCESSO ($TIMESTAMP) ==="

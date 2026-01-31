#!/bin/bash
# Deploy Script - Conecta PRO
# Uso: ./deploy.sh [frontend|backend|all]

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/conecta-pro/backups"
LOG_FILE="/var/log/conecta-pro/deploy_${TIMESTAMP}.log"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[AVISO]${NC} $1" | tee -a "$LOG_FILE"
}

# Criar diretórios necessários
mkdir -p "$BACKUP_DIR" /var/log/conecta-pro

TARGET=${1:-all}

log "=========================================="
log "INICIANDO DEPLOY: $TARGET"
log "=========================================="

cd /opt/conecta-pro

# 1. Backup do Database
log "1/6 - Fazendo backup do database..."
docker exec conecta-pro-postgres pg_dump -U postgres conecta_pro | gzip > "${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz" 2>/dev/null || warn "Backup falhou (não crítico)"

# 2. Pull das últimas mudanças (se usar git)
if [ -d ".git" ]; then
    log "2/6 - Pull do repositório..."
    git pull origin main 2>/dev/null || warn "Git pull falhou"
else
    log "2/6 - Sem repositório git (pulando)"
fi

# 3. Build dos containers
log "3/6 - Build dos containers..."
case $TARGET in
    frontend)
        docker compose build frontend --no-cache || error "Build do frontend falhou"
        ;;
    backend)
        docker compose build backend --no-cache || error "Build do backend falhou"
        ;;
    all)
        docker compose build frontend backend --no-cache || error "Build falhou"
        ;;
esac

# 4. Restart dos serviços
log "4/6 - Reiniciando serviços..."
case $TARGET in
    frontend)
        docker compose up -d frontend
        ;;
    backend)
        docker compose up -d backend
        ;;
    all)
        docker compose up -d frontend backend
        ;;
esac

# 5. Aguardar healthcheck
log "5/6 - Aguardando healthcheck..."
sleep 10

# Verificar status
FRONTEND_STATUS=$(docker inspect --format='{{.State.Health.Status}}' conecta-pro-frontend 2>/dev/null || echo "unknown")
BACKEND_STATUS=$(docker inspect --format='{{.State.Health.Status}}' conecta-pro-backend 2>/dev/null || echo "unknown")

if [ "$FRONTEND_STATUS" != "healthy" ] && [ "$TARGET" != "backend" ]; then
    warn "Frontend ainda não está healthy: $FRONTEND_STATUS"
fi

if [ "$BACKEND_STATUS" != "healthy" ] && [ "$TARGET" != "frontend" ]; then
    warn "Backend ainda não está healthy: $BACKEND_STATUS"
fi

# 6. Limpeza
log "6/6 - Limpando imagens antigas..."
docker image prune -f > /dev/null 2>&1

# Manter apenas últimos 5 backups
ls -t "${BACKUP_DIR}"/db_*.sql.gz 2>/dev/null | tail -n +6 | xargs -r rm

log "=========================================="
log "DEPLOY CONCLUÍDO!"
log "=========================================="

# Status final
echo ""
docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep -E "frontend|backend"
echo ""
log "Log salvo em: $LOG_FILE"
log "Backup salvo em: ${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz"

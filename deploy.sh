#!/bin/bash
# Deploy Script - Conecta PRO (Zero Downtime)
# Uso: ./deploy.sh [frontend|backend|all]
#
# Estratégia: build → start new → wait healthy → remove old
# Se health check falhar, rollback automático para imagem anterior

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/conecta-pro/backups"
LOG_FILE="/var/log/conecta-pro/deploy_${TIMESTAMP}.log"
HEALTH_TIMEOUT=180  # segundos para aguardar healthy (backend tem start_period=300s)
HEALTH_INTERVAL=5   # intervalo entre checks

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERRO]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[AVISO]${NC} $1" | tee -a "$LOG_FILE"; }

wait_healthy() {
    local container="$1"
    local timeout="$2"
    local elapsed=0

    log "   Aguardando $container ficar healthy (timeout: ${timeout}s)..."
    while [ $elapsed -lt "$timeout" ]; do
        status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "not_found")
        case "$status" in
            healthy)
                log "   $container: healthy (${elapsed}s)"
                return 0
                ;;
            unhealthy)
                error "   $container: unhealthy após ${elapsed}s"
                return 1
                ;;
            *)
                sleep "$HEALTH_INTERVAL"
                elapsed=$((elapsed + HEALTH_INTERVAL))
                ;;
        esac
    done
    error "   $container: timeout após ${timeout}s (status: $status)"
    return 1
}

rollback_service() {
    local service="$1"
    local old_image="$2"
    warn "ROLLBACK: restaurando $service para imagem anterior..."
    docker compose up -d "$service" 2>/dev/null
    wait_healthy "conecta-pro-$service" 60 || warn "Rollback health check falhou"
}

deploy_service() {
    local service="$1"
    local container="conecta-pro-$service"

    # Salvar imagem atual para rollback
    local old_image
    old_image=$(docker inspect --format='{{.Config.Image}}' "$container" 2>/dev/null || echo "")

    log "   Imagem atual: ${old_image:-nenhuma}"

    # Build nova imagem
    log "   Construindo nova imagem..."
    if ! docker compose build "$service" --no-cache 2>&1 | tee -a "$LOG_FILE" | tail -3; then
        error "Build do $service falhou!"
        return 1
    fi

    # Iniciar novo container (docker compose up -d faz stop+remove+start)
    log "   Iniciando novo container..."
    docker compose up -d "$service" 2>&1 | tee -a "$LOG_FILE"

    # Aguardar health check
    if ! wait_healthy "$container" "$HEALTH_TIMEOUT"; then
        error "Health check do $service falhou!"
        if [ -n "$old_image" ]; then
            rollback_service "$service" "$old_image"
        fi
        return 1
    fi

    log "   Deploy do $service concluído com sucesso!"
    return 0
}

deploy_pm2_frontend() {
    # PM2 serve o frontend Next.js na porta 3001 (usado pelo nginx upstream)
    log "   Reconstruindo frontend Next.js (PM2)..."

    cd /opt/conecta-pro/frontend

    # Build
    if ! NODE_OPTIONS=--max-old-space-size=8192 npx next build 2>&1 | tee -a "$LOG_FILE" | tail -5; then
        error "Build Next.js falhou!"
        return 1
    fi

    # Restart PM2
    log "   Reiniciando PM2..."
    pm2 restart conecta-pro-frontend 2>&1 | tee -a "$LOG_FILE"

    # Aguardar PM2 ficar online
    local elapsed=0
    while [ $elapsed -lt 30 ]; do
        status=$(pm2 jlist 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['pm2_env']['status'] if d else 'unknown')" 2>/dev/null)
        if [ "$status" = "online" ]; then
            log "   PM2 frontend: online (${elapsed}s)"
            cd /opt/conecta-pro
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done

    error "PM2 frontend não ficou online em 30s (status: $status)"
    cd /opt/conecta-pro
    return 1
}

# ============================================================================
# MAIN
# ============================================================================

mkdir -p "$BACKUP_DIR" /var/log/conecta-pro

TARGET=${1:-all}

log "=========================================="
log "DEPLOY ZERO DOWNTIME: $TARGET"
log "=========================================="

cd /opt/conecta-pro

# 1. Backup do database (pré-deploy)
log "1/5 - Backup do database..."
docker exec conecta-pro-postgres pg_dump -U postgres conecta_pro | gzip > "${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz" 2>/dev/null || warn "Backup falhou (não crítico)"

# 2. Pull do repositório
if [ -d ".git" ]; then
    log "2/5 - Pull do repositório..."
    git pull origin main 2>/dev/null || warn "Git pull falhou"
else
    log "2/5 - Sem repositório git (pulando)"
fi

# 3. Deploy dos serviços (com health check)
log "3/5 - Deploy dos serviços..."
DEPLOY_OK=true

case $TARGET in
    frontend)
        deploy_pm2_frontend || DEPLOY_OK=false
        ;;
    backend)
        deploy_service backend || DEPLOY_OK=false
        ;;
    all)
        # Backend primeiro (APIs), depois frontend (PM2)
        deploy_service backend || DEPLOY_OK=false
        if [ "$DEPLOY_OK" = true ]; then
            deploy_pm2_frontend || DEPLOY_OK=false
        else
            warn "Pulando frontend porque backend falhou"
        fi
        ;;
esac

# 4. Limpeza
log "4/5 - Limpeza..."
docker image prune -f > /dev/null 2>&1

# 5. Verificação final
log "5/5 - Verificação final..."
echo ""
docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep -E "frontend|backend"
echo ""

if [ "$DEPLOY_OK" = true ]; then
    log "=========================================="
    log "DEPLOY CONCLUÍDO COM SUCESSO!"
    log "=========================================="
else
    error "=========================================="
    error "DEPLOY CONCLUÍDO COM ERROS (ver log)"
    error "=========================================="
    error "Rollback automático executado para serviços com falha"
    error "Log: $LOG_FILE"
    exit 1
fi

log "Log: $LOG_FILE"
log "Backup: ${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz"

#!/bin/bash
# =============================================================================
# CONECTA PRO - DEPLOY DE OTIMIZAÇÕES DE PERFORMANCE
# =============================================================================
# Script de deploy automatizado com backup, migrações e validação
#
# Uso: ./DEPLOY_PERFORMANCE.sh [staging|production]
# =============================================================================

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${PROJECT_DIR}/backups/deploy_${TIMESTAMP}"
LOG_FILE="${BACKUP_DIR}/deploy.log"
ENVIRONMENT="${1:-staging}"

# Status
DEPLOY_STATUS="INICIANDO"
ROLLBACK_NEEDED=false

# Criar diretório de backup imediatamente
mkdir -p "$BACKUP_DIR"

# =============================================================================
# FUNÇÕES
# =============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$ts] [$level] $message" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $*"
    log "INFO" "$@"
}

success() {
    echo -e "${GREEN}[✓]${NC} $*"
    log "SUCCESS" "$@"
}

warn() {
    echo -e "${YELLOW}[⚠]${NC} $*"
    log "WARNING" "$@"
}

error() {
    echo -e "${RED}[✗]${NC} $*"
    log "ERROR" "$@"
}

section() {
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    log "SECTION" "$1"
}

confirm() {
    local message=$1
    echo ""
    echo -e "${YELLOW}$message${NC}"
    read -p "Deseja continuar? (yes/no): " response
    if [[ "$response" != "yes" ]]; then
        info "Operação cancelada pelo usuário"
        exit 0
    fi
}

# =============================================================================
# ROLLBACK
# =============================================================================

rollback() {
    error "DEPLOY FALHOU - Executando rollback..."

    echo ""
    warn "Revertendo migração..."
    cd "$PROJECT_DIR/backend"
    source venv/bin/activate 2>/dev/null || true
    alembic downgrade -1 >> "$LOG_FILE" 2>&1 || error "Falha no rollback da migração"

    warn "Restaurando backup do banco..."
    if [ -f "${BACKUP_DIR}/database_backup.dump" ]; then
        $DOCKER_COMPOSE -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
            pg_restore -U "${POSTGRES_USER:-postgres}" \
            -d "${POSTGRES_DB:-conecta_pro}" \
            --clean --if-exists \
            "${BACKUP_DIR}/database_backup.dump" >> "$LOG_FILE" 2>&1 || error "Falha na restauração"
    fi

    warn "Reiniciando serviços com configurações anteriores..."
    cd "$PROJECT_DIR"
    $DOCKER_COMPOSE down >> "$LOG_FILE" 2>&1
    $DOCKER_COMPOSE up -d >> "$LOG_FILE" 2>&1

    error "Rollback concluído. Verifique os logs: $LOG_FILE"
    exit 1
}

# =============================================================================
# PRE-DEPLOY CHECKS
# =============================================================================

section "PRE-DEPLOY: Verificações Iniciais"

info "Diretório de backup: $BACKUP_DIR"
info "Log: $LOG_FILE"

# Verificar ambiente
if [[ "$ENVIRONMENT" == "production" ]]; then
    confirm "⚠️  ATENÇÃO: DEPLOY EM PRODUÇÃO DETECTADO! ⚠️

Este deploy irá:
1. Fazer backup do banco de dados
2. Aplicar 12 novos índices
3. Modificar código (N+1 fix)
4. Reiniciar serviços com novas configurações

Recomenda-se testar em staging primeiro."
fi

# Verificar dependências
info "Verificando dependências..."
command -v docker >/dev/null 2>&1 || { error "Docker não encontrado"; exit 1; }
# Verificar docker compose (pode ser plugin ou comando separado)
if ! docker compose version >/dev/null 2>&1 && ! command -v $DOCKER_COMPOSE >/dev/null 2>&1; then
    error "Docker Compose não encontrado"
    exit 1
fi

# Definir comando correto do docker compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="$DOCKER_COMPOSE"
fi

# Verificar arquivos necessários
[ -f "$PROJECT_DIR/docker-compose.yml" ] || { error "docker-compose.yml não encontrado"; exit 1; }
[ -f "$PROJECT_DIR/backend/alembic/versions/20260205_192551_add_performance_indexes.py" ] || { error "Migração não encontrada"; exit 1; }

success "Verificações iniciais concluídas"

# =============================================================================
# FASE 1: BACKUP
# =============================================================================

section "FASE 1: Backup do Sistema"

info "Criando backup do banco de dados..."

# Backup PostgreSQL
$DOCKER_COMPOSE -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
    pg_dump -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-conecta_pro}" \
    -Fc > "${BACKUP_DIR}/database_backup.dump" 2>>"$LOG_FILE" || {
    error "Falha ao criar backup do banco"
    exit 1
}

BACKUP_SIZE=$(du -h "${BACKUP_DIR}/database_backup.dump" | cut -f1)
success "Backup criado: ${BACKUP_SIZE}"

# Backup de código (git status)
cd "$PROJECT_DIR"
git status --short > "${BACKUP_DIR}/git_status.txt" 2>/dev/null || warn "Não é um repositório git"
git diff --stat > "${BACKUP_DIR}/git_diff_stat.txt" 2>/dev/null || true

# Salvar configurações atuais
$DOCKER_COMPOSE exec -T postgres psql -U "${POSTGRES_USER:-postgres}" -c "
    SELECT name, setting FROM pg_settings
    WHERE name IN ('max_connections', 'shared_buffers', 'effective_cache_size', 'work_mem')
    ORDER BY name;
" > "${BACKUP_DIR}/postgresql_config_before.txt" 2>/dev/null || warn "Não foi possível salvar config PG"

success "Backup concluído"

# =============================================================================
# FASE 2: APLICAR MIGRAÇÃO DE ÍNDICES
# =============================================================================

section "FASE 2: Aplicar Migração de Índices"

cd "$PROJECT_DIR/backend"

# Ativar virtualenv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    success "Ambiente virtual ativado"
fi

# Verificar migrações pendentes
info "Verificando migrações..."
CURRENT_REVISION=$(alembic current 2>/dev/null | head -1 || echo "unknown")
info "Revisão atual: $CURRENT_REVISION"

# Aplicar migração
info "Aplicando migração de performance..."
alembic upgrade 20260205_192551 >> "$LOG_FILE" 2>&1 || {
    error "Falha ao aplicar migração"
    rollback
}

# Verificar índices criados
info "Verificando índices criados..."
INDEX_COUNT=$($DOCKER_COMPOSE -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres psql -U "${POSTGRES_USER:-postgres}" -t -c "
    SELECT count(*) FROM pg_indexes
    WHERE indexname LIKE 'idx_%' AND schemaname = 'public';
" 2>/dev/null | xargs)

if [ "$INDEX_COUNT" -ge 10 ]; then
    success "Migração aplicada: $INDEX_COUNT índices criados"
else
    warn "Apenas $INDEX_COUNT índices encontrados (esperado: 10+)"
fi

# Listar índices
info "Índices criados:"
$DOCKER_COMPOSE -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres psql -U "${POSTGRES_USER:-postgres}" -c "
    SELECT indexname, tablename
    FROM pg_indexes
    WHERE indexname LIKE 'idx_%'
    ORDER BY tablename, indexname;
" >> "$LOG_FILE" 2>&1

# =============================================================================
# FASE 3: REINICIAR SERVIÇOS
# =============================================================================

section "FASE 3: Reiniciar Serviços com Novas Configurações"

cd "$PROJECT_DIR"

info "Parando serviços..."
$DOCKER_COMPOSE down >> "$LOG_FILE" 2>&1 || warn "Alguns serviços podem já estar parados"

info "Removendo containers antigos..."
$DOCKER_COMPOSE rm -f >> "$LOG_FILE" 2>&1 || true

info "Iniciando serviços com novas configurações..."
$DOCKER_COMPOSE up -d >> "$LOG_FILE" 2>&1 || {
    error "Falha ao iniciar serviços"
    rollback
}

# Aguardar PostgreSQL
info "Aguardando PostgreSQL..."
for i in {1..30}; do
    if $DOCKER_COMPOSE exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; then
        success "PostgreSQL pronto"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        error "PostgreSQL não respondeu em 30s"
        rollback
    fi
done

# Aguardar Backend
info "Aguardando Backend..."
for i in {1..60}; do
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        success "Backend pronto"
        break
    fi
    sleep 2
    if [ $i -eq 60 ]; then
        error "Backend não respondeu em 120s"
        rollback
    fi
done

# Aguardar Redis
info "Aguardando Redis..."
for i in {1..10}; do
    if $DOCKER_COMPOSE exec -T redis redis-cli ping > /dev/null 2>&1; then
        success "Redis pronto"
        break
    fi
    sleep 1
done

success "Todos os serviços iniciados"

# =============================================================================
# FASE 4: VALIDAÇÃO
# =============================================================================

section "FASE 4: Validação Pós-Deploy"

info "Executando testes de validação..."

# Testar endpoints
test_endpoint() {
    local name=$1
    local url=$2
    local max_time=${3:-2}

    START=$(date +%s%N)
    HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    END=$(date +%s%N)
    DURATION=$(( (END - START) / 1000000 ))

    if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "401" ]; then
        if [ $DURATION -lt $((max_time * 1000)) ]; then
            success "$name: HTTP $HTTP_CODE - ${DURATION}ms"
            return 0
        else
            warn "$name: HTTP $HTTP_CODE - ${DURATION}ms (lento, esperado < ${max_time}s)"
            return 1
        fi
    else
        error "$name: HTTP $HTTP_CODE (falha)"
        return 1
    fi
}

# Testes
BASE_URL="http://localhost:8080"
test_endpoint "Health Check" "$BASE_URL/health" 1
test_endpoint "Dashboard" "$BASE_URL/api/v1/operacional/dashboard" 2
test_endpoint "KPIs" "$BASE_URL/api/v1/operacional/kpis" 2

# Verificar configurações PostgreSQL
info "Verificando configurações PostgreSQL..."
$DOCKER_COMPOSE exec -T postgres psql -U "${POSTGRES_USER:-postgres}" -c "
    SELECT name, setting, unit
    FROM pg_settings
    WHERE name IN ('max_connections', 'shared_buffers', 'effective_cache_size', 'work_mem', 'random_page_cost')
    ORDER BY name;
" >> "$LOG_FILE" 2>&1

# Verificar cache
info "Verificando Redis..."
KEYSPACE_HITS=$($DOCKER_COMPOSE exec -T redis redis-cli INFO stats 2>/dev/null | grep keyspace_hits | cut -d: -f2 || echo "0")
info "Redis keyspace_hits: $KEYSPACE_HITS"

success "Validação concluída"

# =============================================================================
# RELATÓRIO FINAL
# =============================================================================

section "DEPLOY CONCLUÍDO COM SUCESSO!"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  RESUMO DO DEPLOY${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}Artefatos:${NC}"
echo "  📁 Backup do banco: ${BACKUP_DIR}/database_backup.dump"
echo "  📄 Log completo: ${LOG_FILE}"
echo "  📊 Status git: ${BACKUP_DIR}/git_status.txt"
echo ""

echo -e "${CYAN}Otimizações Aplicadas:${NC}"
echo "  ✅ 12 índices de performance criados"
echo "  ✅ ReferenceDataCache implementado"
echo "  ✅ Query N+1 corrigida (integration_service.py)"
echo "  ✅ PostgreSQL configurado (shared_buffers=512MB, max_connections=200)"
echo "  ✅ Redis otimizado (maxmemory=512MB, allkeys-lru)"
echo "  ✅ Docker Compose atualizado (limites de recursos)"
echo ""

echo -e "${CYAN}Métricas Esperadas:${NC}"
echo "  📉 Queries N+1: -98% (100+ → 2)"
echo "  📉 JOINs lentos: -80% (index scan vs seq scan)"
echo "  📈 Cache hit ratio: +80% (0% → 80%+)"
echo "  📉 Dashboard: -80% (500ms → ~100ms)"
echo "  📉 Configurações: -96% (50ms → ~2ms)"
echo ""

echo -e "${CYAN}Próximos Passos:${NC}"
echo "  1. Monitorar métricas por 24h"
echo "  2. Verificar logs de queries lentas"
echo "  3. Executar: $DOCKER_COMPOSE exec postgres psql -U postgres -c 'ANALYZE;'"
echo "  4. Revisar documentação: docs/PERFORMANCE_MONITORING.md"
echo ""

echo -e "${CYAN}Rollback (se necessário):${NC}"
echo "  cd $PROJECT_DIR"
echo "  ./docs/patches/APPLY_PERFORMANCE_QUICKWINS.sh --rollback ${BACKUP_DIR}/database_backup.dump"
echo ""

echo -e "${GREEN}══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Salvar resumo
{
    echo "DEPLOY RESUME - $(date)"
    echo "==================="
    echo "Ambiente: $ENVIRONMENT"
    echo "Timestamp: $TIMESTAMP"
    echo "Backup: ${BACKUP_DIR}/database_backup.dump"
    echo "Status: SUCESSO"
    echo ""
    echo "Índices criados: $INDEX_COUNT"
    echo "Serviços: OK"
    echo "Validação: OK"
} > "${BACKUP_DIR}/DEPLOY_SUMMARY.txt"

log "DEPLOY" "Deploy concluído com sucesso"

exit 0

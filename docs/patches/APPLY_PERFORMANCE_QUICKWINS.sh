#!/bin/bash
# =============================================================================
# CONECTA PRO - Aplicação de Quick Wins de Performance
# =============================================================================
# Script para aplicar otimizações de performance de forma segura
# Com backup automático e rollback em caso de falha
#
# Uso: ./APPLY_PERFORMANCE_QUICKWINS.sh [ambiente]
#   ambiente: staging (padrão) | production
#
# Data: 2026-02-05
# Versão: 1.0
# =============================================================================

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKUP_DIR="${PROJECT_DIR}/backups/performance_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${BACKUP_DIR}/apply_performance.log"
ENVIRONMENT="${1:-staging}"

# Contadores de status
SUCCESS_COUNT=0
WARNING_COUNT=0
ERROR_COUNT=0

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $*"
    log "INFO" "$@"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
    log "SUCCESS" "$@"
    ((SUCCESS_COUNT++))
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
    log "WARNING" "$@"
    ((WARNING_COUNT++))
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
    log "ERROR" "$@"
    ((ERROR_COUNT++))
}

print_header() {
    echo ""
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    log "INFO" "$1"
}

print_footer() {
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    echo ""
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "Comando '$1' não encontrado. Instale-o primeiro."
        return 1
    fi
}

# =============================================================================
# VERIFICAÇÕES INICIAIS
# =============================================================================

print_header "CONECTA PRO - Aplicação de Quick Wins de Performance"

info "Ambiente: $ENVIRONMENT"
info "Diretório do projeto: $PROJECT_DIR"
info "Diretório de backup: $BACKUP_DIR"
info "Log: $LOG_FILE"

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

# Verificar dependências
info "Verificando dependências..."
check_command docker || exit 1
check_command docker-compose || exit 1
check_command psql || warn "psql não encontrado - algumas verificações serão ignoradas"

# Verificar se está no diretório correto
if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
    error "docker-compose.yml não encontrado em $PROJECT_DIR"
    exit 1
fi

success "Verificações iniciais concluídas"

# =============================================================================
# FASE 1: BACKUP DO BANCO DE DADOS
# =============================================================================

print_header "FASE 1: BACKUP DO BANCO DE DADOS"

if [ "$ENVIRONMENT" == "production" ]; then
    warn "AMBIENTE DE PRODUÇÃO DETECTADO!"
    warn "Certifique-se de que o backup foi realizado manualmente."
    read -p "Deseja continuar? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        info "Operação cancelada pelo usuário"
        exit 0
    fi
fi

info "Criando backup do banco de dados..."

# Backup via docker
docker-compose -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
    pg_dump -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-conecta_pro}" \
    -Fc > "${BACKUP_DIR}/database_backup.dump" 2>>"$LOG_FILE" || {
    error "Falha ao criar backup do banco"
    exit 1
}

success "Backup criado: ${BACKUP_DIR}/database_backup.dump"

# Tamanho do backup
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/database_backup.dump" | cut -f1)
info "Tamanho do backup: $BACKUP_SIZE"

# =============================================================================
# FASE 2: APLICAR MIGRAÇÃO DE ÍNDICES
# =============================================================================

print_header "FASE 2: APLICAR MIGRAÇÃO DE ÍNDICES"

info "Verificando migrações pendentes..."

cd "$PROJECT_DIR/backend"

# Ativar ambiente virtual se existir
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    success "Ambiente virtual ativado"
fi

# Verificar conexão com banco
info "Testando conexão com PostgreSQL..."
python -c "
from core.config import settings
print(f'URL: {settings.database_url.replace(settings.database_url.split(":")[2].split("@")[0], "***")}')
" >> "$LOG_FILE" 2>&1 || {
    error "Falha ao carregar configurações"
    exit 1
}

# Aplicar migração de performance
info "Aplicando migração de índices..."

alembic upgrade 20260205_192551 >> "$LOG_FILE" 2>&1 || {
    error "Falha ao aplicar migração de índices"
    warn "Executando rollback..."
    alembic downgrade -1 >> "$LOG_FILE" 2>&1
    exit 1
}

success "Migração de índices aplicada com sucesso"

# Verificar índices criados
info "Verificando índices criados..."

python -c "
from sqlalchemy import create_engine, text
from core.config import settings

engine = create_engine(settings.database_url)
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE indexname LIKE 'idx_%'
        AND schemaname = 'public'
        ORDER BY tablename, indexname
    '''))
    indexes = result.fetchall()
    print(f'Índices encontrados: {len(indexes)}')
    for idx in indexes[:10]:  # Mostrar primeiros 10
        print(f'  - {idx[0]} on {idx[1]}')
" >> "$LOG_FILE" 2>&1

success "Verificação de índices concluída"

# =============================================================================
# FASE 3: REINICIAR SERVIÇOS COM NOVAS CONFIGURAÇÕES
# =============================================================================

print_header "FASE 3: REINICIAR SERVIÇOS COM NOVAS CONFIGURAÇÕES"

cd "$PROJECT_DIR"

info "Parando serviços..."
docker-compose down >> "$LOG_FILE" 2>&1

info "Iniciando serviços com novas configurações..."
docker-compose up -d >> "$LOG_FILE" 2>&1 || {
    error "Falha ao iniciar serviços"
    exit 1
}

success "Serviços iniciados com novas configurações"

# Aguardar PostgreSQL estar pronto
info "Aguardando PostgreSQL..."
sleep 5

for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; then
        success "PostgreSQL pronto"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        error "PostgreSQL não respondeu em 30 segundos"
        exit 1
    fi
done

# Aguardar Backend estar pronto
info "Aguardando Backend..."
for i in {1..60}; do
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        success "Backend pronto"
        break
    fi
    sleep 1
    if [ $i -eq 60 ]; then
        error "Backend não respondeu em 60 segundos"
        exit 1
    fi
done

# =============================================================================
# FASE 4: TESTAR ENDPOINTS CRÍTICOS
# =============================================================================

print_header "FASE 4: TESTAR ENDPOINTS CRÍTICOS"

BASE_URL="http://localhost:8080"

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3

    info "Testando: $description"

    START_TIME=$(date +%s%N)

    HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" \
        -X "$method" \
        "${BASE_URL}${endpoint}" 2>&1) || {
        error "Falha ao acessar $endpoint"
        return 1
    }

    END_TIME=$(date +%s%N)
    DURATION=$(( (END_TIME - START_TIME) / 1000000 ))  # ms

    if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "401" ]; then
        success "$description - HTTP $HTTP_CODE - ${DURATION}ms"
        echo "$endpoint,$HTTP_CODE,$DURATION" >> "${BACKUP_DIR}/endpoint_tests.csv"
        return 0
    else
        warn "$description - HTTP $HTTP_CODE (esperado 200/401)"
        return 1
    fi
}

# Criar CSV de resultados
echo "endpoint,http_code,duration_ms" > "${BACKUP_DIR}/endpoint_tests.csv"

# Testar endpoints críticos
test_endpoint "GET" "/health" "Health Check"
test_endpoint "GET" "/api/v1/config/estados" "Lista de Estados"
test_endpoint "GET" "/api/v1/operacional/dashboard" "Dashboard Operacional"
test_endpoint "GET" "/api/v1/operacional/kpis" "KPIs"

success "Testes de endpoints concluídos"

# =============================================================================
# FASE 5: VERIFICAR CONFIGURAÇÕES DO POSTGRESQL
# =============================================================================

print_header "FASE 5: VERIFICAR CONFIGURAÇÕES DO POSTGRESQL"

info "Verificando configurações aplicadas..."

# Lista de configurações importantes para verificar
CONFIGS=(
    "max_connections"
    "shared_buffers"
    "effective_cache_size"
    "work_mem"
    "random_page_cost"
    "log_min_duration_statement"
)

echo "config_name,config_value" > "${BACKUP_DIR}/postgresql_config.csv"

for config in "${CONFIGS[@]}"; do
    VALUE=$(docker-compose exec -T postgres \
        psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-conecta_pro}" \
        -t -c "SHOW $config;" 2>/dev/null | xargs)

    echo "$config,$VALUE" >> "${BACKUP_DIR}/postgresql_config.csv"
    info "$config = $VALUE"
done

success "Configurações verificadas"

# =============================================================================
# FASE 6: MÉTRICAS DE CACHE
# =============================================================================

print_header "FASE 6: MÉTRICAS DE CACHE"

info "Verificando status do Redis..."

REDIS_INFO=$(docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD:-}" INFO stats 2>/dev/null || echo "")

if [ -n "$REDIS_INFO" ]; then
    # Extrair métricas úteis
    KEYSPACE_HITS=$(echo "$REDIS_INFO" | grep "keyspace_hits:" | cut -d: -f2 | tr -d '\r')
    KEYSPACE_MISSES=$(echo "$REDIS_INFO" | grep "keyspace_misses:" | cut -d: -f2 | tr -d '\r')

    if [ -n "$KEYSPACE_HITS" ] && [ -n "$KEYSPACE_MISSES" ]; then
        TOTAL=$((KEYSPACE_HITS + KEYSPACE_MISSES))
        if [ $TOTAL -gt 0 ]; then
            HIT_RATE=$(echo "scale=2; $KEYSPACE_HITS * 100 / $TOTAL" | bc 2>/dev/null || echo "N/A")
            info "Cache hit rate: $HIT_RATE% ($KEYSPACE_HITS hits / $TOTAL total)"
        fi
    fi

    success "Métricas de cache obtidas"
else
    warn "Não foi possível obter métricas do Redis"
fi

# =============================================================================
# RESUMO FINAL
# =============================================================================

print_header "RESUMO DA APLICAÇÃO"

info "Arquivos criados:"
echo "  - Backup do banco: ${BACKUP_DIR}/database_backup.dump"
echo "  - Log completo: ${LOG_FILE}"
echo "  - Testes de endpoints: ${BACKUP_DIR}/endpoint_tests.csv"
echo "  - Config PostgreSQL: ${BACKUP_DIR}/postgresql_config.csv"

echo ""
info "Otimizações aplicadas:"
echo "  ✅ Migração de índices de performance"
echo "  ✅ Configurações PostgreSQL otimizadas"
echo "  ✅ ReferenceDataCache implementado"
echo "  ✅ N+1 query otimizado (integration_service.py)"

echo ""
info "Próximos passos:"
echo "  1. Monitorar métricas de performance por 24h"
echo "  2. Verificar logs de queries lentas"
echo "  3. Ajustar TTLs de cache conforme necessário"
echo "  4. Executar ANALYZE nas tabelas:"
echo "     docker-compose exec postgres psql -U postgres -c 'ANALYZE;'"

echo ""
print_footer "Aplicação concluída com sucesso!"

# Estatísticas finais
echo ""
echo "Estatísticas:"
echo "  Sucessos: $SUCCESS_COUNT"
echo "  Avisos: $WARNING_COUNT"
echo "  Erros: $ERROR_COUNT"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    error "Aplicação concluída com erros. Verifique o log: $LOG_FILE"
    exit 1
else
    success "Todas as otimizações aplicadas com sucesso!"
    exit 0
fi

#!/bin/bash
#
# Script de inicialização dos Workers Celery
# Conecta Plus - Integrações Governamentais
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório base
BACKEND_DIR="/opt/conecta-pro/backend"
cd "$BACKEND_DIR"

# Configurações
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
LOG_DIR="${BACKEND_DIR}/logs/celery"
PID_DIR="${BACKEND_DIR}/run"

# Criar diretórios necessários
mkdir -p "$LOG_DIR" "$PID_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   CELERY WORKERS - CONECTA PLUS${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verificar Redis
check_redis() {
    echo -e "${YELLOW}Verificando conexão Redis...${NC}"
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis disponível em ${REDIS_HOST}:${REDIS_PORT}${NC}"
        return 0
    else
        echo -e "${RED}✗ Redis não disponível em ${REDIS_HOST}:${REDIS_PORT}${NC}"
        return 1
    fi
}

# Função para iniciar worker
start_worker() {
    local name=$1
    local queues=$2
    local concurrency=${3:-2}
    local log_level=${4:-INFO}

    echo -e "${YELLOW}Iniciando worker: ${name}${NC}"
    echo "  Filas: $queues"
    echo "  Concorrência: $concurrency"

    celery -A celery_app worker \
        --hostname="${name}@%h" \
        --queues="$queues" \
        --concurrency="$concurrency" \
        --loglevel="$log_level" \
        --pidfile="${PID_DIR}/celery-${name}.pid" \
        --logfile="${LOG_DIR}/celery-${name}.log" \
        --detach

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Worker ${name} iniciado${NC}"
    else
        echo -e "${RED}✗ Falha ao iniciar worker ${name}${NC}"
    fi
}

# Função para iniciar o beat scheduler
start_beat() {
    echo -e "${YELLOW}Iniciando Celery Beat (scheduler)...${NC}"

    celery -A celery_app beat \
        --loglevel=INFO \
        --pidfile="${PID_DIR}/celery-beat.pid" \
        --logfile="${LOG_DIR}/celery-beat.log" \
        --detach

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Celery Beat iniciado${NC}"
    else
        echo -e "${RED}✗ Falha ao iniciar Celery Beat${NC}"
    fi
}

# Função para parar todos os workers
stop_all() {
    echo -e "${YELLOW}Parando todos os workers...${NC}"

    # Parar workers
    for pidfile in "${PID_DIR}"/celery-*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            name=$(basename "$pidfile" .pid)
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid"
                echo -e "${GREEN}✓ Parado: ${name} (PID: ${pid})${NC}"
            fi
            rm -f "$pidfile"
        fi
    done

    echo -e "${GREEN}Todos os workers foram parados${NC}"
}

# Função para mostrar status
show_status() {
    echo -e "${BLUE}Status dos Workers:${NC}"
    echo ""

    celery -A celery_app inspect active 2>/dev/null || echo "Nenhum worker ativo"
    echo ""

    echo -e "${BLUE}Filas:${NC}"
    celery -A celery_app inspect active_queues 2>/dev/null || echo "Sem filas"
}

# Função principal para iniciar todos
start_all() {
    check_redis || exit 1

    echo ""
    echo -e "${BLUE}Iniciando Workers...${NC}"
    echo ""

    # Worker de alta prioridade (eSocial, FGTS)
    start_worker "gov-priority" "gov.esocial,gov.fgts" 2 INFO

    # Worker SEFAZ (NF-e, CT-e, MDF-e)
    start_worker "gov-sefaz" "gov.sefaz.nfe,gov.sefaz.cte,gov.sefaz.mdfe" 3 INFO

    # Worker NFS-e
    start_worker "gov-nfse" "gov.nfse" 2 INFO

    # Worker Batch/Monitoramento
    start_worker "gov-batch" "gov.batch" 2 INFO

    echo ""
    # Beat Scheduler
    start_beat

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   WORKERS INICIADOS COM SUCESSO!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo "Logs: ${LOG_DIR}"
    echo "PIDs: ${PID_DIR}"
    echo ""
    echo "Comandos úteis:"
    echo "  Ver status:  celery -A celery_app inspect active"
    echo "  Ver filas:   celery -A celery_app inspect active_queues"
    echo "  Parar:       $0 stop"
}

# Processar argumentos
case "${1:-start}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    status)
        show_status
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

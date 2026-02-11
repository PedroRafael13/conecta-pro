#!/bin/bash
# =============================================================================
# Script de Execução de Load Tests - ERP Conecta Mais
# =============================================================================
# Uso: ./run-load-test.sh [smoke|full] [staging|prod]
#
# Exemplos:
#   ./run-load-test.sh smoke staging     # Teste rápido em staging
#   ./run-load-test.sh full staging      # Teste completo em staging
# =============================================================================

set -e

# Configurações
TEST_TYPE=${1:-smoke}
ENV=${2:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="/opt/conecta-pro/logs"
RESULTS_FILE="${LOGS_DIR}/load-test-$(date +%Y%m%d-%H%M%S).json"

# URL base por ambiente
if [ "$ENV" == "prod" ]; then
    BASE_URL="https://erp.conectamais.pro"
    echo "⚠️  ATENÇÃO: Testando em PRODUÇÃO!"
    read -p "Tem certeza? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Abortado."
        exit 1
    fi
else
    BASE_URL="http://localhost:8080"
fi

echo "=========================================="
echo "  Load Test - ERP Conecta Mais"
echo "=========================================="
echo "Ambiente: $ENV"
echo "URL: $BASE_URL"
echo "Tipo: $TEST_TYPE"
echo "Saída: $RESULTS_FILE"
echo ""

# Verifica se k6 está instalado
if ! command -v k6 &> /dev/null; then
    echo "❌ k6 não encontrado. Instalando..."
    sudo gpg -k
    sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
        --keyserver hkp://keyserver.ubuntu.com:80 \
        --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
    echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
        sudo tee /etc/apt/sources.list.d/k6.list
    sudo apt-get update && sudo apt-get install -y k6
fi

# Executa o teste
cd "$SCRIPT_DIR"

if [ "$TEST_TYPE" == "smoke" ]; then
    echo "🚀 Executando smoke test..."
    k6 run \
        --env BASE_URL="$BASE_URL" \
        --env ENV="$ENV" \
        --env K6_WEB_DASHBOARD=true \
        --env K6_WEB_DASHBOARD_EXPORT="${RESULTS_FILE%.json}-dashboard.html" \
        --summary-export="$RESULTS_FILE" \
        k6-scenarios.js \
        2>&1 | tee "${LOGS_DIR}/load-test-$(date +%Y%m%d-%H%M%S).log"
else
    echo "🚀 Executando teste completo..."
    k6 run \
        --env BASE_URL="$BASE_URL" \
        --env ENV="$ENV" \
        --env K6_WEB_DASHBOARD=true \
        --summary-export="$RESULTS_FILE" \
        k6-scenarios.js \
        2>&1 | tee "${LOGS_DIR}/load-test-$(date +%Y%m%d-%H%M%S).log"
fi

echo ""
echo "✅ Teste concluído!"
echo "Resultados: $RESULTS_FILE"

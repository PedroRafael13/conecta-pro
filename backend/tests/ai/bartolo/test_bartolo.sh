#!/bin/bash
# ==========================================================================
# Script de Testes do Bartolo AI Assistant
# Fase 2 do Plano de Refinamento
# ==========================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Testes do Bartolo AI Assistant${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Diretório base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="/opt/conecta-pro/backend"
cd "$BACKEND_DIR"

# Função para executar testes
run_test() {
    local test_file=$1
    local test_name=$2

    echo -e "${YELLOW}▶ Executando: ${test_name}${NC}"

    if python -m pytest "tests/ai/bartolo/${test_file}" -v --tb=short 2>&1; then
        echo -e "${GREEN}✓ ${test_name} - PASSOU${NC}"
        return 0
    else
        echo -e "${RED}✗ ${test_name} - FALHOU${NC}"
        return 1
    fi
}

# Contador de resultados
PASSED=0
FAILED=0

echo -e "${BLUE}[1/5] Testando DataConnector Patterns${NC}"
echo "----------------------------------------"
if run_test "test_data_connector_patterns.py" "DataConnector Patterns"; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

echo -e "${BLUE}[2/5] Testando EscalaAgent Patterns${NC}"
echo "----------------------------------------"
if run_test "test_escala_agent_patterns.py" "EscalaAgent Patterns"; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

echo -e "${BLUE}[3/5] Testando SubstituicaoAgent Patterns${NC}"
echo "----------------------------------------"
if run_test "test_substituicao_agent_patterns.py" "SubstituicaoAgent Patterns"; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

echo -e "${BLUE}[4/5] Testando AlertaAgent Patterns${NC}"
echo "----------------------------------------"
if run_test "test_alerta_agent_patterns.py" "AlertaAgent Patterns"; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

echo -e "${BLUE}[5/5] Testando BartoloEngine Integration${NC}"
echo "----------------------------------------"
if run_test "test_bartolo_engine_flow.py" "BartoloEngine Integration"; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

# Resumo
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RESUMO DOS TESTES${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Passou: ${PASSED}${NC}"
echo -e "${RED}✗ Falhou: ${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  ALGUNS TESTES FALHARAM${NC}"
    exit 1
fi

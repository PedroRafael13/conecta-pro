#!/bin/bash
#
# Comandos para Testar Integração API - Frontend <-> Backend
# Conecta PRO v2.0
#

echo "==================================================================="
echo "  CONECTA PRO - Testes de API Backend"
echo "==================================================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para testar endpoint
test_endpoint() {
    local name="$1"
    local url="$2"

    echo -e "${YELLOW}Testando: ${name}${NC}"
    echo "URL: $url"

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ Status: $HTTP_CODE OK${NC}"
        curl -s "$url" | jq . 2>/dev/null || curl -s "$url"
    else
        echo -e "${RED}✗ Status: $HTTP_CODE ERRO${NC}"
    fi

    echo ""
    echo "-------------------------------------------------------------------"
    echo ""
}

# =======================
# 1. HEALTH CHECKS
# =======================
echo "1. HEALTH CHECKS"
echo ""

test_endpoint "Backend Health" "http://localhost:8080/health"

# =======================
# 2. AUTENTICAÇÃO
# =======================
echo "2. AUTENTICAÇÃO (opcional)"
echo ""
echo "Para testar endpoints protegidos, primeiro faça login:"
echo ""
echo "curl -X POST http://localhost:8080/api/v1/auth/login \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"email\":\"admin@conectaplus.com.br\",\"password\":\"senha\"}'"
echo ""
echo "Salve o access_token para usar nos próximos testes:"
echo "export TOKEN='seu_token_aqui'"
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =======================
# 3. BUSCA GLOBAL
# =======================
echo "3. BUSCA GLOBAL"
echo ""

test_endpoint "Busca: 'admin'" "http://localhost:8080/api/v1/search/?q=admin"
test_endpoint "Busca: 'test'" "http://localhost:8080/api/v1/search/?q=test"

# =======================
# 4. KPI TRENDS
# =======================
echo "4. KPI TRENDS"
echo ""

test_endpoint "KPI Trends: 7 dias" "http://localhost:8080/api/v1/operacional/kpi-trends/?period=7d"
test_endpoint "KPI Trends: 30 dias" "http://localhost:8080/api/v1/operacional/kpi-trends/?period=30d"
test_endpoint "KPI Trends: 90 dias" "http://localhost:8080/api/v1/operacional/kpi-trends/?period=90d"

# =======================
# 5. OPENAPI SPEC
# =======================
echo "5. OPENAPI SPEC"
echo ""

echo -e "${YELLOW}Rotas da API v1:${NC}"
curl -s http://localhost:8080/openapi.json | \
    jq -r '.paths | keys[]' | \
    grep "/api/v1" | \
    sort | \
    head -30

echo ""
echo "-------------------------------------------------------------------"
echo ""

# =======================
# 6. DOCUMENTAÇÃO INTERATIVA
# =======================
echo "6. DOCUMENTAÇÃO INTERATIVA"
echo ""
echo "Swagger UI: http://localhost:8080/docs"
echo "ReDoc: http://localhost:8080/redoc"
echo ""

# =======================
# 7. FRONTEND
# =======================
echo "7. FRONTEND"
echo ""
echo "URL: http://localhost:3001"
echo ""
echo "Para testar a integração frontend:"
echo "1. Acesse http://localhost:3001"
echo "2. Faça login"
echo "3. Use Ctrl+K para abrir busca global"
echo "4. Acesse dashboard operacional para ver KPI trends"
echo ""

# =======================
# 8. SERVICE WORKER
# =======================
echo "8. SERVICE WORKER (Notificações Push)"
echo ""
echo "Service Worker: http://localhost:3001/sw.js"
echo ""
echo "Para testar notificações push:"
echo "1. Abra DevTools (F12)"
echo "2. Vá em Application > Service Workers"
echo "3. Verifique se sw.js está registrado"
echo "4. Teste notificação no console:"
echo ""
echo "  import { testNotification } from '@/features/notifications/services/registerServiceWorker';"
echo "  testNotification();"
echo ""

# =======================
# 9. LOGS
# =======================
echo "9. LOGS DOS CONTAINERS"
echo ""
echo "Backend:"
echo "  docker logs -f e5578cd1bf93_conecta-pro-backend"
echo ""
echo "Frontend:"
echo "  docker logs -f conecta-pro-frontend"
echo ""

# =======================
# 10. STATUS DOS SERVIÇOS
# =======================
echo "10. STATUS DOS SERVIÇOS"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep conecta-pro

echo ""
echo "==================================================================="
echo "  Testes concluídos!"
echo "==================================================================="

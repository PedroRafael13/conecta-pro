#!/bin/bash
# =============================================================================
# OpenClaw Setup - Script de instalação automatizada
# =============================================================================
# Uso: bash scripts/openclaw/setup-openclaw.sh
# =============================================================================

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║   🤖 OPENCLAW SETUP - ENGENHEIRO DE SOFTWARE AUTÔNOMO 24/7       ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# =============================================================================
# 1. Verificar pré-requisitos
# =============================================================================
echo -e "${YELLOW}[1/7] Verificando pré-requisitos...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado! Instale primeiro.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado! Instale primeiro.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker e Docker Compose OK${NC}"

# =============================================================================
# 2. Verificar API Key
# =============================================================================
echo -e "\n${YELLOW}[2/7] Verificando API Key...${NC}"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY não encontrada em .env${NC}"
    echo -e "${YELLOW}Por favor, configure primeiro:${NC}"
    echo ""
    echo "  nano .env"
    echo ""
    echo "  # Adicione:"
    echo "  ANTHROPIC_API_KEY=sk-ant-api03-SUA_KEY_AQUI"
    echo "  ANTHROPIC_MODEL=claude-3-5-sonnet-20241022"
    echo "  OPENCLAW_ENABLED=true"
    echo ""
    echo "Obtenha sua key em: https://console.anthropic.com/"
    echo ""
    read -p "Pressione Enter após configurar..."
    source .env
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✅ API Key configurada${NC}"
else
    echo -e "${RED}❌ API Key ainda não configurada. Abortando.${NC}"
    exit 1
fi

# =============================================================================
# 3. Criar networks Docker
# =============================================================================
echo -e "\n${YELLOW}[3/7] Criando networks Docker...${NC}"

docker network create conecta-staging-network 2>/dev/null && echo -e "${GREEN}✅ Network conecta-staging-network criada${NC}" || echo -e "${BLUE}ℹ️  Network conecta-staging-network já existe${NC}"
docker network create conecta-pro-network 2>/dev/null && echo -e "${GREEN}✅ Network conecta-pro-network criada${NC}" || echo -e "${BLUE}ℹ️  Network conecta-pro-network já existe${NC}"

# =============================================================================
# 4. Criar branch staging
# =============================================================================
echo -e "\n${YELLOW}[4/7] Configurando Git (branch staging)...${NC}"

if ! git rev-parse --verify staging &>/dev/null; then
    git checkout -b staging
    git push -u origin staging || echo -e "${YELLOW}⚠️  Não foi possível fazer push (pode ser normal em primeira execução)${NC}"
    echo -e "${GREEN}✅ Branch staging criada${NC}"
else
    echo -e "${BLUE}ℹ️  Branch staging já existe${NC}"
    git checkout staging
fi

# =============================================================================
# 5. Subir ambiente staging
# =============================================================================
echo -e "\n${YELLOW}[5/7] Subindo ambiente staging...${NC}"
echo -e "${BLUE}ℹ️  Isso pode levar 2-3 minutos...${NC}"

docker compose -f docker-compose.staging.yml up -d

echo -e "${BLUE}Aguardando staging inicializar (120s)...${NC}"
for i in {1..120}; do
    echo -n "."
    sleep 1
done
echo ""

# Verificar status
docker compose -f docker-compose.staging.yml ps

echo -e "${GREEN}✅ Ambiente staging iniciado${NC}"

# =============================================================================
# 6. Gerar backlog inicial
# =============================================================================
echo -e "\n${YELLOW}[6/7] Gerando backlog inicial de tarefas...${NC}"

python3 scripts/openclaw/generate-backlog.py

if [ -f "scripts/openclaw/backlog.json" ]; then
    TOTAL_TASKS=$(cat scripts/openclaw/backlog.json | jq -r '.total_tasks' 2>/dev/null || echo "N/A")
    echo -e "${GREEN}✅ Backlog gerado: ${TOTAL_TASKS} tarefas encontradas${NC}"
else
    echo -e "${YELLOW}⚠️  Backlog não gerado (normal em primeira execução)${NC}"
fi

# =============================================================================
# 7. Subir OpenClaw Agent
# =============================================================================
echo -e "\n${YELLOW}[7/7] Subindo OpenClaw Agent...${NC}"

docker compose -f docker-compose.openclaw.yml up -d

sleep 10

# Verificar status
if docker ps | grep -q "openclaw-agent"; then
    echo -e "${GREEN}✅ OpenClaw Agent rodando!${NC}"
else
    echo -e "${RED}❌ OpenClaw Agent não iniciou. Verificando logs...${NC}"
    docker logs openclaw-agent 2>&1 | tail -20
    exit 1
fi

# =============================================================================
# Sucesso!
# =============================================================================
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║   ✅ OPENCLAW INSTALADO E RODANDO COM SUCESSO!                    ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📊 Status:${NC}"
echo ""
docker ps --filter "name=openclaw\|staging" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${BLUE}📝 Próximos passos:${NC}"
echo ""
echo "  1. Acompanhar logs do OpenClaw:"
echo -e "     ${YELLOW}docker logs -f openclaw-agent${NC}"
echo ""
echo "  2. Ver commits do OpenClaw:"
echo -e "     ${YELLOW}git log --author='OpenClaw' --oneline${NC}"
echo ""
echo "  3. Ver progresso:"
echo -e "     ${YELLOW}python3 scripts/openclaw/generate-backlog.py${NC}"
echo ""
echo "  4. Dashboard (se habilitado):"
echo -e "     ${YELLOW}http://$(hostname -I | awk '{print $1}'):8082${NC}"
echo ""

echo -e "${GREEN}🎉 OpenClaw agora trabalha 24/7 melhorando o Conecta PRO!${NC}"
echo ""
echo -e "${BLUE}💡 Dica:${NC} Leia OPENCLAW_MISSION.md para entender os KPIs e objetivos"
echo ""

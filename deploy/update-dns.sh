#!/bin/bash
# =============================================================================
# Conecta PRO - Script de Atualizacao DNS
# =============================================================================
# Este script atualiza o registro A do dominio conectamais.pro
# para apontar para o VPS correto (82.25.75.74)
# =============================================================================

set -e

# Configuracoes
DOMAIN="conectamais.pro"
TARGET_IP="82.25.75.74"
API_TOKEN="${HOSTINGER_API_TOKEN:-}"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "  Conecta PRO - Atualizacao DNS Hostinger"
echo "=============================================="

# Verifica token
if [ -z "$API_TOKEN" ]; then
    echo -e "${RED}Erro: HOSTINGER_API_TOKEN nao definido${NC}"
    echo "Execute: export HOSTINGER_API_TOKEN='seu_token'"
    exit 1
fi

echo -e "${YELLOW}Dominio:${NC} $DOMAIN"
echo -e "${YELLOW}IP Alvo:${NC} $TARGET_IP"
echo ""

# Verifica DNS atual
echo "Verificando DNS atual..."
CURRENT_DNS=$(curl -s -X GET "https://developers.hostinger.com/api/dns/v1/zones/$DOMAIN" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json")

CURRENT_IP=$(echo $CURRENT_DNS | grep -oP '"content":"\K[0-9.]+' | head -1)
echo -e "${YELLOW}IP Atual:${NC} $CURRENT_IP"

if [ "$CURRENT_IP" == "$TARGET_IP" ]; then
    echo -e "${GREEN}DNS ja esta apontando para o IP correto!${NC}"
    exit 0
fi

# Confirma atualizacao
read -p "Deseja atualizar o DNS de $CURRENT_IP para $TARGET_IP? (s/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operacao cancelada."
    exit 0
fi

# Atualiza registro A
echo "Atualizando registro A..."
RESPONSE=$(curl -s -X PUT "https://developers.hostinger.com/api/dns/v1/zones/$DOMAIN" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"zone\": [
            {
                \"name\": \"@\",
                \"type\": \"A\",
                \"ttl\": 300,
                \"records\": [
                    {\"content\": \"$TARGET_IP\"}
                ]
            }
        ],
        \"overwrite\": false
    }")

echo "Resposta: $RESPONSE"

# Verifica se atualizou
sleep 2
echo ""
echo "Verificando nova configuracao..."
NEW_DNS=$(curl -s -X GET "https://developers.hostinger.com/api/dns/v1/zones/$DOMAIN" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json")

NEW_IP=$(echo $NEW_DNS | grep -oP '"content":"\K[0-9.]+' | head -1)

if [ "$NEW_IP" == "$TARGET_IP" ]; then
    echo -e "${GREEN}DNS atualizado com sucesso!${NC}"
    echo -e "${GREEN}$DOMAIN agora aponta para $TARGET_IP${NC}"
else
    echo -e "${YELLOW}DNS pode levar alguns minutos para propagar.${NC}"
    echo "Verifique em: https://dnschecker.org/#A/$DOMAIN"
fi

echo ""
echo "=============================================="
echo "  Proximo passo: Configurar SSL"
echo "  Execute: certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "=============================================="

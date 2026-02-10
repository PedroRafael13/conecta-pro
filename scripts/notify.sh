#!/bin/bash
# =============================================================================
# Script de notificacao multi-canal para Conecta PRO
# Uso: ./notify.sh <channel> <message> [webhook_url]
#   channel    - discord, slack, all
#   message    - Texto da mensagem
#   webhook_url - URL do webhook (opcional se env vars definidas)
#
# Variaveis de ambiente: DISCORD_WEBHOOK, SLACK_WEBHOOK
# =============================================================================

set -euo pipefail

CHANNEL="${1:-}"
MESSAGE="${2:-}"
WEBHOOK_URL="${3:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

if [ -z "$CHANNEL" ] || [ -z "$MESSAGE" ]; then
  echo -e "${RED}Erro: Parametros insuficientes.${NC}"
  echo "Uso: $0 <channel> <message> [webhook_url]"
  exit 1
fi

send_discord() {
  local webhook="${WEBHOOK_URL:-${DISCORD_WEBHOOK:-}}"
  if [ -z "$webhook" ]; then
    echo -e "${YELLOW}Aviso: Webhook Discord nao configurado.${NC}"
    return 1
  fi
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local payload="{\"embeds\":[{\"title\":\"Conecta PRO\",\"description\":\"${MESSAGE}\",\"color\":3447003,\"footer\":{\"text\":\"notify.sh\"},\"timestamp\":\"${timestamp}\"}]}"
  local http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -d "${payload}" "${webhook}")
  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "${GREEN}Discord: OK (HTTP ${http_code})${NC}"
  else
    echo -e "${RED}Discord: Falha (HTTP ${http_code})${NC}"
    return 1
  fi
}

send_slack() {
  local webhook="${WEBHOOK_URL:-${SLACK_WEBHOOK:-}}"
  if [ -z "$webhook" ]; then
    echo -e "${YELLOW}Aviso: Webhook Slack nao configurado.${NC}"
    return 1
  fi
  local payload="{\"attachments\":[{\"color\":\"#3498DB\",\"title\":\"Conecta PRO\",\"text\":\"${MESSAGE}\",\"footer\":\"notify.sh\",\"ts\":$(date +%s)}]}"
  local http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -d "${payload}" "${webhook}")
  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo -e "${GREEN}Slack: OK (HTTP ${http_code})${NC}"
  else
    echo -e "${RED}Slack: Falha (HTTP ${http_code})${NC}"
    return 1
  fi
}

EXIT_CODE=0
case "$CHANNEL" in
  discord) send_discord || EXIT_CODE=$? ;;
  slack)   send_slack || EXIT_CODE=$? ;;
  all)     WEBHOOK_URL="" send_discord || EXIT_CODE=$?; WEBHOOK_URL="" send_slack || EXIT_CODE=$? ;;
  *)       echo -e "${RED}Canal invalido: ${CHANNEL}${NC}"; exit 1 ;;
esac

exit $EXIT_CODE

#!/bin/bash
# Alerta Proativo de Inadimplencia — Nivel 3
# Cron: 0 8 * * 1-5
LOG="/opt/conecta-pro/logs/alertas.log"
mkdir -p /opt/conecta-pro/logs

# Query que retorna dados formatados em 1 linha
RESULT=$(docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t -A -c "
SELECT
  count(*) as qtd,
  coalesce(sum(ra.gross_value), 0) as total,
  string_agg(
    c.name || ': R\$ ' || ra.gross_value::text || ' (' || (CURRENT_DATE - ra.due_date)::text || 'd)',
    E'\n  • '
  ) as detalhes
FROM receivable_accounts ra
LEFT JOIN clients c ON ra.customer_id = c.id
WHERE ra.status NOT IN ('paga','cancelada','baixada')
AND ra.due_date < CURRENT_DATE;" 2>/dev/null)

QTD=$(echo "$RESULT" | cut -d'|' -f1)
TOTAL=$(echo "$RESULT" | cut -d'|' -f2)
DETALHES=$(echo "$RESULT" | cut -d'|' -f3)

if [ "$QTD" = "0" ] || [ -z "$QTD" ]; then
  echo "[$(date)] OK — nenhum inadimplente" >> "$LOG"
  exit 0
fi

TEXTO=$(cat << EOF
⚠️ ALERTA FINANCEIRO $(date '+%d/%m %H:%M')

🔴 ${QTD} conta(s) vencida(s):
  • ${DETALHES}

💸 Total em risco: R$ ${TOTAL}
EOF
)

TG_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" /opt/conecta-pro/.env | cut -d'=' -f2 | head -1)
TG_CHAT=$(grep "^TELEGRAM_CHAT_ID=" /opt/conecta-pro/.env | cut -d'=' -f2 | head -1)

if [ -n "$TG_TOKEN" ] && [ -n "$TG_CHAT" ]; then
  ESCAPED=$(echo "$TEXTO" | python3 -c "import sys,json;print(json.dumps(sys.stdin.read()))")
  curl -sf -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": \"$TG_CHAT\", \"text\": $ESCAPED}" > /dev/null 2>&1 && \
    echo "[$(date)] Alerta enviado: $QTD vencidos, R$ $TOTAL" >> "$LOG" || \
    echo "[$(date)] Falha no envio" >> "$LOG"
fi

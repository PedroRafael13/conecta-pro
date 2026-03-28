#!/bin/bash
# Alerta Proativo de Inadimplencia — Nivel 3
LOG="/opt/conecta-pro/logs/alertas.log"
mkdir -p /opt/conecta-pro/logs

VENCIDOS=$(docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t -c "
SELECT c.name, ra.gross_value, ra.due_date, (CURRENT_DATE - ra.due_date) as dias
FROM receivable_accounts ra
LEFT JOIN clients c ON ra.customer_id = c.id
WHERE ra.status NOT IN ('paga','cancelada','baixada')
AND ra.due_date < CURRENT_DATE
ORDER BY ra.gross_value DESC;" 2>/dev/null | grep -v "^$")

if [ -z "$VENCIDOS" ]; then
  echo "[$(date)] OK — nenhum inadimplente" >> "$LOG"
  exit 0
fi

MSG="⚠️ ALERTA FINANCEIRO $(date '+%d/%m %H:%M')"
TOTAL=0
while IFS='|' read -r nome valor data dias; do
  NOME=$(echo "$nome" | xargs)
  VALOR=$(echo "$valor" | xargs)
  DIAS=$(echo "$dias" | xargs)
  [ -z "$NOME" ] && continue
  MSG="$MSG
  • $NOME: R\$ $VALOR (${DIAS}d atraso)"
  TOTAL=$(python3 -c "print(round($TOTAL + float('${VALOR:-0}'), 2))" 2>/dev/null || echo "$TOTAL")
done <<< "$VENCIDOS"

MSG="$MSG

Total em risco: R\$ $TOTAL"

TG_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" /opt/conecta-pro/.env | cut -d'=' -f2 | head -1)
TG_CHAT=$(grep "^TELEGRAM_CHAT_ID=" /opt/conecta-pro/.env | cut -d'=' -f2 | head -1)

if [ -n "$TG_TOKEN" ] && [ -n "$TG_CHAT" ]; then
  curl -sf -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{\"chat_id\": \"$TG_CHAT\", \"text\": \"$MSG\"}" > /dev/null 2>&1
  echo "[$(date)] Alerta enviado: $TOTAL em risco" >> "$LOG"
else
  echo "[$(date)] Telegram nao configurado" >> "$LOG"
fi

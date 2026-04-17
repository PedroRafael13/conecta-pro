#!/bin/bash
LOG="/opt/conecta-pro/rotinas/logs/onvio_sync_$(date +%Y%m).log"
MES_REF=$(date -d "last month" +%m.%Y 2>/dev/null || date -v-1m +%m.%Y)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando sync Onvio para $MES_REF..." >> $LOG
curl -s -X POST "http://localhost:8080/api/v1/onvio/sync?mes_ref=$MES_REF" >> $LOG 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync concluído" >> $LOG
source /opt/conecta-pro/.env
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}&text=📥 GEDEON: Sync Onvio $MES_REF concluído. Verifique em /modulos/ged/onvio-sync" > /dev/null

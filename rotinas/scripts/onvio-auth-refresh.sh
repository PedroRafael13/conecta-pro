#!/bin/bash
LOG="/opt/conecta-pro/rotinas/logs/onvio_auth_$(date +%Y%m).log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Renovando sessão Onvio..." >> $LOG
cd /opt/conecta-pro
python3 onvio_auth.py >> $LOG 2>&1
if [ $? -eq 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Sessão renovada" >> $LOG
  source /opt/conecta-pro/.env
  curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}&text=✅ GEDEON: Sessão Onvio renovada com sucesso" > /dev/null
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Falha na renovação" >> $LOG
fi

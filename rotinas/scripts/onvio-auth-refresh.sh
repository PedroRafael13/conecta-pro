#!/bin/bash
# REDIS_URL aponta para o container Redis (não localhost — Redis não expõe porta no host)
REDIS_PASS=$(grep REDIS_PASSWORD /opt/conecta-pro/.env | cut -d= -f2 | head -1)
REDIS_IP=$(docker inspect conecta-pro-redis 2>/dev/null | python3 -c "import sys,json; nets=json.load(sys.stdin)[0]['NetworkSettings']['Networks']; print(list(nets.values())[0]['IPAddress'])" 2>/dev/null || echo "172.18.0.14")
export REDIS_URL="redis://:${REDIS_PASS}@${REDIS_IP}:6379/1"

LOG="/opt/conecta-pro/rotinas/logs/onvio_auth_$(date +%Y%m).log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Renovando sessão Onvio (Redis: ${REDIS_IP})..." >> $LOG
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

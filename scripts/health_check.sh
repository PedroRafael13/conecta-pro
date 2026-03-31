#!/bin/bash
# Health check completo do Conecta PRO
# Verifica todos os serviços e reinicia se necessário

BOT_TOKEN="${MONITOR_BOT_TOKEN:-8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ}"  # pragma: allowlist secret
CHAT_ID="${MONITOR_CHAT_ID:-5536961034}"
LOG="/opt/conecta-pro/logs/monitor.log"
HORA=$(date '+%d/%m/%Y %H:%M')
ALERTAS=()

notify() {
    curl -sf -X POST \
        "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -H "Content-Type: application/json" \
        -d "{\"chat_id\":\"${CHAT_ID}\",\"text\":\"$1\",\"parse_mode\":\"HTML\"}" \
        > /dev/null 2>&1
}

# Verificar backend
BACKEND=$(curl -sf -o /dev/null -w "%{http_code}" \
    http://127.0.0.1:8080/docs 2>/dev/null)

if [ "$BACKEND" != "200" ]; then
    echo "[$HORA] Backend DOWN ($BACKEND)" >> "$LOG"
    ALERTAS+=("🔴 Backend: DOWN ($BACKEND)")

    CONTAINER=$(docker ps -a \
        --filter ancestor=conecta-pro-backend \
        --format '{{.Names}}' | head -1)
    if [ -n "$CONTAINER" ]; then
        docker restart "$CONTAINER" > /dev/null 2>&1
        sleep 15
        BACKEND_AFTER=$(curl -sf -o /dev/null -w "%{http_code}" \
            http://127.0.0.1:8080/docs 2>/dev/null)
        if [ "$BACKEND_AFTER" = "200" ]; then
            ALERTAS+=("✅ Backend: Reiniciado OK")
            echo "[$HORA] Backend reiniciado OK" >> "$LOG"
        else
            ALERTAS+=("❌ Backend: Falhou ao reiniciar")
        fi
    fi
fi

# Verificar frontend PM2
PM2_OK=$(pm2 list 2>/dev/null | grep "online" | wc -l)
if [ "$PM2_OK" = "0" ]; then
    ALERTAS+=("🔴 Frontend PM2: DOWN")
    echo "[$HORA] PM2 DOWN — tentando reiniciar" >> "$LOG"
    cd /opt/conecta-pro/frontend || true
    pm2 restart conecta-pro-frontend --update-env > /dev/null 2>&1
    pm2 save > /dev/null 2>&1
fi

# Verificar Redis
REDIS_CONTAINER=$(docker ps --filter ancestor=redis \
    --format '{{.Names}}' | head -1)
if [ -n "$REDIS_CONTAINER" ]; then
    REDIS=$(docker exec "$REDIS_CONTAINER" redis-cli ping 2>/dev/null || echo "FAIL")
    if [ "$REDIS" != "PONG" ]; then
        ALERTAS+=("🔴 Redis: DOWN ou sem resposta")
        echo "[$HORA] Redis DOWN" >> "$LOG"
    fi
fi

# Enviar alertas se houver problemas
if [ ${#ALERTAS[@]} -gt 0 ]; then
    LISTA=$(printf '%s\n' "${ALERTAS[@]}")
    MSG="🚨 <b>ALERTA — CONECTA PRO</b>
⏰ $HORA

$LISTA"
    notify "$MSG"
fi

echo "[$HORA] Health check concluído — ${#ALERTAS[@]} alertas" >> "$LOG"

#!/bin/bash
# Monitor Startup — executado no @reboot após delay inicial
# Aguarda backend ficar disponível antes de iniciar primeiro ciclo
# Timeout: 3 minutos

BOT_TOKEN="${MONITOR_BOT_TOKEN:-8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ}"  # pragma: allowlist secret
CHAT_ID="${MONITOR_CHAT_ID:-5536961034}"
BACKEND_URL="http://127.0.0.1:8080/health"
MAX_WAIT=180   # 3 minutos
INTERVAL=10    # checar a cada 10s
LOG="/opt/conecta-pro/logs/monitor.log"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"
}

telegram_notify() {
    curl -sf -X POST \
      "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      -H "Content-Type: application/json" \
      -d "{\"chat_id\":\"${CHAT_ID}\",\"text\":\"$1\",\"parse_mode\":\"HTML\"}" \
      > /dev/null 2>&1
}

log "=== Monitor Startup iniciado ==="
log "Aguardando backend em ${BACKEND_URL} (max ${MAX_WAIT}s)..."

elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
    if curl -sf --max-time 5 "$BACKEND_URL" > /dev/null 2>&1; then
        log "✅ Backend disponível após ${elapsed}s — iniciando primeiro ciclo"
        break
    fi
    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
    log "⏳ Aguardando backend... ${elapsed}s/${MAX_WAIT}s"
done

if [ $elapsed -ge $MAX_WAIT ]; then
    log "❌ Backend não respondeu em ${MAX_WAIT}s — abortando ciclo inicial"
    telegram_notify "⚠️ <b>MONITOR STARTUP FALHOU</b>
Backend não respondeu em ${MAX_WAIT}s após reboot.
Verifique os containers: docker compose ps
Hora: $(date '+%d/%m %H:%M')"
    exit 1
fi

# Executar primeiro ciclo de monitoramento
log "🚀 Executando primeiro ciclo de monitoramento..."
MONITOR_BOT_TOKEN="$BOT_TOKEN" \
MONITOR_CHAT_ID="$CHAT_ID" \
/usr/bin/python3 /opt/conecta-pro/agents/skills_agent.py >> "$LOG" 2>&1

exit_code=$?
if [ $exit_code -eq 0 ]; then
    log "✅ Primeiro ciclo concluído com sucesso"
else
    log "⚠️ Primeiro ciclo terminou com código $exit_code"
fi

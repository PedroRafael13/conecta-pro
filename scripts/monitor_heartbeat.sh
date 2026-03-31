#!/bin/bash
# Heartbeat do Monitor — roda a cada 6h
# Se parar de chegar, algo está errado

BOT_TOKEN="${MONITOR_BOT_TOKEN:-8562364686:AAESOC6uXddwShWSs3_1-qJ4lBiZHBiSuBQ}"  # pragma: allowlist secret
CHAT_ID="${MONITOR_CHAT_ID:-5536961034}"
STATE_FILE="/opt/conecta-pro/reports/monitor_state.json"

HORA=$(date '+%d/%m %H:%M')

CICLOS=$(python3 -c "
import json, sys
try:
    s = json.load(open('$STATE_FILE'))
    print(s.get('ciclos_executados', 0))
except:
    print('?')
" 2>/dev/null)

SCORE=$(python3 -c "
import json, sys
try:
    s = json.load(open('$STATE_FILE'))
    h = s.get('score_historico', [])
    if h: print(h[-1]['score'])
    else: print('?')
except:
    print('?')
" 2>/dev/null)

TENDENCIA=$(python3 -c "
import json, sys
try:
    s = json.load(open('$STATE_FILE'))
    h = s.get('score_historico', [])
    if len(h) < 4:
        print('→ iniciando')
        sys.exit()
    ultimos = h[-12:]
    diff = ultimos[-1]['score'] - ultimos[0]['score']
    if diff > 0.3: print(f'↑ subindo (+{diff:.1f})')
    elif diff < -0.3: print(f'↓ caindo ({diff:.1f})')
    else:
        sinal = '+' if diff >= 0 else ''
        print(f'→ estável ({sinal}{diff:.1f})')
except:
    print('→ ?')
" 2>/dev/null)

MELHOR=$(python3 -c "
import json, sys
try:
    s = json.load(open('$STATE_FILE'))
    print(s.get('melhor_score', '?'))
except:
    print('?')
" 2>/dev/null)

UPTIME=$(uptime -p 2>/dev/null || uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')

MSG="💚 <b>HEARTBEAT — MONITOR ATIVO</b>
⏰ $HORA
📊 Score atual: <b>${SCORE}/10</b>
📈 Tendência: ${TENDENCIA}
🏆 Melhor score: ${MELHOR}/10
🔄 Ciclos executados: $CICLOS
⚙️ Uptime: $UPTIME
✅ Sistema operacional — próximo ciclo em breve"

curl -sf -X POST \
  "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\":\"${CHAT_ID}\",\"text\":\"${MSG}\",\"parse_mode\":\"HTML\"}" \
  > /dev/null 2>&1

echo "[$(date '+%H:%M:%S')] Heartbeat enviado | score=${SCORE} | ciclos=${CICLOS} | tendencia=${TENDENCIA}"

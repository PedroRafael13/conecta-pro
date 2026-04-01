#!/bin/bash
# Briefing diario Jordan — seg-sex 7h30
LOG="/opt/conecta-pro/logs/briefing.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Briefing..." >> "$LOG"
TK=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
[ -z "$TK" ] && echo "[$(date)] ERRO: token" >> "$LOG" && exit 1
R=$(curl -sf -X POST "http://127.0.0.1:8080/api/v1/ai/briefing/enviar" \
  -H "Authorization: Bearer $TK" 2>/dev/null)
echo "[$(date)] $R" >> "$LOG"

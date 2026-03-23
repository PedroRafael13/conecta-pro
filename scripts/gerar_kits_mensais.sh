#!/bin/bash
# ──────────────────────────────────────────────────────────
# Geração automática de kits documentais mensais
# Executar: dia 1 de cada mês às 02:00
# Crontab:  0 2 1 * * /opt/conecta-pro/scripts/gerar_kits_mensais.sh
# ──────────────────────────────────────────────────────────

LOG="/var/log/conecta-pro/kits_mensais.log"
API="http://localhost:8080"
MES=$(date +%-m)
ANO=$(date +%Y)
REF=$(date +%Y-%m-01)

echo "$(date '+%Y-%m-%d %H:%M:%S') [START] Gerando kits $MES/$ANO" >> "$LOG"

# Obter token
TOKEN=$(curl -sf -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] Falha ao obter token" >> "$LOG"
  exit 1
fi

# Chamar auto-assemble
RESULT=$(curl -sf -X POST \
  "$API/api/v1/ged/auto-assemble?reference_month=$REF" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null)

if [ -z "$RESULT" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] Falha no auto-assemble" >> "$LOG"
  exit 1
fi

KITS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('kits_created',0))" 2>/dev/null)
DOCS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_documents',0))" 2>/dev/null)

echo "$(date '+%Y-%m-%d %H:%M:%S') [OK] $KITS kits criados, $DOCS documentos coletados" >> "$LOG"

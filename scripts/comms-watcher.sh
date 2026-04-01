#!/bin/bash
# ============================================
# Comms Watcher — Monitor de comunicação inter-IA
# Monitora mensagens entre Claude e Kimi
# Uso: bash /opt/conecta-pro/scripts/comms-watcher.sh
# ============================================

COMMS_DIR="/opt/conecta-pro/.comms/messages"
LOG="/tmp/comms-watcher.log"
CLAUDE_OUT="$COMMS_DIR/claude-out.jsonl"
KIMI_OUT="$COMMS_DIR/kimi-out.jsonl"

# Contagem inicial
CLAUDE_LINES=$(wc -l < "$CLAUDE_OUT" 2>/dev/null || echo 0)
KIMI_LINES=$(wc -l < "$KIMI_OUT" 2>/dev/null || echo 0)

echo "========================================" > $LOG
echo "COMMS WATCHER — Iniciado $(date)" >> $LOG
echo "Claude msgs: $CLAUDE_LINES | Kimi msgs: $KIMI_LINES" >> $LOG
echo "========================================" >> $LOG

while true; do
    NEW_CLAUDE=$(wc -l < "$CLAUDE_OUT" 2>/dev/null || echo 0)
    NEW_KIMI=$(wc -l < "$KIMI_OUT" 2>/dev/null || echo 0)

    # Detectar novas mensagens do Claude
    if [ "$NEW_CLAUDE" -gt "$CLAUDE_LINES" ]; then
        DIFF=$((NEW_CLAUDE - CLAUDE_LINES))
        echo "[$(date '+%H:%M:%S')] Claude enviou $DIFF mensagem(ns):" >> $LOG
        tail -$DIFF "$CLAUDE_OUT" | while read line; do
            TYPE=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('type','?'))" 2>/dev/null)
            SUBJECT=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('subject','?'))" 2>/dev/null)
            echo "  → [$TYPE] $SUBJECT" >> $LOG
        done
        CLAUDE_LINES=$NEW_CLAUDE
    fi

    # Detectar novas mensagens do Kimi
    if [ "$NEW_KIMI" -gt "$KIMI_LINES" ]; then
        DIFF=$((NEW_KIMI - KIMI_LINES))
        echo "[$(date '+%H:%M:%S')] Kimi enviou $DIFF mensagem(ns):" >> $LOG
        tail -$DIFF "$KIMI_OUT" | while read line; do
            TYPE=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('type','?'))" 2>/dev/null)
            SUBJECT=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('subject','?'))" 2>/dev/null)
            echo "  → [$TYPE] $SUBJECT" >> $LOG
        done
        KIMI_LINES=$NEW_KIMI
    fi

    # Status periódico (a cada 5 min = 60 ciclos de 5s)
    CYCLE=$((${CYCLE:-0} + 1))
    if [ $((CYCLE % 60)) -eq 0 ]; then
        echo "[$(date '+%H:%M:%S')] Heartbeat — Claude: $NEW_CLAUDE msgs | Kimi: $NEW_KIMI msgs" >> $LOG
    fi

    sleep 5
done

#!/bin/bash
# Script de comunicação IA-to-IA
# Uso: ./comm.sh send <from> <to> <mensagem>
#      ./comm.sh receive <to>
#      ./comm.sh status

COMM_DIR="/opt/conecta-pro/.comm"

send_message() {
    local from=$1
    local to=$2
    local content=$3
    local id=$(uuidgen)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local inbox="$COMM_DIR/$from-to-$to/inbox"

    cat > "$inbox/msg-$id.json" << EOF
{
  "id": "$id",
  "from": "$from",
  "to": "$to",
  "timestamp": "$timestamp",
  "content": "$content",
  "status": "pending"
}
EOF
    echo "✅ Mensagem enviada: $id"
}

receive_message() {
    local to=$1
    local inbox="$COMM_DIR"/*-to-$to/inbox/*.json

    for msg in $inbox; do
        if [ -f "$msg" ]; then
            echo "📨 Nova mensagem:"
            cat "$msg" | jq .

            # Mover para archive
            local dir=$(dirname "$msg")
            local archive="$(dirname "$dir")/archive"
            mv "$msg" "$archive/"
            echo "✅ Movida para archive"
            return 0
        fi
    done
    echo "📭 Nenhuma mensagem nova"
}

show_status() {
    echo "╔════════════════════════════════════════╗"
    echo "║     STATUS DO CANAL IA-to-IA          ║"
    echo "╚════════════════════════════════════════╝"
    echo ""

    for dir in "$COMM_DIR"/*-to-*/inbox; do
        if [ -d "$dir" ]; then
            local count=$(ls -1 "$dir"/*.json 2>/dev/null | wc -l)
            local name=$(basename $(dirname "$dir"))
            echo "📁 $name: $count mensagens pendentes"
        fi
    done
}

case "$1" in
    send)
        send_message "$2" "$3" "$4"
        ;;
    receive)
        receive_message "$2"
        ;;
    status)
        show_status
        ;;
    *)
        echo "Uso: $0 {send <from> <to> <msg>|receive <to>|status}"
        exit 1
        ;;
esac

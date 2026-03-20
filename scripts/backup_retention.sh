#!/bin/bash
# ============================================================================
# Backup Retention Policy - Conecta PRO
# Mantém: últimos 7 diários + 4 semanais (domingos)
# Execução: cron diário às 03:30 UTC (após backup das 03:00)
# ============================================================================

BACKUP_DIR="/opt/conecta-pro/backups/postgresql"
LOG_FILE="/var/log/conecta-backup-retention.log"
DRY_RUN="${1:-}"  # passar --dry-run para simular

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log "=== Início da rotação de backups ==="

if [ ! -d "$BACKUP_DIR" ]; then
    log "ERRO: Diretório $BACKUP_DIR não existe"
    exit 1
fi

# Listar todos os backups ordenados por data (mais recente primeiro)
mapfile -t ALL_BACKUPS < <(ls -t "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null)
TOTAL=${#ALL_BACKUPS[@]}

if [ "$TOTAL" -eq 0 ]; then
    log "Nenhum backup encontrado"
    exit 0
fi

log "Total de backups encontrados: $TOTAL"

# Marcar quais manter
declare -A KEEP

# 1. Manter os 7 mais recentes (diários)
for i in $(seq 0 $((${#ALL_BACKUPS[@]} < 7 ? ${#ALL_BACKUPS[@]} - 1 : 6))); do
    KEEP["${ALL_BACKUPS[$i]}"]=daily
done

# 2. Manter o mais recente de cada domingo das últimas 4 semanas
for week in 0 1 2 3; do
    # Calcular o domingo dessa semana
    sunday=$(date -d "last sunday - $((week * 7)) days" '+%Y%m%d' 2>/dev/null)
    if [ -z "$sunday" ]; then
        continue
    fi

    # Procurar backup desse domingo
    for backup in "${ALL_BACKUPS[@]}"; do
        filename=$(basename "$backup")
        # Extrair data do nome: backup_YYYYMMDD_HHMMSS.sql.gz
        backup_date=$(echo "$filename" | grep -oP '\d{8}' | head -1)
        if [ "$backup_date" = "$sunday" ]; then
            KEEP["$backup"]=weekly
            break
        fi
    done
done

# 3. Deletar os que não estão marcados
DELETED=0
KEPT=0
for backup in "${ALL_BACKUPS[@]}"; do
    if [ -n "${KEEP[$backup]+x}" ]; then
        KEPT=$((KEPT + 1))
        log "  MANTER [${KEEP[$backup]}]: $(basename "$backup") ($(du -h "$backup" | cut -f1))"
    else
        if [ "$DRY_RUN" = "--dry-run" ]; then
            log "  DELETARIA: $(basename "$backup") ($(du -h "$backup" | cut -f1))"
        else
            rm -f "$backup"
            log "  DELETADO: $(basename "$backup")"
        fi
        DELETED=$((DELETED + 1))
    fi
done

log "Resultado: $KEPT mantidos, $DELETED $([ "$DRY_RUN" = "--dry-run" ] && echo "seriam " || echo "")deletados (de $TOTAL total)"
log "=== Fim da rotação ==="

#!/bin/bash
# =============================================================================
# Backup do Banco de Dados — Conecta PRO
# Uso: bash scripts/backup_db.sh [--output /path/to/backup.sql]
# =============================================================================

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEFAULT_OUTPUT="/tmp/conecta_pro_backup_${TIMESTAMP}.sql"
OUTPUT="${1:-$DEFAULT_OUTPUT}"

# Remove --output flag if present
if [ "${1:-}" = "--output" ]; then
    OUTPUT="${2:-$DEFAULT_OUTPUT}"
fi

echo "[INFO] Iniciando backup do banco de dados..."
echo "[INFO] Destino: $OUTPUT"

# Tenta usar variaveis de ambiente ou valores padrao
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_NAME="${DATABASE_NAME:-conecta_pro}"
DB_USER="${DATABASE_USER:-postgres}"

# Executa pg_dump
if command -v pg_dump &> /dev/null; then
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --no-owner --no-acl --if-exists --clean \
        -f "$OUTPUT" 2>&1

    if [ $? -eq 0 ]; then
        SIZE=$(du -h "$OUTPUT" | cut -f1)
        echo "[OK] Backup concluido: $OUTPUT ($SIZE)"
    else
        echo "[ERROR] Falha no backup"
        exit 1
    fi
elif docker ps --format '{{.Names}}' | grep -q postgres; then
    CONTAINER=$(docker ps --format '{{.Names}}' | grep postgres | head -1)
    echo "[INFO] Usando container Docker: $CONTAINER"
    docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" \
        --no-owner --no-acl --if-exists --clean > "$OUTPUT" 2>&1

    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo "[OK] Backup concluido: $OUTPUT ($SIZE)"
else
    echo "[ERROR] pg_dump nao encontrado e nenhum container PostgreSQL rodando"
    exit 1
fi

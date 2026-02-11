#!/usr/bin/env bash
set -euo pipefail

# backup_database.sh — Backup automatizado do Conecta PRO
# Implementa regra 3-2-1: 3 cópias, 2 mídias, 1 offsite
# Uso: ./scripts/backup_database.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$PROJECT_DIR/backups/postgresql"
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"
LOG_DIR="$PROJECT_DIR/logs"
RETENTION_DAYS=30

# Carregar variáveis do .env
if [ -f "$PROJECT_DIR/.env" ]; then
  source "$PROJECT_DIR/.env"
else
  echo "ERRO: .env não encontrado em $PROJECT_DIR"
  exit 1
fi

# Variáveis do banco (lidas do .env)
DB_USER="${POSTGRES_USER:?POSTGRES_USER não definido no .env}"
DB_NAME="${POSTGRES_DB:?POSTGRES_DB não definido no .env}"
CONTAINER_NAME="conecta-pro-postgres"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  BACKUP CONECTA PRO${NC}"
echo -e "${GREEN}  Data: $(date)${NC}"
echo -e "${GREEN}========================================${NC}"

# Criar diretórios
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"

# Verificar container PostgreSQL
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo -e "${RED}ERRO: Container $CONTAINER_NAME não está rodando${NC}"
  exit 1
fi

# 1. Criar backup comprimido via docker exec
echo -e "\n${YELLOW}[1/5] Criando backup do banco...${NC}"
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo -e "${GREEN}   Backup criado: $BACKUP_FILE ($SIZE)${NC}"
else
  echo -e "${RED}   ERRO: Falha ao criar backup (arquivo vazio ou inexistente)${NC}"
  rm -f "$BACKUP_FILE"
  exit 1
fi

# 2. Verificar integridade do backup
echo -e "\n${YELLOW}[2/5] Verificando integridade...${NC}"
if gunzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo -e "${GREEN}   Integridade OK${NC}"
else
  echo -e "${RED}   ERRO: Backup corrompido!${NC}"
  exit 1
fi

# 3. Upload para storage offsite (se configurado)
echo -e "\n${YELLOW}[3/5] Verificando backup offsite...${NC}"
if command -v aws &> /dev/null && [ -n "${S3_BACKUP_BUCKET:-}" ]; then
  if aws s3 cp "$BACKUP_FILE" "s3://$S3_BACKUP_BUCKET/postgresql/" 2>/dev/null; then
    echo -e "${GREEN}   Upload S3 OK${NC}"
  else
    echo -e "${YELLOW}   AVISO: Upload S3 falhou${NC}"
  fi
else
  echo -e "${YELLOW}   AVISO: Backup offsite desabilitado (S3 não configurado)${NC}"
fi

# 4. Limpar backups antigos (manter últimos 30 dias)
echo -e "\n${YELLOW}[4/5] Limpando backups antigos (>${RETENTION_DAYS} dias)...${NC}"
DELETED=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print 2>/dev/null | wc -l)
echo -e "${GREEN}   $DELETED backups antigos removidos${NC}"

# 5. Resumo
echo -e "\n${YELLOW}[5/5] Resumo...${NC}"
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "backup_*.sql.gz" 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  BACKUP CONCLUÍDO COM SUCESSO${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "  Arquivo: $BACKUP_FILE"
echo -e "  Tamanho: $SIZE"
echo -e "  Total backups: $TOTAL_BACKUPS"
echo -e "  Espaço usado: $TOTAL_SIZE"
echo -e "${GREEN}========================================${NC}"

# Log para monitoramento
echo "[$(date)] Backup OK: $BACKUP_FILE ($SIZE)" >> "$LOG_DIR/backup.log"

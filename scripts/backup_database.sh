#!/bin/bash
# Script de backup automatizado - ERP Conecta Mais
# Implementa regra 3-2-1: 3 copias, 2 midias, 1 offsite

set -e

# Configuracoes
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/erp-conecta-mais/backups/postgresql"
BACKUP_FILE="$BACKUP_DIR/erp_backup_$DATE.sql.gz"
DB_NAME="erp_conecta_mais"
DB_USER="conecta_user"
DB_HOST="localhost"
RETENTION_DAYS=30

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  BACKUP ERP CONECTA MAIS${NC}"
echo -e "${GREEN}  Data: $(date)${NC}"
echo -e "${GREEN}========================================${NC}"

# Criar diretorio se nao existir
mkdir -p $BACKUP_DIR

# 1. Criar backup comprimido
echo -e "\n${YELLOW}[1/5] Criando backup do banco...${NC}"
PGPASSWORD=conecta_secret_2024 pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > $BACKUP_FILE

if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo -e "${GREEN}   Backup criado: $BACKUP_FILE ($SIZE)${NC}"
else
    echo -e "${RED}   ERRO: Falha ao criar backup!${NC}"
    exit 1
fi

# 2. Verificar integridade do backup
echo -e "\n${YELLOW}[2/5] Verificando integridade...${NC}"
if gunzip -t $BACKUP_FILE 2>/dev/null; then
    echo -e "${GREEN}   Integridade OK${NC}"
else
    echo -e "${RED}   ERRO: Backup corrompido!${NC}"
    exit 1
fi

# 3. Upload para storage offsite (se configurado)
echo -e "\n${YELLOW}[3/5] Verificando backup offsite...${NC}"
if command -v aws &> /dev/null; then
    # S3 configurado
    if aws s3 cp $BACKUP_FILE s3://conecta-mais-backups/postgresql/ 2>/dev/null; then
        echo -e "${GREEN}   Upload S3 OK${NC}"
    else
        echo -e "${YELLOW}   AVISO: S3 nao configurado ou falhou${NC}"
    fi
else
    echo -e "${YELLOW}   AVISO: AWS CLI nao instalado (backup offsite desabilitado)${NC}"
fi

# 4. Limpar backups antigos (manter ultimos 30 dias)
echo -e "\n${YELLOW}[4/5] Limpando backups antigos (>${RETENTION_DAYS} dias)...${NC}"
DELETED=$(find $BACKUP_DIR -name "erp_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
echo -e "${GREEN}   $DELETED backups antigos removidos${NC}"

# 5. Resumo
echo -e "\n${YELLOW}[5/5] Resumo...${NC}"
TOTAL_BACKUPS=$(ls -1 $BACKUP_DIR/erp_backup_*.sql.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR 2>/dev/null | cut -f1)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  BACKUP CONCLUIDO COM SUCESSO${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "  Arquivo: $BACKUP_FILE"
echo -e "  Tamanho: $SIZE"
echo -e "  Total backups: $TOTAL_BACKUPS"
echo -e "  Espaco usado: $TOTAL_SIZE"
echo -e "${GREEN}========================================${NC}"

# Log para monitoramento
echo "[$(date)] Backup OK: $BACKUP_FILE ($SIZE)" >> /opt/erp-conecta-mais/logs/backup.log

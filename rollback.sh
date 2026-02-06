#!/bin/bash
# Rollback Script - Conecta PRO
# Uso: ./rollback.sh [backup_file.sql.gz]

set -e

BACKUP_DIR="/opt/conecta-pro/backups"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=========================================="
echo -e "ROLLBACK - Conecta PRO"
echo -e "==========================================${NC}"

cd /opt/conecta-pro

# Listar backups disponíveis
echo ""
echo "Backups disponíveis:"
ls -lh "${BACKUP_DIR}"/db_*.sql.gz 2>/dev/null | awk '{print NR". " $9 " (" $5 ")"}'

if [ -z "$1" ]; then
    # Usar backup mais recente
    BACKUP_FILE=$(ls -t "${BACKUP_DIR}"/db_*.sql.gz 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        echo -e "${RED}Nenhum backup encontrado!${NC}"
        exit 1
    fi
    echo ""
    echo -e "${YELLOW}Usando backup mais recente: $BACKUP_FILE${NC}"
else
    BACKUP_FILE="$1"
fi

echo ""
read -p "Confirmar rollback com $BACKUP_FILE? (s/N): " confirm
if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    echo "Rollback cancelado."
    exit 0
fi

echo ""
echo -e "${GREEN}Restaurando database...${NC}"
gunzip -c "$BACKUP_FILE" | docker exec -i conecta-pro-postgres psql -U postgres -d conecta_pro

echo ""
echo -e "${GREEN}Reiniciando serviços...${NC}"
docker compose restart backend

echo ""
echo -e "${GREEN}=========================================="
echo -e "ROLLBACK CONCLUÍDO!"
echo -e "==========================================${NC}"

#!/bin/bash
# Health Check - Conecta PRO
# Uso: ./health.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "HEALTH CHECK - Conecta PRO"
echo "=========================================="
echo ""

# Containers
echo "CONTAINERS:"
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | grep -v "^NAME" | while read line; do
    if echo "$line" | grep -q "healthy"; then
        echo -e "  ${GREEN}✓${NC} $line"
    elif echo "$line" | grep -q "unhealthy"; then
        echo -e "  ${RED}✗${NC} $line"
    else
        echo -e "  ${YELLOW}?${NC} $line"
    fi
done

echo ""

# API Health
echo "ENDPOINTS:"
BACKEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null)
if [ "$BACKEND" == "200" ]; then
    echo -e "  ${GREEN}✓${NC} Backend API: OK (200)"
else
    echo -e "  ${RED}✗${NC} Backend API: $BACKEND"
fi

FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null)
if [ "$FRONTEND" == "200" ] || [ "$FRONTEND" == "307" ] || [ "$FRONTEND" == "302" ]; then
    echo -e "  ${GREEN}✓${NC} Frontend: OK ($FRONTEND)"
else
    echo -e "  ${RED}✗${NC} Frontend: $FRONTEND"
fi

echo ""

# Recursos
echo "RECURSOS:"
DISK=$(df -h / | tail -1 | awk '{print $5}')
DISK_NUM=${DISK%\%}
if [ "$DISK_NUM" -lt 80 ]; then
    echo -e "  ${GREEN}✓${NC} Disco: $DISK usado"
elif [ "$DISK_NUM" -lt 90 ]; then
    echo -e "  ${YELLOW}!${NC} Disco: $DISK usado (atenção)"
else
    echo -e "  ${RED}✗${NC} Disco: $DISK usado (crítico)"
fi

MEM=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$MEM" -lt 80 ]; then
    echo -e "  ${GREEN}✓${NC} RAM: ${MEM}% usado"
elif [ "$MEM" -lt 90 ]; then
    echo -e "  ${YELLOW}!${NC} RAM: ${MEM}% usado (atenção)"
else
    echo -e "  ${RED}✗${NC} RAM: ${MEM}% usado (crítico)"
fi

# Database
DB_SIZE=$(docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -t -c "SELECT pg_size_pretty(pg_database_size('conecta_pro'));" 2>/dev/null | tr -d ' ')
echo -e "  ${GREEN}✓${NC} Database: $DB_SIZE"

echo ""
echo "=========================================="

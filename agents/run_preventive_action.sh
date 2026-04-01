#!/bin/bash
# Executa preventive_action.py dentro do container backend
PG_PASS=$(grep "^POSTGRES_PASSWORD=" /opt/conecta-pro/.env | head -1 | cut -d= -f2)
docker cp /opt/conecta-pro/agents/preventive_action.py conecta-pro-backend:/app/preventive_action.py 2>/dev/null
docker exec -e POSTGRES_PASSWORD="$PG_PASS" conecta-pro-backend python3 /app/preventive_action.py \
  >> /opt/conecta-pro/logs/preventive_action.log 2>&1

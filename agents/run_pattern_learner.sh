#!/bin/bash
# Executa pattern_learner.py dentro do container backend
PG_PASS=$(grep "^POSTGRES_PASSWORD=" /opt/conecta-pro/.env | head -1 | cut -d= -f2)
docker cp /opt/conecta-pro/agents/pattern_learner.py conecta-pro-backend:/app/pattern_learner.py 2>/dev/null
docker exec -e POSTGRES_PASSWORD="$PG_PASS" conecta-pro-backend python3 /app/pattern_learner.py \
  >> /opt/conecta-pro/logs/pattern_learner.log 2>&1

#!/bin/bash
# Sync módulo para todos os workers Celery
# Uso: ./sync_celery_workers.sh nome_do_modulo
MODULO=${1:?'Informe o módulo: ./sync_celery_workers.sh gedeon'}
for CONTAINER in conecta-pro-backend conecta-pro-celery-beat conecta-pro-celery-batch \
  conecta-pro-celery-operacional conecta-pro-celery-integrations conecta-pro-celery-priority; do
  docker exec $CONTAINER find /app/modules/$MODULO/__pycache__ -name "*.pyc" -delete 2>/dev/null || true
  docker cp backend/modules/$MODULO/ $CONTAINER:/app/modules/$MODULO/ && echo "OK: $CONTAINER"
done
docker exec conecta-pro-backend kill -HUP 1

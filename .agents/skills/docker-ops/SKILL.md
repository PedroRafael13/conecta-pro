---
title: Docker Operations
description: Gerenciamento de 12 containers do Conecta PRO
containers: 12
---

# Docker Operations

Orquestração dos 12 containers do ERP Conecta PRO.

## Containers Reais

### Core (5) — docker-compose.yml
```bash
conecta-pro-backend      # FastAPI/Python 3.12
conecta-pro-frontend     # Next.js 16
conecta-pro-postgres     # PostgreSQL 16 Alpine
conecta-pro-redis        # Redis 7 Alpine
conecta-pro-nginx        # Nginx 1.25 reverse proxy
```

### Celery Workers (8) — docker-compose.celery.yml
```bash
conecta-pro-celery-priority       # Filas: gov.esocial, gov.fgts
conecta-pro-celery-sefaz          # Filas: gov.sefaz.nfe, cte, mdfe
conecta-pro-celery-nfse           # Filas: gov.nfse
conecta-pro-celery-batch          # Batch processing
conecta-pro-celery-integrations   # Integrações externas
conecta-pro-celery-operacional    # Tarefas operacionais
conecta-pro-celery-beat           # Scheduler periódico
conecta-pro-flower                # UI de monitoramento Celery
```

## Comandos Essenciais

```bash
# Iniciar stack core
cd /opt/conecta-pro && docker compose up -d

# Iniciar com Celery workers
docker compose -f docker-compose.yml -f docker-compose.celery.yml up -d

# Ver status
docker ps --filter "name=conecta"

# Logs
docker logs -f conecta-pro-backend
docker logs -f conecta-pro-celery-beat

# Shell no container
docker exec -it conecta-pro-backend bash
docker exec -it conecta-pro-postgres psql -U conecta_user conecta_pro

# Restart
docker restart conecta-pro-backend

# Build específico
docker compose build backend --no-cache && docker compose up -d backend

# Limpeza
docker system prune -f
```

## Health Checks

```bash
# Status de todos os containers conecta
docker ps --filter "name=conecta" --format "table {{.Names}}\t{{.Status}}"

# Testar API
curl -f http://localhost:8000/health || echo "API DOWN"

# Redis
docker exec conecta-pro-redis redis-cli ping

# PostgreSQL
docker exec conecta-pro-postgres pg_isready -U conecta_user
```

## Checklist

- [ ] Containers core rodando (`docker ps --filter "name=conecta"`)
- [ ] API respondendo (`curl localhost:8000/health`)
- [ ] Celery workers conectados (verificar via Flower)
- [ ] Redis acessível
- [ ] PostgreSQL acessível
- [ ] Logs sem erros críticos

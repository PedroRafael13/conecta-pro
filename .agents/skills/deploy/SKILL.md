---
title: Deploy Automatizado
description: Pipeline de deploy do Conecta PRO
environments: [dev, staging, production]
---

# Deploy Automatizado

Pipeline de deploy contínuo para ambientes do ERP Conecta PRO.

## Environments

| Ambiente | Branch | URL |
|----------|--------|-----|
| dev | feature/* | dev.conecta.pro |
| staging | develop | staging.conecta.pro |
| production | main | app.conecta.pro |

## Infraestrutura

- **VPS** com SSH via MobaXterm
- **Deploy** via `docker compose` direto na VPS (sem Kubernetes)
- **Proxy** Nginx como reverse proxy
- **Compose files:** `docker-compose.yml` + `docker-compose.celery.yml` + `docker-compose.prod.yml`

## Deploy por Serviço

```bash
cd /opt/conecta-pro

# Backend: rebuild e restart
docker compose build backend --no-cache && docker compose up -d backend

# Frontend: rebuild e restart
docker compose build frontend --no-cache && docker compose up -d frontend

# Stack completa (core + celery)
docker compose -f docker-compose.yml -f docker-compose.celery.yml up -d --build

# Produção
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Rollback

```bash
# Ver imagens anteriores
docker images --filter "reference=conecta-pro*" --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}"

# Rollback: parar, usar imagem anterior, subir
docker compose down
git checkout <commit-anterior>
docker compose up -d --build
```

## Verificação Pós-Deploy

```bash
# Health check API
curl -f http://localhost:8000/health || echo "BACKEND DOWN"

# Verificar containers
docker ps --filter "name=conecta" --format "table {{.Names}}\t{{.Status}}"

# Logs rápidos (últimos erros)
docker logs --tail=50 conecta-pro-backend | grep -i error
docker logs --tail=50 conecta-pro-frontend | grep -i error

# Migrations
docker exec conecta-pro-backend alembic current
```

## Checklist Pré-Deploy

- [ ] Testes passando (`pytest` + `npm run test`)
- [ ] Type check ok (`tsc --noEmit` + `mypy`)
- [ ] Migrations revisadas (`alembic history`)
- [ ] `.env` verificado
- [ ] Backup do banco (`docker exec conecta-pro-postgres pg_dump -U conecta_user conecta_pro > backup.sql`)

## Checklist Pós-Deploy

- [ ] API health ok
- [ ] Frontend carregando
- [ ] Celery workers conectados (Flower)
- [ ] Logs sem erros críticos
- [ ] Testar fluxo principal manualmente

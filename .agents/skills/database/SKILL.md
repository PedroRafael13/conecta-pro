---
title: Database Stack
description: PostgreSQL 16, Redis 7, Alembic migrations para Conecta PRO
stack: [postgresql, redis, alembic]
---

# Database Stack

Gerenciamento de dados do ERP Conecta PRO com PostgreSQL 16, Redis 7 e Alembic.

## Conexões

```yaml
PostgreSQL:
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  database: conecta_pro
  user: ${DB_USER:-conecta}

Redis:
  host: ${REDIS_HOST:-localhost}
  port: ${REDIS_PORT:-6379}
  db: 0
```

## Alembic - Migrations

```bash
# Criar migration
alembic revision -m "adiciona_tabela_faturamento" --autogenerate

# Aplicar migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# Status
alembic current
alembic history --verbose

# Verificar SQL antes de aplicar
alembic upgrade head --sql > migration_preview.sql
```

## Comandos PostgreSQL

```bash
# Backup
pg_dump -h localhost -U conecta conecta_pro > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U conecta conecta_pro < backup.sql

# Análise de queries lentas
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

# Reindexar
REINDEX DATABASE conecta_pro;
```

## Redis - Operações

```bash
# Limpar cache de sessões
redis-cli KEYS "session:*" | xargs redis-cli DEL

# Cache de relatórios
redis-cli EXPIRE "report:daily" 3600

# Monitorar comandos
redis-cli MONITOR

# Estatísticas
redis-cli INFO stats
```

## Estrutura de Tabelas Principais

```
financial.*        - Módulo financeiro (483 endpoints)
operational.*      - Módulo operacional (14 controllers)
gov_esocial.*      - Integrações eSocial
gov_sefaz.*        - Integrações SEFAZ
security_audits.*  - Auditorias LGPD
```

## Checklist de Operações

- [ ] Backup automático configurado
- [ ] Índices otimizados (EXPLAIN ANALYZE)
- [ ] Conexões no pool (< 100)
- [ ] Redis TTL configurado para caches
- [ ] Migration testada em staging
- [ ] ROLLBACK script preparado

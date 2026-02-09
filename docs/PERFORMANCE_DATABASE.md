# 📊 RELATÓRIO DE CONFIGURAÇÃO DE BANCO DE DADOS

**Projeto:** Conecta PRO (PostgreSQL 16)
**Arquivos analisados:** 70+ migrações, 30+ modelos
**Data:** 2026-02-05

---

## 1. Configurações PostgreSQL

### Atual vs Recomendado

```yaml
# ═══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO ATUAL (docker-compose.yml)
# ═══════════════════════════════════════════════════════════════
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-postgres}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-}
    POSTGRES_DB: ${POSTGRES_DB:-conecta_pro}
    PGDATA: /var/lib/postgresql/data/pgdata
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G

# ═══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO RECOMENDADA
# ═══════════════════════════════════════════════════════════════
postgres:
  image: postgres:16-alpine
  container_name: conecta-pro-postgres
  restart: unless-stopped
  environment:
    POSTGRES_USER: ${POSTGRES_USER:-postgres}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-}
    POSTGRES_DB: ${POSTGRES_DB:-conecta_pro}
    PGDATA: /var/lib/postgresql/data/pgdata

  command: >
    postgres
    -c max_connections=200
    -c shared_buffers=512MB
    -c effective_cache_size=1536MB
    -c work_mem=4MB
    -c maintenance_work_mem=128MB
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
    -c checkpoint_completion_target=0.9
    -c log_min_duration_statement=1000
    -c log_checkpoints=on
    -c log_connections=on
    -c log_disconnections=on

  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 1G
```

### Explicação das Configurações

| Parâmetro | Atual | Recomendado | Motivo |
|-----------|-------|-------------|--------|
| `max_connections` | 100 | 200 | Mais conexões para pool |
| `shared_buffers` | 128MB | 512MB | Cache de dados em memória |
| `effective_cache_size` | 4GB | 1536MB | Estimativa para query planner |
| `work_mem` | 4MB | 4MB | Manter (adequado) |
| `maintenance_work_mem` | 64MB | 128MB | Vacuum e criar índices |
| `wal_buffers` | - | 16MB | Write-ahead logging |
| `log_min_duration_statement` | - | 1000ms | Log queries lentas |

---

## 2. Índices Faltantes

### 🔴 CRÍTICO - Foreign Keys sem Índice

```python
# Migração Alembic: add_missing_foreign_key_indexes.py

from alembic import op

def upgrade():
    # GED Documents - FKs frequentemente usadas em joins
    op.create_index('idx_ged_docs_contract', 'ged_documents', ['contract_id'])
    op.create_index('idx_ged_docs_employee', 'ged_documents', ['employee_id'])
    op.create_index('idx_ged_docs_client', 'ged_documents', ['client_id'])

    # GED Folders
    op.create_index('idx_ged_folders_parent', 'ged_folders', ['parent_id'])
    op.create_index('idx_ged_folders_contract', 'ged_folders', ['contract_id'])

    # Occurrences
    op.create_index('idx_occ_attach_occurrence', 'occurrence_attachments', ['occurrence_id'])
    op.create_index('idx_occ_comm_occurrence', 'occurrence_comments', ['occurrence_id'])
    op.create_index('idx_occ_comm_author', 'occurrence_comments', ['author_id'])

    # Allocations
    op.create_index('idx_allocations_employee', 'allocations', ['employee_id'])

    # Substitutions
    op.create_index('idx_subst_original_emp', 'substitutions', ['original_employee_id'])
    op.create_index('idx_subst_substitute', 'substitutions', ['substitute_employee_id'])

    # Scales
    op.create_index('idx_scales_approved_by', 'scales', ['approved_by'])
    op.create_index('idx_scales_published_by', 'scales', ['published_by'])

def downgrade():
    op.drop_index('idx_ged_docs_contract')
    op.drop_index('idx_ged_docs_employee')
    # ... etc
```

### 🟡 MÉDIO - Campos de Busca Frequente

```python
# Migração: add_search_indexes.py

def upgrade():
    # Leads - busca por origem e follow-up
    op.create_index('idx_leads_source', 'leads', ['source'])
    op.create_index('idx_leads_last_contact', 'leads', ['last_contact_at'])

    # Opportunities - pipeline e previsões
    op.create_index('idx_opportunities_priority', 'opportunities', ['priority'])
    op.create_index('idx_opportunities_expected_close', 'opportunities', ['expected_close_date'])
    op.create_index('idx_opportunities_actual_close', 'opportunities', ['actual_close_date'])

    # Candidates - busca RH
    op.create_index('idx_candidates_cpf', 'candidates', ['cpf'])
    op.create_index('idx_candidates_status', 'candidates', ['status'])
    op.create_index('idx_candidates_city', 'candidates', ['city'])

    # Posts - filtros operacionais
    op.create_index('idx_posts_shift_type', 'posts', ['shift_type'])
    op.create_index('idx_posts_city', 'posts', ['city'])

    # GED Documents - filtros
    op.create_index('idx_ged_docs_status', 'ged_documents', ['status'])
    op.create_index('idx_ged_docs_type', 'ged_documents', ['document_type'])
    op.create_index('idx_ged_docs_ocr', 'ged_documents', ['is_ocr_processed'])
```

### 🟢 Índices Compostos Recomendados

```python
# Migração: add_composite_indexes.py

def upgrade():
    # Para queries frequentes de dashboard
    op.create_index(
        'idx_leads_status_source',
        'leads',
        ['status', 'source']
    )

    op.create_index(
        'idx_opportunities_stage_owner',
        'opportunities',
        ['stage', 'owner_id']
    )

    op.create_index(
        'idx_shifts_employee_date',
        'shifts',
        ['employee_id', 'shift_date']
    )

    op.create_index(
        'idx_occurrences_employee_date',
        'occurrences',
        ['employee_id', 'occurred_at']
    )

    op.create_index(
        'idx_occurrences_status_date',
        'occurrences',
        ['status', 'occurred_at']
    )

    op.create_index(
        'idx_posts_status_type',
        'posts',
        ['status', 'post_type']
    )

    op.create_index(
        'idx_candidates_status_source',
        'candidates',
        ['status', 'source']
    )
```

---

## 3. Tabelas para Arquivamento/Particionamento

### Tabelas Críticas

| Tabela | Volume Esperado | Estratégia | Retenção |
|--------|-----------------|------------|----------|
| `audit_logs` | Alto | Particionamento + Arquivamento | 1 ano ativo |
| `access_history` | Alto | Particionamento + Arquivamento | 6 meses ativo |
| `notification_logs` | Médio | Particionamento | 90 dias |
| `time_tracking_records` | Alto | Particionamento | 2 anos ativo |
| `ocr_results` | Médio | Arquivamento | 1 ano |
| `report_executions` | Baixo | Cleanup | 6 meses |
| `fraud_alerts` | Baixo | Particionamento | 3 anos |

### Script de Particionamento

```sql
-- Habilitar pg_partman (extensão para particionamento)
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- Tabela audit_logs particionada
CREATE TABLE audit_logs (
    id UUID DEFAULT gen_random_uuid(),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    user_id UUID,
    tenant_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Criar partições mensais
SELECT partman.create_parent(
    'public.audit_logs',
    'created_at',
    'native',
    'monthly'
);

-- Configurar retenção (manter 12 meses)
UPDATE partman.part_config
SET retention = '12 months',
    retention_keep_table = false
WHERE parent_table = 'public.audit_logs';
```

---

## 4. Manutenção Automática

### Job de VACUUM e ANALYZE

```sql
-- Instalar pg_cron
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Job diário de VACUUM ANALYZE (3h da manhã)
SELECT cron.schedule('vacuum-analyze-daily', '0 3 * * *', $$
  DO $$
  DECLARE
    r RECORD;
  BEGIN
    FOR r IN
      SELECT schemaname, tablename
      FROM pg_tables
      WHERE schemaname = 'public'
    LOOP
      EXECUTE 'ANALYZE ' || quote_ident(r.schemaname) || '.' || quote_ident(r.tablename);
    END LOOP;
  END $$;
$$);

-- Job semanal de VACUUM FULL em tabelas pequenas (domingo 4h)
SELECT cron.schedule('vacuum-full-weekly', '0 4 * * 0', $$
  VACUUM ANALYZE;
$$);
```

### Job de Cleanup

```sql
-- Cleanup de notificações antigas (mensal)
SELECT cron.schedule('cleanup-notifications', '0 4 1 * *', $$
  DELETE FROM notification_logs
  WHERE created_at < NOW() - INTERVAL '90 days';

  DELETE FROM notification_queue
  WHERE processed_at < NOW() - INTERVAL '30 days';
$$);

-- Cleanup de audit_logs (se não usar particionamento)
SELECT cron.schedule('cleanup-audit-logs', '0 2 * * 0', $$
  DELETE FROM audit_logs
  WHERE created_at < NOW() - INTERVAL '1 year';
$$);
```

---

## 5. Monitoramento

### Log de Queries Lentas

```sql
-- Configurar log_min_duration_statement no postgresql.conf
log_min_duration_statement = 1000  -- Log queries > 1 segundo
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

### View para Queries Lentas

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Query para identificar queries lentas
SELECT
    query,
    calls,
    mean_exec_time as avg_time_ms,
    total_exec_time as total_time_ms,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- Queries > 100ms
ORDER BY mean_exec_time DESC
LIMIT 20;
```

---

## 6. Checklist de Implementação

### Semana 1
- [ ] Atualizar docker-compose.yml com novas configurações PostgreSQL
- [ ] Criar migração Alembic para índices críticos
- [ ] Executar migração em staging
- [ ] Verificar query plans com EXPLAIN ANALYZE

### Semana 2
- [ ] Criar migração para índices de busca
- [ ] Configurar pg_cron para manutenção automática
- [ ] Configurar log de queries lentas
- [ ] Testar performance com dados de produção

### Mês 2
- [ ] Implementar particionamento para audit_logs
- [ ] Criar jobs de arquivamento
- [ ] Configurar monitoramento contínuo
- [ ] Documentar processo de manutenção

---

## 7. Comandos Úteis

```bash
# Verificar tamanho das tabelas
psql -d conecta_pro -c "
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
"

# Verificar índices faltantes (heurística)
psql -d conecta_pro -c "
SELECT
    t.tablename,
    indexname,
    c.attname as column
FROM pg_tables t
LEFT JOIN pg_indexes i ON t.tablename = i.tablename
LEFT JOIN pg_constraint con ON con.conrelid = t.tablename::regclass
LEFT JOIN pg_attribute c ON c.attrelid = t.tablename::regclass
WHERE t.schemaname = 'public'
AND con.contype = 'f'  -- Foreign keys
AND NOT EXISTS (
    SELECT 1 FROM pg_indexes pi
    WHERE pi.tablename = t.tablename
    AND pi.indexdef LIKE '%' || c.attname || '%'
)
LIMIT 20;
"

# Cache hit ratio
psql -d conecta_pro -c "
SELECT
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;
"
```

---

**Relatório gerado:** 2026-02-05
**Status:** Aguardando implementação

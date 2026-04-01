# Recomendações de Performance - Fase 3

## 📊 Resumo da Análise

| Métrica | Valor | Status |
|---------|-------|--------|
| Colunas JSONB | 1,220 | ⚠️ |
| Índices GIN em JSONB | 0 | 🔴 |
| Repositórios | 128 | - |
| Com eager loading | 32 | ✅ |
| **Sem eager loading** | **96** | 🔴 |

## 🔴 Problemas Críticos

### 1. Falta de Índices GIN (1220 colunas JSONB)
**Impacto**: Queries em campos JSONB são full table scan
**Solução**: Executar migration `add_gin_indexes_jsonb.py`

```bash
# Executar migration
alembic upgrade +1

# Ou criar índices manualmente (CONCURRENTLY para evitar lock)
CREATE INDEX CONCURRENTLY idx_audit_logs_details_gin
ON audit_logs USING GIN (details);
```

### 2. Repositórios sem Eager Loading (96/128)
**Impacto**: Alto risco de N+1 queries
**Solução**: Adicionar `.options()` nos repositórios

**Exemplo de padrão recomendado:**

```python
# ANTES (problemático)
async def get_employee(self, id: UUID) -> Employee:
    result = await self.session.execute(
        select(Employee).where(Employee.id == id)
    )
    return result.scalar_one()

# DEPOIS (com eager loading)
from sqlalchemy.orm import joinedload, selectinload

async def get_employee(self, id: UUID) -> Employee:
    result = await self.session.execute(
        select(Employee)
        .where(Employee.id == id)
        .options(
            joinedload(Employee.department),
            selectinload(Employee.certificacoes),
        )
    )
    return result.scalar_one()
```

## 🟡 Otimizações Recomendadas

### 3. JSONB Normalization
Colunas JSONB que deveriam ser tabelas separadas:

| Tabela | Campo JSONB | Recomendação |
|--------|-------------|--------------|
| employees | certificacoes | Criar tabela employee_certifications |
| employees | dependentes | Criar tabela employee_dependents |
| diaristas | referencias | Criar tabela diarist_references |
| documentos_fiscais | historico_alteracoes | Criar tabela document_change_log |

### 4. Índices Compostos Sugeridos

```sql
-- Índice para queries de auditoria por data
CREATE INDEX CONCURRENTLY idx_audit_logs_created_at_type
ON audit_logs (created_at, entity_type);

-- Índice para buscas por tenant
CREATE INDEX CONCURRENTLY idx_employees_tenant_active
ON employees (tenant_id, is_active) WHERE is_active = true;

-- Índice para integrações por status
CREATE INDEX CONCURRENTLY idx_integration_queue_status_created
ON integration_sync_queue (status, created_at)
WHERE status IN ('pending', 'failed');
```

## 📋 Checklist de Implementação

- [ ] Executar migration de índices GIN
- [ ] Monitorar performance antes/depois
- [ ] Atualizar 96 repositórios com eager loading
- [ ] Normalizar campos JSONB críticos
- [ ] Criar índices compostos para queries frequentes
- [ ] Configurar alerts para queries lentas (>1s)

## 📊 Queries para Monitoramento

```sql
-- Identificar queries lentas
SELECT query, calls, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Verificar uso de índices
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Tabelas com mais scans sequenciais
SELECT schemaname, relname, seq_scan, seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY seq_scan DESC
LIMIT 10;
```

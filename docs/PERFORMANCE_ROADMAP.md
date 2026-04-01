# 🚀 ROADMAP DE PERFORMANCE - CONECTA PRO v2.0

**Data:** 2026-02-05
**Status:** Pré-deploy
**Objetivo:** Otimizar performance antes do deploy em produção

---

## 📊 Resumo Executivo

| Categoria | Problemas Críticos | Quick Wins | Estimativa de Impacto |
|-----------|-------------------|------------|----------------------|
| Frontend Bundle | 3 | 2 | -23MB (-60% bundle inicial) |
| Queries SQL | 4 N+1, 5 sem LIMIT | 4 índices | -70% latência queries |
| API Endpoints | 15+ sem cache | 8 com cache | -90% tempo dashboard |
| Database | 15+ FKs sem índice | 6 índices | -50% JOIN time |
| Cache Redis | 4 gaps críticos | 3 implementações | -40% consultas PG |

**Total de Otimizações Identificadas:** 40+
**Quick Wins (baixo esforço/alto impacto):** 15

---

## 🎯 FASE 1: QUICK WINS (Pré-Deploy)

### Prioridade 1.1: Frontend - Bundle Size 🔴 CRÍTICO

**Problema:** Bundle inicial carregando 23MB desnecessários

| Ação | Economia | Tempo | Comando |
|------|----------|-------|---------|
| Lazy load XLSX | ~7MB | 30min | Ver abaixo |
| Lazy load shepherd.js | ~2.8MB | 20min | Ver abaixo |
| Otimizar recharts analytics | ~13MB | 45min | Ver abaixo |

**Implementação:**

```typescript
// 1. src/utils/export.ts - Converter XLSX para lazy
export async function exportToExcel(data: any[], filename: string) {
  const XLSX = await import('xlsx');  // Dynamic import
  const ws = XLSX.utils.json_to_sheet(data);
  // ... resto
}

// 2. src/features/onboarding/hooks/useTour.ts
import { useEffect, useState } from 'react';

export function useTour() {
  const [Shepherd, setShepherd] = useState(null);

  useEffect(() => {
    import('shepherd.js').then(mod => setShepherd(mod.default));
  }, []);

  return Shepherd;
}

// 3. src/app/modulos/analytics/page.tsx
import dynamic from 'next/dynamic';

const BarChart = dynamic(() => import('recharts').then(m => ({ default: m.BarChart })), { ssr: false });
const Bar = dynamic(() => import('recharts').then(m => ({ default: m.Bar })), { ssr: false });
// ... outros componentes
```

---

### Prioridade 1.2: Database - Índices Críticos 🔴 CRÍTICO

**Problema:** Foreign keys sem índice causando JOINs lentos

```sql
-- Criar CONCURRENTLY para não bloquear (executar em horário de baixo uso)
CREATE INDEX CONCURRENTLY idx_ged_docs_contract ON ged_documents(contract_id);
CREATE INDEX CONCURRENTLY idx_ged_docs_employee ON ged_documents(employee_id);
CREATE INDEX CONCURRENTLY idx_occ_attach_occurrence ON occurrence_attachments(occurrence_id);
CREATE INDEX CONCURRENTLY idx_occ_comm_occurrence ON occurrence_comments(occurrence_id);
CREATE INDEX CONCURRENTLY idx_leads_source ON leads(source);
CREATE INDEX CONCURRENTLY idx_candidates_status ON candidates(status);
```

**Migração Alembic:**

```python
# backend/alembic/versions/xxx_add_performance_indexes.py
from alembic import op

def upgrade():
    # Índices críticos
    op.create_index('idx_ged_docs_contract', 'ged_documents', ['contract_id'])
    op.create_index('idx_ged_docs_employee', 'ged_documents', ['employee_id'])
    op.create_index('idx_occ_attach_occurrence', 'occurrence_attachments', ['occurrence_id'])
    op.create_index('idx_leads_source', 'leads', ['source'])
    op.create_index('idx_candidates_status', 'candidates', ['status'])

    # Índices compostos
    op.create_index('idx_shifts_employee_date', 'shifts', ['employee_id', 'shift_date'])
    op.create_index('idx_occurrences_employee_date', 'occurrences', ['employee_id', 'occurred_at'])

def downgrade():
    op.drop_index('idx_ged_docs_contract')
    op.drop_index('idx_ged_docs_employee')
    # ... etc
```

---

### Prioridade 1.3: API - Cache em Dashboards 🔴 CRÍTICO

**Problema:** Dashboards consultam banco a cada request

```python
# modules/operacional/controllers/dashboard_controller.py

from core.cache import cache_response

class DashboardController:

    @cache_response(ttl=60, prefix="api:dashboard:main")  # 1 minuto
    async def get_dashboard(self, ...):
        # Dados que mudam frequentemente
        ...

    @cache_response(ttl=300, prefix="api:dashboard:kpis")  # 5 minutos
    async def get_kpis(self, ...):
        # KPIs mais estáveis
        ...

# modules/config/controllers/config_controller.py

@cache_response(ttl=3600, prefix="api:config:system")  # 1 hora
async def get_system_config(...):
    # Configurações raramente mudam
    ...

@cache_response(ttl=86400, prefix="api:config:flags")  # 24 horas
async def get_feature_flags(...):
    # Feature flags por tenant
    ...
```

---

### Prioridade 1.4: Backend - Correções N+1 🟡 ALTA

**Problema:** Loop com query interna em integration_service

```python
# modules/operacional/services/integration_service.py

# ANTES (N+1):
for diarista in diaristas_disponiveis:
    conflito = self.db.query(DiaristSchedule).filter(...)

# DEPOIS (Otimizado):
# Pré-carregar todos os schedules
diarista_ids = [d.id for d in diaristas_disponiveis]
schedules = await self.db.query(DiaristSchedule).filter(
    DiaristSchedule.diarist_id.in_(diarista_ids),
    DiaristSchedule.schedule_date == data
).all()

# Criar mapa para acesso O(1)
schedule_map = {s.diarist_id: s for s in schedules}

for diarista in diaristas_disponiveis:
    conflito = schedule_map.get(diarista.id)  # O(1)
```

---

## 🎯 FASE 2: MÉDIO PRAZO (Primeiras 2 semanas pós-deploy)

### Prioridade 2.1: Operações Async/Celery

**Endpoints que devem usar Celery:**

| Endpoint | Operação | Task Celery |
|----------|----------|-------------|
| `POST /api/v1/financial/fiscal/nfe/{id}/emitir` | Emissão NF-e | `tasks.fiscal.emitir_nfe` |
| `POST /api/v1/financial/fiscal/nfse/{id}/emitir` | Emissão NFSe | `tasks.fiscal.emitir_nfse` |
| `POST /api/v1/operacional/reports/*/export` | Export Excel/PDF | `tasks.reports.generate_export` |
| `POST /api/v1/communication/announcements` | Envio email massa | `tasks.communication.send_bulk` |

**Exemplo de implementação:**

```python
# modules/fiscal/controllers/nfe_controller.py

from celery_app import celery_app

@router.post("/nfe/{id}/emitir")
async def emitir_nfe(
    id: UUID,
    background: BackgroundTasks,  # Opcional para pequenas operações
    current_user: CurrentUser = Depends(get_current_user)
):
    # Para operações longas (API externa SEFAZ)
    task = celery_app.send_task(
        'tasks.fiscal.emitir_nfe',
        args=[str(id), str(current_user.id)],
        queue='fiscal'
    )

    return {
        "message": "Emissão iniciada",
        "task_id": task.id,
        "status_url": f"/api/v1/tasks/{task.id}/status"
    }

# tasks/fiscal_tasks.py

@celery_app.task(bind=True, max_retries=3)
def emitir_nfe(self, nfe_id: str, user_id: str):
    try:
        # Operação longa com API externa
        result = nfe_service.emitir(nfe_id)
        return {"status": "success", "nfe": result}
    except Exception as exc:
        # Retry com backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

### Prioridade 2.2: Cache de Dados de Referência

```python
# core/cache/reference_data.py

from functools import wraps
from core.cache.redis import cache_get, cache_set

class ReferenceDataCache:
    """Cache para dados de referência (UF, cidades, etc.)"""

    @staticmethod
    async def get_estados() -> List[EstadoSchema]:
        cache_key = "ref:estados"

        # Tentar cache
        cached = await cache_get(cache_key)
        if cached:
            return [EstadoSchema(**e) for e in cached]

        # Buscar do banco
        estados = await repository.get_all_estados()

        # Salvar no cache (24h)
        await cache_set(
            cache_key,
            [e.model_dump() for e in estados],
            ttl=86400
        )

        return estados

    @staticmethod
    async def invalidate_estados():
        """Invalidar quando houver mudança (raro)."""
        await cache_delete("ref:estados")

# Uso em controllers
@router.get("/estados")
async def list_estados():
    return await ReferenceDataCache.get_estados()
```

---

### Prioridade 2.3: PostgreSQL Configurações

```yaml
# docker-compose.yml - Adicionar

postgres:
  image: postgres:16-alpine
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
    -c log_min_duration_statement=1000  # Log queries > 1s
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
```

---

## 🎯 FASE 3: LONGO PRAZO (1-3 meses)

### Prioridade 3.1: Particionamento de Tabelas Grandes

```sql
-- Tabela audit_logs particionada por mês
CREATE TABLE audit_logs (
    id UUID,
    action VARCHAR(50),
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Criar partições
CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

### Prioridade 3.2: Materialized Views para Dashboards

```sql
-- View materializada para KPIs do operacional
CREATE MATERIALIZED VIEW mv_operacional_kpis AS
SELECT
    client_id,
    DATE_TRUNC('month', shift_date) as month,
    COUNT(*) as total_shifts,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_shifts,
    AVG(EXTRACT(EPOCH FROM (actual_end - actual_start))/3600) as avg_hours
FROM shifts
GROUP BY client_id, DATE_TRUNC('month', shift_date);

-- Índice na view materializada
CREATE INDEX idx_mv_kpis_client_month ON mv_operacional_kpis(client_id, month);

-- Refresh periódico
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_operacional_kpis;
```

### Prioridade 3.3: Monitoramento Contínuo

```python
# core/monitoring/performance.py

from prometheus_client import Histogram, Counter

# Métricas de performance
query_duration = Histogram(
    'db_query_duration_seconds',
    'Duration of database queries',
    ['query_type', 'table']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

# Decorator para monitorar queries
@monitor_query(table="shifts")
async def get_shifts(...):
    ...
```

---

## 📈 Estimativas de Impacto

| Otimização | Redução Latência | Economia Recursos | UX |
|------------|-----------------|-------------------|-----|
| Lazy load XLSX | - | -7MB bundle | ⭐⭐⭐ Carregamento mais rápido |
| Índices FK | -70% JOINs | -30% CPU DB | ⭐⭐⭐ Queries instantâneas |
| Cache Dashboard | -90% | -50% queries | ⭐⭐⭐⭐⭐ Dashboard instantâneo |
| Correção N+1 | -95% | -80% queries | ⭐⭐⭐⭐⭐ Lista carrega em 100ms |
| Celery NF-e | - | Timeout eliminado | ⭐⭐⭐⭐ Usuário não espera SEFAZ |
| Cache Configs | -98% (50ms→2ms) | -1000 queries/h | ⭐⭐⭐ Resposta imediata |

---

## ✅ Checklist de Implementação

### Semana 1 (Pré-Deploy)
- [ ] 1.1.1 Lazy load XLSX
- [ ] 1.1.2 Lazy load shepherd.js
- [ ] 1.1.3 Otimizar recharts analytics
- [ ] 1.2.1 Criar índices críticos (migração Alembic)
- [ ] 1.2.2 Executar migração em staging
- [ ] 1.3.1 Adicionar @cache_response em dashboards
- [ ] 1.3.2 Adicionar cache em configurações
- [ ] 1.4.1 Corrigir N+1 em integration_service

### Semana 2-3 (Pós-Deploy)
- [ ] 2.1.1 Implementar tasks Celery para NF-e/NFSe
- [ ] 2.1.2 Implementar tasks para exportações
- [ ] 2.2.1 Criar ReferenceDataCache
- [ ] 2.2.2 Cachear estados/cidades
- [ ] 2.3.1 Atualizar docker-compose.yml com configurações PostgreSQL
- [ ] 2.3.2 Configurar log de queries lentas

### Mês 2-3
- [ ] 3.1.1 Implementar particionamento audit_logs
- [ ] 3.1.2 Criar job de arquivamento
- [ ] 3.2.1 Criar materialized views para KPIs
- [ ] 3.2.2 Configurar refresh automático
- [ ] 3.3.1 Implementar métricas Prometheus
- [ ] 3.3.2 Configurar alertas

---

## 🚨 Alertas e Monitoramento

### Queries Lentas (log_min_duration_statement = 1000ms)
```sql
-- Verificar queries lentas
SELECT
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Cache Hit Ratio
```bash
# Redis
redis-cli info stats | grep keyspace

# PostgreSQL cache
SELECT
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;
```

---

## 📝 Referências

- **Bundle Analysis:** `docs/PERFORMANCE_BUNDLE.md`
- **Queries SQL:** `docs/PERFORMANCE_QUERIES.md`
- **API Endpoints:** `docs/PERFORMANCE_API.md`
- **Database:** `docs/PERFORMANCE_DATABASE.md`
- **Cache Redis:** `docs/PERFORMANCE_CACHE.md`

---

**Próximo Passo:** Iniciar FASE 1 - Quick Wins
**Responsável:** DevOps + Backend + Frontend
**Revisão:** Semanal até conclusão da FASE 1

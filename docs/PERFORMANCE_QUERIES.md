# 📊 RELATÓRIO DE ANÁLISE DE QUERIES SQL

**Projeto:** Conecta PRO (Backend FastAPI + SQLAlchemy)
**Diretório:** `/opt/conecta-pro/backend/`
**Data:** 2026-02-05

---

## 🔴 Queries N+1 Encontradas

### 1. `modules/operacional/services/integration_service.py:595-597` 🔴 CRÍTICO

**Código problemático:**
```python
for diarista in diaristas_disponiveis:
    # Verificar se não tem schedule na data
    conflito = self.db.query(DiaristSchedule).filter(
        DiaristSchedule.diarist_id == diarista.id,
        DiaristSchedule.schedule_date == data,
        DiaristSchedule.status.in_(['scheduled', 'confirmed'])
    ).first()
```

**Problema:** Para cada diarista (potencialmente 100+), faz uma query ao banco.

**Impacto:** 100 diaristas = 100 queries extras.

**Solução:**
```python
# Pré-carregar todos os schedules de uma vez
diarista_ids = [d.id for d in diaristas_disponiveis]

schedules_result = await self.db.execute(
    select(DiaristSchedule).where(
        DiaristSchedule.diarist_id.in_(diarista_ids),
        DiaristSchedule.schedule_date == data,
        DiaristSchedule.status.in_(['scheduled', 'confirmed'])
    )
)

# Criar set para lookup O(1)
scheduled_diarista_ids = {
    s.diarist_id for s in schedules_result.scalars().all()
}

# Verificar no loop sem query
for diarista in diaristas_disponiveis:
    conflito = diarista.id in scheduled_diarista_ids
    # ...
```

**Economia:** De N queries para 1 query.

---

### 2. `modules/operacional/occurrences/services/occurrence_ai_analyzer.py:456-458` 🟡 MÉDIO

**Código problemático:**
```python
for keyword in keywords[:3]:
    filters = OccurrenceFilter(search=keyword)
    occurrences, _ = self.repository.list_by_tenant(
        db=db,
        tenant_id=tenant_id,
        filters=filters,
        limit=10
    )
```

**Problema:** 3 queries em loop (uma por keyword).

**Solução:**
```python
# Consolidar em uma query com OR
from sqlalchemy import or_

filters = OccurrenceFilter(
    search=None,
    search_keywords=keywords[:3]  # Novo campo para múltiplas keywords
)

# No repository:
if filters.search_keywords:
    conditions = [
        Occurrence.description.ilike(f'%{kw}%')
        for kw in filters.search_keywords
    ]
    query = query.where(or_(*conditions))
```

---

## 🟡 Queries Sem Paginação (Potencial Problema)

### 1. `modules/operacional/controllers/dashboard_controller.py:511-522` 🔴 CRÍTICO

**Código:**
```python
escalas = db.query(Scale).filter(
    Scale.status == ScaleStatus.IN_PROGRESS,
    Scale.ativo == True
).count()

ocorrencias = db.query(Occurrence).filter(
    Occurrence.data_ocorrencia >= primeiro_dia_mes,
    Occurrence.data_ocorrencia <= data_ref
).count()
```

**Problema:** Contagens sem filtros de tenant podem escalar indefinidamente.

**Solução:**
```python
# Adicionar filtro de tenant sempre
escalas = db.query(Scale).filter(
    Scale.client_id == current_user.client_id,  # Tenant isolation
    Scale.status == ScaleStatus.IN_PROGRESS,
    Scale.ativo == True
).count()

# E adicionar índice composto
# CREATE INDEX idx_scales_client_status ON scales(client_id, status) WHERE ativo = true;
```

---

### 2. `modules/operacional/services/notification_triggers.py:81-94` 🔴 CRÍTICO

**Código:**
```python
late_shifts = (
    self.db.query(Shift, Employee, Post)
    .join(Scale, Shift.scale_id == Scale.id)
    .join(Post, Shift.post_id == Post.id)
    .join(Employee, Shift.employee_id == Employee.id)
    .filter(
        Shift.shift_date == today,
        Shift.status == 'scheduled',
        Shift.planned_start_time < current_time,
        Shift.actual_start_time.is_(None)
    )
    .all()  # <-- Sem LIMIT!
)
```

**Problema:** JOIN de 4 tabelas sem limit pode retornar milhares de registros.

**Solução:**
```python
late_shifts = (
    self.db.query(Shift, Employee, Post)
    .join(Scale, Shift.scale_id == Scale.id)
    .join(Post, Shift.post_id == Post.id)
    .join(Employee, Shift.employee_id == Employee.id)
    .filter(
        Shift.shift_date == today,
        Shift.status == 'scheduled',
        Shift.planned_start_time < current_time,
        Shift.actual_start_time.is_(None)
    )
    .limit(1000)  # Limite de segurança
    .all()
)

# Processar em batches se necessário
for shift_batch in chunks(late_shifts, 100):
    await process_batch(shift_batch)
```

---

### 3. `modules/operacional/controllers/kpi_trends_controller.py:81-108` 🟡 MÉDIO

**Código:**
```python
total_posts = db.query(func.count(Post.id)).scalar()
total_employees = db.query(func.count(Employee.id)).scalar()
total_scales = db.query(func.count(Scale.id)).scalar()
total_occurrences = db.query(func.count(Occurrence.id)).scalar()
```

**Problema:** Contagens globais sem filtros de tenant.

**Solução:**
```python
# Todas as queries devem ter tenant_id
total_posts = db.query(func.count(Post.id)).filter(
    Post.client_id == current_user.client_id
).scalar()
```

---

## 🔵 Subqueries Problemáticas

### 1. `modules/operacional/diaristas/repositories/diarist_repository.py:150-160` 🟡 MÉDIO

**Código:**
```python
subquery = (
    select(DiaristSchedule.diarist_id)
    .where(
        DiaristSchedule.schedule_date == date,
        DiaristSchedule.status.in_(['scheduled', 'confirmed'])
    )
)
query = query.where(~Diarist.id.in_(subquery))
```

**Problema:** `NOT IN` com subquery pode ser ineficiente.

**Solução:**
```python
# Usar NOT EXISTS (geralmente mais eficiente)
from sqlalchemy import exists

subquery = (
    select(DiaristSchedule)
    .where(
        DiaristSchedule.diarist_id == Diarist.id,
        DiaristSchedule.schedule_date == date,
        DiaristSchedule.status.in_(['scheduled', 'confirmed'])
    )
)
query = query.where(~exists(subquery))
```

---

## 🟢 Boas Práticas Encontradas

### ✅ Uso Correto de Eager Loading

**Arquivo:** `modules/operacional/diaristas/repositories/diarist_repository.py`

```python
from sqlalchemy.orm import joinedload

query = query.options(
    joinedload(DiaristAssignment.diarist)
)
```

**Benefício:** Evita N+1 em relacionamentos.

---

### ✅ Paginação Implementada

**Arquivo:** `modules/operacional/repositories/allocation_repository.py:263`

```python
query = query.offset((page - 1) * page_size).limit(page_size)
```

---

### ✅ Uso de IN em vez de N+1

**Arquivo:** `modules/operacional/repositories/allocation_repository.py:295-306`

```python
# Buscar todos de uma vez
emp_result = await self.db.execute(
    select(Employee).where(Employee.id.in_(employee_ids))
)
```

---

## 📊 Índices Sugeridos

### Tabela `shifts` - Índices Críticos

```sql
-- Para queries de turnos atrasados (notification_triggers.py)
CREATE INDEX idx_shifts_date_status_planned
ON shifts(shift_date, status, planned_start_time)
WHERE status = 'scheduled';

-- Para filtros por funcionário e data
CREATE INDEX idx_shifts_employee_date
ON shifts(employee_id, shift_date);

-- Para joins com scales
CREATE INDEX idx_shifts_scale_id_status
ON shifts(scale_id, status);

-- Índice composto para dashboard
CREATE INDEX idx_shifts_dashboard
ON shifts(client_id, shift_date, status)
WHERE ativo = true;
```

### Tabela `diarist_schedules`

```sql
-- Para verificação de conflitos (integration_service.py)
CREATE INDEX idx_diarist_schedules_lookup
ON diarist_schedules(diarist_id, schedule_date, status);

-- Para range queries
CREATE INDEX idx_diarist_schedules_date_range
ON diarist_schedules(schedule_date, start_time, end_time);
```

### Tabela `occurrences`

```sql
-- Para queries por data (dashboard_controller.py)
CREATE INDEX idx_occurrences_date_client
ON occurrences(data_ocorrencia, client_id);

-- Para queries por posto
CREATE INDEX idx_occurrences_post_date
ON occurrences(post_id, data_ocorrencia);

-- Para filtros de status
CREATE INDEX idx_occurrences_status_date
ON occurrences(status, occurred_at)
WHERE is_active = true;
```

### Tabela `scales`

```sql
-- Para filtros de dashboard
CREATE INDEX idx_scales_status_year_month
ON scales(status, year, month, client_id);

-- Para lookups por cliente
CREATE INDEX idx_scales_client_status
ON scales(client_id, status)
WHERE ativo = true;
```

### Tabela `posts`

```sql
-- Para queries por cliente e status
CREATE INDEX idx_posts_client_status
ON posts(client_id, status)
WHERE status = 'active';
```

---

## 🎯 Prioridades de Otimização

### Alta Prioridade (Esta semana)

| # | Problema | Solução | Impacto |
|---|----------|---------|---------|
| 1 | N+1 em integration_service.py | Pré-carregar schedules | -95% queries |
| 2 | LIMIT em notification_triggers.py | Adicionar .limit(1000) | Previne OOM |
| 3 | Tenant isolation em KPIs | Adicionar filtros | Segurança + perf |
| 4 | Índice idx_shifts_date_status_planned | CREATE INDEX | -70% tempo |

### Média Prioridade (Próximo mês)

| # | Problema | Solução | Impacto |
|---|----------|---------|---------|
| 5 | NOT IN → NOT EXISTS | Refatorar subqueries | -20% tempo |
| 6 | Índices em diarist_schedules | CREATE INDEX | -50% tempo |
| 7 | Paginação em todos os .all() | Adicionar LIMIT | Previne problemas |

---

## 📈 Impacto Estimado

| Otimização | Redução de Tempo | Complexidade |
|------------|------------------|--------------|
| Correção N+1 diaristas | 80-95% | Média |
| LIMIT em notificações | 50-70% | Baixa |
| Índice em shifts | 70-90% | Baixa |
| NOT EXISTS vs NOT IN | 20-40% | Média |
| Índices compostos | 30-60% | Baixa |

---

## ✅ Checklist de Implementação

### Correções de Código
- [ ] Corrigir N+1 em `integration_service.py:595`
- [ ] Adicionar LIMIT em `notification_triggers.py:94`
- [ ] Adicionar tenant filter em `kpi_trends_controller.py`
- [ ] Refatorar NOT IN para NOT EXISTS

### Índices (Migração Alembic)
- [ ] `idx_shifts_date_status_planned`
- [ ] `idx_shifts_employee_date`
- [ ] `idx_diarist_schedules_lookup`
- [ ] `idx_occurrences_date_client`
- [ ] `idx_scales_status_year_month`

### Validação
- [ ] Executar queries com EXPLAIN ANALYZE
- [ ] Verificar query plans otimizados
- [ ] Testar carga com dados reais

---

**Relatório gerado:** 2026-02-05
**Status:** Aguardando implementação

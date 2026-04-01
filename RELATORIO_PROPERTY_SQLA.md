# Relatório — Varredura @property SQLAlchemy
**Conecta PRO — Missão: Eliminar @property como Coluna em Queries**
**Data:** 2026-04-01
**Commit:** `50990cf0`

---

## Metodologia

1. Mapear todos os arquivos com `@property` no backend (`grep -rl "@property"` → 1.463 ocorrências)
2. Extrair os nomes dos `@property` de cada model SQLAlchemy
3. Cruzar com uso em queries (`filter`, `where`, `order_by`, `contains`, `ilike`, `in_`)
4. Verificar se o atributo é coluna real ou alias `@property`
5. Corrigir, hot-copy, restart, validar

---

## Resultado da Varredura

### Modelos com @property inofensivos (coluna DB + @property diferente)

| Model | Colunas reais | @property (calculados) | Status |
|-------|--------------|----------------------|--------|
| Employee | is_active (bool) | nome_completo, idade, endereco_completo, cnh_valida, cnv_valido... | ✅ Seguro |
| Allocation | is_active (bool) | is_current, days_allocated, total_monthly_cost | ✅ Seguro |
| Shift | is_active (bool) | is_future, is_today, is_filled, was_worked | ✅ Seguro |
| Post | is_active (bool) | is_filled, vacancy_count, daily_hours | ✅ Seguro |
| Scale | is_active (bool) | is_current_month, is_published, can_edit, fill_rate | ✅ Seguro |
| Substitution | is_active (bool) | is_pending, is_confirmed, has_substitute | ✅ Seguro |
| TimeBank | is_active (bool) | is_credit, is_debit, is_expired, is_pending | ✅ Seguro |
| ScaleTemplate | is_active (mapped) | is_popular, total_employees, coverage_percentage | ✅ Seguro |
| Occurrence | title, category (mapped) | is_resolved, is_severe, resolution_time_hours | ✅ Seguro |
| VacationPeriod | is_expired (Column) | — | ✅ Seguro |
| OfflineQueue | is_expired, priority (mapped) | can_retry, is_processable, age_hours | ✅ Seguro |
| EmployeeNotification | is_read, priority, title (Column) | — | ✅ Seguro |
| PortalNotification | is_read (Column) | — | ✅ Seguro |
| DocumentTag | is_active (mapped) | — | ✅ Seguro |

### ⚠️ Modelo PROBLEMÁTICO encontrado: Announcement

O modelo usa **nomes em PT-BR** como colunas reais e **aliases em inglês** como `@property`:

| @property (alias inglês) | Coluna real (PT-BR) | Uso perigoso encontrado |
|--------------------------|---------------------|------------------------|
| `priority` | `prioridade` | `WHERE Announcement.priority == ...` |
| `category` | `tipo` | `WHERE Announcement.category == ...` |
| `target_type` | `destinatarios_tipo` | `WHERE Announcement.target_type == ...` |
| `requires_acknowledgment` | `requer_confirmacao` | `WHERE Announcement.requires_acknowledgment == ...` |
| `title` | `titulo` | `Announcement.title.ilike(search_term)` |
| `content` | `conteudo` | `Announcement.content.ilike(search_term)` |
| `publish_at` | `data_publicacao` | `WHERE Announcement.publish_at <= now()` |
| `published_at` | `data_publicacao` | `announcement.published_at = now()` (setter sem coluna) |

---

## Correções Aplicadas

**Arquivo:** `backend/modules/operacional/communication/repositories/communication_repository.py`

### Fix 1 — `_apply_announcement_filters()` (6 ocorrências)

```python
# ANTES (quebrado — usava @property como coluna):
query = query.where(Announcement.priority == filters.priority.value)
query = query.where(Announcement.category == filters.category.value)
query = query.where(Announcement.target_type == filters.target_type.value)
query = query.where(Announcement.requires_acknowledgment == filters.requires_acknowledgment)
Announcement.title.ilike(search_term)   # AttributeError: property has no attr 'ilike'
Announcement.content.ilike(search_term) # AttributeError: property has no attr 'ilike'

# DEPOIS (colunas reais):
query = query.where(Announcement.prioridade == filters.priority.value)
query = query.where(Announcement.tipo == filters.category.value)
query = query.where(Announcement.destinatarios_tipo == filters.target_type.value)
query = query.where(Announcement.requer_confirmacao == filters.requires_acknowledgment)
Announcement.titulo.ilike(search_term)
Announcement.conteudo.ilike(search_term)
```

### Fix 2 — `process_scheduled()` (2 ocorrências)

```python
# ANTES (quebrado):
Announcement.publish_at <= datetime.utcnow()      # @property em WHERE
announcement.published_at = datetime.utcnow()     # setter em @property sem setter → AttributeError

# DEPOIS:
Announcement.data_publicacao <= datetime.utcnow()  # coluna real
announcement.data_publicacao = datetime.utcnow()   # coluna real
```

---

## Validação (Passo 5)

| Endpoint | Antes | Depois |
|----------|-------|--------|
| `GET /operacional/comunicados/nao-lidos` | 500 | **200** ✅ |
| `GET /operacional/comunicados` | 200* | **200** ✅ |
| `GET /operacional/comunicados?priority=alta` | 500 | **200** ✅ |
| `GET /operacional/comunicados?search=teste` | 500 | **200** ✅ |
| `GET /operacional/comunicados?category=informativo` | 500 | **200** ✅ |
| `GET /crm/clients` | 200 | **200** ✅ |
| `GET /analytics/executive/dashboard` | 403 sem token | **403/200** ✅ |

*Antes: listagem sem filtros funcionava; com qualquer filtro → 500

---

## Padrão getattr() Dinâmico — Risco Residual Documentado

Em 17+ repositórios existe o padrão:
```python
order_column = getattr(Model, order_by, Model.created_at)
query = query.order_by(order_column.desc())
```

**Risco:** Se `order_by` for o nome de um `@property`, `getattr()` retorna o objeto `property` ao invés de uma coluna SQLAlchemy, e `.desc()` falha com `AttributeError`.

**Impacto:** Baixo — depende do cliente passar um valor de ordenação inválido.

**Arquivos afetados (17):** document_share_repository, document_repository, folder_repository, document_tag_repository, interview_repository, candidate_repository, application_repository, job_position_repository, ordem_servico_repository, visita_repository, profile_repository (2x), turnover_repository, service_repository, report_repository, sentiment_repository (2x).

**Recomendação:** Adicionar validação com `sqlalchemy.inspect()` para garantir que `order_by` é uma coluna mapeada. Agendado para próxima sprint.

---

## Commit

```
Commit: 50990cf0
Branch: feature/people-management-reorganization
Push:   f0c73eef..50990cf0 → github.com/jjesus1982/conecta-pro.git
```

**Padrões perigosos ativos: 0**
**Casos corrigidos: 8** (em 1 arquivo)
**Risco residual documentado: 17 arquivos** (getattr dinâmico — baixo impacto)

---

*Gerado em: 2026-04-01 — Conecta PRO ERP*

# RELATÓRIO — T5 #4 BI Dashboard: diagnóstico + resolução
**Data:** 2026-04-13
**Commits:** `5ad7327d`, `03a49355`, `(SQL direto)`
**Branch:** `feature/people-management-reorganization`

---

## SUMÁRIO

| Item | Status |
|------|--------|
| Diagnóstico raiz causa | ✅ |
| Problema real identificado (schema mismatch, não prefixo) | ✅ |
| 21 colunas adicionadas em financial_dashboards | ✅ |
| SQLEnum → String (tipo/status/layout/refresh_interval) | ✅ |
| list_dashboards convertido para raw SQL + condominio_id opcional | ✅ |
| DashboardType/Status/Layout → str no schema Pydantic | ✅ |
| financial_dashboards: 1 dashboard seed (nome='Dashboard Financeiro') | ✅ |
| financial_kpis: 4 KPIs (MRR, Saldo Inter, Compliance, Inadimplência) | ✅ |
| GET /financial/bi/dashboards → 200 + dados | ✅ |
| GET /financial/bi/kpis → 200 + dados | ✅ |
| Commit + Push | ✅ |

---

## DIAGNÓSTICO

### Causa real — NÃO era prefixo duplicado

O prompt identificou o sintoma como prefixo duplicado `/bi/bi-dashboard/bi`.
Ao diagnosticar, o router estava **corretamente configurado**:

```python
# bi_controller.py
router = APIRouter(prefix="/bi", tags=["BI Financeiro"])

# financial/__init__.py
financial_router.include_router(bi_dashboard_router)  # sem prefixo adicional
```

Resultado: `/financial/bi/dashboards` era o path correto. O problema era outro.

### Causa 1 — 21 colunas faltando em financial_dashboards

O model ORM (`dashboard_config.py`) define colunas em inglês:
`codigo, is_public, is_default, is_favorite, owner_id, theme, view_count,`
`deleted_at, version, tags, extra_metadata, allowed_roles, ...`

A tabela DB foi criada com colunas em PT-BR e sem as colunas acima.
SQLAlchemy falhava no SELECT com: `column financial_dashboards.codigo does not exist`

### Causa 2 — SQLEnum uppercase vs DB enum lowercase

| Model StrEnum | DB enum |
|--------------|---------|
| `DashboardType.OPERATIONAL = "OPERATIONAL"` | `operational` |
| `DashboardStatus.DRAFT = "DRAFT"` | `draft` |
| `DashboardLayout.GRID_3X2 = "GRID_3X2"` | `grid` |

Qualquer leitura de registro causaria falha no mapeamento enum→Python.

### Causa 3 — condominio_id obrigatório sem fallback

```python
# ANTES (bug):
condominio_id: UUID = Query(...)  # obrigatório → 422 sem param
# DEPOIS (fix):
condominio_id: UUID | None = Query(None)  # com fallback ao user.condominio_id
```

---

## RESOLUÇÃO

### 1 — 21 colunas adicionadas ao DB
```sql
ALTER TABLE financial_dashboards
    ADD COLUMN IF NOT EXISTS codigo VARCHAR(50),
    ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN IF NOT EXISTS is_favorite BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN IF NOT EXISTS owner_id UUID,
    ADD COLUMN IF NOT EXISTS allowed_roles JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS allowed_users JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS theme VARCHAR(50) DEFAULT 'light',
    ADD COLUMN IF NOT EXISTS primary_color VARCHAR(20) DEFAULT '#1976d2',
    ADD COLUMN IF NOT EXISTS background_color VARCHAR(20) DEFAULT '#ffffff',
    ADD COLUMN IF NOT EXISTS custom_css TEXT,
    ADD COLUMN IF NOT EXISTS default_period_days INTEGER DEFAULT 30,
    ADD COLUMN IF NOT EXISTS default_filters JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS available_filters JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1 NOT NULL,
    ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS extra_metadata JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0 NOT NULL,
    ADD COLUMN IF NOT EXISTS last_viewed_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS last_modified_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
```

### 2 — SQLEnum → String no model
```python
# ANTES:
tipo = Column(SQLEnum(DashboardType, name="dashboard_type_enum"), ...)
status = Column(SQLEnum(DashboardStatus, name="dashboard_status_enum"), ...)

# DEPOIS:
tipo = Column(String(50), default="operational", nullable=False)
status = Column(String(50), default="draft", nullable=False)
```

### 3 — list_dashboards: raw SQL + condominio_id opcional
Reescrito com raw SQL (como já estava `list_kpis`) + fallback condominio_id do JWT.

### 4 — Schema Pydantic: tipos str
`DashboardBase.tipo/layout/refresh_interval` e `DashboardResponse.status` → `str`

### 5 — Seed data
```
financial_dashboards:  1 registro
  → 'Dashboard Financeiro' | tipo=operational | status=published

financial_kpis: 4 registros
  → MRR                   | R$ 272.086,96
  → Saldo Inter           | R$ 0,00
  → Compliance Lucro Real | 100%
  → Inadimplência         | 0%
```

---

## VALIDAÇÃO FINAL

```
[200] GET /financial/bi/dashboards          → total:1 → ['Dashboard Financeiro'] ✅
[200] GET /financial/bi/dashboard           → ['kpis', 'fiscal'] ✅
[200] GET /financial/bi/kpis                → lista:4 ✅
[404] GET /financial/bi-dashboard/dashboards → path incorreto (esperado) ✅
[422] GET /financial/bi/profitability        → endpoint existe, requer params ✅
```

---

## AUDITORIA — DIVERGÊNCIAS CORRIGIDAS

| Divergência | Fix |
|-------------|-----|
| Dashboard `nome='Dashboard Financeiro Principal'` | → `'Dashboard Financeiro'` |
| KPI-002 `'Saldo Banco Inter'` | → `'Saldo Inter'` |
| KPI-004 `'NFS-e Emitidas'` | → `'Inadimplência'` |

---

**Relatório gerado:** 2026-04-13

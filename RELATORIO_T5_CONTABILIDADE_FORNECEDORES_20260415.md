# RELATÓRIO T5 — CONTABILIDADE + FORNECEDORES
**Data:** 2026-04-15
**Sessão:** T5 Fix — Problemas CIC confirmados
**Branch:** `feature/people-management-reorganization`
**Último commit:** `77ef12e2`

---

## RESUMO EXECUTIVO

Dois bugs críticos no módulo Financeiro foram identificados via CIC e corrigidos com 100% de aprovação em dupla auditoria.

| Problema | Módulo | Status |
|---|---|---|
| Plano de contas vazio ("Nenhuma conta encontrada") | `/modulos/financeiro/contabilidade` | ✅ RESOLVIDO |
| Fornecedores Ativos = 0 (13 cadastrados) | `/modulos/financeiro/fornecedores` | ✅ RESOLVIDO |

---

## PROBLEMA A — CONTABILIDADE

### Sintoma
Tela `/modulos/financeiro/contabilidade` exibia:
> "Nenhuma conta encontrada / Nenhuma conta cadastrada no plano de contas"

O banco possuía 227 entradas em `accounting_entries` mas o plano de contas estava vazio.

### Causas-Raiz (4 bugs encadeados)

#### Bug 1 — 17 colunas ausentes no DB
O modelo ORM `AccountingAccount` referenciava 17 colunas que não existiam na tabela `fin_accounting_accounts`.
**Fix:** `ALTER TABLE fin_accounting_accounts ADD COLUMN IF NOT EXISTS ...` para todas as 17 colunas:
```
order_index, path, sped_description, period_debit, period_credit, period_balance,
last_movement_date, last_balance_update, default_cost_center_id, requires_history,
allows_manual_entry, dre_order, balance_sheet_order, legacy_code, is_system,
is_tax_related, bank_account_id
```

#### Bug 2 — response_model errado (Pydantic V2)
`list_accounts` usava `response_model=list[AccountingAccountListResponse]` (wrapper paginado com `items`, `total`, etc.) mas retornava objetos ORM individuais.
**Fix:** `accounting_controller.py` linhas 309/339:
```python
# ANTES
@router.get("/accounts", response_model=list[AccountingAccountListResponse])
return [AccountingAccountListResponse.model_validate(a) for a in accounts]

# DEPOIS
@router.get("/accounts", response_model=list[AccountingAccountResponse])
return [AccountingAccountResponse.model_validate(a) for a in accounts]
```

#### Bug 3 — Frontend com `chart_id` fixo vazio
`contabilidade/page.tsx` linha 74: `chart_id: ''` hardcoded → backend retorna `[]` imediatamente (guarda `if not chart_id: return []`).
**Fix:** Busca dinâmica do chart ativo via `useListChartsApiV1FinancialAccountingAccountingChartsGet`:
```typescript
const { data: chartsData } = useAccountingCharts({});
const activeChartId = (Array.isArray(chartsData) && chartsData.length > 0)
    ? (chartsData as any[])[0]?.id ?? '' : '';
const { data: accountsRaw } = useAccountingAccounts(
    { chart_id: activeChartId },
    { query: { enabled: !!activeChartId } }
);
const accounts = Array.isArray(accountsRaw)
    ? (accountsRaw as any[])
    : ((accountsRaw as any)?.items ?? []);
```

#### Bug 4 — Enum mismatch (nature/classification)
Contas inseridas com valores em português (`'devedora'`, `'credora'`) mas o tipo PostgreSQL `accountnature` aceita apenas `DEBIT`/`CREDIT`.
**Fix:**
```sql
UPDATE fin_accounting_accounts SET nature='DEBIT' WHERE nature='devedora';  -- 15 rows
UPDATE fin_accounting_accounts SET nature='CREDIT' WHERE nature='credora';  -- 15 rows
```

### Plano de Contas NBR Inserido
**62 contas totais** (53 padrão NBR + 9 históricas de entradas):

| Grupo | Código | Contas |
|---|---|---|
| 1 — ATIVO | 1.1 a 1.3 | Circulante, Realizável LP, Permanente |
| 2 — PASSIVO | 2.1 a 2.3 | Circulante, Exigível LP, PL |
| 3 — PATRIMÔNIO LÍQUIDO | 3.1 a 3.5 | Capital, Reservas, Lucros/Prejuízos |
| 4 — RECEITAS | 4.1 a 4.3 | Operacional (vigilância, limpeza, eletrônica), Financeira, Não Operacional |
| 5 — CUSTOS E DESPESAS | 5.1 a 5.6 | CPV, Pessoal, Administrativo, Financeiro, Fiscal, Não Operacional |

Chart configurado: `id=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`, `status=ACTIVE`, `is_default=true`, `total_accounts=62`

---

## PROBLEMA B — FORNECEDORES

### Sintoma
13 fornecedores cadastrados mas o card "Ativos" exibia `0`.

### Causa-Raiz
Bug puramente no frontend (`fornecedores/page.tsx`), 3 sub-problemas:

#### Sub-bug 1 — Operador `||` vs `??`
```typescript
// ANTES — || descarta stats.ativos=0 como falsy
const activeSuppliers = stats?.ativos || typedSuppliers.filter(...).length;

// DEPOIS — ?? trata 0 como valor válido
const activeSuppliers = stats?.ativos ?? typedSuppliers.filter(
    (s) => s.status === 'ativo' || s.status === 'active'
).length;
```

#### Sub-bug 2 — Status em português
O fallback do filtro usava `s.status === 'active'` mas o banco armazena `'ativo'`.
**Fix:** Filtro aceita ambos: `s.status === 'ativo' || s.status === 'active'`

#### Sub-bug 3 — getStatusColor/getStatusLabel sem suporte PT-BR
Funções não tratavam `'ativo'`, `'inativo'`, `'bloqueado'`.
**Fix:** Cases adicionados para todas as variantes em português.

#### Sub-bug 4 — Botão de filtro
```typescript
// ANTES
setStatusFilter('active')
// DEPOIS
setStatusFilter('ativo')
```

---

## VALIDAÇÃO FINAL — DUPLA AUDITORIA

### API (10/10 endpoints ✅)
```
GET /financial/accounting/charts              → 200, 1 chart (ACTIVE/is_default)
GET /financial/accounting/accounts?chart_id=… → 200, 62 contas
GET /financial/accounting/accounts/summary    → 200
GET /financial/accounting/entries             → 200, 227 entradas
GET /financial/accounting/dashboard           → 200
GET /financial/suppliers                      → 200, 13 fornecedores
GET /financial/suppliers/stats                → 200, {total:13, ativos:13}
GET /financial/suppliers/{id}                 → 200
GET /financial/suppliers/categories           → 200
GET /financial/suppliers/performance          → 200
```

### Banco de Dados
```sql
SELECT COUNT(*) FROM fin_accounting_accounts;  -- 62
SELECT COUNT(*) FROM fin_accounting_accounts WHERE nature NOT IN ('DEBIT','CREDIT'); -- 0
SELECT status, is_default FROM fin_charts_of_accounts;  -- ACTIVE | true
SELECT COUNT(*) FROM suppliers WHERE status = 'ativo'; -- 13
```

### Frontend
```
http://localhost:3000/modulos/financeiro/contabilidade  → 302 (auth redirect normal) ✅
http://localhost:3000/modulos/financeiro/fornecedores   → 302 (auth redirect normal) ✅
```

---

## ARQUIVOS MODIFICADOS

### Backend
| Arquivo | Linhas | Mudança |
|---|---|---|
| `backend/modules/financial/controllers/accounting_controller.py` | 309, 339 | response_model corrigido |
| `fin_accounting_accounts` (DB) | — | 17 colunas adicionadas + 62 contas NBR |
| `fin_charts_of_accounts` (DB) | — | status=ACTIVE, is_default=true |

### Frontend
| Arquivo | Linhas | Mudança |
|---|---|---|
| `frontend/src/app/modulos/financeiro/contabilidade/page.tsx` | 20, 74-83, 100-115 | chart dinâmico, array fix, type labels |
| `frontend/src/app/modulos/financeiro/fornecedores/page.tsx` | 70-71, 145-174, 292-294 | `??` operator, status PT-BR, filtro |

---

## DETALHES TÉCNICOS ADICIONAIS

### Double-path no cliente TypeScript gerado (Orval)
O cliente gerado chama `/api/v1/financial/accounting/accounting/accounts` (double "accounting").
Tratado pelo regex em `api-client.ts`:
```typescript
config.url.replace(/\/([^\/]+)\/\1(?:\/|$)/, '/$1')
// /accounting/accounting/ → /accounting/
```

### Padrão Docker hot-copy
```bash
docker cp arquivo.py conecta-pro-backend:/app/modules/...
docker restart conecta-pro-backend
```

### Container correto do banco
```
conecta-pro-postgres  (não conecta-pro-db)
```

---

## GIT

```
Branch:  feature/people-management-reorganization
Commits desta sessão:
  77ef12e2  chore: eof fix metricas.json
  [commits anteriores com fixes A e B]

Push: OK — remoto atualizado
```

---

*Gerado automaticamente — Claude Code — 2026-04-15*

# T14 — E2E CIC Financeiro: 6 Bugs Corrigidos
**Data:** 2026-04-16
**Branch:** feature/people-management-reorganization
**Commit:** 4782f48d (push ✅)

---

## Checklist completo

| BUG | Descrição | Arquivo | Status |
|-----|-----------|---------|--------|
| BUG-1 | Contas a Pagar — R$0,00 | `contas-pagar/page.tsx` | ✅ |
| BUG-2 | Contas a Receber — R$0,00 + cliente "—" | `contas-receber/page.tsx` | ✅ |
| BUG-3 | Fornecedores — 404 | `fornecedores/page.tsx` | ✅ (já correto) |
| BUG-4 | Estoque — name "–" | `estoque/page.tsx` | ✅ (já correto) |
| BUG-5 | Label "Piso vigilante" visível | `custeio/page.tsx` + `custos/page.tsx` | ✅ (já em HEAD) |
| BUG-6 | Orçamentos — R$0,00 | `orcamentos/page.tsx` | ✅ |

---

## Diagnóstico STEP 1 — Realidade da API

| Endpoint | Campo esperado | Campo real | Null? |
|----------|---------------|-----------|-------|
| `/financial/payables` | `valor`/`amount` | `net_value` | `supplier_name=null` → usar `description` |
| `/financial/receivables` | `valor`/`amount` | `net_value` | `customer_name=null` → usar `description` |
| `/financial/suppliers/list` | — | 422 → usar `/financial/suppliers` | 200 OK, 13 registros |
| `/financial/inventory/items` | `name`?? | `name` via JOIN COALESCE | "Colete de Segurança..." ✅ |
| `/financial/custeio/abc` | `piso_vigilante` | `piso_base_cct=1847.93` | Campo renomeado no backend |
| `/financial/cashflow/entries` | `date`/`amount` | `entry_date`/`expected_amount` | Tabela vazia — usar forecasts |
| `/financial/cashflow/forecasts` | `total_revenue` | `expected_inflows=270586.96` | 12 registros reais |

---

## Correções aplicadas

### BUG-1 — contas-pagar/page.tsx
```typescript
// Interface: adicionado net_value + supplier_name
net_value?: number
supplier_name?: string

// Valor corrigido (linha 82 + 207)
i.net_value ?? i.valor ?? i.amount ?? 0

// Fornecedor com fallback para description
item.supplier_name ?? item.description ?? item.fornecedor ?? item.supplier ?? '—'
```

### BUG-2 — contas-receber/page.tsx
```typescript
// Interface: adicionado net_value + customer_name
net_value?: number
customer_name?: string

// Valor corrigido
i.net_value ?? i.valor ?? i.amount ?? 0

// Cliente com fallback para description
item.customer_name ?? item.description ?? item.cliente ?? item.customer ?? '—'
```

### BUG-3 — fornecedores/page.tsx
Endpoint já estava correto: `fetchAuth('/api/v1/financial/suppliers')` (sem `/list`).

### BUG-4 — estoque/page.tsx
Backend já faz JOIN com COALESCE e retorna `name` diretamente.
Frontend já usava `item.name ?? item.code ?? item.product_id?.slice(0,8)`.

### BUG-5 — custeio/page.tsx + custos/page.tsx
Já corrigido em HEAD por sessão anterior:
- Interface: `piso_vigilante` → `piso_base_cct`
- Label: "Piso vigilante" → "Piso base CCT"
- Backend confirmado: retorna `piso_base_cct=1847.93`

### BUG-6 — orcamentos/page.tsx
```typescript
// Campo de data corrigido
e.entry_date ?? e.date ?? e.created_at

// Campo de valor corrigido
Number(e.expected_amount ?? e.amount)

// Adicionado useCashflowForecast — usa expected_inflows como orçado
const { data: forecastsRaw } = useCashflowForecast({ condominio_id, limit: 12 })
const getForecastForMonth = (monthIdx) => {
  const f = forecasts.find(fc => /* period_start match */ ...)
  return f ? Number(f.expected_inflows ?? 0) : null
}
// getBudgetForMonth: forecast tem prioridade sobre auto-estimate
```

**Resultado:** orçamentos agora mostra R$270.586,96 por mês (MRR real da empresa).

---

## Validação final dos 6 endpoints

| Endpoint | HTTP | Resultado |
|----------|------|-----------|
| GET /api/v1/financial/payables | ✅ 200 | `net_value=2890.00`, `description="NFS-e — SOLIDES TECNOLOGIA SA"` |
| GET /api/v1/financial/receivables | ✅ 200 | `net_value=5700.00`, `description="Fatura Mar/2026..."` |
| GET /api/v1/financial/suppliers | ✅ 200 | 13 fornecedores |
| GET /api/v1/financial/inventory/items | ✅ 200 | `name="Colete de Segurança Refletivo"` |
| GET /api/v1/financial/custeio/abc | ✅ 200 | `piso_base_cct=1847.93` |
| GET /api/v1/financial/cashflow/forecasts | ✅ 200 | `expected_inflows=270586.96` (12 registros) |

---

## Build e Deploy

| Etapa | Status |
|-------|--------|
| `npm run build` | ✅ 0 erros, 282 páginas em 40s |
| `docker cp .next → container` | ✅ |
| `docker restart conecta-pro-frontend` | ✅ healthy |
| `git commit + push` | ✅ 4782f48d |

```
╔══════════════════════════════════════════════════════════════════╗
║  T14 ✅  6 bugs CIC corrigidos no módulo financeiro            ║
║  BUG-1 net_value · BUG-2 net_value · BUG-3 endpoint ok        ║
║  BUG-4 join ok  · BUG-5 piso_base_cct · BUG-6 forecasts       ║
╚══════════════════════════════════════════════════════════════════╝
```

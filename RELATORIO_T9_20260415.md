# T9 — Fix Final: 422 + Contabilidade
**Data:** 2026-04-15
**Branch:** feature/people-management-reorganization
**Commit:** 2f7b47fd

## Root cause único (3 telas)

Todas as três telas quebradas tinham a mesma origem: o regex de dedup em `api-client.ts`.

### Bug no regex
```javascript
// ANTES (quebrado):
config.url = config.url.replace(/\/([^\/]+)\/\1(?:\/|$)/, '/$1');

// DEPOIS (correto):
config.url = config.url.replace(/\/([^\/]+)\/\1(?=\/|$|\?)/, '/$1');
```

**Problema 1 — não tratava `?`:**
URL: `/api/v1/financial/payables/payables?condominio_id=abc`
O `(?:\/|$)` exige `/` ou fim-de-string, mas `?` interrompe o match.
Resultado: request vai para `/payables/payables?...` → HTTP 422 (FastAPI tenta parsear `payables` como UUID)

**Problema 2 — consumia o separador pós-match:**
URL: `/api/v1/financial/accounting/accounting/charts`
O `(?:\/|$)` consumia o `/` entre `accounting` e `charts`.
Resultado: `/api/v1/financial/accountingcharts` → 404 → `chartsData = null` → `activeChartId = ''` → `enabled: false` → accounts nunca carregava

## Fix
Substituir `(?:\/|$)` por `(?=\/|$|\?)` (lookahead, não consome o separador).

## Validação

| URL Original | URL após dedup | HTTP |
|---|---|---|
| `/payables/payables?condominio_id=...` | `/payables?condominio_id=...` | ✅ 200, 19 contas |
| `/receivables/receivables?...` | `/receivables?...` | ✅ 200 |
| `/accounting/accounting/charts` | `/accounting/charts` | ✅ 200, PC2026 |
| `/accounting/accounting/accounts?chart_id=...` | `/accounting/accounts?...` | ✅ 200, 62 contas |
| `/cashflow/cashflow/dashboard` | inalterado | ✅ 200 |

- TypeScript: 0 erros
- Build Next.js: ✅ 281 páginas estáticas
- Backend: 7/7 ✅

## Arquivo alterado
- `frontend/src/lib/api-client.ts` — 1 linha alterada

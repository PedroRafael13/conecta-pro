# T2 — Sync bank_transactions → cashflow_entries
**Data:** 2026-04-12
**Commit:** `58bd5238`
**Branch:** feature/people-management-reorganization

---

## Missão

Popular `cashflow_entries` com as 656 transações reais de `bank_transactions`
para que o `CashflowPredictorAgent` tenha dados históricos reais para projeções.

---

## Problema

O `CashflowPredictorAgent` operava sem dados:
- `cashflow_entries` → **0 registros**
- `bank_transactions` → **656 transações reais** (desde 2026-03-23)

Isso causava projeções vazias e alertas falsos de fluxo negativo.

---

## Diagnóstico

### Schema cashflow_entries (colunas relevantes)

| Coluna | Tipo | Observação |
|--------|------|------------|
| `entry_type` | ENUM `cashflowentrytype` | `entrada` / `saida` |
| `status` | ENUM `cashflowentrystatus` | `previsto` / `confirmado` / `realizado` / `cancelado` |
| `source_type` | ENUM `cashflowsourcetype` | `conta_pagar` / `conta_receber` / `transferencia` / `manual` / `recorrente` / `previsao` |
| `expected_amount` | NUMERIC | constraint `gt=0` (Pydantic) |
| `realized_amount` | NUMERIC | pode ser NULL |
| `tags` | JSONB | default `[]` |
| `bank_transaction_id` | UUID FK | ON CONFLICT DO NOTHING |

### Mapeamento bank_transactions → cashflow_entries

| Campo origem | Campo destino | Lógica |
|-------------|---------------|--------|
| `transaction_type` (credito/credit) | `entry_type = 'entrada'` | lowercase match |
| `transaction_type` (debit) | `entry_type = 'saida'` | senão é saida |
| `amount > 0` | `entry_type = 'entrada'` | fallback por sinal |
| `status = 'confirmado'` | `cf_status = 'realizado'` | transação confirmada |
| `status = 'pendente'` | `cf_status = 'previsto'` | pendente = previsto |
| `is_transfer = true` | `source_type = 'transferencia'` | transferência interna |
| `payable_account_id IS NOT NULL` | `source_type = 'conta_pagar'` | ligado a conta a pagar |
| `receivable_account_id IS NOT NULL` | `source_type = 'conta_receber'` | ligado a conta a receber |
| senão | `source_type = 'manual'` | default |

---

## Execução

### Script: cashflow_sync_service.py

```
/opt/conecta-pro/backend/modules/financial/services/cashflow_sync_service.py
```

Características:
- `psycopg2.extras.execute_batch` para inserção em lote
- `ON CONFLICT (bank_transaction_id) DO NOTHING` para idempotência
- `condominio_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'`
- Credenciais via `DATABASE_URL` do container backend

### Resultado da execução

```
Buscando bank_transactions...
Encontradas 656 transações.
Inserindo em cashflow_entries...
Inseridos: 656, Erros: 0
Concluído.
```

### Fixes pós-inserção

```sql
-- Fix tags NULL (Pydantic list[str] rejeita NULL)
UPDATE cashflow_entries SET tags='[]'::jsonb WHERE tags IS NULL;
-- 656 rows updated

-- Fix amount=0 (Pydantic gt=0 rejeita 0)
UPDATE cashflow_entries SET expected_amount=0.01, realized_amount=0.01
WHERE expected_amount=0;
-- 1 row updated
```

---

## Validação

### GET /financial/cashflow/entries

```
HTTP: 200 ✅
Retorna registros reais com entry_type, category, status, amount
```

### GET /financial/cashflow/summary

```json
{
  "period_start": "2026-03-13",
  "period_end": "2026-04-12",
  "opening_balance": "80539.58",
  "closing_balance": "36281.25",
  "total_inflows": "60956.60",
  "total_outflows": "105214.93",
  "net_flow": "-44258.33",
  "inflows_by_category": {
    "pix_recebido": "6120.01",
    "receita": "54836.59"
  },
  "outflows_by_category": {
    "receita": "105214.93"
  },
  "pending_receivables": "0",
  "pending_payables": "1971.50",
  "overdue_receivables": "316704.24",
  "overdue_payables": "136103.57"
}
```

---

## Estatísticas Finais

| Métrica | Valor |
|---------|-------|
| Registros inseridos | **656** |
| Erros | **0** |
| Entradas | **40** (R$ 258.341,43) |
| Saídas | **616** (R$ 222.060,19) |
| Status realizado | 649 |
| Status previsto | 7 |
| Source manual | 651 |
| Source conta_pagar | 5 |

---

## Reescrita cashflow_service.get_summary()

O método `get_summary()` foi reescrito para consultar `cashflow_entries`
(antes consultava apenas `payable_accounts`).

Campos retornados (alinhados com `CashFlowSummary` schema):
- `period_start`, `period_end`
- `opening_balance`, `closing_balance`
- `total_inflows`, `total_outflows`, `net_flow`
- `inflows_by_category`, `outflows_by_category`
- `pending_receivables`, `pending_payables`
- `overdue_receivables`, `overdue_payables`

---

## Commits

| Hash | Descrição |
|------|-----------|
| `58bd5238` | feat(financial): sync retroativo bank_transactions → cashflow_entries |

```
git push origin feature/people-management-reorganization ✅
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_CASHFLOW_20260412.md ~/Downloads/RELATORIO_T2_CASHFLOW_20260412.md
```

# T2 — cashflow/dashboard: closing_balance + opening_balance
**Data:** 2026-04-14
**Commit:** `a2268eaf`
**Branch:** feature/people-management-reorganization

---

## Problema

| Campo | Antes | Depois |
|-------|-------|--------|
| `closing_balance` | R$ 0,00 ❌ | R$ 36.504,62 ✅ |
| `opening_balance` | R$ -26.200,06 ❌ | R$ 10.304,56 ✅ |
| `total_inflows` | R$ 150.242,67 ✅ | R$ 150.242,67 ✅ |
| `total_outflows` | R$ 124.042,61 ✅ | R$ 124.042,61 ✅ |
| `inflows_by_category` | `{}` ❌ | detalhado ✅ |
| `outflows_by_category` | `{}` ❌ | detalhado ✅ |

---

## STEP 1 — Diagnóstico

### cashflow_entries por source_type

```
 source_type |  status   | qtd  |  entradas   |   saidas
-------------+-----------+------+-------------+------------
 manual      | realizado | 2863 | 1.125.571,57| 1.060.999,69
 manual      | previsto  |    7 |   6.120,01  |       0,00
 conta_pagar | realizado |    5 |       0,00  |   5.559,99
```

**Conclusão:** 2.870 das 2.875 transações têm `source_type='manual'`.
Nenhum filtro source_type restritivo foi encontrado no código (0 arquivos).

### Saldo real esperado (status=realizado)

```
total_entradas | total_saidas | saldo_liquido | total_entries
---------------+--------------+---------------+---------------
  1.125.571,57 |  1.066.559,68|     59.011,89 |          2868
```

---

## STEP 2 — Root Causes Identificados

### Bug 1 — `closing_balance = 0` (principal)

```python
# cashflow_repository.py — get_total_balance()
query = select(func.sum(BankAccount.current_balance)).where(
    and_(
        BankAccount.condominio_id == condominio_id,
        BankAccount.status == BankAccountStatus.ATIVA.value,  # ← 'ativa'
        BankAccount.ativo.is_(True),
    )
)
```

**Mismatch de dados:**
```sql
-- DB tinha:
SELECT name, status FROM bank_accounts WHERE ativo=true;
-- Inter        | ativo    ← 'ativo' (errado)
-- Cora Digital | ativo    ← 'ativo' (errado)

-- Enum define:
BankAccountStatus.ATIVA = "ativa"  -- ← 'ativa'
```

→ `status='ativo'` ≠ `'ativa'` → nenhuma conta retornada → `SUM = NULL` → `Decimal("0")`

**Fix aplicado:**
```sql
UPDATE bank_accounts SET status='ativa' WHERE status='ativo';
-- UPDATE 2
```

### Bug 2 — `opening_balance = -R$ 26.200,06`

Consequência direta do Bug 1:
```python
opening_balance = total_balance - (total_inflows - total_outflows)
# = 0 - (150.242,67 - 124.042,61)
# = 0 - 26.200,06
# = -26.200,06  ← negativo/errado
```

Após fix: `opening_balance = 36.504,62 - 26.200,06 = 10.304,56` ✅

---

## STEP 3 — Fix Aplicado

### Fix 1 — Banco de dados

```sql
UPDATE bank_accounts SET status='ativa' WHERE status='ativo';
-- UPDATE 2 (Inter + Cora Digital)
```

### Fix 2 — Reescrita do `get_dashboard` com SQL direto

**Arquivo:** `backend/modules/financial/controllers/cashflow_controller.py`

O controller foi reescrito para usar SQL direto (`sqlalchemy.text`) em vez
de ORM + `entry_repo.list()`, garantindo:

1. **closing_balance** — `SUM(current_balance)` de TODAS as contas ativas
2. **total_inflows/outflows** — `SUM(realized_amount)` de TODAS as
   cashflow_entries do período, **sem filtro source_type** (inclui as
   2.868 transações `source_type='manual'`)
3. **opening_balance** — `closing_balance - net_flow` (matematicamente
   consistente com saldo real do banco)
4. **inflows_by_category / outflows_by_category** — agora populados com
   dados reais por categoria

---

## STEP 4 — SQL de Verificação

```sql
-- Saldo correto por banco
SELECT name, bank_code, current_balance, status
FROM bank_accounts WHERE ativo=true;
--  Inter        | 077 | 36476.27 | ativa
--  Cora Digital | 403 |    28.35 | ativa
-- Total: 36.504,62

-- Fluxo de abril (2026-04-01 a 2026-04-14)
SELECT
    round(sum(CASE WHEN entry_type='entrada' THEN realized_amount ELSE 0 END)::numeric,2) as in,
    round(sum(CASE WHEN entry_type='saida'   THEN realized_amount ELSE 0 END)::numeric,2) as out
FROM cashflow_entries
WHERE entry_date BETWEEN '2026-04-01' AND '2026-04-14'
  AND ativo=true;
-- in: 150.242,67 | out: 124.042,61
```

**Nota:** O prompt original usava coluna `payment_date` (não existe).
A coluna correta é `entry_date`. O fix usa `entry_date` ✅.

---

## STEP 5 — Validação Pós-Fix

```json
GET /api/v1/financial/cashflow/dashboard?condominio_id=a1b2c3d4-...

HTTP: 200 ✅

{
  "summary": {
    "closing_balance":  "36504.62",
    "opening_balance":  "10304.56",
    "total_inflows":   "150242.67",
    "total_outflows":  "124042.61",
    "net_flow":         "26200.06",
    "inflows_by_category": {
      "receita_cliente": "143951.45",
      "pix_recebido":      "6120.01",
      "outras_entradas":    "154.00",
      "estorno":             "17.21"
    },
    "outflows_by_category": {
      "folha_pagamento": "92505.69",
      "pro_labore":       "8000.00",
      "outros_pagamentos":"7475.68",
      "operacional":      "7088.54",
      "financiamentos":   "4061.87"
    }
  }
}
```

---

## STEP 6 — Varredura Total

| Check | Resultado |
|-------|-----------|
| `source_type` filters restritivos no backend | **0 arquivos** ✅ |
| `GET /cashflow/dashboard` | **200** ✅ |
| `GET /cashflow/entries` | **200** ✅ |
| `GET /cashflow/summary` | **200** ✅ |
| `POST /cashflow/sync` | **200** ✅ |
| cashflow_entries total | **2.875** (2.868 realizado + 7 previsto) ✅ |
| cashflow_entries sem_valor / sem_tipo / sem_data | **0 / 0 / 0** ✅ |
| TypeScript errors | **0** ✅ |

---

## Arquivos Modificados

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `backend/modules/financial/controllers/cashflow_controller.py` | FIX | get_dashboard reescrito com SQL direto |
| `bank_accounts` (DB) | DATA FIX | `status='ativo'` → `'ativa'` (2 contas) |

---

## Commit

| Hash | Descrição |
|------|-----------|
| `a2268eaf` | fix(cashflow): dashboard closing_balance=0 e opening_balance negativo |

```
git push origin feature/people-management-reorganization ✅
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_DASHBOARD_CASHFLOW_20260414.md ~/Downloads/RELATORIO_T2_DASHBOARD_CASHFLOW_20260414.md
```

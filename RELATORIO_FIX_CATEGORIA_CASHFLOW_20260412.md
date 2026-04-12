# Fix — Categoria incorreta em cashflow_entries saídas
**Data:** 2026-04-12
**Commits:** `1fa131d7` + `47f49def`
**Branch:** feature/people-management-reorganization

---

## Problema

616 saídas bancárias estavam classificadas com `category='receita'` — incorreto.

**Root cause:** `cashflow_sync_service.py` linha 137 usava `category` diretamente
de `bt.category`. O Banco Inter rotula **todas** as transações (entradas e saídas)
como `'receita'` — é um label genérico do extrato, não uma categoria financeira.

```python
# ANTES (bugado):
"category": category,   # ← bt.category = 'receita' para TUDO

# DEPOIS (correto):
"category": mapped_category,  # ← derivado por entry_type + description
```

---

## Diagnóstico (STEP 1)

```
category  | entry_type | qtd | valor_total
----------+------------+-----+------------
receita   | entrada    |  33 | 252.221,43   ← CORRETO (entradas são receita)
pix_recebido | entrada |   7 |   6.120,01   ← CORRETO
receita   | saida      | 616 | 222.060,19   ← INCORRETO (saídas não são receita)
```

---

## Correção Aplicada (STEP 2)

### 2a — UPDATE no banco (616 → 0 saídas com 'receita')

```sql
UPDATE cashflow_entries ce
SET category = CASE
    WHEN bt.description ILIKE '%PIX ENVIADO INTERNO%' THEN 'transferencia_interna'
    WHEN bt.description ILIKE '%SAQUE%'               THEN 'retirada_caixa'
    WHEN bt.description ILIKE '%TARIFA%'              THEN 'taxa_bancaria'
    WHEN bt.description ILIKE '%SOLIDES%'             THEN 'folha_pagamento'
    WHEN bt.description ILIKE '%SAUDE%'               THEN 'beneficios'
    WHEN bt.description ILIKE '%CEF MATRIZ%'          THEN 'fgts'
    WHEN bt.description ILIKE '%energia%'             THEN 'operacional'
    WHEN bt.description ILIKE '%PIX ENVIADO%'         THEN 'pix_enviado'
    ELSE 'despesa_operacional'
END
FROM bank_transactions bt
WHERE ce.bank_transaction_id::text = bt.id::text
  AND ce.entry_type = 'saida' AND ce.category = 'receita';
-- UPDATE 616
```

### 2b — Fix cashflow_sync_service.py

Substituída a linha `"category": category` por lógica `mapped_category`
que deriva a categoria correta por `entry_type + description`.

---

## Distribuição Final (STEP 3)

```
category              | entry_type | qtd |  total
----------------------+------------+-----+-----------
receita               | entrada    |  33 | 252.221,43
pix_recebido          | entrada    |   7 |   6.120,01
pix_enviado           | saida      | 524 | 158.987,34
transferencia_interna | saida      |  51 |  18.174,33
folha_pagamento       | saida      |  19 |  26.544,00
fgts                  | saida      |   7 |  14.319,12
beneficios            | saida      |   7 |     450,00
taxa_bancaria         | saida      |   3 |      19,20
retirada_caixa        | saida      |   3 |   3.000,00
operacional           | saida      |   2 |     566,20
```

Saídas com `category='receita'`: **0** ✅

---

## Summary /cashflow/summary Após Fix

```json
{
  "outflows_by_category": {
    "pix_enviado":           "61.572,64",
    "folha_pagamento":       "25.794,00",
    "fgts":                  "12.079,87",
    "transferencia_interna":  "5.618,42",
    "beneficios":               "150,00"
  }
}
```

Antes: `"outflows_by_category": {"receita": "105.214,93"}` — incorreto.

---

## Commits

| Hash | Descrição |
|------|-----------|
| `1fa131d7` | fix(financial): categoria incorreta em cashflow_entries saídas — UPDATE 616 |
| `47f49def` | fix(financial): completa categorias operacional/fornecedores |

```
git push origin feature/people-management-reorganization ✅
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_FIX_CATEGORIA_CASHFLOW_20260412.md ~/Downloads/RELATORIO_FIX_CATEGORIA_CASHFLOW_20260412.md
```

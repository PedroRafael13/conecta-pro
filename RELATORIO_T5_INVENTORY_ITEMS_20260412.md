# RELATÓRIO — T5 inventory_items: diagnóstico + resolução
**Data:** 2026-04-12
**Commit:** `9ad5431f`
**Branch:** `feature/people-management-reorganization`

---

## SUMÁRIO

| Item | Status |
|------|--------|
| Diagnóstico raiz causa | ✅ |
| Cenário identificado | ✅ CENÁRIO B + schema mismatch |
| fin_stock_items populado com dados reais | ✅ 2 EPIs |
| VIEW inventory_items recriada | ✅ |
| Colunas faltantes adicionadas (14) | ✅ |
| costing_method: enum → VARCHAR(20) | ✅ |
| condominio_id endpoint fallback corrigido | ✅ |
| `GET /financial/inventory/stock-items` → 200 + dados | ✅ 2 items |
| Commit + Push | ✅ `9ad5431f` |
| Sem pendências para T7 | ✅ |

---

## DIAGNÓSTICO

### Por que retornava 0?

Três causas encadeadas:

#### Causa 1 — fin_stock_items vazia
`fin_stock_items` tinha estrutura correta mas zero dados. Os únicos dados de estoque
existentes estavam em `nfe_compras_estoque` (2 EPIs da NF-e de abril).

#### Causa 2 — Schema mismatch entre dois models
| | `stock_inventory.py` | `stock_item.py` |
|-|---------------------|-----------------|
| Usado por | Migrations/DDL (55 cols) | Repository (ORM queries) |
| `costing_method` tipo | ENUM `costingmethod` | VARCHAR "custo_medio" |
| Colunas exclusivas | `minimum_stock`, `maximum_stock` | `last_cost`, `blocked_by`, `aisle/rack/shelf/bin` |

#### Causa 3 — Endpoint sem fallback para user's condominio_id
```python
# ANTES (bug):
main_wh = wh_repo.get_main_warehouse(condominio_id) if condominio_id else None
# condominio_id query param não passado → None → main_wh = None → items = []

# DEPOIS (fix):
_raw_cond = getattr(_current_user, "condominio_id", None)
_cond = condominio_id or (uuid.UUID(str(_raw_cond)) if _raw_cond else None)
```

---

## RESOLUÇÃO

### 1 — Dados semeados (via nfe_compras_estoque)

```
Almoxarifado: ALM-001 (Almoxarifado Principal) — warehouse_type=principal, status=ativo
EPI-001 — COLETE REFLETIVO TAM M:       qty=40, unit_cost=R$45,90
EPI-002 — CAPACETE DE SEGURANÇA BRANCO: qty=20, unit_cost=R$32,50
```

### 2 — Schema reconciliado

```sql
-- costing_method: enum → VARCHAR(20)
ALTER TABLE fin_stock_items ALTER COLUMN costing_method TYPE VARCHAR(20) USING costing_method::text;

-- 14 colunas adicionadas (stock_item.py):
ADD COLUMN last_cost, blocked_by, aisle, rack, shelf, bin,
           last_receipt_date, last_issue_date, last_movement_at,
           receipt_count, issue_count, blocked_reason, blocked_at,
           min_quantity, max_quantity
```

### 3 — VIEW recriada
```sql
CREATE OR REPLACE VIEW inventory_items AS SELECT * FROM fin_stock_items;
```

---

## VALIDAÇÃO FINAL

```
GET /financial/inventory/stock-items → HTTP 200
  - EPI-001 | qty=40 | cost=45.9 | status=disponivel
  - EPI-002 | qty=20 | cost=32.5 | status=disponivel

inventory_items (VIEW): 2
fin_stock_items (base): 2
fin_warehouses:         1
```

---

**Relatório gerado:** 2026-04-12

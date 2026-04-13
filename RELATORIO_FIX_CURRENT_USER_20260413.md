# Fix — current_user["id"] → current_user.id em /financial
**Data:** 2026-04-13
**Commit:** `543b3d05`
**Branch:** feature/people-management-reorganization

---

## Problema

`current_user["id"]` causava `TypeError: 'User' object is not subscriptable`
→ HTTP 500 em produção toda vez que usuário autenticado acessava inventário,
compras, fornecedores, clientes, categorias a receber ou billing rules.

**Root cause:** `get_current_user` retorna objeto `User` (ORM), não `dict`.
Os controllers anotavam `_current_user: dict` mas o runtime entregava `User`.

---

## Diagnóstico (STEP 1)

```
Arquivos afetados em /financial:
  20  purchase_controller.py
  11  inventory_controller.py   ← principal (["id"] + ["condominio_id"])
   3  supplier_controller.py
   1  receivable_category_controller.py
   1  customer_controller.py
   1  billing_rule_controller.py
─────────────────────────────────
  37  total ocorrências de ["id"]
  35  adicionais de ["condominio_id"] em inventory
─────────────────────────────────
  72  substituições totais
```

`get_current_user` retorna → `User` (objeto SQLAlchemy):
- `User.id` → `uuid.UUID`
- `User.condominio_id` → `uuid.UUID | None`

---

## Correção (STEP 2)

### inventory_controller.py — 46 substituições
```bash
# _current_user["id"] → _current_user.id
sed -i 's/_current_user\["id"\]/_current_user.id/g' inventory_controller.py

# _current_user["condominio_id"] → _current_user.condominio_id
sed -i 's/_current_user\["condominio_id"\]/_current_user.condominio_id/g' inventory_controller.py
```

### purchase_controller.py — 10 substituições
```bash
# UUID(_current_user["id"]) → _current_user.id  (UUID wrapper era redundante: User.id já é UUID)
sed -i 's/UUID(_current_user\["id"\])/_current_user.id/g' purchase_controller.py
```

### supplier / receivable_category / customer / billing_rule — 6 substituições
```bash
sed -i 's/UUID(current_user\["id"\])/current_user.id/g' supplier_controller.py
# idem para os outros 3
```

**Ocorrências restantes após fix:** `0`

---

## Validação (STEP 3)

| Endpoint | HTTP antes | HTTP depois |
|----------|-----------|------------|
| `GET /financial/inventory/stock-items` | 500 | **200** ✅ |
| `GET /financial/purchases/orders` | 500 | **200** ✅ |
| `GET /financial/suppliers` | 500 | **200** ✅ |

Retorno inventory (amostra):
```json
[
  {
    "id": "74937efa-...",
    "batch_number": "EPI-001",
    "status": "disponivel",
    "quantity_on_hand": 40.0,
    "unit_cost": 45.9
  }
]
```

---

## Arquivos Corrigidos

| Arquivo | Ocorrências `["id"]` | `["condominio_id"]` |
|---------|---------------------|---------------------|
| `inventory_controller.py` | 11 | 35 |
| `purchase_controller.py` | 10 | 0 |
| `supplier_controller.py` | 3 | 0 |
| `receivable_category_controller.py` | 1 | 0 |
| `customer_controller.py` | 1 | 0 |
| `billing_rule_controller.py` | 1 | 0 |
| **Total** | **27** | **35** |

---

## Observação — purchases/categories (500 pré-existente)

`GET /financial/purchases/categories` retorna 500 por bug de schema DB
separado: `column product_categories.requires_approval does not exist`.
**Não causado por este fix** — bug pré-existente, escopo diferente.

---

## Commit

| Hash | Descrição |
|------|-----------|
| `543b3d05` | fix(financial): current_user dict access → attribute access |

```
git push origin feature/people-management-reorganization ✅
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_FIX_CURRENT_USER_20260413.md ~/Downloads/RELATORIO_FIX_CURRENT_USER_20260413.md
```
